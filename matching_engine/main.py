from fastapi import FastAPI, HTTPException
from uuid import uuid4
import requests

from matching_engine.engine import OrderBook
from matching_engine.models import Order
from matching_engine.schemas import(
    OrderCreate,
    OrderResponse,
    CancelResponse,
    TradeResponse,
    OrderBookSnapshot
)

app = FastAPI(title="Trade order matching engine")

engine = OrderBook()

@app.post("/orders/", response_model=OrderResponse)
def create_order(order: OrderCreate):
    new_order = Order(
        id=str(uuid4()),
        side=order.side.lower(),
        price=order.price,
        quantity=order.quantity
    )

    try:
        engine.add_order(new_order)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 
    
    return new_order


@app.delete("/orders/{order_id}", response_model=CancelResponse)
def cancel_order(order_id:str):
    success = engine.cancel_order(order_id)

    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"success": True}

@app.get("/orderbook", response_model=OrderBookSnapshot)
def get_orderbook():
    return engine.get_orderbook_snapshot()

@app.get("/trades", response_model=list[TradeResponse])
def get_trades():
    return engine.get_trades()

@app.get("/health")
def health():
    return {"status": "ok"}

AI_SERVICE_URL = "http://127.0.0.1:8001/ai/recommend"
@app.post("/recommend")
def recommend_order(order: OrderCreate):
    orderbook = engine.get_orderbook_snapshot()

    payload = {
        "orderbook": orderbook,
        "order": {
            "price": order.price,
            "quantity": order.quantity
        }
    }

    try:
        res = requests.post(AI_SERVICE_URL, json=payload, timeout=3)
        res.raise_for_status()
        return res.json()

    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="AI service unavailable")
