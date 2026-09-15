import csv
import io


def _criar_categoria(client, nome):
    return client.post("/categorias", json={"nome": nome}).json()


def _criar_transacao(client, **kwargs):
    dados = {"data": "2026-08-01", "descricao": "Transação", "valor": 10.0, "tipo": "saida"}
    dados.update(kwargs)
    return client.post("/transacoes", json=dados).json()


def _linhas_csv(resposta):
    return list(csv.reader(io.StringIO(resposta.text)))


def test_export_csv_sem_filtro_retorna_todas_transacoes(client):
    t1 = _criar_transacao(client, descricao="Mercado", valor=100.0, tipo="saida")
    t2 = _criar_transacao(client, descricao="Salário", valor=2000.0, tipo="entrada")

    resposta = client.get("/export.csv")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/csv")
    linhas = _linhas_csv(resposta)
    assert linhas[0] == ["id", "data", "descricao", "valor", "tipo", "categoria_id"]
    ids = {linha[0] for linha in linhas[1:]}
    assert ids == {str(t1["id"]), str(t2["id"])}


def test_export_csv_respeita_filtros(client):
    mercado = _criar_categoria(client, "Mercado")
    lazer = _criar_categoria(client, "Lazer")
    t1 = _criar_transacao(
        client, descricao="Compras", valor=100.0, tipo="saida", categoria_id=mercado["id"]
    )
    _criar_transacao(
        client, descricao="Cinema", valor=50.0, tipo="saida", categoria_id=lazer["id"]
    )

    resposta = client.get("/export.csv", params={"categoria": str(mercado["id"])})

    linhas = _linhas_csv(resposta)
    ids = {linha[0] for linha in linhas[1:]}
    assert ids == {str(t1["id"])}


def test_export_csv_formata_valor_com_duas_casas(client):
    _criar_transacao(client, descricao="Assinatura", valor=9.5, tipo="saida")

    resposta = client.get("/export.csv")

    linhas = _linhas_csv(resposta)
    assert linhas[1][3] == "9.50"


def test_export_csv_propaga_erro_de_validacao_dos_filtros(client):
    resposta = client.get(
        "/export.csv", params={"data_inicio": "2026-08-10", "data_fim": "2026-08-01"}
    )

    assert resposta.status_code == 422
    assert "erro" in resposta.json()
