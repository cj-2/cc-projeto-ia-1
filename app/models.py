from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TransacaoCreate(BaseModel):
    data: date
    descricao: str
    valor: float = Field(gt=0)
    tipo: Literal["entrada", "saida"]


class Transacao(BaseModel):
    id: int
    data: date
    descricao: str
    valor: float
    tipo: Literal["entrada", "saida"]
