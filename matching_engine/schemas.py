from pydantic import BaseModel
from typing import List

class OrderCreate(BaseModel):
    side: str
    price: float
    quantity: int

class OrderResponse(BaseModel):
    id: str
    side: str
    price: float
    quantity: int

class CancelResponse(BaseModel):
    success: bool

class TradeResponse(BaseModel):
    buy_order_id: str
    sell_order_id: str
    price: float
    quantity: int

class OrderBookSnapshot(BaseModel):
    buy_orders: List[dict]
    sell_orders: List[dict]