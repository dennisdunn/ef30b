import machine 
import asyncio
from lib.i2c_responder import I2CResponder

I2C_DEVICE_ADDR = 0x42
I2C_DEVICE_ID = 0x00
I2C_SDA = 0
I2C_CLK = 1

TICK_WAIT = 0.200 # 5ms

# I2C Echo
# Read a buffer and then wait for a read request and write it back out

async def blink():
    led = machine.Pin(25,machine.Pin.OUT)
    while True:
        led.toggle()
        await asyncio.sleep(TICK_WAIT)


async def main(bus):
    asyncio.create_task(blink())
    while True:
        print("Waiting for write request.")
        while not bus.write_data_is_available():
            await asyncio.sleep(0)
        print("Receiving write data.")
        data = bus.get_write_data()
        print(data)
        print("Waiting for read request.")
        while not bus.read_is_pending():
            await asyncio.sleep(0)
        print("Sending requested data.")
        bus.put_read_data(data[0])

if __name__ == "__main__":
    try:
        bus = I2CResponder(I2C_DEVICE_ID, I2C_SDA, I2C_CLK, I2C_DEVICE_ADDR)
        print("I2C Echo Server --- starting")
        asyncio.run(main(bus))
    finally:
        print("I2C Echo Server --- stopping")
        machine.reset()
    