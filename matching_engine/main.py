from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import asyncio

from matching_engine.engine import OrderBook
from matching_engine.models import Order
from matching_engine.events import EventStream
from matching_engine.metrics import Metrics
from matching_engine.market_simulator import MarketSimulator

app = FastAPI(title="Real-Time Market Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection manager - 

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                self.disconnect(connection)

manager      = ConnectionManager()
event_stream = EventStream()
metrics      = Metrics()
engine       = OrderBook(event_stream=event_stream, metrics=metrics)
simulator    = MarketSimulator(engine)

event_stream.set_ws_manager(manager, asyncio.get_event_loop())

simulator.start()

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.websocket("/ws/orderbook")
async def websocket_orderbook(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            snapshot = engine.get_orderbook_snapshot()
            await websocket.send_json(snapshot)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/orders")
def create_order(payload: dict):
    order = Order(
        id=str(uuid4()),
        side=payload["side"],
        price=float(payload["price"]),
        quantity=int(payload["quantity"]),
    )
    engine.add_order(order)
    return {"id": order.id}


@app.get("/orderbook")
def orderbook():
    return engine.get_orderbook_snapshot()


@app.get("/trades")
def trades():
    return engine.get_trades()


@app.get("/events")
def events():
    return event_stream.get_latest()


@app.get("/metrics")
def get_metrics():
    return metrics.snapshot()


@app.post("/load/{level}")
def set_load(level: str):
    if level not in ["low", "medium", "high"]:
        return {"error": "Invalid level"}
    simulator.set_load(level)
    return {"status": f"Load set to {level}"}


@app.post("/speed/{delay}")
def set_speed(delay: float):
    simulator.set_speed(delay)
    return {"status": f"Speed set to {delay}s delay"}


@app.post("/pause")
def pause_market():
    simulator.pause()
    return {"status": "Market paused"}


@app.post("/resume")
def resume_market():
    simulator.resume()
    return {"status": "Market resumed"}