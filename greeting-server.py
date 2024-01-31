# saved as greeting-server.py
import Pyro5.api
import pathlib

daemon = Pyro5.api.Daemon()             # make a Pyro daemon
uri = daemon.register(Pyro5.api.expose(pathlib.Path))    # register the greeting maker as a Pyro object

print("Ready. Object uri =", uri)       # print the uri so we can use it in the client later
daemon.requestLoop()                    # start the event loop of the server to wait for calls
