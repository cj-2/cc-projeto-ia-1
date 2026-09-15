import re

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse

from app.database import get_connection
from app.models import CategoriaTotal, ResumoMensal, Saldo

router = APIRouter()

MES_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


@router.get("/saldo", response_model=Saldo)
def obter_saldo() -> Saldo:
    conn = get_connection()
    linha = conn.execute(
        "SELECT "
        "COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor END), 0) AS entradas, "
        "COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor END), 0) AS saidas "
        "FROM transacoes"
    ).fetchone()
    conn.close()

    entradas = round(linha["entradas"], 2)
    saidas = round(linha["saidas"], 2)
    return Saldo(entradas=entradas, saidas=saidas, saldo=round(entradas - saidas, 2))


@router.get("/resumo", response_model=ResumoMensal)
def obter_resumo(mes: str) -> ResumoMensal | Response:
    if not MES_PATTERN.match(mes):
        return JSONResponse(
            status_code=422,
            content={"erro": "mes deve estar no formato YYYY-MM (ex.: 2026-08)"},
        )

    conn = get_connection()

    linha = conn.execute(
        "SELECT "
        "COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor END), 0) AS entradas, "
        "COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor END), 0) AS saidas "
        "FROM transacoes WHERE strftime('%Y-%m', data) = ?",
        (mes,),
    ).fetchone()

    linhas_categorias = conn.execute(
        "SELECT c.nome AS categoria, SUM(t.valor) AS total "
        "FROM transacoes t JOIN categorias c ON c.id = t.categoria_id "
        "WHERE t.tipo = 'saida' AND strftime('%Y-%m', t.data) = ? "
        "GROUP BY c.nome ORDER BY total DESC",
        (mes,),
    ).fetchall()

    conn.close()

    entradas = round(linha["entradas"], 2)
    saidas = round(linha["saidas"], 2)
    por_categoria = [
        CategoriaTotal(categoria=l["categoria"], total=round(l["total"], 2))
        for l in linhas_categorias
    ]

    return ResumoMensal(
        mes=mes,
        entradas=entradas,
        saidas=saidas,
        saldo=round(entradas - saidas, 2),
        por_categoria=por_categoria,
    )
