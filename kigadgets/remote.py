"""
Start a server to remote control KiCAD.
"""

import logging
import threading

import Pyro5.server
from Pyro5.api import expose, serve

# from kigadgets import pcbnew_bare as pcbnew

from .board import Board

log = logging.getLogger(__name__)


@expose
class Pcbnew:
    @staticmethod
    def refresh():
        """Refresh the board."""
        import pcbnew
        pcbnew.Refresh()


def _run_server():
    log.info("Starting Pyro5 server")
    try:
        serve(
            {
                Pcbnew: "kigadgets.Pcbnew",
                Board: "kigadgets.Board",
            }
        )
    except Exception as ex:
        log.exception("Pyro5 server failed with exception: %s", ex)
        raise


def start_server() -> threading.Thread:
    """Start a pryo5 server to remote control KiCAD."""
    # NOTE: this seems to immediately kill KiCAD if
    # run as a daemon thread
    return threading.Thread(target=_run_server).start()
