import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service

from config import EDGE_DRIVER_PATH, GLPI_PASS, GLPI_USER


def iniciar_driver_e_logar_no_glpi():
    """
    Inicia o driver do Selenium e realiza o login no GLPI.

    Returns:
        WebDriver: Objeto do WebDriver se o login for bem-sucedido, caso contrário, retorna None.
    """
    print("🚀 Iniciando navegador em modo headless...")
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("--disable-logging")
    options.add_argument("--headless=new")

    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)

    try:
        print("🔐 Acessando GLPI...")
        driver.get("https://suporte.rn.senac.br/front/ticket.php")

        usuario = driver.find_element(By.ID, "login_name")
        senha = driver.find_element(By.ID, "login_password")
        usuario.send_keys(GLPI_USER)
        senha.send_keys(GLPI_PASS)
        senha.submit()

        time.sleep(5)
        url_atual = driver.current_url
        if "login" in url_atual.lower() or "ticket.php" not in url_atual:
            print("❌ Falha na autenticação! Verifique usuário e senha.")
            driver.quit()
            return None
        return driver

    except Exception as e:
        print(f"❌ Erro ao acessar o GLPI: {e}")
        driver.quit()
        return None


def sessao_esta_ativa(driver):
    """
    Verifica se a sessão do GLPI está ativa.

    Args:
        driver (WebDriver): Objeto do WebDriver.

    Returns:
        bool: True se a sessão estiver ativa, False caso contrário.
    """
    try:
        driver.get("https://suporte.rn.senac.br/front/ticket.php")
        time.sleep(3)
        url_atual = driver.current_url.lower()
        return "login" not in url_atual and "ticket.php" in url_atual
    except:
        return False
