from fastapi import FastAPI

from app import database

app = FastAPI(title="Controle de Gastos Pessoais")


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()
