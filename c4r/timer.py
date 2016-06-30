import threading
from c4r.logger import get_logger

log = get_logger()


class RecurringTimer(object):
    def __init__(self, interval=10, callback=None):
        self.interval = interval
        self.callback = callback

        self._lock = threading.Lock()
        self._stop = False
        self._timer = None

    def start(self):
        self.run_callback()
        self._start_timer()

    def _start_timer(self):
        self._timer = threading.Timer(self.interval, self.on_tick)
        self._timer.start()

    def run_callback(self):
        if self.callback is not None:
            self.callback()

    def on_tick(self):
        try:
            self.run_callback()
        finally:
            with self._lock:
                if not self._stop:
                    self._start_timer()

    def stop(self):
        with self._lock:
            self._stop = True
            if self._timer is not None:
                self._timer.cancel()
