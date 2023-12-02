from machine import Pin
import machine
import asyncio
import random

from multiplexer import Mux

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
        self._pin = Pin(groupGpio, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_UP)

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

class LookupTable:
    def __init__(self, table, default):
        self._table = table
        self._default = default

    def get(self, value):
        try:
            return self._table[value]
        except:
            return self._default

class Registers:
    DISPLAY = 0
    GREEN_LED = 1
    YELLOW_LED = 2
    RED0_LED = 3
    RED1_LED = 4
    BLUE_LED = 5
    MSB = 128
    LSB = 129
    LED = 130
    ALL = 255

    def __init__(self):
        self._registers = [0]*6
        self._display = [255]*2

    def _bitsToInt(self,bitlist):
        out = 0
        for bit in bitlist:
            out = (out << 1) | bit
        return out

    def get(self, regNum):
        if regNum == Registers.ALL:
            return self._registers
        elif regNum == Registers.MSB:
            return self._display[0]
        elif regNum == Registers.LSB:
            return self._display[1]
        elif regNum == Registers.LED:
            ledBits = [0]*7 # [self._registers[n] for n in range(Registers.GREEN_LED, Registers.BLUE_LED)] + [0]*2 + [self._registers[Registers.BLUE_LED]]
            return self._bitsToInt(ledBits)
        else:
            return self._registers[regNum]

    def set(self, regNum, value):
        if regNum == Registers.DISPLAY:
            digits = [int(d) for d in str(value)]
            self._display = [255]*(len(self._display) - len(digits)) + digits
        self._registers[regNum] = value

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
    


class ChipSelectMux(Mux):
    def __init__(self, context, chipSelect, regNum):
        super().__init__(context)
        self._chipSelect = chipSelect
        self._regNum = regNum
        self._segmentLookup = LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)

    async def loop(self, wait):
        while self.isRunning:
            ctx = self._context
            value = await ctx.registers.get(self._regNum) 
            await ctx.pins.set(self._segmentLookup.get(value))
            self._chipSelect.enabled = True
            await asyncio.sleep(wait)
            self._chipSelect.enabled = False

async def main():
    pins = [13,14,15,16,17,18,19]
    context = MuxContext(AsyncRegisters(), AsyncPinSet(*[Pin(n, Pin.OUT) for n in pins]))
    selectors = [ChipSelect(n) for n in [2,3,4]]
    for selector, reg in zip(selectors, range(Registers.MSB,Registers.LED+1)):
        mux = ChipSelectMux(context, selector, reg)
        mux.start(0.005)
    while True:
        await context.registers.set(Registers.DISPLAY, random.randint(0,99) )
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()