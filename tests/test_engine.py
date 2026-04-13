import pytest
from matching_engine.models import Order
from matching_engine.engine import OrderBook

def make_order(side, price, quantity, order_id=None):
    import uuid
    return Order(
        id=order_id or str(uuid.uuid4()),
        side=side,
        price=float(price),
        quantity=quantity,
    )

@pytest.fixture
def fresh_engine():
    return OrderBook()

# Test 1 - Full Match - buyer and sellet have equal quantity, both fully consumed

def test_full_match(fresh_engine):
    engine = fresh_engine

    buy  = make_order("buy",  price=200, quantity=10)
    sell = make_order("sell", price=200, quantity=10)

    engine.add_order(buy)
    engine.add_order(sell)

    assert len(engine.trades) == 1 # exactly one trade should have been created
    trade = engine.trades[0]

    assert trade.quantity == 10
    assert trade.price == 200.0 # trade must record correct quantity and price

    assert len(engine.buy_orders) == 0
    assert len(engine.sell_orders) == 0 #both heaps must be completely empty that means no remaining orders


# Test 2 - Partial Fill - buyer has more

def test_partial_fill_buyer_has_more(fresh_engine):
    """
    Scenario: Buyer wants 10, seller only has 6.
    Trade should be for 6.
    Buyer should remain with 4 units still in the book.
    Seller fully consumed.
    """
    engine = fresh_engine

    buy  = make_order("buy",  price=200, quantity=10)
    sell = make_order("sell", price=195, quantity=6)

    engine.add_order(buy)
    engine.add_order(sell)

    assert len(engine.trades) == 1
    assert engine.trades[0].quantity == 6     # only 6 traded
    assert engine.trades[0].price == 195.0    # seller's price

    # buyer still has 4 left in the book
    assert len(engine.buy_orders) == 1
    assert engine.buy_orders[0].quantity == 4

    # seller fully consumed — heap empty
    assert len(engine.sell_orders) == 0

# Test 3 - Partial Fill - seller has more

def test_partial_fill_seller_has_more(fresh_engine):
    """
    Scenario: Buyer wants 4, seller has 10.
    Trade for 4.
    Seller stays with 6 remaining.
    """
    engine = fresh_engine

    buy  = make_order("buy",  price=200, quantity=4)
    sell = make_order("sell", price=198, quantity=10)

    engine.add_order(buy)
    engine.add_order(sell)

    assert len(engine.trades) == 1
    assert engine.trades[0].quantity == 4

    # buyer fully consumed
    assert len(engine.buy_orders) == 0

    # seller stays with 6 remaining
    assert len(engine.sell_orders) == 1
    assert engine.sell_orders[0].quantity == 6

# Test 4 - No match - price gap

def test_no_match_price_gap(fresh_engine):
    """
    Scenario: Buyer offers ₹95 but seller wants ₹100.
    No trade should happen.
    Both orders should remain in their heaps.
    """
    engine = fresh_engine

    buy  = make_order("buy",  price=95,  quantity=5)
    sell = make_order("sell", price=100, quantity=5)

    engine.add_order(buy)
    engine.add_order(sell)

    # zero trades — the condition best_buy.price < best_sell.price caused a break
    assert len(engine.trades) == 0

    # both orders still sitting in the book waiting for better counterparty
    assert len(engine.buy_orders) == 1
    assert len(engine.sell_orders) == 1

# Test 5 - Multiple matches from one order

def test_one_buy_matches_multiple_sellers(fresh_engine):
    """
    Scenario: One big buy order matches multiple smaller sell orders.
    Buyer wants 30, three sellers each have 10.
    Should produce 3 trades, buyer fully consumed.
    """
    engine = fresh_engine

    # add three separate sell orders first
    sell1 = make_order("sell", price=100, quantity=10)
    sell2 = make_order("sell", price=101, quantity=10)
    sell3 = make_order("sell", price=102, quantity=10)

    engine.add_order(sell1)
    engine.add_order(sell2)
    engine.add_order(sell3)

    # now add one large buy order that can match all three
    big_buy = make_order("buy", price=105, quantity=30)
    engine.add_order(big_buy)

    # should have produced exactly 3 trades
    assert len(engine.trades) == 3

    # trades should have happened at each seller's price (lowest first)
    prices = [t.price for t in engine.trades]
    assert 100.0 in prices
    assert 101.0 in prices
    assert 102.0 in prices

    # buyer fully consumed
    assert len(engine.buy_orders) == 0

    # all sellers consumed
    assert len(engine.sell_orders) == 0

# test 6 - price time priority

def test_price_time_priority(fresh_engine):
    """
    Scenario: Two sell orders at the same price.
    The one placed earlier should match first.
    """
    import time
    engine = fresh_engine

    # sell1 placed before sell2 — both at same price
    sell1 = make_order("sell", price=100, quantity=5, order_id="sell-first")
    time.sleep(0.01)   # tiny sleep so timestamps are genuinely different
    sell2 = make_order("sell", price=100, quantity=5, order_id="sell-second")

    engine.add_order(sell1)
    engine.add_order(sell2)

    # now a buy that can only fill one
    buy = make_order("buy", price=100, quantity=5)
    engine.add_order(buy)

    assert len(engine.trades) == 1
    # the first sell order should have matched — not the second
    assert engine.trades[0].sell_order_id == "sell-first"

    # sell2 still in the book
    assert len(engine.sell_orders) == 1
    assert engine.sell_orders[0].id == "sell-second"

def test_invalid_side_raises_error(fresh_engine):
    """
    Scenario: Someone passes side='hold' instead of buy/sell.
    Engine should raise ValueError — never silently accept garbage.
    """
    engine = fresh_engine
    bad_order = make_order("hold", price=100, quantity=5)

    with pytest.raises(ValueError):
        engine.add_order(bad_order)

def test_trade_records_correct_order_ids(fresh_engine):
    """
    Verify the trade stores the correct buyer and seller IDs.
    Important for trade history and audit trails.
    """
    engine = fresh_engine

    buy  = make_order("buy",  price=200, quantity=5, order_id="my-buy-123")
    sell = make_order("sell", price=195, quantity=5, order_id="my-sell-456")

    engine.add_order(buy)
    engine.add_order(sell)

    assert len(engine.trades) == 1
    assert engine.trades[0].buy_order_id  == "my-buy-123"
    assert engine.trades[0].sell_order_id == "my-sell-456"