from decouple import config

BINANCE_API_KEY = config('BINANCE_API_KEY')
BINANCE_API_KEY_TESTNET = config('BINANCE_API_KEY_TESTNET')
BINANCE_API_KEY_TESTNET_GABRIEL = config('BINANCE_API_KEY_TESTNET_GABRIEL')
BINANCE_API_KEY_SPOT = config('BINANCE_API_KEY_SPOT')

BINANCE_API_SECRET = config('BINANCE_API_SECRET')
BINANCE_API_SECRET_TESTNET = config('BINANCE_API_SECRET_TESTNET')
BINANCE_API_SECRET_TESTNET_GABRIEL = config('BINANCE_API_SECRET_TESTNET_GABRIEL')
BINANCE_API_SECRET_SPOT = config('BINANCE_API_SECRET_SPOT')

TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
TELEGRAM_GROUP_ID = config('TELEGRAM_GROUP_ID', default=None)
