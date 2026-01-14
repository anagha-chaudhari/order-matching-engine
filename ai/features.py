# ai/features.py

def extract_features(orderbook: dict, order: dict):
    """
    Extract simple, meaningful market microstructure features.
    Returns a list of numeric features for ML model.
    """

    buy_orders = orderbook.get("buy_orders", [])
    sell_orders = orderbook.get("sell_orders", [])

    # Handle empty book safely
    if not buy_orders or not sell_orders:
        return [0.0, 0.0, order["quantity"], 0.0]

    best_buy = max(buy_orders, key=lambda x: x["price"])
    best_sell = min(sell_orders, key=lambda x: x["price"])

    # Feature 1: Bid-ask spread
    spread = best_sell["price"] - best_buy["price"]

    # Feature 2: Order book imbalance
    buy_volume = sum(o["quantity"] for o in buy_orders)
    sell_volume = sum(o["quantity"] for o in sell_orders)
    imbalance = (buy_volume - sell_volume) / max(buy_volume + sell_volume, 1)

    # Feature 3: Order size
    size = order["quantity"]

    # Feature 4: Price distance from best bid
    price_distance = abs(order["price"] - best_buy["price"])

    return [spread, imbalance, size, price_distance]
