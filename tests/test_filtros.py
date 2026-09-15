def _criar_categoria(client, nome):
    return client.post("/categorias", json={"nome": nome}).json()


def _criar_transacao(client, **kwargs):
    dados = {"data": "2026-08-01", "descricao": "Transação", "valor": 10.0, "tipo": "saida"}
    dados.update(kwargs)
    return client.post("/transacoes", json=dados).json()


def _popular_transacoes(client):
    mercado = _criar_categoria(client, "Mercado")
    lazer = _criar_categoria(client, "Lazer")

    t1 = _criar_transacao(
        client,
        data="2026-08-05",
        descricao="Compras do mês",
        valor=100.0,
        tipo="saida",
        categoria_id=mercado["id"],
    )
    t2 = _criar_transacao(
        client,
        data="2026-08-15",
        descricao="Cinema",
        valor=50.0,
        tipo="saida",
        categoria_id=lazer["id"],
    )
    t3 = _criar_transacao(
        client,
        data="2026-09-01",
        descricao="Mercadinho",
        valor=200.0,
        tipo="saida",
        categoria_id=mercado["id"],
    )
    return mercado, lazer, t1, t2, t3


def test_filtro_por_categoria_id(client):
    mercado, _, t1, _, t3 = _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"categoria": str(mercado["id"])})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"], t3["id"]}


def test_filtro_por_categoria_nome(client):
    _, lazer, _, t2, _ = _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"categoria": lazer["nome"]})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t2["id"]}


def test_filtro_por_periodo(client):
    _, _, t1, t2, t3 = _popular_transacoes(client)

    resposta = client.get(
        "/transacoes", params={"data_inicio": "2026-08-01", "data_fim": "2026-08-31"}
    )
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"], t2["id"]}
    assert t3["id"] not in ids


def test_filtro_apenas_data_inicio(client):
    _, _, t1, t2, t3 = _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"data_inicio": "2026-08-10"})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t2["id"], t3["id"]}
    assert t1["id"] not in ids


def test_filtro_apenas_data_fim(client):
    _, _, t1, t2, t3 = _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"data_fim": "2026-08-10"})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"]}
    assert t2["id"] not in ids
    assert t3["id"] not in ids


def test_filtro_por_faixa_de_valor(client):
    t1, t2, t3 = _popular_transacoes(client)[2:]

    resposta = client.get("/transacoes", params={"valor_min": "60", "valor_max": "150"})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"]}
    assert t2["id"] not in ids
    assert t3["id"] not in ids


def test_filtro_apenas_valor_min(client):
    t1, t2, t3 = _popular_transacoes(client)[2:]

    resposta = client.get("/transacoes", params={"valor_min": "100"})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"], t3["id"]}
    assert t2["id"] not in ids


def test_filtro_apenas_valor_max(client):
    t1, t2, t3 = _popular_transacoes(client)[2:]

    resposta = client.get("/transacoes", params={"valor_max": "100"})
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"], t2["id"]}
    assert t3["id"] not in ids


def test_filtros_combinados(client):
    mercado, _, t1, _, t3 = _popular_transacoes(client)

    resposta = client.get(
        "/transacoes",
        params={
            "categoria": str(mercado["id"]),
            "data_inicio": "2026-08-01",
            "data_fim": "2026-08-31",
            "valor_min": "50",
            "valor_max": "150",
        },
    )
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"]}
    assert t3["id"] not in ids


def test_filtros_combinados_categoria_por_nome(client):
    mercado, _, t1, _, t3 = _popular_transacoes(client)

    resposta = client.get(
        "/transacoes",
        params={
            "categoria": mercado["nome"],
            "data_inicio": "2026-08-01",
            "data_fim": "2026-08-31",
            "valor_min": "50",
            "valor_max": "150",
        },
    )
    ids = {t["id"] for t in resposta.json()}
    assert ids == {t1["id"]}
    assert t3["id"] not in ids


def test_filtro_categoria_id_inexistente_retorna_lista_vazia(client):
    _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"categoria": "9999"})
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_filtro_categoria_nome_inexistente_retorna_lista_vazia(client):
    _popular_transacoes(client)

    resposta = client.get("/transacoes", params={"categoria": "Categoria Inexistente"})
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_filtro_data_invalida_retorna_422(client):
    resposta = client.get("/transacoes", params={"data_inicio": "não-é-uma-data"})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_filtro_valor_invalido_retorna_422(client):
    resposta = client.get("/transacoes", params={"valor_min": "abc"})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_filtro_periodo_invertido(client):
    resposta = client.get(
        "/transacoes", params={"data_inicio": "2026-08-31", "data_fim": "2026-08-01"}
    )
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_filtro_faixa_de_valor_invertida(client):
    resposta = client.get("/transacoes", params={"valor_min": "200", "valor_max": "100"})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()
