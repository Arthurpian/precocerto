# Grupo

Márcio Gastaldi - RM98811.
Arthur Bessa Pian - RM99215.
Davi Desenzi - RM550849.
João Victor - RM551410.
Fabrício Gutierrez Saavedra - RM97631.

# 💸 Preço Certo: monitor de preços com alerta no Telegram

Uma automação em Python que acompanha o preço de produtos em várias lojas online e manda uma mensagem no Telegram quando algum produto chega no preço que você quer pagar.

## O problema

Esperar um produto baixar de preço é chato: você precisa abrir o site todo dia, em várias lojas, e lembrar quanto custava antes. Com o **Preço Certo**, você cadastra o link e o preço alvo uma vez, e o programa verifica sozinho e avisa no celular.

## Como funciona

```
produtos.csv ──► extrator.py ──► main.py ──► telegram_bot.py ──► 📱 Telegram
(link + alvo)    (lê o preço)    (compara,     (API REST do
                                  salva         Telegram)
                                  histórico)
```

1. `main.py` lê a lista de produtos em `produtos.csv`.
2. Para cada link, o `extrator.py` baixa a página (`requests`) e lê o preço nos **dados estruturados schema.org (JSON-LD)**, o bloco que as lojas publicam para o Google mostrar o preço nas buscas.
3. O preço é salvo em `historico.csv`.
4. Se o preço estiver **igual ou abaixo do alvo** e tiver **mudado** desde a última verificação, o `telegram_bot.py` envia o alerta pela **API REST do Telegram**.

### Por que JSON-LD?

Testamos três formas de achar o preço na página da Kabum:

| Método | Preço encontrado | Resultado |
|---|---|---|
| Dados estruturados (JSON-LD) | R$ 399,90 | ✅ correto |
| Meta tags | não existe | — |
| Procurar o primeiro "R$" no texto | R$ 681,81 | ❌ errado |

Procurar "R$" no texto pega o primeiro valor que aparece (parcelamento, produto recomendado...). O JSON-LD diz de forma explícita qual é o preço do produto. Por isso o **mesmo código funciona em várias lojas**, sem programar site por site.

### Lojas testadas

| Loja | Funciona? |
|---|---|
| Kabum | ✅ |
| Fast Shop | ✅ |
| Carrefour | ✅ |
| Magazine Luiza, Casas Bahia, Pichau, Leroy Merlin, Netshoes | ❌ bloqueiam acesso automatizado (HTTP 403) |

As lojas que bloqueiam robôs foram respeitadas: o projeto não tenta burlar proteções anti-bot. O script `testar_extracao.py` mostra o teste feito em cada loja.

## Tecnologias

- **Python 3**
- **requests**: download das páginas e chamadas à API do Telegram
- **BeautifulSoup4**: leitura do HTML e dos dados JSON-LD
- **python-dotenv**: leitura do token do Telegram a partir do arquivo `.env`
- **API REST do Telegram** (`sendMessage`, `getUpdates`)
- **CSV**: lista de produtos e histórico de preços

## Estrutura

```
precocerto/
├── main.py              # programa principal
├── extrator.py          # lê o preço de uma página (JSON-LD)
├── telegram_bot.py      # envia mensagens pelo Telegram
├── pegar_chat_id.py     # ajuda a descobrir o seu chat_id
├── testar_extracao.py   # teste de quais lojas permitem leitura
├── produtos.csv         # seus produtos e preços alvo
├── requirements.txt
└── .gitignore           # impede que o .env (com o token) vá para o GitHub
```

## Como usar

### 1. Instalar

```bash
pip install -r requirements.txt
```

### 2. Criar o bot do Telegram

1. No Telegram, fale com o **@BotFather**, mande `/newbot` e guarde o **token**.
2. Crie um arquivo `.env` na pasta do projeto:
   ```
   TELEGRAM_TOKEN=seu_token
   ```
3. Mande `/start` para o seu bot e rode `python pegar_chat_id.py`.
4. Copie a linha `TELEGRAM_CHAT_ID=...` para o `.env`.
5. Teste com `python telegram_bot.py`.

### 3. Cadastrar produtos

Edite o `produtos.csv`:

```csv
url,preco_alvo
https://www.kabum.com.br/produto/...,350.00
```

### 4. Rodar

```bash
python main.py               # verifica uma vez
python main.py --repetir 30  # verifica a cada 30 minutos
```

Exemplo de saída:

```
=== Verificação 15/10/2026 16:36 — 3 produtos ===

[site.fastshop.com.br] Ferro de Passar a Vapor e a Seco Electrolux Experience Care
  Preço atual: R$ 169,00  |  Alvo: R$ 180,00
  🔔 Preço no alvo! Enviando alerta...
```

## Limitações

- Só funciona em lojas que publicam JSON-LD e não bloqueiam acesso automatizado.
- O programa precisa ficar rodando (`--repetir`) para monitorar continuamente.
- O alerta considera o preço principal publicado pela loja (que pode ser o preço no PIX ou à vista).

## Ideias futuras

- Agendar a execução automática pelo Agendador de Tarefas do Windows.
- Gráfico da evolução de preço a partir do `historico.csv`.
- Cadastrar produtos mandando o link direto para o bot no Telegram.
