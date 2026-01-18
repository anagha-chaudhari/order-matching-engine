import heapq
import time
from typing import List
from .models import Order, Trade


class OrderBook:
    def __init__(self, event_stream=None, metrics=None):
        self.buy_orders: List[Order] = []
        self.sell_orders: List[Order] = []
        self.trades: List[Trade] = []

        self.event_stream = event_stream
        self.metrics = metrics

    def add_order(self, order: Order):
        start = time.time()

        if self.metrics:
            self.metrics.record_order()

        if order.side == "buy":
            heapq.heappush(self.buy_orders, order)
        elif order.side == "sell":
            heapq.heappush(self.sell_orders, order)
        else:
            raise ValueError("Invalid side")

        if self.event_stream:
            self.event_stream.emit(
                f"Order received: {order.side.upper()} {order.quantity} @ {order.price}"
            )

        self.match_orders(start)

    def match_orders(self, start_time):
        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]

            if best_buy.price < best_sell.price:
                break

            qty = min(best_buy.quantity, best_sell.quantity)
            price = best_sell.price

            trade = Trade(
                buy_order_id=best_buy.id,
                sell_order_id=best_sell.id,
                price=price,
                quantity=qty,
            )

            self.trades.append(trade)

            best_buy.quantity -= qty
            best_sell.quantity -= qty

            if best_buy.quantity == 0:
                heapq.heappop(self.buy_orders)

            if best_sell.quantity == 0:
                heapq.heappop(self.sell_orders)

            latency = time.time() - start_time

            if self.metrics:
                self.metrics.record_trade(latency)

            if self.event_stream:
                self.event_stream.emit(
                    f"Trade executed: {qty} @ {price} (latency {int(latency * 1000)} ms)"
                )

    def get_orderbook_snapshot(self):
        return {
            "buy_orders": [
                {"price": o.price, "quantity": o.quantity}
                for o in sorted(self.buy_orders, reverse=True)
            ],
            "sell_orders": [
                {"price": o.price, "quantity": o.quantity}
                for o in sorted(self.sell_orders)
            ],
        }

    def get_trades(self):
        return [
            {
                "buy_order_id": t.buy_order_id,
                "sell_order_id": t.sell_order_id,
                "price": t.price,
                "quantity": t.quantity,
            }
            for t in self.trades
        ]
