import logging
import os


def setup_logging(level=logging.INFO):
    root = logging.getLogger()

    if getattr(setup_logging, "_configured", False):
        return

    os.makedirs("logs", exist_ok=True)

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    file_handler = logging.FileHandler("logs/processing.log")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    setup_logging._configured = True
