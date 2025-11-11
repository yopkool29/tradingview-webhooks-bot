import os
import uuid
import winreg
import psutil
from utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)


class NtUtils:
    """Utility class for NinjaTrader operations using ATI (Automated Trading Interface)"""
    
    def __init__(self):
        self.personal_root = None
        self.connected = False
        self.account = os.getenv("NT_ACCOUNT", "Sim101")
        self.check_process = os.getenv("NT_CHECK_PROCESS", "true").lower() == "true"
        
    def initialize(self) -> bool:
        """
        Initialize NinjaTrader connection by finding the personal root directory
        
        IMPORTANT: ATI (Automated Trading Interface) must be enabled in NinjaTrader:
        1. Open NinjaTrader
        2. Go to Tools > Options
        3. Select "Automated Trading Interface"
        4. Check "Enable"
        5. Click OK
        """
        try:
            # Get the personal root directory from registry
            self.personal_root = self._get_personal_root_from_registry()
            
            if not self.personal_root:
                logger.error("Personal root not found in registry")
                logger.error("Make sure NinjaTrader is installed correctly")
                self.connected = False
                return False
            
            logger.info(f"NinjaTrader personal root: {self.personal_root}")
            
            # Check if incoming folder exists (ATI must be enabled)
            incoming_folder = os.path.join(self.personal_root, 'incoming')
            if not os.path.exists(incoming_folder):
                logger.error(f"Incoming folder not found: {incoming_folder}")
                logger.error("ATI (Automated Trading Interface) must be enabled in NinjaTrader!")
                logger.error("Go to: Tools > Options > Automated Trading Interface > Enable")
                self.connected = False
                return False
            
            logger.info(f"ATI incoming folder found: {incoming_folder}")
            
            # Check if NinjaTrader is running
            if self.check_process:
                is_running, pid = self._check_if_process_running('NinjaTrader.exe')
                if not is_running:
                    logger.error("NinjaTrader.exe is not running")
                    logger.error("Please start NinjaTrader before sending commands")
                    self.connected = False
                    return False
                logger.info(f"NinjaTrader.exe is running (PID: {pid})")
            
            self.connected = True
            logger.info("NinjaTrader ATI connection initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing NinjaTrader connection: {e}")
            self.connected = False
            return False
    
    def _get_personal_root_from_registry(self):
        """Get NinjaTrader personal root directory from Windows registry"""
        base_reg_path = r'SOFTWARE\NinjaTrader, LLC'
        versions = ['NinjaTrader 8', 'NinjaTrader 7']
        
        for version in versions:
            reg_path = os.path.join(base_reg_path, version)
            
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            if 'cmp' in subkey_name:
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    personal_root, reg_type = winreg.QueryValueEx(subkey, 'PERSONAL_ROOT')
                                    return personal_root
                        except OSError:
                            break
                        i += 1
            except OSError:
                continue
        
        return None
    
    def _check_if_process_running(self, process_name):
        """Check if a process is running"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if process_name.lower() in proc.info['name'].lower():
                    return True, proc.info['pid']
            return False, None
        except Exception as e:
            logger.error(f"An error occurred while checking process: {e}")
            return False, None
    
    def execute_command(self, command):
        """
        Execute a command by writing to NinjaTrader's incoming folder
        
        Args:
            command: ATI command string (e.g., "PLACE;Sim101;NQ 12-24;BUY;1;MARKET;;;DAY;;;;")
        
        Returns:
            bool: True if command was written successfully, False otherwise
        """
        if not self.connected or not self.personal_root:
            logger.error("Not connected to NinjaTrader")
            return False
        
        try:
            # Create unique filename in incoming folder
            file_name = os.path.join(self.personal_root, 'incoming', f'oif{uuid.uuid4()}.txt')
            logger.info(f"Writing command to: {file_name}")
            logger.debug(f"Command: {command}")
            
            # Write command to file
            with open(file_name, 'w') as f:
                f.write(command)
            
            logger.info("Command executed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error writing command to file: {e}")
            return False
    
    def shutdown(self):
        """Shutdown NinjaTrader connection"""
        self.connected = False
        logger.info("NinjaTrader connection closed")
