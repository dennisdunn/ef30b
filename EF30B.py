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
        self.__running = False
        self.__timer = Timer()
        self.__freq = 100

    def __tick(self, timer):
        try:
            for group in self.__groups:
                group.on()
                time.sleep(.001)
                group.off()
        except:
            self.stop(timer)


    def freq(self, freq=None):
        if f == None:
            return self.__freq
        else:
            self.__freq = freq

    def value(self, n):
        digits = [int(d) for d in str(n)]
        values = [None]*(len(self.__groups) - len(digits)) + digits
        for group, m in zip(self.__groups, values):
            group.value(m)
        return n

    def start(self):
        self.__timer.init(mode=Timer.PERIODIC, freq=self.__freq, callback=self.__tick)
        self.__led.on()

    def stop(self, ignore=None):
        self.__timer.deinit()
        self.__led.off()

               
# test env

leds = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]
msb = SevenSegment(2, *leds)
lsb = SevenSegment(3, *leds)
plex = LedGroupMultiplexer(msb,lsb)
timer = Timer()

plex.start()
# timer.init(mode=Timer.ONE_SHOT, period=5000, callback=plex.stop)
for n in range(100):
    plex.value(n)
    time.sleep(0.2)
# plex.stop()
