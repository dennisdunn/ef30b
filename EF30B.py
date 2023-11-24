from machine import Pin, Timer
import time

class LedGroup:
    def __init__(self, groupGpio, *leds):
        self.__pin = Pin(groupGpio, Pin.OPEN_DRAIN, value=1)
        self.__leds = leds
        self.__state = None

    def enabled(self, enabled=None):
        if enabled == None:
            return not self.__pin.value()
        else:
            self.__pin.value(not enabled)

    def state(self, values=None):
        self.__state = values
        if values != None:
            for led, value in zip(self.__leds, values):
                led.value(value)

    def on(self):
        if self.__state != None:
            self.enabled(True)
        else:
            self.enabled(False)

    def off(self):
        self.enabled(False)

class SevenSegment(LedGroup):
    def __init__(self, groupGpio, *leds):
        super().__init__(groupGpio, *leds)
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
    
    def value(self, n=None):
        if n == None:
            super().state(None)
        else:
            super().state(self.__lookup[n])

class LedGroupMultiplexer:
    def __init__(self, *groups):
        self.__groups = groups
        self.__running = False
        self.__timer = Timer
        self.freq = 30

    def __tick(self):
        for group in groups:
            group.on()
            time.sleep(len(self.__groups)/self.freq)
            group.off()

    def value(self, n):
        for group, m in zip(self.__groups,[int(d) for d in str(n)]):
            group.value(m)

    def start(self):
        self.__timer.init(mode=Timer.PERIODIC, freq=self.freq)
        self.__running = True

    def stop(self):
        self.__timer.deinit()
        self.__running = False

               
# test env

leds = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]
msb = SevenSegment(2, *leds)
lsb = SevenSegment(3, *leds)
plex = LedGroupMultiplexer(msb,lsb)