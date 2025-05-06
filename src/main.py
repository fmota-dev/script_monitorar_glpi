import time

from base_de_conhecimento import carregar_base_de_conhecimento
from chamados import gerenciar_chamados
from glpi import iniciar_driver_e_logar_no_glpi, sessao_esta_ativa

if __name__ == "__main__":
    base_conhecimento = carregar_base_de_conhecimento()
    driver = iniciar_driver_e_logar_no_glpi()

    try:
        while True:
            try:
                if not driver or not sessao_esta_ativa(driver):
                    print(
                        "🔄 Sessão expirada ou driver não iniciado. Reautenticando..."
                    )
                    if driver:
                        driver.quit()
                    driver = iniciar_driver_e_logar_no_glpi()
            except Exception as e:
                print(f"⚠️ Erro ao verificar a sessão: {e}")
                if driver:
                    driver.quit()
                driver = iniciar_driver_e_logar_no_glpi()

            if driver:
                gerenciar_chamados(driver, base_conhecimento)
            else:
                print("❌ Falha ao iniciar ou restaurar a sessão.")

            print("⏳ Aguardando 10 minutos para a próxima verificação...\n")
            time.sleep(600)

    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário.")
    finally:
        if driver:
            driver.quit()
            print("🧹 Navegador encerrado com sucesso.")
