import os
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger
from .nt_utils import NtUtils

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtFlatten(Action, NtUtils):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        NtUtils.__init__(self)
        self.initialize()

    def __del__(self):
        self.shutdown()

    def __flatten(self, symbol, account=None):

        if not self.connected:
            logger.error("Not connected to NinjaTrader")
            return False

        # Use account from env if not provided
        if account is None:
            account = self.account

        # Build ATI command to close all positions
        # CLOSEPOSITION command closes all positions for the specified instrument
        command = f"CLOSEPOSITION;{account};{symbol};;;;;;;;;;"

        logger.info(f"Closing all positions for {symbol} on account {account}")
        
        # Execute command
        result = self.execute_command(command)
        
        if result:
            logger.info(f"Flatten command executed successfully: {command}")
        else:
            logger.error(f"Failed to execute flatten command: {command}")
        
        return result

    def __flatten_strategy(self, symbol, strategy, strategy_id, account=None):

        # Use account from env if not provided
        if account is None:
            account = self.account

        # Build ATI command to close positions for specific strategy
        command = f"CLOSEPOSITION;{account};{symbol};;;;;;;;{strategy};{strategy_id}"

        logger.info(f"Closing positions for {symbol} - Strategy: {strategy} ({strategy_id})")
        
        # Execute command
        result = self.execute_command(command)
        
        if result:
            logger.info(f"Flatten strategy command executed successfully: {command}")
        else:
            logger.error(f"Failed to execute flatten strategy command: {command}")
        
        return result

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # required

        if os.getenv("NT_ENABLED", "false").lower() == "false":
            logger.warning("NinjaTrader is disabled (NT_ENABLED=false in .env)")
            return

        # Reinitialize if not connected
        if not self.connected:
            if not self.initialize():
                logger.error("Failed to initialize NinjaTrader connection")
                return

        data = self.validate_data()

        logger.info(f"Received webhook data: {data}")

        # Check if strategy-specific flatten is requested
        strategy = data.get("strategy")
        strategy_id = data.get("strategy_id")
        
        if strategy and strategy_id:
            # Flatten specific strategy
            result = self.__flatten_strategy(
                symbol=data.get("symbol"),
                strategy=strategy,
                strategy_id=strategy_id,
                account=self.account,
            )
        else:
            # Flatten all positions for the symbol
            result = self.__flatten(
                symbol=data.get("symbol"),
                account=self.account,
            )

        if result:
            logger.info("Flatten execution completed successfully")
        else:
            logger.error("Flatten execution failed")
