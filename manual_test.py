# manual_test.py

from matching_engine.engine import OrderBook
from matching_engine.models import Order
import uuid

engine = OrderBook()

engine.add_order(Order(str(uuid.uuid4()), "buy", 100, 10))
engine.add_order(Order(str(uuid.uuid4()), "sell", 95, 4))

print("Trades:")
for trade in engine.get_trades():
    print(trade)

print("\nOrderbook:")
print(engine.get_orderbook_snapshot())
