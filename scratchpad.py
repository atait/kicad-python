#%%
import Pyro5.api
import Pyro5.errors

from typing import TYPE_CHECKING
import Pyro5.api


if TYPE_CHECKING:
    from kigadgets.board import Board


uri = "PYRONAME:kigadgets.Board"

board = Pyro5.api.Proxy(uri)

# %%
# The fun things!

b: "Board" = board.from_editor()
for i in range(10):
    b.add_via((50, 50 + i * 5))

#%%

with Pyro5.api.Proxy("PYRONAME:kigadgets.Pcbnew") as pcbnew:
    pcbnew.refresh()
