from fastapi import FastAPI
from uuid import uuid4

from matching_engine.engine import OrderBook
from matching_engine.models import Order
from matching_engine.events import EventStream
from matching_engine.metrics import Metrics
from matching_engine.market_simulator import MarketSimulator

app = FastAPI(title="Real-Time Market Simulator")

event_stream = EventStream()
metrics = Metrics()

engine = OrderBook(event_stream=event_stream, metrics=metrics)

simulator = MarketSimulator(engine)
simulator.start()


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
