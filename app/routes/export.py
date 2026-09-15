import csv
import io
from datetime import date

from fastapi import APIRouter, Response

from app.routes.transacoes import listar_transacoes

router = APIRouter()


@router.get("/export.csv")
def exportar_csv(
    categoria: str | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    valor_min: float | None = None,
    valor_max: float | None = None,
) -> Response:
    resultado = listar_transacoes(categoria, data_inicio, data_fim, valor_min, valor_max)
    if isinstance(resultado, Response):
        return resultado

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "data", "descricao", "valor", "tipo", "categoria_id"])
    for transacao in resultado:
        writer.writerow(
            [
                transacao.id,
                transacao.data.isoformat(),
                transacao.descricao,
                f"{transacao.valor:.2f}",
                transacao.tipo,
                transacao.categoria_id if transacao.categoria_id is not None else "",
            ]
        )

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="extrato.csv"'},
    )
