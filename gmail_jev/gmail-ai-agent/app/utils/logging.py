import logging
import os
import sys

def setup_logger():
    logger = logging.getLogger("gmail-ai")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")

    # Console handler — force UTF-8 so emoji/₹ don't crash on Windows
    if hasattr(sys.stdout, "buffer"):
        import io
        utf8_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    else:
        utf8_stdout = sys.stdout

    ch = logging.StreamHandler(utf8_stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler — UTF-8 always
    os.makedirs("logs", exist_ok=True)
    fh = logging.FileHandler("logs/agent.log", encoding="utf-8")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger

logger = setup_logger()
