from api.app import create_app
from src.utils import model_load

import sys
import signal
import gc
import multiprocessing.resource_tracker as rt

def handle_exit(sig, frame):
    print("Gracefully shutting down...")
    try:
        rt.cleanup()
    except:
        pass
    gc.collect()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

app = create_app()