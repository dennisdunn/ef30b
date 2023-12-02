import machine
import asyncio

class Mux:
    def __init__(self, context=None):
        self._context = context
        self._running = False

    @property
    def isRunning(self):
        return self._running

    async def loop(self,wait):
        cnt = 0
        while self.isRunning:
            print(".",end="")
            cnt += 1
            if not cnt % 16:
                cnt = 0
                print()
            await asyncio.sleep(wait)

    def start(self, wait=0.0):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self.loop(wait))
        return self._task
    
    def stop(self):
        if self._running:
            self._running = False
            self._task.cancel()

async def main():
    mux = Mux()
    mux.start(0.1)
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()
