class Statistics:
    """Statistics from the Mojang API.

    Three values are present when a statistics response is recieved from the API, the total amount of copies sold, the total amount of copies sold in 24 hours, and the sale velocity in seconds.

    Attributes:
        raw_data (dict): The raw json response recieved from the API.

    """

    VALID_METRICS = [
        "item_sold_minecraft",
        "prepaid_card_redeemed_minecraft",
        "item_sold_cobalt",
        "item_sold_scrolls",
        "prepaid_card_redeemed_cobalt",
        "item_sold_dungeons",
    ]

    def __init__(self, raw_data: dict):
        # Rather than using self.__dict__.update(raw_data), I decided to convert the attributes to snake_case.
        self.total = raw_data.get("total")
        self.last_24h = raw_data.get("last24h")
        self.sale_velocity = raw_data.get("saleVelocityPerSeconds")

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<Statistics {}>".format(" ".join(arguments))
