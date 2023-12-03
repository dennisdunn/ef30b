import machine
import asyncio
import random

from EF30B import DisplayMux, AsyncRegisters,PinSet,LookupTable,Selector,SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT,Register

async def main():
    mux = DisplayMux({
        DisplayMux.REGISTERS:AsyncRegisters(),
        DisplayMux.PINS:PinSet.create(13,14,15,16,17,18,19),
        DisplayMux.SELECTORS:[Selector.create(n) for n in [2,3,4]],
        DisplayMux.SEGMENT_LUT:LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)
    })

    mux.start(1/120)

    while True:
        for n in range(0,99):
            led = random.randint(1,5)
            await mux.context[DisplayMux.REGISTERS].toggle(led)
            await mux.context[DisplayMux.REGISTERS].set(Register.DISPLAY, n)
            await asyncio.sleep(.5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        machine.reset()
