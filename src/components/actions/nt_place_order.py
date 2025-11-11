import os
import logging
import uuid
from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.formatting import _convert_to_float, _convert_to_int
from utils.log import get_logger
from .nt_utils import NtUtils

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


class NtPlaceOrder(Action, NtUtils):

    def __init__(self):
        super().__init__()
        if os.getenv("NT_ENABLED", "false").lower() == "false":
            return
        NtUtils.__init__(self)
        self.initialize()

    def __del__(self):
        self.shutdown()

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
        Place an order in NinjaTrader
        
        Args:
            symbol: Instrument name (e.g., "NQ 12-24", "ES 12-24")
            order_type: "BUY" or "SELL"
            quantity: Number of contracts
            account: Account name (default from env)
            order_kind: "MARKET", "LIMIT", "STOP", "STOPLIMIT"
            limit_price: Limit price for LIMIT or STOPLIMIT orders
            stop_price: Stop price for STOP or STOPLIMIT orders
            tif: Time in force - "DAY", "GTC", "GTD", "IOC", "FOK"
            oco: OCO order ID
            order_id: Custom order ID
            strategy: Strategy name
            strategy_id: Strategy ID
            tp: Take Profit price (will place a LIMIT order at this price)
            sl: Stop Loss price (will place a STOP order at this price)
        
        Returns:
            bool: True if order was placed successfully
            
        Note:
            TP/SL orders are placed as OCO (One-Cancels-Other) orders after the main order.
            When one is filled, the other is automatically cancelled.
        """

        # Use account from env if not provided
        if account is None:
            account = self.account

        # Validate order type
        order_type = order_type.upper()
        if order_type not in ["BUY", "SELL"]:
            logger.error(f"Invalid order type: {order_type}")
            return False

        # Convert quantity to int
        quantity = _convert_to_int(quantity)
        if quantity is None or quantity <= 0:
            logger.error(f"Invalid quantity: {quantity}")
            return False

        # Validate order kind
        order_kind = order_kind.upper()
        if order_kind not in ["MARKET", "LIMIT", "STOP", "STOPLIMIT"]:
            logger.error(f"Invalid order kind: {order_kind}")
            return False

        # Format prices
        limit_price_str = str(limit_price) if limit_price is not None else ""
        stop_price_str = str(stop_price) if stop_price is not None else ""

        oco_id = None
        use_oco_on_entry = False
        
        if tp is not None or sl is not None:
            oco_id = f"OCO_{uuid.uuid4().hex[:8]}"
            logger.info(f"Generated OCO ID for TP/SL: {oco_id}")
            
            # Only use OCO on entry order if it's not MARKET
            if order_kind != "MARKET":
                use_oco_on_entry = True
                logger.info(f"Using OCO on entry order (order type: {order_kind})")
            else:
                logger.info(f"MARKET order - TP/SL will be placed as separate OCO pair after fill")
        
        # Use the OCO ID for the entry order only if it's not MARKET
        oco_str = oco_id if use_oco_on_entry else oco

        # Build ATI command
        command = f"PLACE;{account};{symbol};{order_type};{quantity};{order_kind};{limit_price_str};{stop_price_str};{tif};{oco_str};{order_id};{strategy};{strategy_id}"

        logger.info(f"Placing {order_type} order: {quantity} {symbol} @ {order_kind}")
        
        # Execute command
        result = self.execute_command(command)
        
        if result:
            logger.info(f"Order placed successfully: {command}")
            
            # Place TP/SL orders if specified
            if oco_id is not None:
                
                # Determine TP/SL order types based on entry direction
                if order_type == "BUY":
                    tp_action = "SELL"
                    sl_action = "SELL"
                else:  # SELL
                    tp_action = "BUY"
                    sl_action = "BUY"
                
                # Place Take Profit order (LIMIT)
                if tp is not None:
                    tp_price = _convert_to_float(tp)
                    if tp_price is not None:
                        tp_command = f"PLACE;{account};{symbol};{tp_action};{quantity};LIMIT;{tp_price};;{tif};{oco_id};;{strategy};{strategy_id}"
                        tp_result = self.execute_command(tp_command)
                        if tp_result:
                            logger.info(f"Take Profit order placed: {tp_command}")
                        else:
                            logger.error(f"Failed to place Take Profit order")
                
                # Place Stop Loss order (STOPMARKET)
                if sl is not None:
                    sl_price = _convert_to_float(sl)
                    if sl_price is not None:
                        sl_command = f"PLACE;{account};{symbol};{sl_action};{quantity};STOPMARKET;;{sl_price};{tif};{oco_id};;{strategy};{strategy_id}"
                        sl_result = self.execute_command(sl_command)
                        if sl_result:
                            logger.info(f"Stop Loss order placed: {sl_command}")
                        else:
                            logger.error(f"Failed to place Stop Loss order")
        else:
            logger.error(f"Failed to place order: {command}")
        
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

        # Place order based on webhook data
        result = self.__place_order(
            symbol=data.get("symbol"),
            order_type=data.get("order_type"),
            quantity=data.get("quantity", 1),
            account=self.account,
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
