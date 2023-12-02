from machine import Pin
import machine
import asyncio
import random

<<<<<<< HEAD
class PinGroup:
    """Enable or disable a group of pins as a whole.
    
    The source of the values for the pins is any object with
    a value() property."""
    def __init__(self, groupGpio, source, *pins):
        self._pin = Pin(groupGpio, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_UP)
        self._pins = pins
        self._source = source

    @property
    def enabled(self):
        return not self._pin.value()
    
    @enabled.setter
    def enabled(self, value):
        for pin, pinValue in zip(self._pins, self._source.value):
            pin.value(pinValue)
        self._pin.value(not value)

   
class SevenSegment(): 
    def __init__(self):
        self._value = None
        self._lookup = [[1,1,1,1,1,1,0],
                        [0,1,1,0,0,0,0],
                        [1,1,0,1,1,0,1],
                        [1,1,1,1,0,0,1],
                        [0,1,1,0,0,1,1],
                        [1,0,1,1,0,1,1],
                        [0,0,1,1,1,1,1],
                        [1,1,1,0,0,0,0],
                        [1,1,1,1,1,1,1],
                        [1,1,1,0,0,1,1]]
        
    @property
    def value(self):
        if self._value == None:
            return [0,0,0,0,0,0,0]
        return self._value
    
    @value.setter
    def value(self, value=None):
        if value == None:
            self._value = value
        else:
            self._value = self._lookup[value]

    @staticmethod
    def getDigits(value, size=2):
        """Get the digits of the value as [MSB...LSB]"""
        digits = [int(d) for d in str(value)]
        return [None]*(size - len(digits)) + digits

class LedPanel():
    def __init__(self):
        self._green = False # timer 
        self._yellow = False # hi/lo
        self._red0 = False # temp
        self._red1 = False # flame
        self._blue = False # power

    @property
    def green(self):
        return self._green
    
    @green.setter
    def green(self, value):
        self._green = value

    @property
    def yellow(self):
        return self._yellow
    
    @yellow.setter
    def yellow(self, value):
        self._yellow = value

    @property
    def red0(self):
        return self._red0
    
    @red0.setter
    def red0(self, value):
        self._red0 = value

    @property
    def red1(self):
        return self._red1
    
    @red1.setter
    def red1(self, value):
        self._red1 = value

    @property
    def blue(self):
        return self._blue
    
    @blue.setter
    def blue(self, value):
        self._blue = value

    @property
    def value(self):
        return [self._green,self._yellow,self._red0,self._red1,0,0,self._blue]

class Multiplexer:
    def __init__(self, *pinGroups):
        self._groups = pinGroups
        
    @property
    def groups(self):
        return self._groups
    
    async def eventLoop(self):
        while True:
            for pinGroup in self._groups:
                pinGroup.enabled = True
                await asyncio.sleep(0.005)
                pinGroup.enabled = False

##############################################################################

class demo:
    def __init__(self,*sources):
        self._msb = sources[0]
        self._lsb = sources[1]
        self._led = sources[2]

    async def eventLoop(self, period=0.1):
        while True:
            n = random.randint(0,99)

            [self._msb.value, self._lsb.value] = SevenSegment.getDigits(n)

            self._led.red0=n%2 # odd
            self._led.red1=not self._led.red0 # even

            self._led.green=not (n%3) # fizz
            self._led.yellow=not (n%5) # buzz
            self._led.blue=self._led.green and self._led.yellow # fizzbuzz
            
            await asyncio.sleep(period)

def listener():
    async def eventLoop():
        pass

async def main():
    pins = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]

    msb = SevenSegment()
    lsb = SevenSegment()
    led = LedPanel()

    mux = Multiplexer(PinGroup(2, msb, *pins), PinGroup(3, lsb, *pins), PinGroup(4, led, *pins))
    poc = demo(msb,lsb,led) 

    asyncio.create_task(mux.eventLoop())
    asyncio.create_task(poc.eventLoop(0.5))

    await asyncio.sleep(15)

    for group in mux.groups:
        group.enabled = False

if __name__ == "__main__":
    asyncio.run(main())
=======
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
    context = MuxContext(AsyncRegisters(), AsyncPinSet(*[Pin(n, Pin.OUT) for n in pins]))
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
>>>>>>> spike/i2c
