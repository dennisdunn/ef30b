import time
from lib.register import Register
from lib.coro import Coro

class Display(Coro):
    SEGMENT_LUT = "SEGMENT_LUT"
    REGISTERS = "REGISTERS"
    SELECTORS = "SELECTORS"
    DELAY = "DELAY"
    PINS = "PINS"

    def __init__(self, context):
        super().__init__(context)

    def _getDigits(self, size, value):
        digits = [int(d) for d in str(value)]
        return [255]*(size-len(digits)) + digits

    async def tick(self):
        wait = self.context[Display.DELAY] / 3
        lut = self.context[Display.SEGMENT_LUT]

        registerValues = await self.context[Display.REGISTERS].get(Register.ALL)
        displayValue = await self.context[Display.REGISTERS].get(Register.DISPLAY)

        ledValues = registerValues[1:5]+[0,0]+registerValues[5:]            
        display =[lut.get(n) for n in self._getDigits(2, displayValue)] + [ledValues]

        for selector, value in zip(self.context[Display.SELECTORS], display):
            self.context[Display.PINS].value = value
            selector.enabled = True
            time.sleep(wait)
            selector.enabled = False
