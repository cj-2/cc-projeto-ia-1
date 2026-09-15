from fastapi import APIRouter, HTTPException, Response

from app.database import get_connection
from app.models import Transacao, TransacaoCreate

router = APIRouter()


@router.post("/transacoes", response_model=Transacao, status_code=201)
def criar_transacao(transacao: TransacaoCreate) -> Transacao:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO transacoes (data, descricao, valor, tipo) VALUES (?, ?, ?, ?)",
        (
            transacao.data.isoformat(),
            transacao.descricao,
            transacao.valor,
            transacao.tipo,
        ),
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return Transacao(id=novo_id, **transacao.model_dump())


@router.get("/transacoes", response_model=list[Transacao])
def listar_transacoes() -> list[Transacao]:
    conn = get_connection()
    linhas = conn.execute(
        "SELECT id, data, descricao, valor, tipo FROM transacoes ORDER BY data DESC, id DESC"
    ).fetchall()
    conn.close()
    return [Transacao(**dict(linha)) for linha in linhas]


@router.put("/transacoes/{id}", response_model=Transacao)
def atualizar_transacao(id: int, transacao: TransacaoCreate) -> Transacao:
    conn = get_connection()
    existe = conn.execute("SELECT id FROM transacoes WHERE id = ?", (id,)).fetchone()
    if existe is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Transação não encontrada")

    conn.execute(
        "UPDATE transacoes SET data = ?, descricao = ?, valor = ?, tipo = ? WHERE id = ?",
        (
            transacao.data.isoformat(),
            transacao.descricao,
            transacao.valor,
            transacao.tipo,
            id,
        ),
    )
    conn.commit()
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
