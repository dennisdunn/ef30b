import machine 
import asyncio
import random
from annunciators import Blinker
from EF30B import AsyncPinSet,AsyncRegisters,Selector,DisplayMux,MuxContext,Registers

I2C_DEVICE_ADDR = 0x42
I2C_DEVICE_ID = 0x00
I2C_SDA = 0
I2C_CLK = 1

TICK_WAIT = 1.0
BLNK_WAIT = 0.2
DISP_WAIT = 0.005

SEGMENT_PINS = [13,14,15,16,17,18,19]
CHIP_PINS = [2,3,4]
CHIP_REGS = [Registers.MSB, Registers.LSB, Registers.LED]

async def main():
    blinky = Blinker(machine.Pin(25,machine.Pin.OUT))
    blinky.start(BLNK_WAIT)

    registers = AsyncRegisters()
    pins = AsyncPinSet(*[machine.Pin(n) for n in SEGMENT_PINS])
    context = MuxContext(registers, pins)

    selects = [Selector(n) for n in CHIP_PINS]
    for select,reg in zip(selects, CHIP_REGS):
        mux = DisplayMux(context, select, reg)
        mux.start(DISP_WAIT)

    while True:
        n = random.randint(0,99)
        await registers.set(Registers.DISPLAY, n)
        print(await registers.get(Registers.ALL))
        print(await pins.value)
        await asyncio.sleep(TICK_WAIT)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()