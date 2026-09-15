import sqlite3
from datetime import date

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
def listar_transacoes(
    categoria: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
) -> list[Transacao] | Response:
    if data_inicio is not None and data_fim is not None and data_inicio > data_fim:
        return JSONResponse(
            status_code=422,
            content={"erro": "data_inicio não pode ser posterior a data_fim"},
        )
    if valor_min is not None and valor_max is not None and valor_min > valor_max:
        return JSONResponse(
            status_code=422,
            content={"erro": "valor_min não pode ser maior que valor_max"},
        )

    condicoes = []
    parametros: list[object] = []
    join_categoria = False

    if categoria is not None:
        try:
            categoria_id = int(categoria)
            condicoes.append("t.categoria_id = ?")
            parametros.append(categoria_id)
        except ValueError:
            join_categoria = True
            condicoes.append("c.nome = ?")
            parametros.append(categoria)

    if data_inicio is not None:
        condicoes.append("t.data >= ?")
        parametros.append(data_inicio.isoformat())
    if data_fim is not None:
        condicoes.append("t.data <= ?")
        parametros.append(data_fim.isoformat())
    if valor_min is not None:
        condicoes.append("t.valor >= ?")
        parametros.append(valor_min)
    if valor_max is not None:
        condicoes.append("t.valor <= ?")
        parametros.append(valor_max)

    query = "SELECT t.id, t.data, t.descricao, t.valor, t.tipo, t.categoria_id FROM transacoes t"
    if join_categoria:
        query += " JOIN categorias c ON c.id = t.categoria_id"
    if condicoes:
        query += " WHERE " + " AND ".join(condicoes)
    query += " ORDER BY t.data DESC, t.id DESC"

    conn = get_connection()
    linhas = conn.execute(query, parametros).fetchall()
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
