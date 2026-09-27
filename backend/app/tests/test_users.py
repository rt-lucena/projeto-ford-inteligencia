def test_usuario_atenticado_acessa_proprio_perfil(client, usuario):
    login = client.post(
        "/auth/token",
        data={
            "username": "teste@teste.com",
            "password": "12345678",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        "/users/me/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "teste@teste.com"
    assert data["nome"] == "Usuário Teste"


def test_usuario_sem_token_nao_acessa_perfil(client):
    response = client.get("/users/me/")

    assert response.status_code == 401