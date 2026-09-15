import sqlite3

DB_PATH = "gastos.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    # Garante que o arquivo/conexão SQLite existe. As tabelas específicas
    # de cada feature são criadas na implementação da spec correspondente.
    conn = get_connection()
    conn.close()
