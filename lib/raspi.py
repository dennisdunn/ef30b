from machine import Pin

class Selector:
    "Enable/disable a common-cathode pin set."
    def __init__(self, pin):
        self._pin = pin

    @property
    def enabled(self):
        return not self._pin.value()
    
    @enabled.setter
    def enabled(self, value): 
        self._pin.value(not value)

    @staticmethod
    def create(*gpios):
        return [Selector(Pin(pin, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_UP)) for pin in gpios]
    
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

    @staticmethod
    def create(*gpios):
        return PinSet(*[Pin(n, Pin.OUT) for n in gpios])
