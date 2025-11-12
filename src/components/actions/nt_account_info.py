import os
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger
from .nt_wrapper.nt_wrapper import NtWrapper

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtAccountInfo(Action):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        self.nt = NtWrapper()

    def __del__(self):
        if hasattr(self, 'nt'):
            self.nt.shutdown()

    def __get_account_info(self, account=None):
        """
        Get account information using the configured mode (AddOn only)
        
        Args:
            account: Account name (optional, defaults to NT_ACCOUNT)
        
        Returns:
            dict: Account information or None
        """
        return self.nt.get_account_info(account=account)

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

        account = data.get("account", os.getenv("NT_ACCOUNT"))
        if not account:
            logger.error("Account name is required")
            return

        result = self.__get_account_info(account=account)

        if result:
            logger.info(f"Account info retrieved successfully: {result}")
        else:
            logger.error("Failed to retrieve account info")
