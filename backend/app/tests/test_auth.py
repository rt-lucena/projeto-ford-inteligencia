from unittest.mock import patch

from app.dependencies.auth_dependencies import get_current_admin_user

def obter_token(client, email, senha="12345678"):
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": senha,
        },
    )

    assert response.status_code == 200

    return response.json()


def headers_autenticacao(client, email):
    token = obter_token(client, email)

    return {
        "Authorization": f"Bearer {token}",
    }

def test_login_sucesso(client, usuario):
    response = client.post(
        "/auth/token",
        data={
            "username": "teste@teste.com",
            "password": "12345678",
        },
    )
    
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in data


def test_login_senha_incorreta(client, usuario):
    response = client.post(
        "/auth/token",
        data={
            "username": "teste@teste.com",
            "password": "senha_errada",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_usuario_inexistente(client):
    response = client.post(
        "/auth/token",
        data={
            "username": "naoexiste@teste.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 401

def test_refresh_token_sucesso(client, usuario):
    dados = obter_token(client, email="teste@teste.com")

    response = client.post(
        "/auth/refresh",
        headers={
            "Authorization": (
                f"Bearer {dados['access_token']}"
            )
        },
    )

    assert response.status_code == 200

    novo_token = response.json()

    assert novo_token["token_type"] == "bearer"
    assert novo_token["access_token"]


def test_refresh_sem_token_retorna_401(client):
    response = client.post(
        "/auth/refresh"
    )

    assert response.status_code == 401


def test_refresh_com_token_invalido_retorna_401(client):
    response = client.post(
        "/auth/refresh",
        headers={
            "Authorization": "Bearer token-invalido"
        },
    )

    assert response.status_code == 401


def test_perfil_com_token_invalido_retorna_401(client):
    response = client.get(
        "/users/me/",
        headers={
            "Authorization": "Bearer token-invalido"
        },
    )

    assert response.status_code == 401
    
def test_usuario_comum_e_rejeitado_pela_dependencia_admin(
    db,
    usuario,
):
    resultado = None

    try:
        import asyncio

        asyncio.run(
            get_current_admin_user(usuario)
        )
    except Exception as exc:
        resultado = exc

    assert resultado is not None
    assert resultado.status_code == 403
    assert resultado.detail == "Privilégios insuficientes."


def test_admin_e_aceito_pela_dependencia_admin(
    admin,
):
    import asyncio

    resultado = asyncio.run(
        get_current_admin_user(admin)
    )

    assert resultado == admin
    assert resultado.role == "admin"
    