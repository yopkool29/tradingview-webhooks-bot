import os
import logging
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger
from .nt_wrapper.nt_wrapper import NtWrapper

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtPlaceOrder(Action):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        self.nt = NtWrapper()

    def __del__(self):
        if hasattr(self, 'nt'):
            self.nt.shutdown()

    def __place_order(
        self,
        symbol,
        order_type,
        quantity,
        account=None,
        order_kind="MARKET",
        limit_price=None,
        stop_price=None,
        tif="DAY",
        oco="",
        order_id="",
        strategy="",
        strategy_id="",
        tp=None,
        sl=None,
    ):
        """
        Place an order in NinjaTrader using the configured mode (ATI or AddOn)
        """
        return self.nt.place_order(
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            account=account,
            order_kind=order_kind,
            limit_price=limit_price,
            stop_price=stop_price,
            tif=tif,
            oco=oco,
            order_id=order_id,
            strategy=strategy,
            strategy_id=strategy_id,
            tp=tp,
            sl=sl,
        )

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

        # Place order based on webhook data
        result = self.__place_order(
            symbol=data.get("symbol"),
            order_type=data.get("order_type"),
            quantity=data.get("quantity", 1),
            account=data.get("account", os.getenv("NT_ACCOUNT", "Sim101")),
            order_kind=data.get("order_kind", "MARKET"),
            limit_price=data.get("limit_price"),
            stop_price=data.get("stop_price"),
            tif=data.get("tif", "DAY"),
            oco=data.get("oco", ""),
            order_id=data.get("order_id", ""),
            strategy=data.get("strategy", ""),
            strategy_id=data.get("strategy_id", ""),
            tp=data.get("tp"),
            sl=data.get("sl"),
        )

        if result:
            logger.info("Order execution completed successfully")
        else:
            logger.error("Order execution failed")
