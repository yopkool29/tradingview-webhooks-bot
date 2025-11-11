import os
import logging
from components.actions.base.action import Action
import MetaTrader5 as mt5
from dotenv import load_dotenv
from utils.formatting import _convert_to_float, _convert_to_int
from utils.log import get_logger
from .mt_utils import MtUtils

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class MtPlaceOrder(Action, MtUtils):

    def __init__(self):
        super().__init__()
        self.login()

    def __del__(self):
        self.logout()

    def __place_order(
        self,
        magic,
        symbol,
        order_type,
        volume,
        price=None,
        deviation=20,
        tp=None,
        sl=None,
        tp_rel=None,
        sl_rel=None,
    ):
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Symbol {symbol} not found")
            return None

        magic = _convert_to_int(magic)

        if magic is None or not isinstance(magic, int):
            logger.error("Magic number is missing or invalid")
            return None

        if order_type not in ["buy", "sell"]:
            logger.error("Invalid order type")
            return None

        # Récupérer les propriétés du symbole
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Failed to get symbol info for {symbol}")
            return None

        volume = _convert_to_float(volume)
        if volume is None:
            logger.error("Volume is missing or invalid")
            return None

        digits = symbol_info.digits

        # Calculer le prix d'entrée
        if price is not None:
            entry_price = _convert_to_float(price)
        else:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick for {symbol}")
                return None
            entry_price = tick.ask if order_type == "buy" else tick.bid

        # Calculer les prix TP/SL à partir des valeurs relatives
        if tp_rel is not None:
            point_value = mt5.symbol_info(symbol).point
            if order_type == "buy":
                tp = entry_price + (tp_rel * point_value)
            else:  # sell
                tp = entry_price - (tp_rel * point_value)
            tp = round(tp, digits)

        if sl_rel is not None:
            point_value = mt5.symbol_info(symbol).point
            if order_type == "buy":
                sl = entry_price - (sl_rel * point_value)
            else:  # sell
                sl = entry_price + (sl_rel * point_value)
            sl = round(sl, digits)

        try:

            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": (
                    mt5.ORDER_TYPE_BUY if order_type == "buy" else mt5.ORDER_TYPE_SELL
                ),
                "price": (
                    price or mt5.symbol_info_tick(symbol).ask
                    if order_type == "buy"
                    else mt5.symbol_info_tick(symbol).bid
                ),
                "deviation": deviation,
                "magic": magic,
                "comment": f"TradingView Webhook {magic}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # print(test_req)
            # print(request)
            # request = test_req

            # Ajouter TP et SL s'ils sont fournis
            if tp is not None:
                request["tp"] = tp
            if sl is not None:
                request["sl"] = sl

            # Send order to MT5
            result = mt5.order_send(request)
            print("Order result:", result)
            return result

        except Exception as e:
            print("An error occurred:", e)
            return None

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required

        if os.getenv("MT5_ENABLED", "false").lower() == "false":
            logger.warning("MetaTrader 5 is disabled (MT5_ENABLED=false in .env)")
            return

        # Vérifier si on est connecté
        terminal_info = mt5.terminal_info()
        if terminal_info is None or not terminal_info.connected:
            if not self.login():
                return

        data = self.validate_data()

        print("Received webhook data:", data)

        # Place order based on webhook data
        self.__place_order(
            magic=data.get("magic"),
            symbol=data.get("symbol"),
            order_type=data.get("order_type"),
            volume=data.get("volume", 0.1),
            price=data.get("price"),
            deviation=data.get("deviation", 10),
            tp=data.get("tp"),
            sl=data.get("sl"),
            tp_rel=data.get("tp_rel"),
            sl_rel=data.get("sl_rel"),
        )
