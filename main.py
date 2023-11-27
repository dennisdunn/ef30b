from machine import Pin
import asyncio
from EF30B import PinGroup, PinGroupMultiplexer, SevenSegmentPanel,LedPanel


# test env
async def main():
    pins = [Pin(n, Pin.OUT) for n in [13,14,15,16,17,18,19]]
    msb = PinGroup(2, *pins)
    lsb = PinGroup(3, *pins)
    leds = PinGroup(4, *pins)

    digits = SevenSegmentPanel(msb,lsb)
    panel = LedPanel(leds)
    panel.TEMP=True
    panel.HILO=True
    panel.TIMER=True
    panel.FLAME=True
    panel.POWER=True

    plex = PinGroupMultiplexer(*(panel.getPinGroups()+digits.getPinGroups()))

    try:
        plex.start()
        for n in range(100):
            digits.setValue(n)
            panel.setValue()
            await asyncio.sleep_ms(200)
    finally:  
        plex.stop()

if __name__ == "__main__":
    asyncio.run(main())