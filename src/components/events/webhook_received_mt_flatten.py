from components.events.base.event import Event


class WebhookReceivedMtFlatten(Event):
    def __init__(self):
        super().__init__()
