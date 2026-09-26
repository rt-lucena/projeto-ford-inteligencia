import json
import os
import re
from typing import Dict, List, Optional

import httpx

# Import da biblioteca oficial do Groq
from groq import Groq

# Tentativa de carregar a chave de API das configurações globais
try:
    from app.core.config import settings

    GROQ_API_KEY = getattr(settings, "GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))
except ImportError:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")


class GroqService:
    """
    Serviço para interagir com modelos de linguagem através da API da Groq.
    Responsável por extrair especificações técnicas de textos brutos, garantindo
    o retorno em um formato JSON rigoroso.
    """

    def __init__(
        self,
        model_name: str = "openai/gpt-oss-20b",
        temperature: float = 0.1,
        timeout: float = 30.0,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.timeout = timeout

        if not GROQ_API_KEY or GROQ_API_KEY == "SUA_CHAVE_AQUI":
            print("⚠️ AVISO: GROQ_API_KEY não configurada. A extração real falhará.")

        http_client_customizado = httpx.Client(verify=False)

        self.client = Groq(
            api_key=GROQ_API_KEY,
            timeout=self.timeout,
            http_client=http_client_customizado,
        )

    def extrair_especificacao(
        self,
        texto_cru: str,
        atributos: Dict[str, str],
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
        limite_caracteres: Optional[int] = 4000,
    ) -> Dict[str, str]:
        """
        Extrai atributos técnicos de um único texto utilizando a IA.
        """
        # Trunca o texto se um limite for definido
        if limite_caracteres and len(texto_cru) > limite_caracteres:
            print(f"✂️ Texto truncado de {len(texto_cru)} para {limite_caracteres} caracteres.")
            texto_cru = texto_cru[:limite_caracteres] + "... [TEXTO CORTADO PARA ECONOMIZAR TOKENS]"

        prompt = self._construir_prompt(
            texto_cru,
            atributos,
            marca,
            modelo,
            versao,
            ano,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=self.temperature,
            )

            conteudo = response.choices[0].message.content.strip()

            # Tenta interpretar a resposta como JSON diretamente
            try:
                resultado = json.loads(conteudo)
            except json.JSONDecodeError:
                # Fallback: Tenta localizar o bloco JSON usando Regex
                json_match = re.search(r"\{.*\}", conteudo, re.DOTALL)
                if json_match:
                    resultado = json.loads(json_match.group())
                else:
                    print(
                        f"❌ Erro: resposta da IA não contém JSON válido: {conteudo[:200]}",
                    )
                    return {attr: "não disponível" for attr in atributos}

            # Validação estrita: garante que todas as chaves solicitadas existam
            for attr in atributos:
                if attr not in resultado:
                    resultado[attr] = "não disponível"

            return resultado

        except Exception as e:
            print(f"❌ Erro ao chamar a API da Groq: {e}")
            return {attr: "não disponível" for attr in atributos}

    def processar_artigos(
        self,
        artigos: List[Dict[str, str]],
        atributos: Dict[str, str],
        marca: str,
        modelo: str,
        versao: str,
        ano: int,
        limite_caracteres: Optional[int] = None, # 🔥 NOVO: Repassa o limite para a extração
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
            print(f"🧠 Extraindo dados com IA: {url} (fonte={fonte})")

            resultado = self.extrair_especificacao(
                texto_completo,
                atributos,
                marca,
                modelo,
                versao,
                ano,
                limite_caracteres=limite_caracteres, # 🔥 Repassa o valor
            )
            resultado["fonte"] = fonte
            resultados.append(resultado)

        return resultados

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

        return f"""
        Você é um especialista automotivo focado em extração de dados técnicos.
        Sua tarefa é analisar o texto fornecido e extrair as especificações técnicas para o veículo {marca} {modelo} {versao} {ano}.

        🔥 REGRAS RÍGIDAS DE FOCO E SÍNTESE (MUITO IMPORTANTE):
        - O texto pode conter comparações com outras motorizações (ex: versões híbridas vs combustão pura). Extraia ESTRITAMENTE os dados correspondentes à versão '{versao}'. Ignore dados de versões superiores ou inferiores.
        - Seja conciso na descrição do motor. Evite termos de marketing. Exemplo correto: "2.0 Dynamic Force 16V". Exemplo incorreto: "Incrível motor 2.0 Dynamic Force 16V ciclo Atkinson flex com injeção direta".

        REGRAS GERAIS:
        1. Retorne APENAS um JSON válido. Sem formatação markdown, sem explicações, sem texto antes ou depois.
        2. O JSON deve conter EXATAMENTE estas chaves: [{chaves_esperadas}].
        3. Se uma informação não estiver no texto, preencha o valor com a string exata "não disponível". NÃO invente ou deduza dados.
        4. Regras de formatação específicas:
            - 'comprimento', 'largura', 'altura': Use EXCLUSIVAMENTE milímetros (mm). Não use metros.
            - 'peso': Use quilogramas (kg).
            - 'potencia' e 'torque': Inclua as rotações (rpm) se disponíveis (ex: 397 cv a 4.000 rpm).
            - 'preco': Mantenha a moeda e formatação original (ex: R$ 499.000).
            - 'suspensao', 'freios', 'rodas_e_pneus': Detalhe se a informação estiver presente (ex: Traseira Multilink, Discos ventilados, Aro 17).
            - 'modos_de_conducao': Retorne uma ÚNICA STRING com os modos separados por vírgula (ex: "Normal, Esporte, Baja"). NÃO retorne arrays ou listas.
            - 'propulsao': Defina estritamente o princípio de funcionamento do motor. Use APENAS "Combustão", "Híbrido" ou "Elétrico".
            - 'tipo_combustivel': Defina apenas a fonte de energia consumida. Use "Flex", "Gasolina", "Diesel" ou, se for 100% elétrico, "Eletricidade".
        5. Seja EXTREMAMENTE conciso nos valores. Máximo de 5 a 8 palavras por campo (exceto quando listar os modos de condução).

        TEXTO PARA ANÁLISE:
        {texto}

        RETORNO ESPERADO (Apenas JSON válido):
        {{
            "motor": "...",
            "potencia": "...",
            "torque": "...",
            "cambio": "...",
            "numero_de_marchas": "...",
            "tracao": "...",
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
        }}
        """


# ==========================================
# BLOCO DE VALIDAÇÃO (TESTE LOCAL)
# ==========================================
if __name__ == "__main__":
    import json

    print("--- Testando GroqService com Contrato de 15 Chaves ---")

    servico = GroqService()

    texto_teste = (
        "A Ford Ranger Raptor 2025 impressiona pelas dimensões: 5360 mm de comprimento, "
        "2028 mm de largura e 1926 mm de altura, pesando 2415 kg. O tanque de combustível comporta 80 litros. "
        "Sob o capô, o motor 3.0 V6 bi-turbo entrega 397 cv e 59,4 kgfm de torque, acoplado a um "
        "câmbio automático de 10 marchas com tração 4x4. Ela atinge 100 km/h em apenas 5,8 segundos, "
        "com velocidade máxima limitada a 180 km/h. O consumo urbano é de 8,3 km/l e o rodoviário chega a 10,2 km/l."
    )

    atributos_front = {
        "motor": "",
        "potencia": "",
        "torque": "",
        "cambio": "",
        "tracao": "",
        "suspensao": "",
        "freios": "",
        "rodas_e_pneus": "",
        "farois": "",
        "modos_de_conducao": "",
        "preco": "",
        "comprimento": "",
        "largura": "",
        "altura": "",
        "capacidade_do_tanque": "",
        "peso": "",
        "aceleracao_0_100": "",
    }

    print("Processando extração na API da Groq...")
    try:
        resultado = servico.extrair_especificacao(
            texto_cru=texto_teste,
            atributos=atributos_front,
            marca="Ford",
            modelo="Ranger",
            versao="Raptor",
            ano=2025,
        )
        print("\n✅ Resposta Estruturada (Contrato do Frontend):")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"\n⚠️ Falha no teste: {e}")
