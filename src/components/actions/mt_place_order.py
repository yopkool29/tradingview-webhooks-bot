import os
from components.actions.base.action import Action
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MtPlaceOrder(Action):
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

    def __place_order(self, symbol, order_type, volume, price=None):
        try:
            # Prepare order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "type": mt5.ORDER_TYPE_BUY if order_type == 'buy' else mt5.ORDER_TYPE_SELL,
                "price": price or mt5.symbol_info_tick(symbol).ask if order_type == 'buy' else mt5.symbol_info_tick(symbol).bid,
                "deviation": 20,
                "magic": 234000,
                "comment": "TradingView Webhook",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Send order to MT5
            result = mt5.order_send(request)
            print("Order result:", result)
            return result
        
        except Exception as e:
            print("An error occurred:", e)
            return None

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required

        # Vérifier si on est connecté
        terminal_info = mt5.terminal_info()
        if terminal_info is None or not terminal_info.connected:
            self.__login()

        data = self.validate_data()

        print('Received webhook data:', data)
        
        # Place order based on webhook data
        self.__place_order(
            symbol=data.get('symbol'),
            order_type=data.get('order_type'),
            volume=data.get('volume', 0.1),
            price=data.get('price')
        )
