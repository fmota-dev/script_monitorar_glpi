import json
import os
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

EDGE_DRIVER_PATH = r"C:\edgedriver_win64\msedgedriver.exe"

load_dotenv()


# Função para obter variáveis de ambiente e garantir que não sejam None
def get_env_var(var_name: str) -> str:
    value: Optional[str] = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(
            f"⚠️ Erro: A variável de ambiente '{var_name}' não está definida ou está vazia no arquivo .env."
        )
    return value


# Definição segura das variáveis
GMAIL_USER = get_env_var("GMAIL_USER")
GMAIL_PASSWORD = get_env_var("GMAIL_PASSWORD")
DESTINATARIO = get_env_var("DESTINATARIO")
GLPI_USER = get_env_var("GLPI_USER")
GLPI_PASS = get_env_var("GLPI_PASS")

# Caminho para o arquivo que armazenará os chamados enviados
CHAMADOS_ENVIADOS_PATH = "chamados_enviados.json"


# Função para carregar a base de conhecimentos
def carregar_base_de_conhecimento():
    print("📚 Carregando base de conhecimento...")

    # Detecta se está sendo executado a partir do PyInstaller
    if getattr(sys, "frozen", False):
        # Quando empacotado, use sys._MEIPASS para obter o caminho correto
        caminho_base = os.path.join(
            getattr(sys, "_MEIPASS", ""), "base_de_conhecimentos.json"
        )
    else:
        # No ambiente de desenvolvimento, o arquivo está no mesmo diretório do script
        caminho_base = os.path.join(
            os.path.dirname(__file__), "base_de_conhecimentos.json"
        )

    # Abrir o arquivo JSON
    with open(caminho_base, "r", encoding="utf-8") as file:
        return json.load(file)["conhecimentos"]


# Função para buscar chamados na base de conhecimento
def buscar_coincidencias(chamado, base_conhecimento):
    resultados = []
    chamado_lower = chamado.lower()
    for item in base_conhecimento:
        coincidencias = sum(
            1 for palavra in item["palavras_chave"] if palavra in chamado_lower
        )
        if coincidencias > 1:
            resultados.append(
                {
                    "titulo": item["titulo"],
                    "categoria": item["categoria"],
                    "coincidencias": coincidencias,
                }
            )
    return sorted(resultados, key=lambda x: x["coincidencias"], reverse=True)


# Função para carregar os chamados já enviados
def carregar_chamados_enviados():
    if os.path.exists(CHAMADOS_ENVIADOS_PATH):
        with open(CHAMADOS_ENVIADOS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return []  # Retorna uma lista vazia se o arquivo não existir


# Função para salvar os chamados já enviados
def salvar_chamados_enviados(chamados_enviados):
    with open(CHAMADOS_ENVIADOS_PATH, "w", encoding="utf-8") as file:
        json.dump(chamados_enviados, file, ensure_ascii=False, indent=4)


# Função para enviar e-mail
def enviar_email(titulo_chamado, link_chamado):
    try:
        # Criando o e-mail
        subject = "🚨 Alerta de chamado em potencial"
        body = f"📌 Título: {titulo_chamado}\n🔗 Link: {link_chamado}"

        msg = MIMEMultipart()
        msg["From"] = GMAIL_USER
        msg["To"] = DESTINATARIO
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Enviando o e-mail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, DESTINATARIO, msg.as_string())

        print("✅ E-mail enviado com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


# Função principal para abrir o GLPI e extrair títulos
def abrir_glpi_e_extrair_titulos():
    print("🚀 Iniciando navegador em modo headless...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")

    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)

    print("🔐 Acessando GLPI...")
    driver.get("https://suporte.rn.senac.br/front/ticket.php")

    usuario = driver.find_element(By.ID, "login_name")
    senha = driver.find_element(By.ID, "login_password")

    usuario.send_keys(GLPI_USER)
    senha.send_keys(GLPI_PASS)
    senha.submit()

    time.sleep(5)

    print("📄 Coletando títulos e categorias dos chamados...")
    titulos = driver.find_elements(By.CSS_SELECTOR, 'a[id^="Ticket"][data-hasqtip]')
    lista_categorias = driver.find_elements(By.CSS_SELECTOR, 'td[valign="top"]')
    lista_categorias_filtradas = [
        categoria.text for categoria in lista_categorias if ">" in categoria.text
    ]

    chamados = []
    for titulo_elemento, categoria in zip(titulos, lista_categorias_filtradas):
        titulo_texto = titulo_elemento.text
        href = titulo_elemento.get_attribute("href")  # Captura o link completo
        chamados.append({"titulo": titulo_texto, "categoria": categoria, "link": href})

    base_conhecimento = carregar_base_de_conhecimento()

    # Carregar chamados já enviados
    chamados_enviados = carregar_chamados_enviados()

    chamados_verificados = 0
    chamados_enviados_com_sucesso = 0
    chamados_nao_enviados = 0

    # Manter uma lista para os títulos que foram enviados nessa execução
    chamados_enviados_hoje = []

    for chamado in chamados:
        print(f"\n🔎 Verificando chamado: {chamado['titulo']}")
        resultados = buscar_coincidencias(chamado["titulo"], base_conhecimento)
        if resultados:
            for resultado in resultados:
                titulo_chamado = resultado["titulo"]
                link_chamado = chamado["link"]
                # Verificar se o título já foi enviado
                if titulo_chamado not in chamados_enviados:
                    # Enviar o e-mail
                    enviar_email(titulo_chamado, link_chamado)
                    chamados_enviados_com_sucesso += 1
                    # Adicionar o título à lista de chamados enviados hoje
                    chamados_enviados_hoje.append(titulo_chamado)
                else:
                    chamados_nao_enviados += 1
        else:
            chamados_nao_enviados += 1

        chamados_verificados += 1

    # Salvar os chamados enviados hoje no arquivo
    chamados_enviados.extend(chamados_enviados_hoje)
    salvar_chamados_enviados(chamados_enviados)

    chamados_enviados_anteriormente = (
        len(chamados_enviados) - chamados_enviados_com_sucesso
    )

    # Exibir o resumo
    print(f"\n✅ Resumo da execução:")
    print(f"   - Chamados verificados: {chamados_verificados}")
    print(f"   - Chamados enviados: {chamados_enviados_com_sucesso}")
    print(f"   - Chamados já enviados anteriormente: {chamados_enviados_anteriormente}")

    driver.quit()
    print("✅ Processo finalizado.")


if __name__ == "__main__":
    try:
        while True:
            abrir_glpi_e_extrair_titulos()
            print("⏳ Aguardando 10 minutos para a próxima verificação...\n")
            time.sleep(600)  # 600 segundos = 10 minutos
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário.")
