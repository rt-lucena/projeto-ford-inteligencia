# app/services/llm_service.py
import json
import re
from typing import Dict, List, Optional

import httpx

# Tenta carregar a URL do Ollama a partir das configurações globais
try:
    from app.core.config import settings

    OLLAMA_BASE_URL = getattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
except ImportError:
    OLLAMA_BASE_URL = "http://localhost:11434"


class LLMService:
    """
    Serviço para extração de especificações técnicas via LLM local (Ollama).
    Usa o modelo gemma4:e2b rodando em http://localhost:11434.
    Interface pública idêntica ao GroqService anterior.
    """

    def __init__(
        self,
        model_name: str = "gemma4:e2b",
        temperature: float = 0.1,
        timeout: float = 360.0,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout
        self.base_url = OLLAMA_BASE_URL

        print(
            f"🤖 LLMService iniciado: model={self.model_name} | endpoint={self.base_url}",
        )

    # ------------------------------------------------------------------
    # API pública (mesma assinatura do GroqService)
    # ------------------------------------------------------------------

    def extrair_especificacao(
        self,
        texto_cru: str,
        atributos: Dict[str, str],
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
        limite_caracteres: Optional[int] = 2500,
    ) -> Dict[str, str]:
        """
        Extrai atributos técnicos de um único texto usando o LLM local.
        """
        if limite_caracteres and len(texto_cru) > limite_caracteres:
            print(
                f"✂️ Texto truncado de {len(texto_cru)} para {limite_caracteres} chars.",
            )
            texto_cru = texto_cru[:limite_caracteres] + "... [TEXTO CORTADO]"

        prompt = self._construir_prompt(
            texto_cru,
            atributos,
            marca,
            modelo,
            versao,
            ano,
        )

        try:
            conteudo = self._chamar_ollama(prompt)

            # Tenta interpretar a resposta como JSON diretamente
            try:
                resultado = json.loads(conteudo)
            except json.JSONDecodeError:
                # Fallback: localiza o primeiro bloco JSON com Regex
                json_match = re.search(r"\{.*\}", conteudo, re.DOTALL)
                if json_match:
                    try:
                        resultado = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        print(f"❌ JSON inválido mesmo após regex: {conteudo[:300]}")
                        return {attr: "não disponível" for attr in atributos}
                else:
                    print(f"❌ Nenhum JSON encontrado na resposta: {conteudo[:300]}")
                    return {attr: "não disponível" for attr in atributos}

            # Garante que todas as chaves solicitadas existam na resposta
            for attr in atributos:
                if attr not in resultado:
                    resultado[attr] = "não disponível"

            return resultado

        except Exception as e:
            print(f"❌ Erro ao chamar o Ollama: {e}")
            return {attr: "não disponível" for attr in atributos}

    def processar_artigos(
        self,
        artigos: List[Dict[str, str]],
        atributos: Dict[str, str],
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
        limite_caracteres: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Processa uma lista de artigos e retorna os atributos extraídos de cada um,
        preservando a fonte original.
        """
        resultados = []
        for idx, artigo in enumerate(artigos):
            titulo = artigo.get("titulo", "")
            conteudo = artigo.get("conteudo", "")
            fonte = artigo.get("fonte", "desconhecido")
            url = artigo.get("url", f"artigo_{idx + 1}")

            if not conteudo.strip():
                print(f"⚠️ Ignorando artigo sem conteúdo: {url}")
                continue

            texto_completo = f"{titulo}\n{conteudo}" if titulo else conteudo
            print(f"🧠 Extraindo dados com IA local: {url} (fonte={fonte})")

            resultado = self.extrair_especificacao(
                texto_completo,
                atributos,
                marca,
                modelo,
                versao,
                ano,
                limite_caracteres=limite_caracteres,
            )
            resultado["fonte"] = fonte
            resultados.append(resultado)

        return resultados

    # ------------------------------------------------------------------
    # Métodos internos
    # ------------------------------------------------------------------

    def _chamar_ollama(self, prompt: str) -> str:
        """
        Faz a chamada HTTP ao endpoint /api/chat do Ollama e retorna o texto gerado.
        Usa 'format: json' para forçar saída JSON válida.
        """
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            # Força o modelo a retornar JSON bem formado
            "format": "json",
            "options": {
                "temperature": self.temperature,
                # Tokens suficientes para o JSON de 22 campos com valores curtos
                "num_predict": 1024,
            },
        }

        response = httpx.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"].strip()

    def _construir_prompt(
        self,
        texto: str,
        atributos_esperados: dict,
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
    ) -> str:
        chaves_esperadas = ", ".join(f'"{k}"' for k in atributos_esperados.keys())

        return f"""Você é um especialista automotivo focado em extração de dados técnicos.
Sua tarefa é analisar o texto fornecido e extrair as especificações técnicas para o veículo {marca} {modelo} {versao} {ano}.

🔥 REGRAS RÍGIDAS DE FOCO E SÍNTESE (MUITO IMPORTANTE):
- O texto pode conter comparações com outras motorizações. Extraia ESTRITAMENTE os dados da versão '{versao}'. Ignore dados de outras versões.
- Seja conciso na descrição do motor. Evite termos de marketing.

REGRAS GERAIS:
1. Retorne APENAS um JSON válido. Sem markdown, sem explicações, sem texto antes ou depois.
2. O JSON deve conter EXATAMENTE estas chaves: [{chaves_esperadas}].
3. Se uma informação não estiver no texto, preencha com a string exata "não disponível". NÃO invente dados.
4. Regras de formatação:
   - 'comprimento', 'largura', 'altura': Use EXCLUSIVAMENTE milímetros (mm).
   - 'peso': Use quilogramas (kg).
   - 'potencia' e 'torque': Inclua as rotações (rpm) se disponíveis.
   - 'preco': Mantenha a moeda e formatação original (ex: R$ 499.000).
   - 'modos_de_conducao': Uma ÚNICA STRING com os modos separados por vírgula. NÃO use arrays.
   - 'propulsao': Use APENAS "Combustão", "Híbrido" ou "Elétrico".
   - 'tipo_combustivel': Use "Flex", "Gasolina", "Diesel" ou "Eletricidade".
5. Seja EXTREMAMENTE conciso. Máximo de 5 a 8 palavras por campo.

TEXTO PARA ANÁLISE:
{texto}

RETORNO ESPERADO (apenas JSON válido, sem nenhum texto adicional):
{{
  "motor": "...",
  "potencia": "...",
  "torque": "...",
  "cambio": "...",
  "numero_de_marchas": "...",
  "tracao": "...",
  "propulsao": "...",
  "suspensao": "...",
  "freios": "...",
  "rodas_e_pneus": "...",
  "farois": "...",
  "modos_de_conducao": "...",
  "comprimento": "...",
  "largura": "...",
  "altura": "...",
  "capacidade_do_tanque": "...",
  "peso": "...",
  "aceleracao_0_100": "...",
  "velocidade_maxima": "...",
  "consumo_urbano": "...",
  "consumo_rodoviario": "...",
  "preco": "...",
  "tipo_combustivel": "..."
}}"""


# ====
# BLOCO DE VALIDAÇÃO (TESTE LOCAL)
# ====
if __name__ == "__main__":
    print("--- Testando LLMService com Ollama + gemma4:e2b ---")

    servico = LLMService()

    texto_teste = (
        "A Ford Ranger Raptor 2025 impressiona pelas dimensões: 5360 mm de comprimento, "
        "2028 mm de largura e 1926 mm de altura, pesando 2415 kg. O tanque comporta 80 litros. "
        "Sob o capô, o motor 3.0 V6 bi-turbo entrega 397 cv e 59,4 kgfm de torque, "
        "câmbio automático de 10 marchas com tração 4x4. Atinge 100 km/h em 5,8 s, "
        "velocidade máxima 180 km/h. Consumo urbano 8,3 km/l, rodoviário 10,2 km/l."
    )

    atributos_front = {
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

    print("Processando extração via Ollama local...")
    try:
        resultado = servico.extrair_especificacao(
            texto_cru=texto_teste,
            atributos=atributos_front,
            marca="Ford",
            modelo="Ranger",
            versao="Raptor",
            ano=2025,
        )
        print("\n✅ Resposta Estruturada:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n⚠️ Falha no teste: {e}")
