import os
import MetaTrader5 as mt5
from utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)


class MtUtils:
    def __init__(self):
        pass

    def login(self) -> bool:
        if os.getenv("MT5_ENABLED", "false").lower() == "false":
            return False

        try:
            # Get credentials from environment variables
            login = int(os.getenv("MT5_LOGIN", "123456"))
            password = os.getenv("MT5_PASSWORD", "your_password")
            server = os.getenv("MT5_SERVER", "your_server")

            if not mt5.initialize():
                error_code = mt5.last_error()
                print("initialize() failed, error code =", error_code)
                raise Exception(f"MT5 initialization failed: {error_code}")

            # Login to MT5 account
            self.authorized = mt5.login(login, password, server)
            if not self.authorized:
                error_code = mt5.last_error()
                print("login failed, error code =", error_code)
                mt5.shutdown()
                raise Exception(f"MT5 login failed: {error_code}")

            account_info = mt5.account_info()
            logger.info(f"Connected to MT5 demo account")
            logger.info(f"Login: {account_info.login}")
            logger.info(f"Balance: {account_info.balance}")
            logger.info(f"Server: {account_info.server}")
            logger.info(f"Currency: {account_info.currency}")

            self.connected = True
            
            return True

        except Exception as e:
            logger.error(f"Error initializing MT5 connection: {e}")
            self.connected = False
            return False

    def logout(self):
        if os.getenv("MT5_ENABLED", "false").lower() == "false":
            return
        if not self.connected:
            return
        mt5.shutdown()
        self.connected = False
