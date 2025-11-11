from components.events.base.event import Event


class WebhookReceivedNtFlatten(Event):
    """Event triggered when a NinjaTrader flatten webhook is received"""
    def __init__(self):
        super().__init__()
