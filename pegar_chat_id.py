import os

import requests
from dotenv import load_dotenv

# Descobre o seu chat_id. Antes de rodar:
#  1) coloque TELEGRAM_TOKEN=... no arquivo .env
#  2) abra o seu bot no Telegram e mande /start (ou qualquer mensagem)
# Uso:  py pegar_chat_id.py

load_dotenv()
token = os.getenv("TELEGRAM_TOKEN")
if not token:
    raise SystemExit("Falta o TELEGRAM_TOKEN no arquivo .env")

dados = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=10).json()

if not dados.get("ok"):
    raise SystemExit(f"Token inválido? Resposta do Telegram: {dados}")
if not dados["result"]:
    raise SystemExit("Nenhuma mensagem encontrada. Mande /start para o seu bot e rode de novo.")

vistos = set()
for atualizacao in dados["result"]:
    chat = (atualizacao.get("message") or {}).get("chat")
    if chat and chat["id"] not in vistos:
        vistos.add(chat["id"])
        print(f"Chat de {chat.get('first_name', '')}: TELEGRAM_CHAT_ID={chat['id']}")
