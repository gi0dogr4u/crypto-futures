import logging
import os
import re
from binance.client import Client
from binance.enums import SIDE_BUY, ORDER_TYPE_LIMIT, TIME_IN_FORCE_GTC
from telegram import Update
from telegram.ext import CallbackContext
from config import BINANCE_API_KEY_TESTNET, BINANCE_API_SECRET_TESTNET


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingBot:
    def __init__(self):
        self.binance_client = Client(
            api_key=BINANCE_API_KEY_TESTNET,
            api_secret=BINANCE_API_SECRET_TESTNET,
            testnet=True
        )
        self.log_account_info()

    def log_account_info(self):
        try:
            account_info = self.binance_client.get_account()
            logging.info(f"Account Information: {account_info}")
        except Exception as e:
            logging.error(f"Error retrieving account information: {e}")

    @staticmethod
    async def receber_mensagens(update: Update, context: CallbackContext):
        if 'TELEGRAM_GROUP_ID' in os.environ and str(update.message.chat_id) != os.environ['TELEGRAM_GROUP_ID']:
            logger.warning("Ignorando mensagem de chat não autorizado.")
            return

        logger.info(f"Mensagem recebida: {update.message.text}")
        bot = context.bot_data.setdefault("bot", TradingBot())
        await bot.interpretar_mensagem(update.message.text)

    async def interpretar_mensagem(self, mensagem):
        pattern = re.compile(
            r'\$(\w+) / (\w+)\s*COMPRA \((\d+x)\)\s*([\d.]+ a [\d.]+)\s*Take profit:\s*(.*?)Stop loss:\s*([\d.]+)',
            re.DOTALL)
        match = pattern.match(mensagem)
        if match:
            par_trading_moeda, par_trading_contra, alavancagem, intervalo_precos, alvos_str, stop_loss_str = match.groups()
            par_trading = f"{par_trading_moeda}{par_trading_contra}"
            alvos = [float(x.split('-')[1].strip()) for x in alvos_str.split('\n') if '-' in x]
            stop_loss = float(stop_loss_str.strip())

            if len(alvos) > 1:
                take_profit1, take_profit2 = alvos[:2]

                max_allowed_percentage = 10.0
                try:
                    take_profit2 = float(take_profit2)

                    take_profit = take_profit1 if not 0.0 <= take_profit2 <= max_allowed_percentage else take_profit2
                except ValueError:
                    take_profit = take_profit1
            else:
                take_profit = alvos[0]

            logger.info(
                f"Mensagem interpretada: \nPar de Trading: {par_trading}, Alavancagem: {alavancagem}, "
                f"Intervalo de Preços: {intervalo_precos}, Take Profit Escolhido: {take_profit}, Stop Loss: {stop_loss}")

            self.abrir_ordem(par_trading, alavancagem, intervalo_precos, take_profit, stop_loss)
        else:
            logger.warning("A mensagem não corresponde ao padrão esperado.")

    def abrir_ordem(self, par_trading, alavancagem, intervalo_precos, take_profit, stop_loss):
        symbol = par_trading.replace(" / ", "")
        quantidade = int(re.search(r'\d+', alavancagem).group())
        preco_min, preco_max = map(float, intervalo_precos.split(" a "))

        percent_price_filter = self.get_percent_price_by_side_filter(symbol)
        if not percent_price_filter:
            return

        avg_price = float(self.binance_client.get_avg_price(symbol=symbol)['price'])

        take_profit_price = avg_price * (1 + take_profit / 100)
        take_profit_price = self.ajustar_precisao_e_verificar_filtro(symbol, take_profit_price)

        stop_loss_price = avg_price * (1 - stop_loss / 100)
        stop_loss_price = self.ajustar_precisao_e_verificar_filtro(symbol, stop_loss_price)

        print(f"Symbol: {symbol}")
        print(f"Avg Price: {avg_price}")
        print(f"Preco Max: {preco_max}")
        print(f"Take Profit Price: {take_profit_price}")
        print(f"Stop Loss Price: {stop_loss_price}")

        if take_profit_price is not None and stop_loss_price is not None:
            if self.is_price_within_percent_price_by_side_filter(symbol, take_profit_price, percent_price_filter) and \
                    self.is_price_within_percent_price_by_side_filter(symbol, stop_loss_price, percent_price_filter):
                self.criar_ordem_take_profit(symbol, quantidade, take_profit_price)
                self.criar_ordem_stop_loss(symbol, quantidade, stop_loss_price)
            else:
                logger.error("Preço máximo ou mínimo fora dos limites do filtro PERCENT_PRICE_BY_SIDE.")
        else:
            logger.error("Erro ao ajustar preços de take profit e stop loss.")

    def criar_ordem_take_profit(self, symbol, quantidade, take_profit_price):
        order_params = {
            'symbol': symbol,
            'side': SIDE_BUY,
            'type': ORDER_TYPE_LIMIT,
            'quantity': quantidade,
            'timeInForce': TIME_IN_FORCE_GTC,
            'price': take_profit_price
        }
        try:
            response = self.binance_client.create_order(**order_params)
            logger.info(f"Ordem de Take Profit criada com sucesso: {response}")
        except Exception as e:
            logger.error(f"Erro ao criar ordem de Take Profit: {e}")

    def criar_ordem_stop_loss(self, symbol, quantidade, stop_loss_price):
        order_params = {
            'symbol': symbol,
            'side': SIDE_BUY,
            'type': ORDER_TYPE_LIMIT,
            'quantity': quantidade,
            'timeInForce': TIME_IN_FORCE_GTC,
            'price': stop_loss_price
        }
        try:
            response = self.binance_client.create_order(**order_params)
            logger.info(f"Ordem de Stop Loss criada com sucesso: {response}")
        except Exception as e:
            logger.error(f"Erro ao criar ordem de Stop Loss: {e}")

    def get_price_filter(self, symbol):
        info = self.binance_client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                return float(f['minPrice']), float(f['maxPrice'])
        logger.error(f"Não foi possível encontrar o filtro 'PRICE_FILTER' para o símbolo {symbol}.")
        return None, None

    def get_price_precision(self, symbol):
        info = self.binance_client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                precision = f['tickSize'].find('1') - 1
                return max(0, precision)
        logger.error(f"Não foi possível encontrar o filtro 'PRICE_FILTER' para o símbolo {symbol}.")
        return None

    def ajustar_precisao_e_verificar_filtro(self, symbol, price):
        precision = self.get_price_precision(symbol)
        price = round(price, precision)

        min_price, max_price = self.get_price_filter(symbol)
        if not (min_price <= price <= max_price):
            logger.error(f"Preço fora do filtro PRICE_FILTER permitido: {price}")
            return None

        return price

    def get_percent_price_by_side_filter(self, symbol):
        info = self.binance_client.get_symbol_info(symbol)
        for f in info['filters']:
            if f['filterType'] == 'PERCENT_PRICE_BY_SIDE':
                return f
        logger.error(f"Não foi possível encontrar o filtro 'PERCENT_PRICE_BY_SIDE' para o símbolo {symbol}.")
        return None

    def is_price_within_percent_price_by_side_filter(self, symbol, price, percent_price_filter):
        avg_price = float(self.binance_client.get_avg_price(symbol=symbol)['price'])
        bid_multiplier_up = float(percent_price_filter['bidMultiplierUp'])
        bid_multiplier_down = float(percent_price_filter['bidMultiplierDown'])
        ask_multiplier_up = float(percent_price_filter['askMultiplierUp'])
        ask_multiplier_down = float(percent_price_filter['askMultiplierDown'])

        min_bid_price = avg_price * bid_multiplier_down
        max_bid_price = avg_price * bid_multiplier_up
        min_ask_price = avg_price * ask_multiplier_down
        max_ask_price = avg_price * ask_multiplier_up

        is_within_bid = min_bid_price <= price <= max_bid_price
        is_within_ask = min_ask_price <= price <= max_ask_price

        return is_within_bid or is_within_ask
