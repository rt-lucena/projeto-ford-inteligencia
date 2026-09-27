from datetime import datetime, timedelta

from app.models.user_model import User
from app.schemas.history_schema import HistoricoCreate
from app.services.history_service import (
    anonimize_old_history,
    create_history,
    get_user_history,
)
from app.services.vehicle_service import create_veiculo


def criar_especificacoes():
    return {
        "motor": "3.0 V6",
        "potencia": "397 cv",
        "torque": "583 Nm",
    }


def criar_veiculo_teste(db, modelo="Ranger"):
    return create_veiculo(
        db=db,
        marca="Ford",
        modelo=modelo,
        versao="Raptor",
        ano=2025,
        fonte="teste",
        especificacoes=criar_especificacoes(),
    )


def obter_token(client, email="teste@teste.com", senha="12345678"):
    response = client.post(
        "/auth/token",
        data={
            "username": email,
            "password": senha,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]

def headers_autenticacao(
    client,
    email="teste@teste.com",
    senha="12345678",
):
    token = obter_token(client, email, senha)

    return {
        "Authorization": f"Bearer {token}",
    }


def test_create_history_individual(db, usuario):
    veiculo = criar_veiculo_teste(db)

    dados = HistoricoCreate(
        tipo="individual",
        id_veiculo=veiculo.id,
    )

    historico = create_history(
        db,
        usuario.id,
        dados,
    )

    assert historico.id is not None
    assert historico.id_usuario == usuario.id
    assert historico.tipo == "individual"
    assert historico.id_veiculo == veiculo.id
    assert historico.id_veiculo1 is None
    assert historico.id_veiculo2 is None


def test_create_history_comparacao(db, usuario):
    veiculo1 = criar_veiculo_teste(db, "Ranger")
    veiculo2 = criar_veiculo_teste(db, "Mustang")

    dados = HistoricoCreate(
        tipo="comparacao",
        id_veiculo=veiculo1.id,
        id_veiculo1=veiculo1.id,
        id_veiculo2=veiculo2.id,
    )

    historico = create_history(
        db,
        usuario.id,
        dados,
    )

    assert historico.tipo == "comparacao"
    assert historico.id_veiculo == veiculo1.id
    assert historico.id_veiculo1 == veiculo1.id
    assert historico.id_veiculo2 == veiculo2.id


def test_get_user_history_retorna_apenas_historico_do_usuario(
    db,
    usuario,
):
    outro_usuario = User(
        nome="Outro Usuário",
        email="outro@teste.com",
        senha_hash="hash",
        role="user",
    )

    db.add(outro_usuario)
    db.commit()
    db.refresh(outro_usuario)

    veiculo = criar_veiculo_teste(db)

    create_history(
        db,
        usuario.id,
        HistoricoCreate(
            tipo="individual",
            id_veiculo=veiculo.id,
        ),
    )

    create_history(
        db,
        outro_usuario.id,
        HistoricoCreate(
            tipo="individual",
            id_veiculo=veiculo.id,
        ),
    )

    historicos = get_user_history(
        db,
        usuario.id,
    )

    assert len(historicos) == 1
    assert historicos[0].id_usuario == usuario.id


def test_anonimize_old_history_remove_usuario(
    db,
    usuario,
):
    veiculo = criar_veiculo_teste(db)

    historico = create_history(
        db,
        usuario.id,
        HistoricoCreate(
            tipo="individual",
            id_veiculo=veiculo.id,
        ),
    )

    historico.criado_em = (
        datetime.utcnow() - timedelta(days=120)
    )

    db.commit()

    anonimize_old_history(
        db,
        days=90,
    )

    db.refresh(historico)

    assert historico.id_usuario is None


def test_anonimize_old_history_preserva_registro_recente(
    db,
    usuario,
):
    veiculo = criar_veiculo_teste(db)

    historico = create_history(
        db,
        usuario.id,
        HistoricoCreate(
            tipo="individual",
            id_veiculo=veiculo.id,
        ),
    )

    anonimize_old_history(
        db,
        days=90,
    )

    db.refresh(historico)

    assert historico.id_usuario == usuario.id


def test_criar_historico_endpoint(
    client,
    usuario,
    db,
):
    veiculo = criar_veiculo_teste(db)

    token = obter_token(client)

    response = client.post(
        "/historico/",
        json={
            "tipo": "individual",
            "id_veiculo": veiculo.id,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["tipo"] == "individual"
    assert data["id_veiculo"] == veiculo.id
    assert data["id_usuario"] == usuario.id


def test_listar_historico_endpoint(
    client,
    usuario,
    db,
):
    veiculo = criar_veiculo_teste(db)

    create_history(
        db,
        usuario.id,
        HistoricoCreate(
            tipo="individual",
            id_veiculo=veiculo.id,
        ),
    )

    token = obter_token(client)

    response = client.get(
        "/historico/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id_veiculo"] == veiculo.id


def test_historico_sem_autenticacao(client):
    response = client.get("/historico/")

    assert response.status_code == 401


def test_limpeza_historico_antigo_endpoint(
    client,
    admin,
):
    response = client.delete(
        "/historico/limpeza-antigos",
        headers=headers_autenticacao(
            client,
            "admin@teste.com",
        ),
    )

    assert response.status_code == 200
    
def test_limpeza_historico_sem_token_retorna_401(client):
    response = client.delete(
        "/historico/limpeza-antigos"
    )

    assert response.status_code == 401
    
def test_limpeza_historico_usuario_comum_retorna_403(
    client,
    usuario,
):
    response = client.delete(
        "/historico/limpeza-antigos",
        headers=headers_autenticacao(
            client,
            "teste@teste.com",
        ),
    )

    assert response.status_code == 403
    
def test_limpeza_historico_admin_retorna_200(
    client,
    admin,
):
    response = client.delete(
        "/historico/limpeza-antigos",
        headers=headers_autenticacao(
            client,
            "admin@teste.com",
        ),
    )

    assert response.status_code == 200