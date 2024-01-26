from telegram.ext import Application, MessageHandler, filters
from config import TELEGRAM_TOKEN
from trading_bot import TradingBot


def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    async def message_handler(update, context):
        await TradingBot.receber_mensagens(update, context)

    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    application.add_handler(message_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
