import asyncio
from bot import writecource, start_bot
import logging


async def main():
    logging.basicConfig(level=logging.INFO, filename="log.log")
    try:
        await asyncio.gather(writecource(), start_bot())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
