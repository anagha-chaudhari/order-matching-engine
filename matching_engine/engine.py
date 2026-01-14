import heapq
from typing import List
from .models import Order, Trade

class OrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.trades = []

        self.active_orders = {} #------------------track all active orders by id

    def add_order(self, order: Order):
        if order.side == "buy":
            heapq.heappush(self.buy_orders, order)
        elif order.side == "sell":
            heapq.heappush(self.sell_orders, order)
        else:
            raise ValueError("Order side must be either buy or sell.")
        
        self.active_orders[order.id] = order
        self.match_orders()

    def cancel_order(self, order_id: str) -> bool:
        order = self.active_orders.pop(order_id, None)
        if not order:
            return False
        
        # heap deletion by value is complex, so used lazy cancellation by marking orders inactive which simplifies logic while keeping performance
        order.quantity = 0
        return True
    
    def modify_order(self, order_id: str, new_quantity: int) -> bool:
        order = self.active_orders.get(order_id)
        if not order:
            return False
        
        order.quantity = new_quantity
        return True

    def match_orders(self):
        while self.buy_orders and self.sell_orders:
            while self.buy_orders and self.buy_orders[0].quantity == 0:
                heapq.heappop(self.buy_orders)

            while self.sell_orders and self.sell_orders[0].quantity == 0:
                heapq.heappop(self.sell_orders)

            if not self.buy_orders or not self.sell_orders:
                return 
            
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]

            if best_buy.price < best_sell.price:
                break

            traded_quantity = min(best_buy.quantity, best_sell.quantity)
            trade_price = best_sell.price

            trade = Trade(
                buy_order_id = best_buy.id,
                sell_order_id = best_sell.id,
                price = trade_price,
                quantity = traded_quantity
            )
            self.trades.append(trade)

            best_buy.quantity -= traded_quantity
            best_sell.quantity -= traded_quantity

            if best_buy.quantity == 0:
                heapq.heappop(self.buy_orders)

            if best_sell.quantity == 0:
                heapq.heappop(self.sell_orders)

    def get_orderbook_snapshot(self):
        return {
                "buy_orders": [
                    {"price": o.price, "quantity": o.quantity}
                    for o in sorted(self.buy_orders)
                ],
                "sell_orders": [
                    {"price": o.price, "quantity": o.quantity}
                    for o in sorted(self.sell_orders)
                ]
            }
            
        
    def get_trades(self):
        return self.trades #-------------------------- return all executed trades