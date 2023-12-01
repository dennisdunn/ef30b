from machine import Pin
import asyncio
from i2c_responder import I2CResponder

SEG_LUT = [[1,1,1,1,1,1,0],
        [0,1,1,0,0,0,0],
        [1,1,0,1,1,0,1],
        [1,1,1,1,0,0,1],
        [0,1,1,0,0,1,1],
        [1,0,1,1,0,1,1],
        [0,0,1,1,1,1,1],
        [1,1,1,0,0,0,0],
        [1,1,1,1,1,1,1],
        [1,1,1,0,0,1,1]]

SEG_DEFAULT = [0,0,0,0,0,0,0]

SDA = 31 # Pin(26, Pin.ALT_I2C)
SCL = 32 # Pin(27, Pin.ALT_I2C)


class PinSet:
    def __init__(self, *pins):
        self._pins = pins

    @property
    def value(self):
        return [pin.value() for pin in self._pins]

    @value.setter
    def value(self, values):
        for pin,value in zip(self._pins, values):
            pin.value(value)

class CommonGround:
    """Enable/disable a group of pins."""
    def __init__(self, gpio):
        self._ctl = Pin(gpio, mode=Pin.OPEN_DRAIN, value=1, pull=Pin.PULL_UP)

    @property
    def enabled(self):
        return not self._ctl.value()
    
    @enabled.setter
    def enabled(self, value):
        self._ctl.value(not value)

class Provider:
    def __init__(self, registers):
        self._registers = registers

    def setup(self, pins):
        pass

class SegProvider(Provider):
    def __init__(self, reg_no, registers):
        super().__init__(registers)
        self._reg_no = reg_no
        self._lut = LUT(SEG_LUT,SEG_DEFAULT)

    def setup(self, pinset):
        r = self._registers
        pinset.value = self._lut.get(r.get(self._reg_no))

class LedProvider(Provider):
    def __init__(self, registers):
        super().__init__(registers)
        
    def setup(self, pinset):
        r = self._registers
        pinset.value = [r.get(n) for n in range(Registers.GREEN_LED, Registers.RED1_LED+1)]+[0,0]+[r.get(Registers.BLUE_LED)]

class Mux:
    TICK_WAIT = 0.005 # 5 ms

    def __init__(self, segments, controllers, providers):
        self._segments = segments
        self._controllers = controllers
        self._providers = providers

    async def loop(self):
        while True:
            for ctl, provider in zip(self._controllers,self._providers):
                provider.setup(self._segments)
                ctl.enabled = True
                await asyncio.sleep(Mux.TICK_WAIT)
                ctl.enabled = False

class LUT:
    def __init__(self, table, default):
        self._table = table
        self._default = default

    def get(self, idx):
        try:
            return self._table[idx]
        except:
            return self._default
        
class Registers:
    DIGITAL_DISPLAY = 0
    GREEN_LED = 1
    YELLOW_LED = 2
    RED0_LED = 3
    RED1_LED = 4
    BLUE_LED = 5
    MSB = 10
    LSB = 11
    ALL = 255

    def __init__(self):
        self._registers = [0,0,0,0,0,0]
        self.digits = [255,255]

    def get(self, reg_no):
        match reg_no:
            case Registers.MSB:
                return self.digits[0]
            case Registers.LSB:
                return self.digits[1]
            case Registers.ALL:
                return self._registers
            case _:
                return self._registers[reg_no]

    def set(self, reg_no, value):
        self._registers[reg_no] = value
        if reg_no == Registers.DIGITAL_DISPLAY:
            self.digits = self._getDigits(value)

    def _getDigits(self, value):
        """Get the digits of the value as [MSB...LSB]"""
        digits = [int(d) for d in str(value)]
        return [255]*(2 - len(digits)) + digits

class Responder:
    def __init__(self, registers):
        self._registers = registers

    def read(self, reg_no):
        return self._registers.get(reg_no)

    def write(self, reg_no, value):
        self._registers.set(reg_no, value)

    async def loop(self):
        pass

async def main():
    registers = Registers()
    segments = PinSet([Pin(n, Pin.OUT) for n in range(13,20)])
    controllers = [CommonGround(n) for n in range(2,5)]
    providers = [SegProvider(Registers.MSB, registers), SegProvider(Registers.LSB,registers), LedProvider(registers)]
    mux = Mux(segments, controllers, providers)
    responder = Responder(registers)

if __name__ == "__main__":
    pass