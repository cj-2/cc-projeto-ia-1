import sqlite3

from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse

from app.database import get_connection
from app.models import Transacao, TransacaoCreate

router = APIRouter()


@router.post("/transacoes", response_model=Transacao, status_code=201)
def criar_transacao(transacao: TransacaoCreate) -> Transacao | Response:
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO transacoes (data, descricao, valor, tipo, categoria_id) VALUES (?, ?, ?, ?, ?)",
            (
                transacao.data.isoformat(),
                transacao.descricao,
                transacao.valor,
                transacao.tipo,
                transacao.categoria_id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(
            status_code=422,
            content={"erro": f"categoria_id {transacao.categoria_id} não existe"},
        )
    novo_id = cursor.lastrowid
    conn.close()
    return Transacao(id=novo_id, **transacao.model_dump())


@router.get("/transacoes", response_model=list[Transacao])
def listar_transacoes(categoria: str | None = None) -> list[Transacao]:
    conn = get_connection()

    if categoria is None:
        linhas = conn.execute(
            "SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes "
            "ORDER BY data DESC, id DESC"
        ).fetchall()
    else:
        try:
            categoria_id = int(categoria)
            linhas = conn.execute(
                "SELECT id, data, descricao, valor, tipo, categoria_id FROM transacoes "
                "WHERE categoria_id = ? ORDER BY data DESC, id DESC",
                (categoria_id,),
            ).fetchall()
        except ValueError:
            linhas = conn.execute(
                "SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id "
                "FROM transacoes t JOIN categorias c ON c.id = t.categoria_id "
                "WHERE c.nome = ? ORDER BY t.data DESC, t.id DESC",
                (categoria,),
            ).fetchall()

    conn.close()
    return [Transacao(**dict(linha)) for linha in linhas]


@router.put("/transacoes/{id}", response_model=Transacao)
def atualizar_transacao(id: int, transacao: TransacaoCreate) -> Transacao | Response:
    conn = get_connection()
    existe = conn.execute("SELECT id FROM transacoes WHERE id = ?", (id,)).fetchone()
    if existe is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    try:
        conn.execute(
            "UPDATE transacoes SET data = ?, descricao = ?, valor = ?, tipo = ?, categoria_id = ? "
            "WHERE id = ?",
            (
                transacao.data.isoformat(),
                transacao.descricao,
                transacao.valor,
                transacao.tipo,
                transacao.categoria_id,
                id,
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(
            status_code=422,
            content={"erro": f"categoria_id {transacao.categoria_id} não existe"},
        )
    conn.close()
    return Transacao(id=id, **transacao.model_dump())


@router.delete("/transacoes/{id}", status_code=204)
def excluir_transacao(id: int) -> Response:
    conn = get_connection()
    existe = conn.execute("SELECT id FROM transacoes WHERE id = ?", (id,)).fetchone()
    if existe is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    conn.execute("DELETE FROM transacoes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return Response(status_code=204)
