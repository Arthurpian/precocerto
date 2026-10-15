import json

import requests
from bs4 import BeautifulSoup

# Extrai título e preço de uma página de produto usando os dados estruturados
# schema.org (JSON-LD) que as lojas publicam para o Google.
# Funciona em qualquer loja que publique esse padrão e não bloqueie robôs (ex.: Kabum).

CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


class ErroExtracao(Exception):
    """Erro com mensagem amigável: site bloqueou, preço não encontrado, etc."""


def _procurar_produto(dados):
    """O JSON-LD pode vir como objeto, lista ou dentro de '@graph'. Procura o Product."""
    if isinstance(dados, list):
        for item in dados:
            achado = _procurar_produto(item)
            if achado:
                return achado
    elif isinstance(dados, dict):
        if dados.get("@type") == "Product":
            return dados
        if "@graph" in dados:
            return _procurar_produto(dados["@graph"])
    return None


def obter_preco(url):
    """Devolve {'titulo': str, 'preco': float} ou levanta ErroExtracao."""
    try:
        resp = requests.get(url, headers=CABECALHOS, timeout=15)
    except requests.RequestException as erro:
        raise ErroExtracao(f"falha de conexão: {erro}")

    if resp.status_code in (403, 429):
        raise ErroExtracao(f"a loja bloqueou o acesso automatizado (HTTP {resp.status_code})")
    if resp.status_code != 200:
        raise ErroExtracao(f"resposta inesperada (HTTP {resp.status_code})")

    # resp.content (bytes) em vez de resp.text: o BeautifulSoup lê o charset
    # declarado na própria página e evita acentos quebrados ("BritÃ¢nia")
    soup = BeautifulSoup(resp.content, "html.parser")
    for bloco in soup.find_all("script", type="application/ld+json"):
        try:
            produto = _procurar_produto(json.loads(bloco.string or ""))
        except json.JSONDecodeError:
            continue
        if not produto:
            continue

        ofertas = produto.get("offers", {})
        if isinstance(ofertas, list):        # algumas lojas mandam várias ofertas
            ofertas = ofertas[0]
        preco = ofertas.get("price") or ofertas.get("lowPrice")
        if preco:
            return {"titulo": produto.get("name", "(sem nome)"), "preco": float(preco)}

    raise ErroExtracao("a página não tem dados estruturados de preço (JSON-LD)")


if __name__ == "__main__":  # teste rápido:  py extrator.py
    teste = ("https://www.kabum.com.br/produto/191898/robo-aspirador-e-passa-pano-kabum-smart-100-"
             "5-modos-de-limpeza-sensor-anti-queda-carregamento-automatico-aplicativo-bivolt-branco-kbsf005")
    try:
        print(obter_preco(teste))
    except ErroExtracao as erro:
        print("Erro:", erro)
