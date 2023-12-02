import machine
import asyncio

class Mux:
    DELAY = "DELAY"
    RUNNING = "RUNNING"
    
    def __init__(self, context):
        self._context = context
        self._running = False

    @property
    def isRunning(self):
        return self._running
    
    @property
    def context(self):
        return self._context

    async def tick(self):
        pass

    async def _loop(self):
        while self.isRunning:
            await self.tick()
            await asyncio.sleep(self.context[Mux.DELAY])

    def start(self, delay=0.0):
        self.context[Mux.DELAY] = delay
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
        return self._task
    
    def stop(self):
        if self._running:
            self._running = False
            self._task.cancel()

class _Demo(Mux):
    async def tick(self):
        print(".",end="")
        n = self.context["n"]
        n+=1
        if n > 16:
            print(self.context)
            n = 0
        self.context["n"]=n

async def main():
    mux = _Demo({"n":0})
    mux.start(0.1)
    print(mux.context)
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()
