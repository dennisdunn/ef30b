from machine import Pin
import asyncio

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

    async def _tick(self):
        while True:
            for pinGroup in self._groups:
                pinGroup.enabled = True
                await asyncio.sleep(0.005)
                pinGroup.enabled = False

    def start(self):
        self._task = asyncio.create_task(self._tick())

    def stop(self):    
        self._task.cancel()   
        for group in self._groups:
            group.enabled = False


##############################################################################

async def main():
    pins = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]

    msb = SevenSegment()
    lsb = SevenSegment()
    led = LedPanel()
    mux = Multiplexer(PinGroup(2, msb, *pins), PinGroup(3, lsb, *pins), PinGroup(4, led, *pins))

    try:
        mux.start()
        for n in range(100):
            digits = SevenSegment.getDigits(n)
            msb.value = digits[0]
            lsb.value = digits[1]

            led.red0=n%2 # even
            led.red1=not led.red0 # odd

            led.green=n%3 # fizz
            led.yellow=n%5 # buzz
            led.blue=led.green and led.yellow # fizzbuzz

            await asyncio.sleep(0.2)
    finally:  
        mux.stop()

if __name__ == "__main__":
    asyncio.run(main())