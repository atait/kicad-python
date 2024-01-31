from Pyro5.api import expose, serve
from kigadgets.util import register_yielded


import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()


@expose
class Returned(object):
    def __init__(self, value) -> None:
        self._value = value

    @property
    def value(self):
        return self._value


@expose
class Dummy(object):
    @property
    @register_yielded
    def thingos(self):
        for i in range(3):
            yield Returned(i)


serve({Dummy: "dummy"})
