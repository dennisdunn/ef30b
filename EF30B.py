import machine
import asyncio
import random

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

class ChipSelect:
    def __init__(self, groupGpio):
        self._pin = machine.Pin(groupGpio, mode=machine.Pin.OPEN_DRAIN, value=1, pull=machine.Pin.PULL_UP)

    @property
    def enabled(self):
        return not self._pin.value()
    
    @enabled.setter
    def enabled(self, value): 
        self._pin.value(not value)
    
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

class AsyncPinSet(PinSet):
    def __init__(self, *pins):
        super().__init__(*pins)
        self._lock = asyncio.Lock()

    async def get(self):
        async with self._lock:
            return self.value
        
    async def set(self, values):
        async with self._lock:
            self.value = values

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

class MuxContext:
    def __init__(self, registers, pins):
        self._registers = registers
        self._pins = pins

    @property
    def pins(self):
        return self._pins
    
    @property
    def registers(self):
        return self._registers

class DisplayMux(Mux):
    def __init__(self, ctx, selects):
        super().__init__(context=ctx)
        self._selects = selects
        self._lut = LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)

    def _getDigits(self, size, value):
        digits = [int(d) for d in str(value)]
        return [None]*(size-len(digits)) + digits
    
    async def _show(self, selector, value, wait):
        await self._context.pins.set(value)
        selector.enabled = True
        await asyncio.sleep(wait)
        selector.enabled = False
    
    async def loop(self, wait):
        self._wait = wait
        while self.isRunning:
            values = await self._context.registers.get(Register.ALL)

            leds = values[1:5]+[0,0]+values[5:]            
            display =[self._lut.get(n) for n in self._getDigits(2, values[Register.DISPLAY])] + [leds]
            
            for selector, value in zip(self._selects, display):
                await self._show(selector, value, wait)

            await asyncio.sleep(0)

async def main():
    pins = [13,14,15,16,17,18,19]
    context = MuxContext(AsyncRegisters(), AsyncPinSet(*[machine.Pin(n, machine.Pin.OUT) for n in pins]))
    selectors = [ChipSelect(n) for n in [2,3,4]]
    mux = DisplayMux(context, selectors)

    mux.start(0.005)

    while True:
        for n in range(0,99):
            led = random.randint(1,5)
            await context.registers.toggle(led)
            await context.registers.set(Register.DISPLAY, n)
            await asyncio.sleep(.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()
