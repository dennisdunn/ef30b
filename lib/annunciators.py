import asyncio
import machine
from lib.coro import Coro

class Blinker(Coro):
    def __init__(self, gpio):
        super().__init__({})
        self._pin = machine.Pin(gpio,machine.Pin.OUT)

    async def tick(self):
        self._pin.toggle()

async def main():
    b = Blinker(25)
    b.start(delay=0.2)    
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()