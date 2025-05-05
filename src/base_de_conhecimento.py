import json
import os
import sys

from config import CHAMADOS_ENVIADOS_PATH


def carregar_base_de_conhecimento():
    """
    Carrega a base de conhecimento a partir de um arquivo JSON.

    Returns:
        list: Lista de conhecimentos carregados do arquivo.
    """
    print("📚 Carregando base de conhecimento...")
    if getattr(sys, "frozen", False):
        caminho_base = os.path.join(
            getattr(sys, "_MEIPASS", "src"), "../data/base_de_conhecimentos.json"
        )
    else:
        caminho_base = os.path.join(
            os.path.dirname(__file__), "../data/base_de_conhecimentos.json"
        )
    with open(caminho_base, "r", encoding="utf-8") as file:
        return json.load(file)["conhecimentos"]


def buscar_coincidencias(chamado, base_conhecimento):
    """
    Busca coincidências entre o chamado e a base de conhecimento.

    Args:
        chamado (str): Texto do chamado.
        base_conhecimento (list): Base de conhecimento a ser comparada.

    Returns:
        list: Lista de resultados ordenada por número de coincidências.
    """
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


def carregar_chamados_enviados():
    """Carrega os chamados enviados anteriormente a partir de um arquivo JSON."""
    if os.path.exists(CHAMADOS_ENVIADOS_PATH):
        with open(CHAMADOS_ENVIADOS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return []


def salvar_chamados_enviados(chamados_enviados):
    """Salva os chamados enviados no arquivo JSON."""
    with open(CHAMADOS_ENVIADOS_PATH, "w", encoding="utf-8") as file:
        json.dump(chamados_enviados, file, ensure_ascii=False, indent=4)


# Variável global de chamados enviados
CHAMADOS_ENVIADOS = carregar_chamados_enviados()
