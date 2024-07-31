import asyncio
import aiohttp
from . import cfg
import logging

logging.basicConfig(level=logging.DEBUG, filename="log.log")

hdr = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive",
}


async def getcource(token: str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://tonapi.io/v2/rates?tokens={token}&currencies=usd", headers=hdr
            ) as response:
                if response.status != 200:
                    logging.error(f"Failed to fetch data: {response.status}")
                    return None
                data = await response.json()
            price = data["rates"][token]["prices"]["USD"]
            return f"{price}"
    except aiohttp.ClientError as e:
        logging.error(f"Client error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return None


async def writecource():
    print("[#DEBUG] 'Get bull Price' module is active...")
    while True:
        text = str(await getcource(cfg.bull_MASTER_ADDRESS))
        with open("temp/cource.txt", "w") as f:
            f.write(text.replace(",", "."))
        await asyncio.sleep(60)


def readcource():
    with open("temp/cource.txt", "r") as f:
        course = float(f.read())
    return course
