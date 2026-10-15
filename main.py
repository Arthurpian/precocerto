"""
Monitor de preços: lê os produtos de produtos.csv, consulta o preço atual
em cada loja e avisa no Telegram quando o preço chega no valor que você quer.

Uso:
  py main.py              -> verifica uma vez
  py main.py --repetir 30 -> verifica a cada 30 minutos (Ctrl+C para parar)
"""
import argparse
import csv
import os
import time
from datetime import datetime

from extrator import ErroExtracao, obter_preco
from telegram_bot import enviar_mensagem

ARQ_PRODUTOS = "produtos.csv"
ARQ_HISTORICO = "historico.csv"


def ler_produtos():
    """Lê produtos.csv -> lista de {'url': ..., 'preco_alvo': float}."""
    with open(ARQ_PRODUTOS, encoding="utf-8") as f:
        return [{"url": linha["url"].strip(), "preco_alvo": float(linha["preco_alvo"])}
                for linha in csv.DictReader(f) if linha["url"].strip()]


def ultimo_preco_registrado(url):
    """Procura no histórico o último preço visto para essa URL (ou None)."""
    if not os.path.exists(ARQ_HISTORICO):
        return None
    ultimo = None
    with open(ARQ_HISTORICO, encoding="utf-8") as f:
        for linha in csv.DictReader(f):
            if linha["url"] == url:
                ultimo = float(linha["preco"])
    return ultimo


def salvar_no_historico(titulo, url, preco):
    """Acrescenta uma linha em historico.csv (cria o arquivo com cabeçalho na 1ª vez)."""
    novo = not os.path.exists(ARQ_HISTORICO)
    with open(ARQ_HISTORICO, "a", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        if novo:
            escritor.writerow(["data_hora", "titulo", "url", "preco"])
        escritor.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), titulo, url, preco])


def reais(valor):
    """399.9 -> 'R$ 399,90' (formato brasileiro)."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def verificar_todos():
    produtos = ler_produtos()
    print(f"\n=== Verificação {datetime.now():%d/%m/%Y %H:%M} — {len(produtos)} produtos ===")

    for item in produtos:
        url, alvo = item["url"], item["preco_alvo"]
        loja = url.split("/")[2].replace("www.", "")  # ex.: kabum.com.br

        try:
            dados = obter_preco(url)
        except ErroExtracao as erro:
            print(f"\n[{loja}] ❌ {erro}")
            continue  # uma loja com problema não para as outras

        preco, titulo = dados["preco"], dados["titulo"]
        anterior = ultimo_preco_registrado(url)  # lê ANTES de salvar o preço novo
        salvar_no_historico(titulo, url, preco)

        print(f"\n[{loja}] {titulo[:60]}")
        print(f"  Preço atual: {reais(preco)}  |  Alvo: {reais(alvo)}"
              + (f"  |  Antes: {reais(anterior)}" if anterior is not None else ""))

        if preco <= alvo and preco != anterior:
            # Avisa só quando o preço MUDOU, para não repetir o alerta a cada verificação
            print("  🔔 Preço no alvo! Enviando alerta...")
            enviar_mensagem(
                f"🔔 Baixou o preço!\n\n{titulo}\n"
                f"Agora: {reais(preco)} (seu alvo: {reais(alvo)})\n"
                + (f"Antes: {reais(anterior)}\n" if anterior is not None else "")
                + f"\n{url}"
            )
        elif preco <= alvo:
            print("  Preço no alvo, mas igual à última verificação (alerta já enviado).")
        else:
            print(f"  Faltam {reais(preco - alvo)} para o alvo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de preços com alerta no Telegram")
    parser.add_argument("--repetir", type=int, metavar="MIN",
                        help="repete a verificação a cada MIN minutos")
    args = parser.parse_args()

    verificar_todos()
    while args.repetir:
        print(f"\nPróxima verificação em {args.repetir} min (Ctrl+C para parar)...")
        time.sleep(args.repetir * 60)
        verificar_todos()
