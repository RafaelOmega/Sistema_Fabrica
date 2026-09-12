import os
import sys

# Garante que a raiz do projeto esteja no sys.path ao rodar `pytest`
# de qualquer diretório, para que `import app...` sempre funcione.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# app/config.py levanta RuntimeError se DB_NAME4/DB_PASSWORD não
# estiverem definidas (por design, para não deixar o app real subir
# sem configuração). Os testes de unidade da camada de services NUNCA
# tocam um banco de verdade (os repositórios são substituídos por
# MagicMock em cada teste), mas o simples ato de importar
# app.services.* passa por app.database.connection -> app.config,
# então precisamos de valores dummy só para o import não falhar.
os.environ.setdefault("DB_NAME4", "test_db_nao_utilizado")
os.environ.setdefault("DB_PASSWORD", "test_password_nao_utilizada")
