"""
Start a server to remote control KiCAD.
"""

import threading

from Pyro5.api import serve
from .board import Board
import logging

log = logging.getLogger(__name__)


def _run_server():
    log.info("Starting Pyro5 server")
    serve(
        {
            Board: "kigadgets.Board",
        }
    )


def start_server() -> threading.Thread:
    """Start a pryo5 server to remote control KiCAD."""
    # NOTE: this seems to immediately kill KiCAD if
    # run as a daemon thread
    return threading.Thread(target=_run_server).start()
