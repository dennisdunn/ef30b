from machine import Pin, Timer

class DigitSelect:
    def __init__(self, gpio) -> None:
        self.__pin = Pin(gpio, Pin.OPEN_DRAIN, value=1)
        
    def enabled(self, enabled=None):
        if enabled == None:
            return not self.__pin.value()
        else:
            self.__pin.value(not enabled)
            
    def enable(self):
        self.enabled(True)
            
    def disable(self):
        self.enabled(False)
        
    
class Segment:
    def __init__(self, gpio) -> None:
        self.__pin = Pin(gpio, Pin.OUT)
            
    def value(self, value=None):
        return self.__pin.value(value)
        
    def on(self):
        self.value(True)
        
    def off(self):
        self.value(False)
        
    def toggle(self):
        if self.value():
            self.off()
        else:
            self.on()
            
class SegmentController:
    def __init__(self, *segments) -> None:
        self.__segments = segments
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

    @staticmethod
    def create(*gpios):
        return SegmentController([Segment(gpio) for gpio in gpios])

    def update(self, n):
        for i in range(len(self.__segments)):
            self.__segments[i].value(self.__lookup[n][i])         

class MultipleDigitDisplay:
    def __init__(self, segmentController, *digitSelectors):
        self.__controller = segmentController
        self.__selectors = digitSelectors
        self.__values = [-1]*len(digitSelectors)
        self.__timer = Timer()

    @staticmethod
    def create(segmentController, *gpios):
        return MultipleDigitDisplay(segmentController,[DigitSelector(gpio) for gpio in gpios])
            
    def value(self, value):
        values = [-1]*len(self.__selectors) + [int(d) for d in str(value)]
        values.reverse()
        end=len(self.__selectors)
        values = values[0:end] 
        values.reverse()
        self.__values = values
            
    def on(self):
        
        def update(timer):
            for display,value in zip(self.__selectors,self.__values):
                self.__controller.update(value)
                display.enable()
                time.sleep(1/100)
                display.disable()
                
        for display in self.__selectors:
            display.enabled(True)
            
        self.__timer.init(mode=Timer.PERIODIC, freq=100, callback=update)
    
    def off(self):
        self.__timer.deinit()
        for display in self.__selectors:
            display.enabled(False)
        
    def clear(self):
        self.off()
               

