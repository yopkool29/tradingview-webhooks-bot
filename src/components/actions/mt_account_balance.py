import os
from components.actions.base.action import Action
import MetaTrader5 as mt5
from dotenv import load_dotenv
from utils.log import get_logger
from .mt_utils import MtUtils

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class MtAccountBalance(Action, MtUtils):

    def __init__(self):
        super().__init__()
        # Initialize MT5 connection
        self.login()

    def __del__(self):
        self.logout()

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

        # Get account balance
        account_info = mt5.account_info()
        if account_info is None:
            print("Failed to get account info")
        else:
            balance = account_info.balance
            print(f"Account balance: {balance}")
