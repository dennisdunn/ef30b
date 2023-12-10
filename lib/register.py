import asyncio

class Register:
    DISPLAY = 0
    GREEN_LED = 1
    YELLOW_LED = 2
    RED0_LED = 3
    RED1_LED = 4
    BLUE_LED = 5
    ALL = 255

class Registers:
    def __init__(self):
        self._registers = [0]*6

    def get(self, regNum):
        if regNum == Register.ALL:
            return self._registers
        else:
            return self._registers[regNum]

    def set(self, regNum, value):
        if regNum == Register.ALL:
            self._registers = value
        else:
            self._registers[regNum] = value

    def toggle(self, regNum):
        if regNum < Register.GREEN_LED and regNum > Register.BLUE_LED:
            pass
        else:
            self._registers[regNum] = not self._registers[regNum]

class AsyncRegisters(Registers):
    def __init__(self):
        super().__init__()
        self._lock = asyncio.Lock()

    async def get(self, regNum):
        async with self._lock:
            return super().get(regNum)

    async def set(self, regNum, value):
        async with self._lock:
            super().set(regNum, value)

    async def toggle(self, regNum):
        async with self._lock:
            super().toggle(regNum)