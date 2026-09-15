from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app import database
from app.routes import transacoes

app = FastAPI(title="Controle de Gastos Pessoais")
app.include_router(transacoes.router)


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    primeiro_erro = exc.errors()[0]
    campo = primeiro_erro["loc"][-1]
    mensagem = f"{campo}: {primeiro_erro['msg']}"
    return JSONResponse(status_code=422, content={"erro": mensagem})
