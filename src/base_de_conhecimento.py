import json
import os
import re
import sys
import unicodedata

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


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def buscar_coincidencias(chamado: str, base_conhecimento: list) -> list:
    """
    Busca coincidências entre o chamado e a base de conhecimento,
    removendo acentos e pontuação, e casando palavras inteiras.
    """
    resultados = []
    norm_chamado = normalize(chamado)

    for item in base_conhecimento:
        norm_palavras = [normalize(p) for p in item["palavras_chave"]]
        coincidencias = 0

        for p in norm_palavras:
            # regex \b para palavra inteira
            if re.search(rf"\b{re.escape(p)}\b", norm_chamado):
                coincidencias += 1

        # exige pelo menos 2 keywords diferentes
        if coincidencias > 1:
            resultados.append(
                {
                    "titulo": item["titulo"],
                    "categoria": item["categoria"],
                    "coincidencias": coincidencias,
                }
            )

    # ordena quem teve mais coincidências no topo
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
