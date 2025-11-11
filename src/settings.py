# actions
# REGISTERED_ACTIONS = ['AsyncDemo', 'PrintData']
# REGISTERED_EVENTS = ['WebhookReceived']
# REGISTERED_LINKS = []

# actions
REGISTERED_ACTIONS = [
    "AsyncDemo",
    "PrintData",
    # MT5 Actions
    "MtPrintData",
    "MtAccountBalance",
    "MtPlaceOrder",
    "MtFlatten",
    # NinjaTrader Actions
    "NtPlaceOrder",
    "NtFlatten",
]

# events
REGISTERED_EVENTS = [
    "WebhookReceived",
    # MT5 Events
    "WebhookReceivedMtBalance",
    "WebhookReceivedMtOrder",
    "WebhookReceivedMtFlatten",
    # NinjaTrader Events
    "WebhookReceivedNtOrder",
    "WebhookReceivedNtFlatten",
]

# links
REGISTERED_LINKS = [
    # MT5 Links
    ("MtAccountBalance", "WebhookReceivedMtBalance"),
    ("MtFlatten", "WebhookReceivedMtOrder"), # flatten avant
    ("MtPlaceOrder", "WebhookReceivedMtOrder"), # place les ordres apres
    ("MtFlatten", "WebhookReceivedMtFlatten"),
    # NinjaTrader Links
    ("NtFlatten", "WebhookReceivedNtOrder"), # flatten avant
    ("NtPlaceOrder", "WebhookReceivedNtOrder"), # place les ordres apres
    ("NtFlatten", "WebhookReceivedNtFlatten"),
]
