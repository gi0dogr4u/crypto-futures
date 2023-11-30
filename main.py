from binance import Client
from telegram import Bot

# Chaves da API da Binance
api_key = '473EpWqGhTpx2wjSHm9QVmcYZguP3UvXdTPqeHJ2EHkw9CFCmgWoHpNm8RQlBh69'
api_secret = '0CrcmMYCmIWLWWFSJrsVJhPolkQgvPqsjyMc7vFP6bHyRKejUdMshe8uJcQzpuuF'

# Token do bot do Telegram
telegram_token = '6769253952:AAHc5p1UFPLYa5M5noXoI-m0YZ-k8TP-gWU'

# ID do grupo no Telegram
group_id = -4033459746  # Substitua pelo ID real do seu grupo

# Inicializar clientes da Binance e do Telegram
binance_client = Client(api_key, api_secret)
telegram_bot = Bot(token=telegram_token)

