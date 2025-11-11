from components.events.base.event import Event


class WebhookReceivedNtOrder(Event):
    """Event triggered when a NinjaTrader order webhook is received"""
    def __init__(self):
        super().__init__()
