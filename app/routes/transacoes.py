from fastapi import APIRouter

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
