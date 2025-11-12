import os
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger
from .nt_wrapper.nt_wrapper import NtWrapper

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtOrderInfo(Action):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        self.nt = NtWrapper()

    def __del__(self):
        if hasattr(self, 'nt'):
            self.nt.shutdown()

    def __get_orders(self, account=None):
        """
        Get all working orders using the configured mode (AddOn only)
        
        Args:
            account: Account name (optional, defaults to NT_ACCOUNT)
        
        Returns:
            list: List of orders or None
        """
        return self.nt.get_orders(account=account)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

        if os.getenv("NT_ENABLED", "false").lower() == "false":
            logger.warning("NinjaTrader is disabled (NT_ENABLED=false in .env)")
            return

        if not hasattr(self, 'nt') or not self.nt.connected:
            logger.error("NinjaTrader is not connected")
            return

        data = self.validate_data()
        logger.info(f"Received webhook data: {data}")

        account = data.get("account", os.getenv("NT_ACCOUNT", "Sim101"))

        result = self.__get_orders(account=account)

        if result is not None:
            logger.info(f"Orders retrieved successfully: {result}")
        else:
            logger.error("Failed to retrieve orders")
