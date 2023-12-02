import asyncio
import machine
from multiplexer import Mux

class Blinker(Mux):
    def __init__(self, pin):
        super().__init__()
        self._pin = pin

    async def loop(self, wait):
        while self.isRunning:
            self._pin.toggle()
            await asyncio.sleep(wait)

async def main():
    b = Blinker(machine.Pin(25,machine.Pin.OUT))
    b.start(wait=0.2)    
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()