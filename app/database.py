import sqlite3

DB_PATH = "gastos.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            tipo TEXT NOT NULL,
            categoria_id INTEGER REFERENCES categorias(id)
        )
        """
    )

    colunas = {linha["name"] for linha in conn.execute("PRAGMA table_info(transacoes)")}
    if "categoria_id" not in colunas:
        conn.execute(
            "ALTER TABLE transacoes ADD COLUMN categoria_id INTEGER REFERENCES categorias(id)"
        )

    conn.commit()
    conn.close()
