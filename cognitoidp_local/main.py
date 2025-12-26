import logging
import os
import signal
import sys
import threading

from moto.server import ThreadedMotoServer

from cognitoidp_local import patch
from cognitoidp_local.storage import StorageManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

COGNITO_DB = "cognito.db"


def get_data_file_path():
    """
    Determines the best location for the database file.
    1. Checks ENV variable 'DATA_FILE'
    2. Checks if the '/data' directory exists and is writable (Docker default)
    3. Fallbacks to 'cognito.db' in the current working directory (Local dev)
    """
    env_path = os.getenv("DATA_FILE")
    if env_path:
        return env_path
    docker_vol_path = "/data"
    if os.path.exists(docker_vol_path) and os.access(docker_vol_path, os.W_OK):
        return os.path.join(docker_vol_path, COGNITO_DB)
    return f"./{COGNITO_DB}"


DATA_FILE = get_data_file_path()
PORT = int(os.getenv("PORT", 4566))
SAVE_INTERVAL = 60


def run():
    patch.apply_all()
    manager = StorageManager(DATA_FILE)
    manager.load()
    stop_event = threading.Event()

    def auto_save_loop():
        while not stop_event.is_set():
            if stop_event.wait(SAVE_INTERVAL):
                break
            manager.save()

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signal.Signals(signum).name}.")
        stop_event.set()
        manager.save()
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    saver_thread = threading.Thread(target=auto_save_loop, daemon=True)
    saver_thread.start()

    logger.info(f"Starting Server on port {PORT}")
    server = ThreadedMotoServer(ip_address="0.0.0.0", port=PORT)
    server.start()

    stop_event.wait()


if __name__ == "__main__":
    run()
