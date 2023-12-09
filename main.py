import machine
import asyncio

from EF30B import DisplayMux, AsyncRegisters,PinSet,LookupTable,Selector,SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT,Register

ADDR_SELECT_1 = machine.Pin(22,pull=machine.Pin.PULL_UP)
ADDR_SELECT_2 = machine.Pin(21,pull=machine.Pin.PULL_UP)

ADDR_1 = 0x42
ADDR_2 = 0x62

async def demo():
    mux = DisplayMux({
        DisplayMux.REGISTERS:AsyncRegisters(),
        DisplayMux.PINS:PinSet.create(13,14,15,16,17,18,19),
        DisplayMux.SELECTORS:[Selector.create(n) for n in [2,3,4]],
        DisplayMux.SEGMENT_LUT:LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)
    })

    mux.start(1/120)
    
    while True:
        for n in range(0,100):
            isOdd = n % 2
            isFizz = not n % 3
            isBuzz = not n % 5
            await mux.context[DisplayMux.REGISTERS].set(Register.RED0_LED, isOdd)
            await mux.context[DisplayMux.REGISTERS].set(Register.RED1_LED, not isOdd)
            await mux.context[DisplayMux.REGISTERS].set(Register.GREEN_LED, isBuzz)
            await mux.context[DisplayMux.REGISTERS].set(Register.YELLOW_LED, isFizz and isBuzz)
            await mux.context[DisplayMux.REGISTERS].set(Register.BLUE_LED, isFizz)
            await mux.context[DisplayMux.REGISTERS].set(Register.DISPLAY, n)
            await asyncio.sleep(.5)

async def main(i2c_addr):
    pass

if __name__ == "__main__":
    try:
        if ADDR_SELECT_1.value() and ADDR_SELECT_2.value():
            asyncio.run(demo())
        elif not ADDR_SELECT_1.value():
            asyncio.run(main(ADDR_1))
        elif not ADDR_SELECT_1.value():
            asyncio.run(main(ADDR_2))        
        else:            
            raise Exception("Can't determine the I2C address.")
    except Exception as e:
        print(e)
    finally:
        machine.reset()
