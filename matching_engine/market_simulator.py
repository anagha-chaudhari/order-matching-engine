import threading
import random
import time
from uuid import uuid4
from .models import Order


class MarketSimulator:
    def __init__(self, engine):
        self.engine = engine
        self.running = False
        self.delay = 0.5
        self.paused = False

    def set_speed(self, delay: float):
        self.delay = delay

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def start(self):
        self.running = True
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()

    def run(self):
        price = 100.0

        while self.running:
            if self.paused:
                time.sleep(0.2)
                continue

            side = random.choice(["buy", "sell"])
            price += random.uniform(-0.5, 0.5)
            quantity = random.randint(1, 10)

            order = Order(
                id=str(uuid4()),
                side=side,
                price=round(price, 2),
                quantity=quantity,
            )

            self.engine.add_order(order)
            time.sleep(self.delay)
