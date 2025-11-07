import os
import logging
from components.actions.base.action import Action
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Initialize logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MtFlatten(Action):
    def __init__(self):
        super().__init__()

        self.__login()

    def __login(self):

        # Get credentials from environment variables
        login = int(os.getenv('MT5_LOGIN', '123456'))
        password = os.getenv('MT5_PASSWORD', 'your_password')
        server = os.getenv('MT5_SERVER', 'your_server')

        if not mt5.initialize():
            print("initialize() failed, error code =", mt5.last_error())
            quit()

        # Login to MT5 account
        self.authorized = mt5.login(login, password, server)
        if not self.authorized:
            print("login failed, error code =", mt5.last_error())
            mt5.shutdown()
            quit()

    def __logout(self):
        mt5.shutdown()

    def __del__(self):
        """Destructor to ensure MT5 shutdown"""
        self.__logout()
        print("MT5 connection closed in destructor")

    def __flatten(self, magic, symbol):
        # Vérifier que le symbole existe
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Symbol {symbol} not found")
            return None

        # Vérifier que le magic number est valide
        if not isinstance(magic, int):
            logger.error("Magic number must be an integer")
            return None

        # Récupérer toutes les positions ouvertes pour ce symbole
        positions = mt5.positions_get(symbol=symbol)
        if positions is None:
            logger.error(f"Failed to get positions for {symbol}, error: {mt5.last_error()}")
            return None
        elif len(positions) == 0:
            logger.info(f"No open positions for {symbol}")
            return None

        # Filtrer par magic number
        positions = [p for p in positions if p.magic == magic]
        if not positions:
            logger.info(f"No open positions for {symbol} with magic {magic}")
            return None

        # Fermer chaque position
        for position in positions:
            # Déterminer le type d'ordre opposé pour fermer
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(symbol).ask

            # Préparer la requête de fermeture
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": position.volume,
                "type": order_type,
                "position": position.ticket,
                "price": price,
                "deviation": 20,
                "magic": magic,
                "comment": f"Close trade #{position.ticket}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            # Envoyer la requête
            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                logger.error(f"Failed to close position {position.ticket}: {result.comment}")
            else:
                logger.info(f"Closed position {position.ticket}")

        return True

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required

        # Vérifier si on est connecté
        terminal_info = mt5.terminal_info()
        if terminal_info is None or not terminal_info.connected:
            self.__login()

        data = self.validate_data()

        print('Received webhook data:', data)
        
        # Place order based on webhook data
        self.__flatten(
            magic=data.get('magic'),
            symbol=data.get('symbol'),
        )
