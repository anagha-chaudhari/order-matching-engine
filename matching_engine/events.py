from collections import deque
from threading import Lock
import asyncio


class EventStream:
    def __init__(self, max_size=200):
        self._events = deque(maxlen=max_size)
        self._lock = Lock()

        self._ws_manager = None
        self._loop = None

    def set_ws_manager(self, manager, loop):
        self._ws_manager = manager
        self._loop = loop

    def emit(self, message: str):
        # Step 1: store the event as before
        with self._lock:
            self._events.appendleft(message)

        # Step 2: if WebSocket is set up, push immediately to all clients
        # This runs from the simulator's background thread (sync world)
        # So we use run_coroutine_threadsafe to safely cross into async world
        if self._ws_manager and self._loop:
            asyncio.run_coroutine_threadsafe(
                self._ws_manager.broadcast(message),  
                self._loop                             
            )
        # run_coroutine_threadsafe is non-blocking — it submits the task
        # and returns immediately. The simulator thread continues without waiting.

    def get_latest(self):
        with self._lock:
            return list(self._events)