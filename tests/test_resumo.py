def test_saldo(client):
    client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Salário", "valor": 1000.0, "tipo": "entrada"},
    )
    client.post(
        "/transacoes",
        json={"data": "2026-08-02", "descricao": "Aluguel", "valor": 400.0, "tipo": "saida"},
    )

    resposta = client.get("/saldo")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["entradas"] == 1000.0
    assert corpo["saidas"] == 400.0
    assert corpo["saldo"] == 600.0


def test_resumo_mensal(client):
    mercado = client.post("/categorias", json={"nome": "Mercado"}).json()

    client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Salário", "valor": 1000.0, "tipo": "entrada"},
    )
    client.post(
        "/transacoes",
        json={
            "data": "2026-08-05",
            "descricao": "Compras",
            "valor": 150.0,
            "tipo": "saida",
            "categoria_id": mercado["id"],
        },
    )
    client.post(
        "/transacoes",
        json={"data": "2026-09-01", "descricao": "Fora do mês", "valor": 999.0, "tipo": "saida"},
    )

    resposta = client.get("/resumo", params={"mes": "2026-08"})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["entradas"] == 1000.0
    assert corpo["saidas"] == 150.0
    assert corpo["saldo"] == 850.0
    assert corpo["por_categoria"] == [{"categoria": "Mercado", "total": 150.0}]


def test_resumo_mes_invalido(client):
    resposta = client.get("/resumo", params={"mes": "2026-13"})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()
