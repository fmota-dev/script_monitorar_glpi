import os
import tempfile
import time
from urllib.parse import urljoin

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from base_de_conhecimento import (
    CHAMADOS_ENVIADOS,
    buscar_coincidencias,
    salvar_chamados_enviados,
)
from utils.email import enviar_email


def verificar_status_pendente(driver):
    """Verifica se o status do chamado é 'pendente'."""
    try:
        driver.find_element(By.CSS_SELECTOR, "i.itilstatus.waiting.fas.fa-circle")
        print("  ⏸️  Chamado marcado como Pendente. Ignorando processamento.")
        return True
    except:
        return False


def coletar_textos_e_imagens(container):
    """Coleta textos e imagens do container de detalhes do chamado."""
    descricao = "\n".join(
        [p.text.strip() for p in container.find_elements(By.TAG_NAME, "p")]
    )
    imagens = [
        img.get_attribute("src")
        for img in container.find_elements(
            By.CSS_SELECTOR, 'div[class^="pswp-img"] img'
        )
    ]
    return descricao, imagens


def ajustar_urls_imagens(imagens, base_url):
    """Ajusta URLs relativas para absolutas."""
    return [
        img if img.startswith("http") else urljoin(base_url, img) for img in imagens
    ]


def baixar_imagens(imagens, pasta_destino, driver):
    """Baixa imagens para o disco usando os cookies do Selenium."""
    os.makedirs(pasta_destino, exist_ok=True)
    session = requests.Session()
    for c in driver.get_cookies():
        session.cookies.set(c["name"], c["value"], domain=c.get("domain"))

    caminhos = []
    for idx, src in enumerate(imagens, start=1):
        try:
            resp = session.get(src, stream=True)
            resp.raise_for_status()
            ext = resp.headers.get("Content-Type", "").split("/")[-1] or "jpg"
            path = os.path.join(pasta_destino, f"img_{idx}.{ext}")
            with open(path, "wb") as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            caminhos.append(path)
            print(f"✔️ Baixada: {path}")
        except Exception as ex:
            print(f"❌ Falha ao baixar {src}: {ex}")
    return caminhos


def extrair_detalhes_chamado(
    driver, url, baixar_imagens_flag=False, pasta_destino=None
):
    """Extrai detalhes do chamado, incluindo descrição e imagens."""
    driver.get(url)
    time.sleep(2)

    if verificar_status_pendente(driver):
        return "(Chamado Pendente)", [], True

    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "rich_text_container"))
        )
    except Exception as e:
        print(f"⚠️ Erro ao carregar detalhes do chamado: {e}")
        return "(Não foi possível carregar conteúdo)", [], False

    try:
        descricao, imagens = coletar_textos_e_imagens(container)
        imagens = ajustar_urls_imagens(imagens, driver.current_url)
    except Exception as e:
        print(f"⚠️ Erro ao extrair descrição/imagens: {e}")
        return "(Erro na extração)", [], False

    if baixar_imagens and imagens and pasta_destino:
        imagens = (
            baixar_imagens(imagens, pasta_destino, driver)
            if baixar_imagens_flag
            else imagens
        )

    return descricao.strip(), imagens, False


def coletar_chamados(driver):
    """Coleta os títulos, categorias e links dos chamados."""
    print("📄 Coletando títulos e categorias dos chamados...")
    titulos = driver.find_elements(By.CSS_SELECTOR, 'a[id^="Ticket"][data-hasqtip]')
    categorias = driver.find_elements(By.CSS_SELECTOR, 'td[valign="top"]')
    categorias_filtradas = [c.text for c in categorias if ">" in c.text]

    chamados = [
        {
            "titulo": titulo_elem.text,
            "categoria": categoria,
            "link": titulo_elem.get_attribute("href"),
            "id": titulo_elem.get_attribute("href").split("=")[-1],
        }
        for titulo_elem, categoria in zip(titulos, categorias_filtradas)
    ]

    print(f"   - Total de chamados encontrados: {len(chamados)}")
    return chamados


def verificar_e_enviar_chamado(driver, chamado, base_conhecimento, processados):
    """Processa um único chamado, verificando coincidências e enviando e-mail."""
    print(f"\n🔎 Verificando chamado: {chamado['titulo']} (ID {chamado['id']})")

    resultados = buscar_coincidencias(chamado["titulo"], base_conhecimento)
    if (
        not resultados
        or chamado["id"] in CHAMADOS_ENVIADOS
        or chamado["id"] in processados
    ):
        return False

    with tempfile.TemporaryDirectory() as pasta_temp:
        descricao, imagens, pendente = extrair_detalhes_chamado(
            driver, chamado["link"], baixar_imagens_flag=True, pasta_destino=pasta_temp
        )
        if pendente:
            return False

        print("✅ Chamado a enviar:")
        print(f"   Título:    {chamado['titulo']}")
        print(f"   Link:      {chamado['link']}")
        print(f"   ID:        {chamado['id']}")
        print(f"   Descrição: {descricao[:100]}{'...' if len(descricao) > 100 else ''}")
        print(f"   Imagens:   {len(imagens)}")
        for idx, img in enumerate(imagens, 1):
            print(f"      {idx}. {img}")

        enviar_email(
            chamado["titulo"], chamado["link"], descricao, imagens, chamado["id"]
        )

    processados.add(chamado["id"])
    return True


def gerenciar_chamados(driver, base_conhecimento):
    """Extrai títulos e categorias dos chamados, processa e envia e-mails."""
    chamados = coletar_chamados(driver)
    processados = set()
    verificados = enviados_sucesso = nao_enviados = 0

    for chamado in chamados:
        verificados += 1
        if verificar_e_enviar_chamado(driver, chamado, base_conhecimento, processados):
            enviados_sucesso += 1
        else:
            nao_enviados += 1

    CHAMADOS_ENVIADOS.extend(processados)
    salvar_chamados_enviados(CHAMADOS_ENVIADOS)

    print(f"\n✅ Resumo da execução:")
    print(f"   - Chamados verificados: {verificados}")
    print(f"   - Chamados enviados: {enviados_sucesso}")
    print(
        f"   - Chamados já enviados anteriormente: {len(CHAMADOS_ENVIADOS) - enviados_sucesso}"
    )
