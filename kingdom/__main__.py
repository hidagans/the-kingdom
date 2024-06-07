import asyncio
import sys
from os import execl
from pyrogram import idle

from kingdom import *

LOOP = asyncio.get_event_loop()

async def main():
    await bot.start()
    console.info("Bot Running")
    await asyncio.gather(loadPlugins(), idle())


if __name__ == "__main__":
    LOOP.run_until_complete(main())
    console.info("Bot Stoped")
