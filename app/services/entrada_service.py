import re

from sqlalchemy.exc import IntegrityError

from app.models.entrada import Entrada
from app.repositories.entrada_repository import EntradaRepository
from app.repositories.regra_produto_especial_repository import (
    RegraProdutoEspecialRepository,
)
from app.utils.logger import get_logger

logger = get_logger("entrada_service")


class EntradaService:
    def __init__(self):
        self.repo = EntradaRepository()
        self.regra_repo = RegraProdutoEspecialRepository()
        # Cache em memória das regras especiais por código de produto.
        # Evita ir ao banco a cada tecla digitada no código do produto
        # (a tela chama obter_regra_produto em tempo real). O cache é
        # invalidado automaticamente sempre que uma regra é criada,
        # editada ou removida através deste service.
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

    def _validar(self, sequencia, data_entrada, motivo_id, itens):
        if not sequencia:
            raise ValueError("Sequência não gerada.")

        # A sequência é gerada automaticamente, mas o campo é editável
        # na tela (usuário pode digitar manualmente para pesquisar ou
        # forçar um valor). obter_proxima_sequencia() depende de
        # cast(sequencia, Integer) no banco, então um valor não numérico
        # quebraria a geração de sequência para todas as entradas
        # seguintes. Bloqueamos isso aqui.
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
                raise ValueError(
                    f"Item {i + 1}: produto não informado."
                )
            if not item.get("unidade"):
                raise ValueError(
                    f"Item {i + 1}: unidade não informada."
                )
            # A conversão (float()) e a checagem de faixa (<=0, <0) são
            # feitas em passos separados. Antes, o `raise ValueError`
            # da checagem de faixa ficava dentro do mesmo `try` que
            # captura ValueError da conversão — então o próprio
            # `except` abaixo capturava essa exceção e substituía a
            # mensagem específica ("deve ser maior que zero") por uma
            # genérica ("quantidade inválida"), escondendo do usuário
            # o motivo real da rejeição.
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

    def salvar(self, sequencia, data_entrada, motivo_id, itens_data,
               entrada_id=None, alteracoes_custo=None):
        """
        Salva entrada + itens (+ alterações de custo se houver)
        na MESMA transação. Tudo commita ou tudo faz rollback.
        """
        self._validar(sequencia, data_entrada, motivo_id, itens_data)

        from app.database.connection import session_scope
        from app.repositories.alteracao_custo_repository import (
            AlteracaoCustoRepository,
        )
        from app.repositories.produto_repository import ProdutoRepository

        alteracao_repo = AlteracaoCustoRepository()
        produto_repo = ProdutoRepository()

        try:
            with session_scope() as session:
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

                # 2. Salvar itens com diff (mesma sessão). Reatribuímos
                # `entrada` ao valor retornado (em vez de continuar
                # usando a referência antiga) para não depender de
                # detalhe interno do SQLAlchemy sobre session.merge()
                # retornar ou não a mesma instância.
                entrada = self.repo.salvar_com_itens(
                    entrada, itens_data, session=session
                )

                # 3. Salvar alterações de custo + atualizar produto
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
                    f"Entrada salva (transação única): ID={entrada.id}, "
                    f"sequencia={entrada.sequencia}, "
                    f"itens={len(itens_data)}"
                )
                return entrada
        except IntegrityError:
            logger.warning(
                f"Conflito de integridade ao salvar entrada "
                f"(provável sequência duplicada concorrente): {sequencia}"
            )
            raise ValueError(
                "Já existe uma entrada com esta sequência. "
                "Tente novamente."
            )
        # ValueError e outras exceções sobem naturalmente;
        # session_scope() já garante o rollback de tudo.

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
