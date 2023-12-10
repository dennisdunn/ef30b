from lib.coro import Coro
import asyncio

class _Demo(Coro):
    async def tick(self):
        print(".",end="")
        n = self.context["n"]
        n+=1
        if n > 16:
            print(self.context)
            n = 0
        self.context["n"]=n

async def main():
    mux = _Demo({"n":0})
    mux.start(0.1)
    print(mux.context)
    while True:
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
