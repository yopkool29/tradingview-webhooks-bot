import os
import logging
import requests
from utils.log import get_logger
from utils.formatting import _convert_to_float, _convert_to_int

logger = get_logger(__name__)


class NtAddOn:
    """NinjaTrader AddOn HTTP API implementation"""
    
    def __init__(self):
        self.host = os.getenv("NT_ADDON_HOST", "localhost")
        self.port = int(os.getenv("NT_ADDON_PORT", "8181"))
        self.base_url = f"http://{self.host}:{self.port}"
        self.account = os.getenv("NT_ACCOUNT", "Sim101")
        self.connected = False
        self.initialize()
    
    def initialize(self):
        """Check if AddOn is available"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            if response.status_code == 200:
                self.connected = True
                logger.info(f"Connected to NinjaTrader AddOn at {self.base_url}")
                return True
            else:
                logger.error(f"NinjaTrader AddOn returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to NinjaTrader AddOn: {e}")
            logger.error(f"Make sure the NinjaTrader AddOn is running and listening on {self.base_url}")
            return False
    
    def shutdown(self):
        """Cleanup"""
        self.connected = False
    
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
        """Place order using HTTP API"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader AddOn")
            return False
        
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
        
        # Build request payload
        payload = {
            "account": account,
            "symbol": symbol,
            "action": order_type,
            "quantity": quantity,
            "orderType": order_kind,
            "limitPrice": limit_price,
            "stopPrice": stop_price,
            "tif": tif,
            "oco": oco,
            "orderId": order_id,
            "strategy": strategy,
            "strategyId": strategy_id,
            "tp": tp,
            "sl": sl,
        }
        
        logger.info(f"Placing {order_type} order: {quantity} {symbol} @ {order_kind}")
        
        try:
            response = requests.post(
                f"{self.base_url}/order/place",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Order placed successfully: {result}")
                return True
            else:
                logger.error(f"Failed to place order: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error placing order: {e}")
            return False
    
    def flatten(self, symbol, account=None, strategy="", strategy_id=""):
        """Close all positions using HTTP API"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader AddOn")
            return False
        
        if account is None:
            account = self.account
        
        payload = {
            "account": account,
            "symbol": symbol,
            "strategy": strategy,
            "strategyId": strategy_id,
        }
        
        logger.info(f"Closing all positions for {symbol} on account {account}")
        
        try:
            response = requests.post(
                f"{self.base_url}/position/flatten",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Position closed successfully: {result}")
                return True
            else:
                logger.error(f"Failed to close position: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error closing position: {e}")
            return False
    
    def get_positions(self, account=None):
        """Get current positions"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader AddOn")
            return None
        
        if account is None:
            account = self.account
        
        try:
            response = requests.get(
                f"{self.base_url}/positions",
                params={"account": account},
                timeout=5
            )
            
            if response.status_code == 200:
                positions = response.json()
                logger.info(f"Positions retrieved: {positions}")
                return positions
            else:
                logger.error(f"Failed to get positions: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting positions: {e}")
            return None
    
    def get_account_info(self, account=None):
        """Get account information"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader AddOn")
            return None
        
        if account is None:
            account = self.account
        
        try:
            response = requests.get(
                f"{self.base_url}/account",
                params={"account": account},
                timeout=5
            )
            
            if response.status_code == 200:
                account_info = response.json()
                logger.info(f"Account info retrieved: {account_info}")
                return account_info
            else:
                logger.error(f"Failed to get account info: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_orders(self, account=None):
        """Get all working orders"""
        
        if not self.connected:
            logger.error("Not connected to NinjaTrader AddOn")
            return None
        
        if account is None:
            account = self.account
        
        try:
            response = requests.get(
                f"{self.base_url}/orders",
                params={"account": account},
                timeout=5
            )
            
            if response.status_code == 200:
                orders = response.json()
                logger.info(f"Orders retrieved: {orders}")
                return orders
            else:
                logger.error(f"Failed to get orders: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting orders: {e}")
            return None
