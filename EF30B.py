from machine import Pin, Timer
import time, asyncio

class LedGroup:
    def __init__(self, groupGpio, *leds):
        self.__pin = Pin(groupGpio, Pin.OPEN_DRAIN, value=1)
        self.__leds = leds

    def enable(self, enabled=None):
        if enabled == None:
            return not self.__pin.value()
        else:
            self.__pin.value(not enabled)

    def value(self, values=None):
        if values == None:
            return [led.value() for led in self.__leds]
        else:
            for led, value in zip(self.__leds, values):
                led.value(value)

class SevenSegment(LedGroup):
    def __init__(self, groupGpio, *leds):
        super().__init__(groupGpio, *leds)
        self.__value = None
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
    
    def value(self, value=None):
        if value == None:
            return  self.__value
        else:
            self.__value = value

    def on(self):
        if self.__value != None:
            super().value(self.__lookup[self.__value])
            self.enable(True)

    def off(self):
        self.enable(False)

    def clear(self):
        self.__value = None

class LedGroupMultiplexer:
    def __init__(self, *groups):
        self.__led = Pin(25, Pin.OUT)
        self.__groups = groups

    async def __tick(self):
        while True:
            for group in self.__groups:
                group.on()
                await asyncio.sleep_ms(5)
                group.off()

    def value(self, n):
        digits = [int(d) for d in str(n)]
        values = [None]*(len(self.__groups) - len(digits)) + digits
        for group, m in zip(self.__groups, values):
            group.value(m)
        return n

    async def start(self):
        self.__task = asyncio.create_task(self.__tick())
        self.__led.on()

    def stop(self):
        self.__task.cancel()        
        for group in self.__groups:
            group.enable(False)
        self.__led.off()

               
# test env
async def main():
    leds = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]
    msb = SevenSegment(2, *leds)
    lsb = SevenSegment(3, *leds)
    panel = SevenSegment(4, *leds)
    plex = LedGroupMultiplexer(panel,msb,lsb)

    asyncio.create_task(plex.start())
    for n in range(90,110):
        plex.value(n)
        await asyncio.sleep_ms(250)
        
    plex.stop()
