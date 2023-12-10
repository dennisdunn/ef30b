import machine
from lib.coro import Coro

class Blinker(Coro):
    def __init__(self, gpio):
        super().__init__({})
        self._pin = machine.Pin(gpio,machine.Pin.OUT)

    async def tick(self):
        self._pin.toggle()
