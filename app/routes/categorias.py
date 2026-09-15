import sqlite3

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.database import get_connection
from app.models import Categoria, CategoriaCreate

router = APIRouter()


@router.post("/categorias", response_model=Categoria, status_code=201)
def criar_categoria(categoria: CategoriaCreate) -> Categoria | Response:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO categorias (nome) VALUES (?)", (categoria.nome,)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(
            status_code=422,
            content={"erro": f"categoria '{categoria.nome}' já existe"},
        )
    novo_id = cursor.lastrowid
    conn.close()
    return Categoria(id=novo_id, nome=categoria.nome)


@router.get("/categorias", response_model=list[Categoria])
def listar_categorias() -> list[Categoria]:
    conn = get_connection()
    linhas = conn.execute("SELECT id, nome FROM categorias ORDER BY id").fetchall()
    conn.close()
    return [Categoria(**dict(linha)) for linha in linhas]
