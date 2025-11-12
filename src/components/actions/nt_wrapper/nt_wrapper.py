import os
import logging
from utils.log import get_logger
from .nt_ati import NtATI
from .nt_addon import NtAddOn

logger = get_logger(__name__)


class NtWrapper:
    """
    Wrapper that routes to either ATI or AddOn implementation based on NT_MODE
    """
    
    def __init__(self):
        self.mode = os.getenv("NT_MODE", "ATI").upper()
        self.implementation = None
        self.connected = False
        
        if self.mode == "ATI":
            logger.info("Using NinjaTrader ATI mode (file-based)")
            self.implementation = NtATI()
        elif self.mode == "ADDON":
            logger.info("Using NinjaTrader AddOn mode (HTTP API)")
            self.implementation = NtAddOn()
        else:
            logger.error(f"Invalid NT_MODE: {self.mode}. Must be 'ATI' or 'ADDON'")
            return
        
        self.connected = self.implementation.connected if self.implementation else False
    
    def initialize(self):
        """Initialize the selected implementation"""
        if self.implementation:
            return self.implementation.initialize()
        return False
    
    def shutdown(self):
        """Shutdown the selected implementation"""
        if self.implementation:
            self.implementation.shutdown()
    
    def place_order(self, **kwargs):
        """
        Place an order using the selected implementation
        
        Args:
            symbol: Instrument name
            order_type: "BUY" or "SELL"
            quantity: Number of contracts
            account: Account name (optional)
            order_kind: "MARKET", "LIMIT", "STOP", "STOPLIMIT"
            limit_price: Limit price (optional)
            stop_price: Stop price (optional)
            tif: Time in force (default: "DAY")
            oco: OCO order ID (optional)
            order_id: Custom order ID (optional)
            strategy: Strategy name (optional)
            strategy_id: Strategy ID (optional)
            tp: Take Profit price (optional)
            sl: Stop Loss price (optional)
        
        Returns:
            bool: True if order was placed successfully
        """
        if not self.implementation:
            logger.error("No implementation available")
            return False
        
        return self.implementation.place_order(**kwargs)
    
    def flatten(self, symbol, account=None, strategy="", strategy_id=""):
        """
        Close all positions for a symbol
        
        Args:
            symbol: Instrument name
            account: Account name (optional)
            strategy: Strategy name (optional)
            strategy_id: Strategy ID (optional)
        
        Returns:
            bool: True if positions were closed successfully
        """
        if not self.implementation:
            logger.error("No implementation available")
            return False
        
        return self.implementation.flatten(symbol, account, strategy, strategy_id)
    
    def get_positions(self, account=None):
        """
        Get current positions (AddOn mode only)
        
        Args:
            account: Account name (optional)
        
        Returns:
            list: List of positions or None
        """
        if not self.implementation:
            logger.error("No implementation available")
            return None
        
        if self.mode == "ADDON":
            return self.implementation.get_positions(account)
        else:
            logger.warning("get_positions() is only available in AddOn mode")
            return None
    
    def get_account_info(self, account=None):
        """
        Get account information (AddOn mode only)
            
        Args:
            account: Account name (optional)
        
        Returns:
            dict: Account information or None
        """
        if not self.implementation:
            logger.error("No implementation available")
            return None
        
        if self.mode == "ADDON":
            return self.implementation.get_account_info(account)
        else:
            logger.warning("get_account_info() is only available in AddOn mode")
            return None
    
    def get_orders(self, account=None):
        """
        Get all working orders (AddOn mode only)
        
        Args:
            account: Account name (optional)
        
        Returns:
            list: List of orders or None
        """
        if not self.implementation:
            logger.error("No implementation available")
            return None
        
        if self.mode == "ADDON":
            return self.implementation.get_orders(account)
        else:
            logger.warning("get_orders() is only available in AddOn mode")
            return None
