import machine
import asyncio
from lib.lut import LookupTable
from lib.raspi import PinSet,Selector
from lib.display import Display
from lib.register import AsyncRegisters,Register
from lib.protocol import Protocol

I2C_ADDR_A = 0x42
I2C_ADDR_B = 0x62

def getI2cAddr():
    pin_a = machine.Pin(22,mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
    pin_b = machine.Pin(21,mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
    if not pin_a.value():
        return I2C_ADDR_A
    elif not pin_b.value():
        return I2C_ADDR_B
    else:
        raise Exception("Can't determine I2C device address.")
    
async def main():
    
    display = Display({
        Display.REGISTERS:AsyncRegisters(),
        Display.PINS:PinSet.create(13,14,15,16,17,18,19),
        Display.SELECTORS:Selector.create(2,3,4),
        Display.SEGMENT_LUT:LookupTable.create()
    })

    protocol = Protocol({
        Protocol.I2C_ADDR: getI2cAddr(),
        Protocol.REGISTER: display.context[Display.REGISTERS]
    })

    tasks = [display.start(1/120), protocol.start(0.50)]

    while True:
        await asyncio.sleep(0)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass