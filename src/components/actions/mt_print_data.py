from components.actions.base.action import Action
from dotenv import load_dotenv
from utils.log import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

class MtPrintData(Action):
    def __init__(self):
        super().__init__()

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)  # this is required

        if os.getenv("MT5_ENABLED", "false").lower() == "false":
            logger.warning("MetaTrader 5 is disabled (MT5_ENABLED=false in .env)")
            return

        """
        Custom run method. Add your custom logic here.
        """
        print(self.name, '---> action has run!')

        data = self.validate_data()  # always get data from webhook by calling this method!

        print('MtPrintData => Data from webhook:', data)
