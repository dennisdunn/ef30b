import machine 
import asyncio
from lib.i2c_responder import I2CResponder

I2C_DEVICE_ADDR = 0x42
I2C_DEVICE_ID = 0x00
I2C_SDA = 0
I2C_CLK = 1

TICK_WAIT = 0.200 # 5ms

async def main(i2c_addr):
    bus = I2CResponder(I2C_DEVICE_ID, I2C_SDA, I2C_CLK, i2c_addr)
    print("I2C Echo Server")
    print(f"Listening at address {hex(i2c_addr)} on bus {hex(I2C_DEVICE_ID)}")
    try:
        while True:
            while not bus.write_data_is_available():
                await asyncio.sleep(0)
            print("PING...")
            data = bus.get_write_data()
            print(f"Received... {data}")
            while not bus.read_is_pending():
                await asyncio.sleep(0)
            print("PONG...")
            bus.put_read_data(data[0])
    finally:
        print("Shutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main(I2C_DEVICE_ADDR))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
    