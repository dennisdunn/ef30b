from machine import Pin
import asyncio
from EF30B import PinGroup, Multiplexer, SevenSegment, LedPanel

async def main():
    pins = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]

    msb = SevenSegment()
    lsb = SevenSegment()
    led = LedPanel()
    mux = Multiplexer(PinGroup(2, msb, *pins), PinGroup(3, lsb, *pins), PinGroup(4, led, *pins))

    led.red0=True
    led.yellow=True
    led.green=True
    led.red1=True
    led.blue=True

    try:
        mux.start()
        for n in range(100):
            digits = SevenSegment.getDigits(n)
            msb.value = digits[0]
            lsb.value = digits[1]
            await asyncio.sleep(0.2)
    finally:  
        mux.stop()

if __name__ == "__main__":
    asyncio.run(main())