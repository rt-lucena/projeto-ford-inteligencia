from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)


def test_hash_e_verificacao_de_senha():
    senha = "minha_senha_123"

    senha_hash = get_password_hash(senha)

    assert senha_hash != senha
    assert verify_password(senha, senha_hash)


def test_senha_incorreta_nao_e_validada():
    senha = "minha_senha_123"

    senha_hash = get_password_hash(senha)

    assert not verify_password("senha_errada", senha_hash)


def test_criacao_de_token():
    token = create_access_token(
        data={"sub": "teste@teste.com"}
    )

    assert token is not None
    assert isinstance(token, str)