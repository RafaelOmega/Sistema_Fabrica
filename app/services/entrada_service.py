import re

from sqlalchemy.exc import IntegrityError

from app.models.entrada import Entrada
from app.repositories.consumo_producao_repository import (
    ConsumoProducaoRepository,
)
from app.repositories.entrada_repository import EntradaRepository
from app.repositories.ficha_tecnica_repository import FichaTecnicaRepository
from app.repositories.movimento_estoque_repository import (
    MovimentoEstoqueRepository,
)
from app.repositories.regra_produto_especial_repository import (
    RegraProdutoEspecialRepository,
)
from app.utils.logger import get_logger

logger = get_logger("entrada_service")


class EntradaService:
    def __init__(self):
        self.repo = EntradaRepository()
        self.regra_repo = RegraProdutoEspecialRepository()
        # Dependências para o modo produção (ficha técnica)
        self.ficha_repo = FichaTecnicaRepository()
        self.movimento_repo = MovimentoEstoqueRepository()
        self.consumo_repo = ConsumoProducaoRepository()
        # Cache em memória das regras especiais por código de produto.
        # Evita ir ao banco a cada tecla digitada no código do produto
        # (a tela chama obter_regra_produto em tempo real).
        # O cache é invalidado automaticamente sempre que uma regra é
        # criada, editada ou removida através deste service.
        self._cache_regras = None

    def listar_todos(self):
        return self.repo.listar_todos()

    def buscar_por_id(self, entrada_id):
        return self.repo.buscar_por_id(entrada_id)

    def buscar_por_sequencia(self, sequencia):
        return self.repo.buscar_por_sequencia(sequencia)

    def buscar_com_itens(self, entrada_id):
        return self.repo.buscar_com_itens(entrada_id)

    def obter_proxima_sequencia(self):
        return self.repo.obter_proxima_sequencia()

    # ---------- Produção (ficha técnica) ----------

    def buscar_ficha_por_produto(self, produto_id):
        """Ficha técnica do produto acabado, ou None se não houver."""
        return self.ficha_repo.buscar_por_produto(produto_id)

    def _processar_producao(self, session, entrada, itens_data,
                            sacos_produzidos):
        """Baixa a matéria-prima da ficha técnica proporcionalmente ao
        total de sacos lançados no item (não à batida completa).
        Ex.: ficha de 21 sacos, item com 1 saco → baixa 1/21 de cada MP.
        O custo do produto acabado é o que a tela/cadastro já fornece —
        nada é recalculado aqui. DENTRO da transação do salvar()."""
        if len(itens_data) != 1:
            raise ValueError(
                "Lançamento de produção deve ter apenas o produto acabado."
            )
        item_pa = itens_data[0]
        produto_id = item_pa.get("produto_id")
        if not produto_id:
            raise ValueError("Item de produção sem produto informado.")

        ficha = self.ficha_repo.buscar_por_produto(produto_id)
        if not ficha:
            raise ValueError("Produto acabado sem ficha técnica cadastrada.")

        ficha, itens_ficha = self.ficha_repo.buscar_com_itens(ficha.id)
        if not itens_ficha:
            raise ValueError("Ficha técnica sem itens de matéria-prima.")

        if not sacos_produzidos or float(sacos_produzidos) <= 0:
            raise ValueError("Informe a quantidade produzida (sacos).")

        # Proporção: baixa proporcional aos SACOS do item, não à batida
        # completa.
        fator = float(sacos_produzidos) / float(ficha.sacos_batida)

        for item in itens_ficha:
            qtd_kg = float(item["quantidade_kg"]) * fator
            # Saldo NEGATIVO é permitido (decisão de negócio) — não há
            # bloqueio por estoque insuficiente.
            saldo = self.movimento_repo.saldo_atual(item["produto_id"])
            custo_medio = saldo["custo_medio"]

            self.consumo_repo.criar_com_movimento(
                session=session,
                entrada_id=entrada.id,
                produto_id=item["produto_id"],
                quantidade_kg=qtd_kg,
                custo_unitario=custo_medio,
                data_producao=entrada.data_entrada,
            )

        logger.info(
            f"Produção processada | entrada_id={entrada.id} | "
            f"sacos={sacos_produzidos} | fator={fator:.4f} | "
            f"itens_baixa={len(itens_ficha)}"
        )

    # ---------- Regras de produto especial (existente) ----------

    def obter_regra_produto(self, codigo_produto):
        """Retorna a regra especial do produto (dict com 'descricao' e
        'divisor_custo'), ou None se não houver.

        As regras agora vêm do banco (tabela regras_produtos_especiais)
        em vez de um dicionário fixo no código-fonte: adicionar um novo
        produto especial não exige mais alterar código nem gerar um
        novo build/exe.
        """
        if self._cache_regras is None:
            self._carregar_cache_regras()
        return self._cache_regras.get(str(codigo_produto))

    def _carregar_cache_regras(self):
        regras = self.regra_repo.listar_todos()
        self._cache_regras = {
            regra.codigo_produto: {
                "descricao": regra.descricao,
                "divisor_custo": float(regra.divisor_custo),
            }
            for regra in regras
        }

    def invalidar_cache_regras(self):
        """Força releitura das regras especiais na próxima consulta.
        Chame após criar/editar/excluir uma regra."""
        self._cache_regras = None

    def listar_regras_produtos_especiais(self):
        return self.regra_repo.listar_todos()

    def salvar_regra_produto_especial(self, codigo_produto, descricao,
                                      divisor_custo, regra_id=None):
        codigo_produto = (codigo_produto or "").strip()
        descricao = (descricao or "").strip()
        if not codigo_produto:
            raise ValueError("Informe o código do produto.")
        if not descricao:
            raise ValueError("Informe a descrição da regra.")
        try:
            divisor = float(divisor_custo)
            if divisor <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Divisor de custo inválido.")
        resultado = self.regra_repo.salvar(
            codigo_produto=codigo_produto,
            descricao=descricao,
            divisor_custo=divisor,
            regra_id=regra_id,
        )
        self.invalidar_cache_regras()
        logger.info(
            f"Regra de produto especial salva: codigo={codigo_produto}, "
            f"divisor_custo={divisor}"
        )
        return resultado

    def excluir_regra_produto_especial(self, regra_id):
        sucesso = self.regra_repo.excluir_por_id(regra_id)
        if not sucesso:
            raise ValueError("Regra de produto especial não encontrada.")
        self.invalidar_cache_regras()
        logger.info(f"Regra de produto especial excluída: ID={regra_id}")
        return True

    # ---------- Validação ----------

    def _validar(self, sequencia, data_entrada, motivo_id, itens):
        if not re.fullmatch(r"\d+", str(sequencia)):
            raise ValueError("Sequência deve conter apenas números.")
        if not data_entrada:
            raise ValueError("Informe a data de entrada.")
        if not motivo_id:
            raise ValueError("Selecione um motivo de entrada.")
        if not itens:
            raise ValueError("Adicione pelo menos um item à entrada.")
        for i, item in enumerate(itens):
            if not item.get("produto_id"):
                raise ValueError(f"Item {i + 1}: produto não informado.")
            if not item.get("unidade"):
                raise ValueError(f"Item {i + 1}: unidade não informada.")
            try:
                qtde = float(item.get("quantidade", 0))
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: quantidade inválida.")
            if qtde <= 0:
                raise ValueError(
                    f"Item {i + 1}: quantidade deve ser maior que zero."
                )
            try:
                custo = float(item.get("custo", 0))
            except (ValueError, TypeError):
                raise ValueError(f"Item {i + 1}: custo inválido.")
            if custo < 0:
                raise ValueError(
                    f"Item {i + 1}: custo não pode ser negativo."
                )

    # ---------- salvar (com suporte a produção) ----------

    def salvar(self, sequencia, data_entrada, motivo_id, itens_data,
               entrada_id=None, alteracoes_custo=None,
               producao=False, sacos_produzidos=None):
        """
        Salva entrada + itens (+ alterações de custo se houver) na MESMA
        transação. Tudo commita ou tudo faz rollback.

        Com producao=True (motivo com flag de produção), também cria as
        baixas da ficha técnica (consumos_producao + kardex
        CONSUMO_PRODUCAO), proporcionalmente aos sacos do item — tudo na
        mesma transação. O custo do produto acabado é o fornecido pela
        tela (custo cadastrado).
        """
        self._validar(sequencia, data_entrada, motivo_id, itens_data)

        from app.database.connection import session_scope
        from app.models.motivo_entrada import Motivo_Entrada
        from app.repositories.alteracao_custo_repository import (
            AlteracaoCustoRepository,
        )
        from app.repositories.produto_repository import ProdutoRepository

        alteracao_repo = AlteracaoCustoRepository()
        produto_repo = ProdutoRepository()

        try:
            with session_scope() as session:
                # 0. Em produção, confere a flag do motivo no banco
                #    (não confia no que a tela mandou).
                if producao:
                    motivo = session.get(Motivo_Entrada, motivo_id)
                    if not motivo or not motivo.producao:
                        raise ValueError(
                            "Motivo selecionado não é de produção."
                        )

                # 1. Build/save entrada
                if entrada_id:
                    entrada = session.get(Entrada, entrada_id)
                    if not entrada:
                        raise ValueError(
                            "Entrada não encontrada para edição."
                        )
                    entrada.sequencia = sequencia
                    entrada.data_entrada = data_entrada
                    entrada.motivo_entrada_id = motivo_id
                else:
                    entrada = Entrada(
                        sequencia=sequencia,
                        data_entrada=data_entrada,
                        motivo_entrada_id=motivo_id,
                    )
                    session.add(entrada)

                session.flush()

                # 2. Produção: remove baixas anteriores (edição ou mudança
                # de motivo) e recria se ainda for produção.
                if entrada_id:
                    self.consumo_repo.excluir_por_entrada(session, entrada.id)
                if producao:
                    self._processar_producao(
                        session, entrada, itens_data, sacos_produzidos
                    )

                # 3. Salvar itens com diff (mesma sessão) + kardex da
                # ENTRADA do produto acabado (custo do cadastro).
                entrada = self.repo.salvar_com_itens(
                    entrada, itens_data, session=session
                )

                # 4. Salvar alterações de custo + atualizar produto
                if alteracoes_custo:
                    for alt in alteracoes_custo:
                        alteracao_repo.registrar(
                            codigo_produto=alt["codigo_produto"],
                            custo_anterior=alt["custo_anterior"],
                            custo_atual=alt["custo_atual"],
                            session=session,
                        )
                        produto_repo.atualizar_custo(
                            produto_id=alt["produto_id"],
                            novo_custo=alt["custo_atual"],
                            session=session,
                        )

                session.flush()
                session.refresh(entrada)
                session.expunge(entrada)

                logger.info(
                    f"Entrada salva | id={entrada.id} | "
                    f"sequencia={sequencia} | itens={len(itens_data)} | "
                    f"producao={producao}"
                )
                return entrada

        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar entrada "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma entrada com esta sequência. Tente novamente."
            )

    def salvar_com_alteracao_custo(self, sequencia, data_entrada, motivo_id,
                                   itens_data, entrada_id=None,
                                   alteracoes_custo=None):
        """
        Mantido por compatibilidade — delega para o método `salvar`
        unificado, que já é transacional.
        """
        return self.salvar(
            sequencia=sequencia,
            data_entrada=data_entrada,
            motivo_id=motivo_id,
            itens_data=itens_data,
            entrada_id=entrada_id,
            alteracoes_custo=alteracoes_custo,
        )

    def excluir(self, entrada_id):
        sucesso = self.repo.excluir_por_id(entrada_id)
        if not sucesso:
            raise ValueError("Entrada não encontrada.")
        logger.info(f"Entrada excluída: ID={entrada_id}")
        return True
