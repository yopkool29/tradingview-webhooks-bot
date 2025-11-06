import os
from components.actions.base.action import Action
import MetaTrader5 as mt5
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MtAccountBalance(Action):
    def __init__(self):
        super().__init__()
        # Initialize MT5 connection
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

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required
        
        # Vérifier si on est connecté
        terminal_info = mt5.terminal_info()
        if terminal_info is None or not terminal_info.connected:
            self.login()

        # Get account balance
        account_info = mt5.account_info()
        if account_info is None:
            print("Failed to get account info")
        else:
            balance = account_info.balance
            print(f"Account balance: {balance}")
