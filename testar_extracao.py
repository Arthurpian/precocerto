"""
Teste rápido: consigo ler o preço desses links?

Tenta 3 estratégias em cada página e mostra qual funcionou.
O resultado diz como vamos escrever o extrator.py de verdade.

Uso:  python testar_extracao.py
"""
import json
import re

import requests
from bs4 import BeautifulSoup

LINKS = [
    "https://www.kabum.com.br/produto/191898/robo-aspirador-e-passa-pano-kabum-smart-100-5-modos-de-limpeza-sensor-anti-queda-carregamento-automatico-aplicativo-bivolt-branco-kbsf005",
    "https://site.fastshop.com.br/ferro-de-passar-a-vapor-e-a-seco-electrolux-experience-care----esi60-exesi60azl_prd/p",
    "https://www.carrefour.com.br/produto/fritadeira-air-fryer-britania-baf65a-65l-visor-glass-1700w-preto-110v-338273887",
    "https://www.leroymerlin.com.br/fechadura-intelbras-fd-1000-d-preta-de-sobrepor-com-senha_92474032",
    "https://www.netshoes.com.br/p/bastao-de-led-jbl-partylight-stick-bluetooth-N26-096Z-006",
]

# Sem esse cabeçalho, muitos sites percebem que é um robô e recusam a página
CABECALHOS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}


def estrategia_json_ld(soup):
    """1) Dados estruturados schema.org (o padrão que o Google lê)."""
    for bloco in soup.find_all("script", type="application/ld+json"):
        try:
            dados = json.loads(bloco.string or "")
        except json.JSONDecodeError:
            continue
        for item in dados if isinstance(dados, list) else [dados]:
            if item.get("@type") == "Product":
                ofertas = item.get("offers", {})
                if isinstance(ofertas, list):
                    ofertas = ofertas[0]
                preco = ofertas.get("price") or ofertas.get("lowPrice")
                if preco:
                    return float(preco)
    return None


def estrategia_meta(soup):
    """2) Meta tags de preço (usadas por Facebook/WhatsApp ao compartilhar o link)."""
    for nome in ["product:price:amount", "og:price:amount"]:
        tag = soup.find("meta", property=nome)
        if tag and tag.get("content"):
            return float(tag["content"])
    return None


def estrategia_texto(soup):
    """3) Plano B: procura o primeiro 'R$ 1.234,56' no texto visível."""
    achado = re.search(r"R\$\s*([\d.]+,\d{2})", soup.get_text(" "))
    if achado:
        return float(achado.group(1).replace(".", "").replace(",", "."))
    return None


for link in LINKS:
    print("\n" + link[:80] + "...")
    try:
        resp = requests.get(link, headers=CABECALHOS, timeout=15)
    except requests.RequestException as erro:
        print("  ERRO de conexão:", erro)
        continue

    print("  Status HTTP:", resp.status_code, "(200 = ok; 403/429 = site bloqueou)")
    if resp.status_code != 200:
        continue

    soup = BeautifulSoup(resp.text, "html.parser")
    titulo = soup.find("h1")
    print("  Produto:", titulo.get_text(strip=True) if titulo else "(não achei o título)")
    print("  1) JSON-LD:  ", estrategia_json_ld(soup))
    print("  2) Meta tags:", estrategia_meta(soup))
    print("  3) Texto R$: ", estrategia_texto(soup))
