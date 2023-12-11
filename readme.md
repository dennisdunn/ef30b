# EF-30B-disp Driver
This project repurposes a blown **EF-30B-disp** display board taken from
an electric fireplace as an I2C-addressable panel. The panel
consists of five LEDs and a two digit, 7-segment module. 

The original, blown, driver chip on the display board was
removed and replaced with 2, 8-pin, male headers. The four pin
interface socket was replaced with a 4-pin, right-angled, male
header.

The 8-pin headers connect with 2, 8-pin, female headers on 
a perfboard carrying a Raspberry Pi Pico MCU. The Pico is running
MicroPython.

When discussing pin numbers, the device is oriented so that the digits are upright and pin 1 is towards the top of the panel.

## Connecting the Panel
The 4-pin header connects power and the I2C bus to the panel. 

Pin|Function
---|---
1|VSYS
2|GND
3|SDA
4|SCL

## I2C Protocol
Querying or setting the registers is a two step process. First, write the register number to the device. Next, the controller writes a value to set the register or initiates a read to read the registers current value.

Register|Name
--------|----
0|Displayed value
1|Green LED
2|Yellow LED
3|Red LED #1
4|Red LED #2
5|Blue LED

### Selecting the I2C address
On the right side of the carrier board is a 3-pin header. Moving the jumper selects one of two device addresses.

Jumper Position|Selected Address
---|---
1-2|0x42
2-3|0x62

## ef30b Tool
The `bin/` folder contains a bash shell script to send commands to the device. It depends on the `i2c-tools` package.
 
 ```bash
 e30b <device_addr> <cmd> [subcmd]
 ```

 Command|Subcommand
 ---|---
 show|number between 0-99
 read|
 green|on, off, read
 yellow|on, off, read
 red1|on, off, read
 red2|on, off, read
 blue|on, off, read

## Display Board Notes
The **EF-30B-disp** circuit board is divided into a set of seven, common cathode, segments
and three chip select lines. When CS_0 is low, the seven segments of digit 0 (MSB)
are connected to ground and light up. When CS_1 is low, digit 1 (LSB) is enabled and 
when CS_2 is low, the LEDs are enabled. The LEDs are connected to segments A,B,C,D,E, and G.

## References
[I2CResponder](https://github.com/epmoyer/I2CResponder)