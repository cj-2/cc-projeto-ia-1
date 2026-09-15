def test_criar_categoria(client):
    resposta = client.post("/categorias", json={"nome": "Transporte"})
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["nome"] == "Transporte"
    assert corpo["id"] is not None


def test_criar_categoria_nome_vazio(client):
    resposta = client.post("/categorias", json={"nome": "   "})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_criar_categoria_duplicada(client):
    client.post("/categorias", json={"nome": "Saúde"})
    resposta = client.post("/categorias", json={"nome": "Saúde"})
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_listar_categorias(client):
    client.post("/categorias", json={"nome": "Educação"})
    client.post("/categorias", json={"nome": "Moradia"})

    resposta = client.get("/categorias")
    assert resposta.status_code == 200
    nomes = {c["nome"] for c in resposta.json()}
    assert nomes == {"Educação", "Moradia"}
