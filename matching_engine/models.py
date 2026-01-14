from dataclasses import dataclass, field
import time

@dataclass(order=True)
class Order:
    sort_index: tuple = field(init=False, repr=False)
    id: str
    side: str
    price: float
    quantity: int
    timestamp: float = field(default_factory=time.time)

    # Price time priority - implemented using heap with a custom sort_index where buy orders are sorted by -price (higher first) and sell orders by price (lower first) along with timestamp

    def __post_init__(self):
        if self.side == "buy":
            self.sort_index = (-self.price, self.timestamp)

        else:
            self.sort_index = (self.price, self.timestamp)

@dataclass
class Trade:
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int
    timestamp: float = field(default_factory=time.time)