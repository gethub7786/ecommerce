import threading
import time
import logging

class RepeatedTimer:
    """Run a function at a specified interval in seconds."""
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self._timer = None
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        logging.info("Running scheduled task %s", self.function.__name__)
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as exc:
            logging.exception("Scheduled task failed: %s", exc)

    def start(self):
        if not self.is_running:
            logging.info("Starting timer for %s every %s seconds", self.function.__name__, self.interval)
            self._timer = threading.Timer(self.interval, self._run)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer:
            self._timer.cancel()
        logging.info("Stopped timer for %s", self.function.__name__)
        self.is_running = False
