class Statistics:

    VALID_METRICS = [
        "item_sold_minecraft",
        "prepaid_card_redeemed_minecraft",
        "item_sold_cobalt",
        "item_sold_scrolls",
        "prepaid_card_redeemed_cobalt",
        "item_sold_dungeons",
    ]

    def __init__(self, raw_data: dict):
        self.total = raw_data.get("total")
        self.last_24h = raw_data.get("last24h")
        self.sale_velocity = raw_data.get("saleVelocityPerSeconds")

    def __repr__(self):
        arguments = [f"{k}={v}" for k, v in self.__dict__.items()]
        return "<Statistics {}>".format(" ".join(arguments))
