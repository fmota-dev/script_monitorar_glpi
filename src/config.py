import os
from typing import Optional

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()


def get_env_var(var_name: str) -> str:
    """
    Obtém o valor de uma variável de ambiente e garante que ela não seja vazia.

    Args:
        var_name (str): Nome da variável de ambiente.

    Returns:
        str: Valor da variável de ambiente.

    Raises:
        ValueError: Se a variável não estiver definida ou estiver vazia.
    """
    value: Optional[str] = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise ValueError(
            f"⚠️ Erro: A variável de ambiente '{var_name}' não está definida ou está vazia no arquivo .env."
        )
    return value


# Carregar variáveis de ambiente essenciais
GMAIL_USER = get_env_var("GMAIL_USER")
GMAIL_PASSWORD = get_env_var("GMAIL_PASSWORD")
DESTINATARIO = get_env_var("DESTINATARIO")
GLPI_USER = get_env_var("GLPI_USER")
GLPI_PASS = get_env_var("GLPI_PASS")
EDGE_DRIVER_PATH = r"C:\edgedriver_win64\msedgedriver.exe"
CHAMADOS_ENVIADOS_PATH = os.path.join(
    os.path.dirname(__file__), "../data/chamados_enviados.json"
)
