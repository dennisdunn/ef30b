import machine
import asyncio

class Coro:
    """A startable/stoppable coroutine."""
    
    DELAY = "DELAY"
    RUNNING = "RUNNING"
    
    def __init__(self, context={}):
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
            await asyncio.sleep(self.context[Coro.DELAY])

    def start(self, delay=0.0):
        self.context[Coro.DELAY] = delay
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._loop())
        return self._task
    
    def stop(self):
        if self._running:
            self._running = False
            self._task.cancel()
