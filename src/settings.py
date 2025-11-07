# actions
# REGISTERED_ACTIONS = ['AsyncDemo', 'PrintData']
# REGISTERED_EVENTS = ['WebhookReceived']
# REGISTERED_LINKS = []

# actions
REGISTERED_ACTIONS = [
    "AsyncDemo",
    "PrintData",
    "MtPrintData",
    "MtAccountBalance",
    "MtPlaceOrder",
    "MtFlatten",
]

# events
REGISTERED_EVENTS = [
    "WebhookReceived",
    "WebhookReceivedMtBalance",
    "WebhookReceivedMtOrder",
    "WebhookReceivedMtFlatten",
]

# links
REGISTERED_LINKS = [
    ("MtAccountBalance", "WebhookReceivedMtBalance"),
    ("MtFlatten", "WebhookReceivedMtOrder"), # flatten avant
    ("MtPlaceOrder", "WebhookReceivedMtOrder"), # place les ordres apres
    ("MtFlatten", "WebhookReceivedMtFlatten"),
]
