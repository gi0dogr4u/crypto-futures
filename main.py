from binance import Client
from telegram import Bot
from decouple import config

# Chaves da API da Binance
api_key = config('BINANCE_API_KEY')
api_secret = config('BINANCE_API_SECRET')

# Token do bot do Telegram
telegram_token = config('TELEGRAM_TOKEN')

# ID do grupo no Telegram
group_id = int(config('TELEGRAM_GROUP_ID'))

# Inicializar clientes da Binance e do Telegram
binance_client = Client(api_key, api_secret)
telegram_bot = Bot(token=telegram_token)

