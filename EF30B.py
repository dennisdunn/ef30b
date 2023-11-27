from machine import Pin
import asyncio

class PinGroup:
    """Enable or disable a group of pins as a whole."""
    def __init__(self, groupGpio, *pins):
        self.__pin = Pin(groupGpio, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_UP)
        self.__pins = pins
        self.__value = None

    def getValue(self, value=None):
        return self.__value

    def setValue(self, value):
           self.__value = value

    def enable(self, enabled):
        if enabled == None:
            return not self.__pin.value()
        else:
            if self.__value:
                for pin, value in zip(self.__pins, self.__value):
                    pin.value(value)
            self.__pin.value(not enabled)

class BasePanel(): 
    """Provides a way to set the value of a bunch of pin groups."""
    def __init__(self, *pinGroups):
        self.__pinGroups = pinGroups

    def getPinGroups(self):
        return self.__pinGroups
    
    def setValue(self, value):
        pass
    
class SevenSegmentPanel(BasePanel): 
    """Combines multiple PinGroups digits into one display."""
    def __init__(self, *pinGroups):
        super().__init__(*pinGroups)
        self.__lookup = [[1,1,1,1,1,1,0],
                        [0,1,1,0,0,0,0],
                        [1,1,0,1,1,0,1],
                        [1,1,1,1,0,0,1],
                        [0,1,1,0,0,1,1],
                        [1,0,1,1,0,1,1],
                        [0,0,1,1,1,1,1],
                        [1,1,1,0,0,0,0],
                        [1,1,1,1,1,1,1],
                        [1,1,1,0,0,1,1]]

    def setValue(self, value):
        digits = [int(d) for d in str(value)]
        values = [None]*(len(self.__pinGroups) - len(digits)) + digits
        for digit, idx in zip(self.__pinGroups, values):
            if idx == None:
                digit.setValue([0,0,0,0,0,0,0])
            else:
                digit.setValue(self.__lookup[idx])

class LedPanel(BasePanel):
    def __init__(self, groupGpio, *pins):
        super().__init__(groupGpio, *pins)
        self.TIMER = False
        self.HILO = False
        self.TEMP = False
        self.FLAME = False
        self.POWER = False

    def setValue(self, value=None):
        self.__pinGroups[0].setValue([self.TIMER, self.HILO,self.TEMP,self.FLAME,0,0,self.POWER])

class PinGroupMultiplexer:
    def __init__(self, *pinGroups):
        self.__led = Pin(25, Pin.OUT)
        self.__groups = pinGroups

    async def __tick(self):
        while True:
            for pinGroup in self.__groups:
                pinGroup.enable(True)
                await asyncio.sleep_ms(5)
                pinGroup.enable(False)

    def start(self):
        self.__task = asyncio.create_task(self.__tick())
        self.__led.on()

    def stop(self):    
        self.__task.cancel()   
        for group in self.__groups:
            group.enable(False)
        self.__led.off() 
