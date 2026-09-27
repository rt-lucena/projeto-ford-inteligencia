# app/services/scraper_service.py
import json
import os
import sys
import ssl
import subprocess
from pathlib import Path

ssl._create_default_https_context = ssl.create_default_context

FILE_PATH = Path(__file__).resolve()
BACKEND_DIR = FILE_PATH.parent.parent.parent

# Garante que o projeto está no PYTHONPATH
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["SCRAPY_SETTINGS_MODULE"] = "app.scraping.settings"

def get_blog_scrapy(carro: str) -> list[dict]:
    """
    Orquestra a chamada do Scrapy isolando-o em um subprocesso.
    Evita colisão do Event Loop (asyncio) com o servidor do FastAPI.
    """
    data_raw_dir = BACKEND_DIR / "data" / "raw"
    data_raw_dir.mkdir(parents=True, exist_ok=True)

    # 🧹 Limpa os arquivos antigos para a IA não ler lixo
    for arquivo in data_raw_dir.glob("*.json*"):
        try:
            arquivo.unlink()
            print(f"🗑️ Cache antigo removido: {arquivo.name}")
        except Exception:
            pass

    temp_file = data_raw_dir / "temp_results.jsonl"
    perm_file = data_raw_dir / "scraping.json"

    print(f"🚀 Iniciando processo isolado do Scrapy para: {carro}...")

    # 🔥 A MÁGICA: Executa este próprio arquivo como um robô independente
    try:
        subprocess.run(
            [sys.executable, str(FILE_PATH), carro, str(temp_file)],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro ao rodar as aranhas do Scrapy: {e}")

    # Lê os dados que o subprocesso isolado gravou no arquivo temporário
    resultados = []
    if temp_file.exists():
        with open(temp_file, "r", encoding="utf-8") as f:
            for linha in f:
                if linha.strip():
                    resultados.append(json.loads(linha))

        # Consolida no arquivo final que a IA consome
        with open(perm_file, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=4)

        temp_file.unlink()  # Remove o temporário
        print(f"✅ Sucesso! {len(resultados)} itens coletados e salvos em {perm_file}")
    else:
        print("⚠️ Aviso: Nenhum dado foi retornado pelas spiders.")

    return resultados


# ==============================================================================
# 🕷️ BLOCO DE EXECUÇÃO ISOLADA DO SCRAPY (Roda fora do FastAPI)
# ==============================================================================
if __name__ == "__main__":
    # Captura os argumentos passados pelo subprocess.run()
    carro_query = sys.argv[1] if len(sys.argv) > 1 else "Ford Ranger Raptor"

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    settings_scrapy = get_project_settings()

    # Injeta dinamicamente o nome do arquivo temporário
    if len(sys.argv) > 2:
        temp_file_arg = sys.argv[2]
        settings_scrapy.set("FEEDS", {temp_file_arg: {"format": "jsonl", "encoding": "utf8"}})

    process = CrawlerProcess(settings_scrapy)

    from app.scraping.spiders.automaistv_spider import AutoMaisTVSpider
    from app.scraping.spiders.caranddriver_spider import CarAndDriverSpider
    from app.scraping.spiders.motor1_spider import Motor1Spider

    process.crawl(AutoMaisTVSpider, carro=carro_query)
    process.crawl(CarAndDriverSpider, carro=carro_query)
    process.crawl(Motor1Spider, carro=carro_query)

    # Inicia as aranhas. Quando terminarem, esse processo auxiliar morre liberando a memória.
    process.start()
