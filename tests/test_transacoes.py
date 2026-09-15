def test_criar_transacao(client):
    resposta = client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Salário", "valor": 3000.0, "tipo": "entrada"},
    )
    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["id"] is not None
    assert corpo["descricao"] == "Salário"
    assert corpo["categoria_id"] is None


def test_criar_transacao_tipo_invalido(client):
    resposta = client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Teste", "valor": 10.0, "tipo": "invalido"},
    )
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_criar_transacao_valor_nao_positivo(client):
    resposta = client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Teste", "valor": 0, "tipo": "saida"},
    )
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_criar_transacao_descricao_vazia(client):
    resposta = client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "   ", "valor": 10.0, "tipo": "saida"},
    )
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_criar_transacao_categoria_inexistente(client):
    resposta = client.post(
        "/transacoes",
        json={
            "data": "2026-08-01",
            "descricao": "Teste",
            "valor": 10.0,
            "tipo": "saida",
            "categoria_id": 999,
        },
    )
    assert resposta.status_code == 422
    assert "erro" in resposta.json()


def test_listar_transacoes_sem_filtro(client):
    client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "A", "valor": 10.0, "tipo": "entrada"},
    )
    client.post(
        "/transacoes",
        json={"data": "2026-08-02", "descricao": "B", "valor": 20.0, "tipo": "saida"},
    )

    resposta = client.get("/transacoes")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_atualizar_transacao_inexistente(client):
    resposta = client.put(
        "/transacoes/999",
        json={"data": "2026-08-01", "descricao": "X", "valor": 10.0, "tipo": "entrada"},
    )
    assert resposta.status_code == 404


def test_excluir_transacao_inexistente(client):
    resposta = client.delete("/transacoes/999")
    assert resposta.status_code == 404


def test_atualizar_e_excluir_transacao(client):
    criada = client.post(
        "/transacoes",
        json={"data": "2026-08-01", "descricao": "Original", "valor": 10.0, "tipo": "entrada"},
    ).json()

    atualizada = client.put(
        f"/transacoes/{criada['id']}",
        json={"data": "2026-08-02", "descricao": "Editada", "valor": 15.0, "tipo": "saida"},
    )
    assert atualizada.status_code == 200
    assert atualizada.json()["descricao"] == "Editada"

    excluida = client.delete(f"/transacoes/{criada['id']}")
    assert excluida.status_code == 204

    resposta = client.get("/transacoes")
    assert resposta.json() == []
