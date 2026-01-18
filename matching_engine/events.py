from collections import deque
from threading import Lock

class EventStream:
    def __init__(self, max_size=200):
        self._events = deque(maxlen=max_size)
        self._lock = Lock()

    def emit(self, message: str):
        with self._lock:
            self._events.appendleft(message)

    def get_latest(self):
        with self._lock:
            return list(self._events)
