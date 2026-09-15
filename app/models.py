from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TransacaoCreate(BaseModel):
    data: date
    descricao: str
    valor: float = Field(gt=0)
    tipo: Literal["entrada", "saida"]
    categoria_id: int | None = None

    @field_validator("descricao")
    @classmethod
    def descricao_nao_vazia(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("descricao não pode ser vazia")
        return valor


class Transacao(BaseModel):
    id: int
    data: date
    descricao: str
    valor: float
    tipo: Literal["entrada", "saida"]
    categoria_id: int | None = None


class CategoriaCreate(BaseModel):
    nome: str

    @field_validator("nome")
    @classmethod
    def nome_nao_vazio(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("nome não pode ser vazio")
        return valor


class Categoria(BaseModel):
    id: int
    nome: str
