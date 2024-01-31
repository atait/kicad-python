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

# # %%
# try:
#     b: "Board" = board.from_editor()
#     for via in b.vias:
#         print(via.drill)
#     # print(b.filename)
# except Exception:
#     print("Pyro traceback:")
#     print("".join(Pyro5.errors.get_pyro_traceback()))

# %%
b: "Board" = board.from_editor()
for i in range(10):
    b.add_via((50, 50 + i * 5))

# # %%
# len(list(b.vias))
# # %%

# b: "Board" = board.from_editor()
# b.add_via((101, 50))

# %%
with Pyro5.api.Proxy("PYRONAME:kigadgets.Pcbnew") as pcbnew:
    pcbnew.refresh()

# %%
