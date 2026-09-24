# app/services/vehicle_service.py
#
# MIGRAÇÃO: substituído import de groq_service → llm_service
# Toda a lógica de negócio permanece idêntica.

import datetime
import hashlib
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.vehicle_model import Veiculo
from app.services.consensus_service import ConsensusService
from app.services.data_loader_service import DataLoaderService
from app.services.fipe_service import FipeService
from app.services.llm_service import (
    LLMService,
)
from app.services.youtube_service import get_youtube_transcripts


class VehicleService:
    """
    Serviço central de veículos.
    Responsável por orquestrar regras de negócio, chamadas à IA e acesso a dados.
    """

    def __init__(self):
        self.data_loader = DataLoaderService()
        self.llm_service = LLMService()

        # Dicionário padrão (Contrato rígido de 23 chaves alinhado com o Frontend)
        self.atributos_esperados = {
            "motor": "",
            "potencia": "",
            "torque": "",
            "cambio": "",
            "numero_de_marchas": "",
            "tracao": "",
            "propulsao": "",
            "suspensao": "",
            "freios": "",
            "rodas_e_pneus": "",
            "farois": "",
            "modos_de_conducao": "",
            "comprimento": "",
            "largura": "",
            "altura": "",
            "capacidade_do_tanque": "",
            "peso": "",
            "aceleracao_0_100": "",
            "velocidade_maxima": "",
            "consumo_urbano": "",
            "consumo_rodoviario": "",
            "preco": "",
            "tipo_combustivel": "",
        }

    def processar_veiculo_com_ia(
        self,
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
    ) -> Dict[str, str]:
        """
        Orquestra o pipeline completo:
        Lê artigos do Scrapy → Extrai via LLM local → Aplica Consenso.
        """
        print(
            f"\n🚀 Iniciando orquestração da IA para: {marca} {modelo} {versao} {ano}",
        )

        print("🎥 Transcrições do YouTube desativadas (serviço em manutenção).")
        # try:
        #     get_youtube_transcripts(f"{marca} {modelo} {versao} {ano}", max_results=2)
        # except Exception as e:
        #     print(f"⚠️ Aviso: Não foi possível baixar transcrições do YouTube: {e}")

        # 1. Carrega os artigos brutos do diretório raw
        artigos = self.data_loader.carregar_artigos()
        if not artigos:
            print(
                "⚠️ Nenhum artigo encontrado no diretório raw. Retornando 'não disponível'.",
            )
            return {attr: "não disponível" for attr in self.atributos_esperados}

        print(f"📚 {len(artigos)} artigos carregados. Enviando para o LLM local...")

        # 2. Processa cada artigo individualmente usando o LLM local
        resultados_ia = self.llm_service.processar_artigos(
            artigos=artigos,
            atributos=self.atributos_esperados,
            marca=marca,
            modelo=modelo,
            versao=versao,
            ano=ano,
        )

        # Garante que nenhum valor seja Array/Lista antes de ir para o Consenso.
        resultados_sanitizados = []
        for resultado in resultados_ia:
            sanitizado = {}
            for k, v in resultado.items():
                if isinstance(v, list):
                    sanitizado[k] = ", ".join(str(item) for item in v)
                else:
                    sanitizado[k] = str(v)
            resultados_sanitizados.append(sanitizado)

        # 3. Aplica a votação ponderada para resolver conflitos entre as fontes
        print("⚖️ Aplicando consenso por votação ponderada...")
        resultado_final = ConsensusService.combinar_por_votacao(
            resultados=resultados_sanitizados,
            atributos=self.atributos_esperados,
        )

        # 4. Consulta a FIPE para atualizar o preço se o veículo for de ano anterior
        ano_atual = datetime.now().year
        if ano < ano_atual:
            print(f"📅 Veículo de {ano}. Consultando valor atualizado na FIPE...")
            preco_fipe = FipeService.buscar_preco_fipe(marca, modelo, versao, ano)
            if preco_fipe:
                resultado_final["preco"] = preco_fipe
                print(f"💰 Preço atualizado pela FIPE: {preco_fipe}")
            else:
                print("⚠️ FIPE não encontrou match. Mantendo preço extraído pelo LLM.")

        return resultado_final


def gerar_hash_busca(
    marca: str,
    modelo: str,
    versao: str,
    ano: int,
) -> str:
    chave = (
        f"{marca.strip().lower()}|"
        f"{modelo.strip().lower()}|"
        f"{versao.strip().lower()}|"
        f"{ano}"
    )
    return hashlib.sha256(chave.encode("utf-8")).hexdigest()


def get_veiculo_by_hash(db: Session, hash_busca: str):
    return db.query(Veiculo).filter(Veiculo.hash_busca == hash_busca).first()


def create_veiculo(
    db: Session,
    marca: str,
    modelo: str,
    versao: str,
    ano: int,
    fonte: str,
    especificacoes: dict,
):
    hash_busca = gerar_hash_busca(marca, modelo, versao, ano)
    veiculo = Veiculo(
        marca=marca,
        modelo=modelo,
        versao=versao,
        ano=ano,
        fonte=fonte,
        hash_busca=hash_busca,
        **especificacoes,
    )
    db.add(veiculo)
    db.commit()
    db.refresh(veiculo)
    return veiculo


def update_veiculo(
    db: Session,
    veiculo: Veiculo,
    especificacoes: dict,
    fonte: str,
):
    for chave, valor in especificacoes.items():
        setattr(veiculo, chave, valor)
    veiculo.fonte = fonte
    db.commit()
    db.refresh(veiculo)
    return veiculo


# ====
# BLOCO DE VALIDAÇÃO (TESTE LOCAL)
# ====
if __name__ == "__main__":
    import json

    print("--- Testando Orquestração Completa (VehicleService + Ollama) ---")
    servico = VehicleService()
    try:
        ficha_tecnica = servico.processar_veiculo_com_ia(
            marca="Ford",
            modelo="Ranger",
            versao="Raptor",
            ano=2025,
        )
        print("\n✅ Ficha Técnica Consolidada:")
        print(json.dumps(ficha_tecnica, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ Erro durante a orquestração: {e}")
