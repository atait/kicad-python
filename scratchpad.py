# %%
import Pyro5.api
import Pyro5.errors
import sys

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from kigadgets.board import Board

# %%
import Pyro5.api


uri = "PYRONAME:kigadgets.Board"

board = Pyro5.api.Proxy(uri)

# # %%
# try:
#     for results in dummy.thingos:
#         print(results)
# except Exception:
#     print("Pyro traceback:")
#     print("".join(Pyro5.errors.get_pyro_traceback()))

# %%
try:
    b: "Board" = board.from_editor()
    for via in b.vias:
        print(via)
    # print(b.filename)
except Exception:
    print("Pyro traceback:")
    print("".join(Pyro5.errors.get_pyro_traceback()))

# %%
uri = "PYRONAME:dummy"

dummy = Pyro5.api.Proxy(uri)

for results in dummy.thingos:
    print(results.value)
# %%
