import os

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME4")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Modo SSL da conexão com o Postgres (opcional). Valores aceitos pelo
# psycopg2: disable, allow, prefer, require, verify-ca, verify-full.
# Deixe DB_SSLMODE sem definir para manter o comportamento atual
# (o driver decide o padrão, "prefer"). Defina como "require" (ou mais
# forte) quando o banco estiver acessível pela rede/fora de localhost.
DB_SSLMODE = os.getenv("DB_SSLMODE", "").strip()

if not DB_NAME:
    raise RuntimeError("Variável de ambiente DB_NAME4 não definida.")
if not DB_PASSWORD:
    raise RuntimeError("Variável de ambiente DB_PASSWORD não definida.")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
if DB_SSLMODE:
    DATABASE_URL += f"?sslmode={DB_SSLMODE}"
