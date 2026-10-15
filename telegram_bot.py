import os

import requests
from dotenv import load_dotenv

# Envia mensagens pelo bot do Telegram usando a API REST oficial.
# O token e o chat_id ficam no arquivo .env (que NÃO vai para o GitHub).

load_dotenv()  # lê o .env e coloca os valores nas variáveis de ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def telegram_configurado():
    return bool(TOKEN and CHAT_ID)


def enviar_mensagem(texto):
    """Manda `texto` para o seu Telegram. Sem .env configurado, só mostra no terminal."""
    if not telegram_configurado():
        print("  [Telegram não configurado — a mensagem seria esta]\n" + texto)
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    resposta = requests.post(url, data={"chat_id": CHAT_ID, "text": texto}, timeout=10)
    resposta.raise_for_status()  # token ou chat_id errado → erro aparece na hora


if __name__ == "__main__":  # teste:  py telegram_bot.py
    enviar_mensagem("Teste do monitor de preços ✅")
    print("Mensagem enviada!" if telegram_configurado() else "Configure o .env para enviar de verdade.")
