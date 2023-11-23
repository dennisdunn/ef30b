from machine import Pin, Timer
import time

class DigitSelect:
    def __init__(self, gpio) -> None:
        self.__pin = Pin(gpio, Pin.OPEN_DRAIN, value=1)
        
    def enabled(self, enabled=None):
        if enabled == None:
            return not self.__pin.value()
        else:
            self.__pin.value(not enabled)
        
    
class Segment:
    def __init__(self, gpio) -> None:
        self.__pin = Pin(gpio, Pin.OUT)
        
    def isOn(self):
        return self.__pin.value()
    
    def set(self, value):
        self.__pin.value(value)
        
    def on(self):
        self.set(True)
        
    def off(self):
        self.set(False)
        
    def toggle(self):
        if self.isOn():
            self.off()
        else:
            self.on()
            
class SingleDigitDisplay:
    def __init__(self, select, segments) -> None:
        self.__select = select
        self.__segments = segments
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
        
    def value(self, value):
        self.__value = value
                
    def on(self):       
        self.__select.enabled(True)
        
    def off(self):
        self.__select.enabled(False)
        
    def update(self):
        if self.__value == None:
            for segment in self.__segments:
                segment.off()
        else:
            for i in range(7):
                self.__segments[i].set(self.__lookup[self.__value][i])         

class MultipleDigitDisplay:
    def __init__(self, *digitDisplays):
        self.__digitDisplays = digitDisplays
        self.__timer = Timer()
            
    def value(self, value):
        displays = list(reversed(self.__digitDisplays))
        digits = list(reversed([int(d) for d in str(value)]))
        for display,n in zip(displays,digits+[None]*(len(displays)-len(digits))):
            display.value(n)
            
    def on(self):
        for display in self.__digitDisplays:
            display.on()
    
    def off(self):
        for display in self.__digitDisplays:
            display.off()
        self.__timer.deinit()
            
    def update(self):
        pass
    
DS1 = DigitSelect(2)
DS2 = DigitSelect(3)
DS3 = DigitSelect(4)

segments = [Segment(13),Segment(14),Segment(15),Segment(16),Segment(17),Segment(18),Segment(19)]

# for i in range(7):   
#     segments[i].off()
#     
# for i in range(7):
#     DS1.enabled(True)
#     segments[i].on()
#     time.sleep(1)
#     DS1.enabled(False)

MSD = SingleDigitDisplay(DS1,segments)
LSD = SingleDigitDisplay(DS2,segments)

LEDS = SingleDigitDisplay(DS3,segments)

Disp = MultipleDigitDisplay(MSD, LSD)


for i in range(10):
    Disp.value(i)
    Disp.on()
    time.sleep(0.5)
    Disp.off()
#         MSD.off()
