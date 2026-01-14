import uuid
from matching_engine.engine import OrderBook
from matching_engine.models import Order


def create_order(side, price, qty):
    return Order(
        id=str(uuid.uuid4()),
        side=side,
        price=price,
        quantity=qty
    )


def test_basic_match():
    engine = OrderBook()

    buy = create_order("buy", 100, 10)
    sell = create_order("sell", 95, 5)

    engine.add_order(buy)
    engine.add_order(sell)

    trades = engine.get_trades()

    assert len(trades) == 1
    assert trades[0].quantity == 5
    assert buy.quantity == 5


def test_no_match():
    engine = OrderBook()

    buy = create_order("buy", 90, 10)
    sell = create_order("sell", 100, 5)

    engine.add_order(buy)
    engine.add_order(sell)

    assert len(engine.get_trades()) == 0


def test_cancel_order():
    engine = OrderBook()

    order = create_order("buy", 100, 10)
    engine.add_order(order)

    success = engine.cancel_order(order.id)

    assert success is True
    assert order.quantity == 0


def test_modify_order():
    engine = OrderBook()

    order = create_order("buy", 100, 10)
    engine.add_order(order)

    success = engine.modify_order(order.id, 3)

    assert success is True
    assert order.quantity == 3
