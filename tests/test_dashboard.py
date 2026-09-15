def test_raiz_serve_dashboard_html(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
    assert "<html" in resposta.text.lower()


def test_rota_dashboard_serve_o_mesmo_html(client):
    resposta = client.get("/dashboard")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"].startswith("text/html")
