import asyncio
import machine
from lib.i2c_responder import I2CResponder
from lib.coro import Coro
from lib.register import AsyncRegisters

I2C_ADDR = "I2C_ADDR"
REGISTERS = "REGISTERS"

I2C_ADDR = 0x42
I2C_DEVICE_ID = 0x00
I2C_SDA = 0
I2C_CLK = 1

class Protocol(Coro):
    def __init__(self, context):
        super().__init__(context)
        self.bus = I2CResponder(I2C_DEVICE_ID, I2C_SDA, I2C_CLK, context[I2C_ADDR])

    async def tick(self):
        try:
            # wait for the controller to initiate an exchange
            if self.bus.write_data_is_available():
                # read the register number from the controller
                register = self.bus.get_write_data()[0]
                print(f'Register # {hex(register)}')

                # wait for a read or write request
                if self.bus.write_data_is_available():

                    # write the value to the register
                    value = self.bus.get_write_data()[0]
                    print(f'Writing {hex(value)} to register {hex(register)}')
                    await self.context[REGISTERS].set(register, value)

                elif self.bus.read_is_pending():

                    # read the value from the register
                    value = await self.context[REGISTERS].get(register)            
                    print(f'Reading {hex(value)} from register {hex(register)}')
                    self.bus.put_read_data(await self.context[REGISTERS].get(register))
        except Exception as e:
            print(e)
    
async def main():
    protocol = Protocol({
        I2C_ADDR: 0x42,
        REGISTERS: AsyncRegisters()
    })
    
    try:
        print("Protocol.start()")
        protocol.start(0.05)
        while True:
            await asyncio.sleep(0)
    except:
        print("Protocol.stop()")
        protocol.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)