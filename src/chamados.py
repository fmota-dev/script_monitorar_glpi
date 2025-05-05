from selenium.webdriver.common.by import By

from base_de_conhecimento import (
    CHAMADOS_ENVIADOS,
    buscar_coincidencias,
    salvar_chamados_enviados,
)
from utils.email import enviar_email


def extrair_titulos_e_processar(driver, base_conhecimento):
    """
    Coleta os títulos e categorias dos chamados, verifica coincidências na base de conhecimento e envia e-mails.

    Args:
        driver (WebDriver): Objeto do WebDriver.
        base_conhecimento (list): Base de conhecimento carregada.
    """
    print("📄 Coletando títulos e categorias dos chamados...")
    titulos = driver.find_elements(By.CSS_SELECTOR, 'a[id^="Ticket"][data-hasqtip]')
    for titulo in titulos:
        print(f"     - {titulo.text}")
    print(f"   - Total de chamados encontrados: {len(titulos)}")

    categorias = driver.find_elements(By.CSS_SELECTOR, 'td[valign="top"]')
    categorias_filtradas = [c.text for c in categorias if ">" in c.text]

    chamados = []
    for titulo, categoria in zip(titulos, categorias_filtradas):
        chamados.append(
            {
                "titulo": titulo.text,
                "categoria": categoria,
                "link": titulo.get_attribute("href"),
            }
        )

    enviados_hoje = []
    verificados = 0
    enviados_sucesso = 0
    nao_enviados = 0

    for chamado in chamados:
        print(f"\n🔎 Verificando chamado: {chamado['titulo']}")
        resultados = buscar_coincidencias(chamado["titulo"], base_conhecimento)
        if resultados:
            for resultado in resultados:
                if resultado["titulo"] not in CHAMADOS_ENVIADOS:
                    enviar_email(resultado["titulo"], chamado["link"])
                    enviados_hoje.append(resultado["titulo"])
                    enviados_sucesso += 1
                else:
                    nao_enviados += 1
        else:
            nao_enviados += 1
        verificados += 1

    CHAMADOS_ENVIADOS.extend(enviados_hoje)
    salvar_chamados_enviados(CHAMADOS_ENVIADOS)

    print(f"\n✅ Resumo da execução:")
    print(f"   - Chamados verificados: {verificados}")
    print(f"   - Chamados enviados: {enviados_sucesso}")
    print(
        f"   - Chamados já enviados anteriormente: {len(CHAMADOS_ENVIADOS) - enviados_sucesso}"
    )
