import time


class Metrics:
    def __init__(self):
        self.total_orders = 0
        self.total_trades = 0

        self.latencies = []

        self.start_time = time.time()

    def record_order(self):
        self.total_orders += 1

    def record_trade(self, latency):
        self.total_trades += 1
        self.latencies.append(latency)

    def snapshot(self):
        runtime = time.time() - self.start_time

        orders_per_sec = round(self.total_orders / runtime, 2) if runtime > 0 else 0
        trades_per_sec = round(self.total_trades / runtime, 2) if runtime > 0 else 0

        avg_latency_ms = (
            round((sum(self.latencies) / len(self.latencies)) * 1000, 2)
            if self.latencies else 0
        )

        match_rate = (
            round((self.total_trades / self.total_orders) * 100, 2)
            if self.total_orders > 0 else 0
        )

        return {
            "orders": self.total_orders,
            "trades": self.total_trades,
            "uptime_sec": int(runtime),
            "orders_per_sec": orders_per_sec,
            "trades_per_sec": trades_per_sec,
            "avg_latency_ms": avg_latency_ms,
            "match_rate_percent": match_rate,
        }
