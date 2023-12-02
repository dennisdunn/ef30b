import machine
import asyncio
import random
import time

from multiplexer import Mux
from lut import LookupTable

SEGMENT_TABLE = [[1,1,1,1,1,1,0],
                [0,1,1,0,0,0,0],
                [1,1,0,1,1,0,1],
                [1,1,1,1,0,0,1],
                [0,1,1,0,0,1,1],
                [1,0,1,1,0,1,1],
                [0,0,1,1,1,1,1],
                [1,1,1,0,0,0,0],
                [1,1,1,1,1,1,1],
                [1,1,1,0,0,1,1]]

SEGMENT_TABLE_DEFAULT = [0]*7

class Selector:
    def __init__(self, pin):
        self._pin = pin

    @property
    def enabled(self):
        return not self._pin.value()
    
    @enabled.setter
    def enabled(self, value): 
        self._pin.value(not value)

    @staticmethod
    def create(gpio):
        return Selector(machine.Pin(gpio, mode=machine.Pin.OPEN_DRAIN, value=1, pull=machine.Pin.PULL_UP))
    
class PinSet(): 
    """Set/get the values for a bunch of pins at the same time."""
    def __init__(self, *pins):
        self._pins = pins

    @property
    def value(self):
        return [pin.value() for pin in self._pins]
    
    @value.setter
    def value(self, values):
        for pin, value in zip(self._pins, values):
            pin.value(value)

    @staticmethod
    def create(*gpios):
        return PinSet(*[machine.Pin(n, machine.Pin.OUT) for n in gpios])

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

class DisplayMux(Mux):
    SEGMENT_LUT = "SEGMENT_LUT"
    REGISTERS = "REGISTERS"
    SELECTORS = "SELECTORS"
    DELAY = "DELAY"
    PINS = "PINS"

    def __init__(self, context):
        super().__init__(context)

    def _getDigits(self, size, value):
        digits = [int(d) for d in str(value)]
        return [255]*(size-len(digits)) + digits

    async def tick(self):
        wait = self.context[DisplayMux.DELAY] / 3
        lut = self.context[DisplayMux.SEGMENT_LUT]

        registerValues = await self.context[DisplayMux.REGISTERS].get(Register.ALL)
        displayValue = await self.context[DisplayMux.REGISTERS].get(Register.DISPLAY)

        ledValues = registerValues[1:5]+[0,0]+registerValues[5:]            
        display =[lut.get(n) for n in self._getDigits(2, displayValue)] + [ledValues]

        for selector, value in zip(self.context[DisplayMux.SELECTORS], display):
            self.context[DisplayMux.PINS].value = value
            selector.enabled = True
            time.sleep(wait)
            selector.enabled = False

async def main():
    mux = DisplayMux({
        DisplayMux.REGISTERS:AsyncRegisters(),
        DisplayMux.PINS:PinSet.create(13,14,15,16,17,18,19),
        DisplayMux.SELECTORS:[Selector.create(n) for n in [2,3,4]],
        DisplayMux.SEGMENT_LUT:LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)
    })

    mux.start(1/120)

    while True:
        for n in range(0,99):
            led = random.randint(1,5)
            await mux.context[DisplayMux.REGISTERS].toggle(led)
            await mux.context[DisplayMux.REGISTERS].set(Register.DISPLAY, n)
            await asyncio.sleep(.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()
