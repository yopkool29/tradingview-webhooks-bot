from components.events.base.event import Event


class WebhookReceivedMtBalance(Event):
    def __init__(self):
        super().__init__()
