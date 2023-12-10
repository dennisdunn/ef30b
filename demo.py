import machine
import asyncio
from lib.lut import LookupTable
from lib.raspi import PinSet,Selector
from lib.display import Display
from lib.register import AsyncRegisters,Register

async def main():
    coro = Display({
        Display.REGISTERS:AsyncRegisters(),
        Display.PINS:PinSet.create(13,14,15,16,17,18,19),
        Display.SELECTORS:Selector.create(2,3,4),
        Display.SEGMENT_LUT:LookupTable.create()
    })

    coro.start(1/120)
    
    while True:
        for n in range(0,100):
            isOdd = n % 2
            isFizz = not n % 3
            isBuzz = not n % 5
            await coro.context[Display.REGISTERS].set(Register.RED0_LED, isOdd)
            await coro.context[Display.REGISTERS].set(Register.RED1_LED, not isOdd)
            await coro.context[Display.REGISTERS].set(Register.GREEN_LED, isBuzz)
            await coro.context[Display.REGISTERS].set(Register.YELLOW_LED, isFizz and isBuzz)
            await coro.context[Display.REGISTERS].set(Register.BLUE_LED, isFizz)
            await coro.context[Display.REGISTERS].set(Register.DISPLAY, n)
            await asyncio.sleep(.5)

if __name__ == "__main__":
    try:
        asyncio.run(main()) 
    finally:
        machine.reset()
