import re
import logging
from binance.client import Client
from decouple import config
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext


# Configurações
BINANCE_API_KEY = config('BINANCE_API_KEY')
BINANCE_API_SECRET = config('BINANCE_API_SECRET')
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')

# Clientes API
binance_client = Client(api_key=BINANCE_API_KEY, api_secret=BINANCE_API_SECRET)

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self):
        self.pattern = re.compile(r'\$(\w+) / (\w+)\s*COMPRA \((\d+x)\)\s*([\d.]+ a [\d.]+)\s*Take profit:\s*(.*?)Stop loss:\s*([\d.]+)', re.DOTALL)

    async def interpretar_mensagem(self, mensagem):
        logger.info(f"Recebendo mensagem para interpretar: \n{mensagem}")
        match = self.pattern.match(mensagem)
        if match:
            par_trading_moeda, par_trading_contra, alavancagem, intervalo_precos, alvos, stop_loss = match.groups()
            par_trading = f"{par_trading_moeda} / {par_trading_contra}"
            logger.info(f"Mensagem interpretada: \nPar de Trading: {par_trading}, Alavancagem: {alavancagem}, Intervalo de Preços: {intervalo_precos}, Alvos: {alvos}, Stop Loss: {stop_loss}")
            # Processamento adicional aqui
        else:
            logger.warning("A mensagem não corresponde ao padrão esperado.")


async def receber_mensagens(update: Update, context: CallbackContext):
    logger.info(f"Mensagem recebida: {update.message.text}")
    bot = context.bot_data.setdefault("bot", TradingBot())
    await bot.interpretar_mensagem(update.message.text)


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, receber_mensagens)
    application.add_handler(message_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
