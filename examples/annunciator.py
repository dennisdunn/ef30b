import asyncio
from lib.annunciators import Blinker

async def main():
    b = Blinker(25)
    b.start(delay=0.2)    
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass