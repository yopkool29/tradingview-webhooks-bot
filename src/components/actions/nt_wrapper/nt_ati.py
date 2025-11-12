import os
import uuid
import logging
from utils.log import get_logger
from utils.formatting import _convert_to_float, _convert_to_int
from ..nt_utils import NtUtils

logger = get_logger(__name__)


class NtATI(NtUtils):
    """NinjaTrader ATI (Automated Trading Interface) implementation"""
    
    def __init__(self):
        super().__init__()
        self.initialize()
    
    def place_order(
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
        """Place order using ATI file-based interface"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader")
            return False
        
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
        
        # Generate OCO ID if TP/SL are specified
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
    
    def flatten(self, symbol, account=None, strategy="", strategy_id=""):
        """Close all positions using ATI"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader")
            return False
        
        if account is None:
            account = self.account
        
        # Build ATI command to close all positions
        command = f"CLOSEPOSITION;{account};{symbol};;;;;;;;;;"
        
        logger.info(f"Closing all positions for {symbol} on account {account}")
        
        # Execute command
        result = self.execute_command(command)
        
        if result:
            logger.info(f"Position closed successfully: {command}")
        else:
            logger.error(f"Failed to close position: {command}")
        
        return result
