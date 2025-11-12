import os
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger
from .nt_wrapper.nt_wrapper import NtWrapper

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtFlatten(Action):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        self.nt = NtWrapper()

    def __del__(self):
        if hasattr(self, 'nt'):
            self.nt.shutdown()

    def __flatten(self, symbol, account=None):
        """
        Close all positions for a symbol using the configured mode (ATI or AddOn)
        """
        return self.nt.flatten(symbol=symbol, account=account)

    def __flatten_strategy(self, symbol, strategy, strategy_id, account=None):
        """
        Close positions for a specific strategy using the configured mode (ATI or AddOn)
        """
        return self.nt.flatten(symbol=symbol, account=account, strategy=strategy, strategy_id=strategy_id)

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required

        if os.getenv("NT_ENABLED", "false").lower() == "false":
            logger.warning("NinjaTrader is disabled (NT_ENABLED=false in .env)")
            return

        # Check if wrapper is connected
        if not hasattr(self, 'nt') or not self.nt.connected:
            logger.error("NinjaTrader is not connected")
            return

        data = self.validate_data()

        logger.info(f"Received webhook data: {data}")

        # Check if strategy-specific flatten is requested
        strategy = data.get("strategy")
        strategy_id = data.get("strategy_id")
        
        # Get account from webhook data or environment
        account = data.get("account", os.getenv("NT_ACCOUNT", "Sim101"))
        
        if strategy and strategy_id:
            # Flatten specific strategy
            result = self.__flatten_strategy(
                symbol=data.get("symbol"),
                strategy=strategy,
                strategy_id=strategy_id,
                account=account,
            )
        else:
            # Flatten all positions for the symbol
            result = self.__flatten(
                symbol=data.get("symbol"),
                account=account,
            )

        if result:
            logger.info("Flatten execution completed successfully")
        else:
            logger.error("Flatten execution failed")
