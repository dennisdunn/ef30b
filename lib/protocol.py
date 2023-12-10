import asyncio
import machine
from lib.i2c_responder import I2CResponder
from lib.coro import Coro
from lib.register import AsyncRegisters


I2C_DEVICE_ID = 0x00
I2C_SDA = 0
I2C_CLK = 1

class Protocol(Coro):
    I2C_ADDR = "I2C_ADDR"
    REGISTER = "REGISTER"

    def __init__(self, context):
        super().__init__(context)
        self.bus = I2CResponder(I2C_DEVICE_ID, I2C_SDA, I2C_CLK, context[Protocol.I2C_ADDR])

    async def tick(self):
        # wait for the controller to initiate an exchange
        if self.bus.write_data_is_available():
            # read the register number from the controller
            register = self.bus.get_write_data()[0]
            # wait for a read or write request
            if self.bus.write_data_is_available():
                # write the value to the register
                value = self.bus.get_write_data()[0]
                await self.context[Protocol.REGISTER].set(register, value)
            elif self.bus.read_is_pending():
                # read the value from the register
                value = await self.context[Protocol.REGISTER].get(register)     
                self.bus.put_read_data(await self.context[Protocol.REGISTER].get(register))