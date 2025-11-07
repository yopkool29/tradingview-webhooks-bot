from components.events.base.event import Event


class WebhookReceivedMtOrder(Event):
    def __init__(self):
        super().__init__()
