import asyncio
import sys
from os import execl
from pyrogram import idle
from importlib import import_module

from kingdom import *
from kingdom.modules import loadModule


LOOP = asyncio.get_event_loop()


async def loadPlugins():
    modules = loadModule()
    for mod in modules:
        imported_module = import_module(f"kingdom.modules.{mod}")

    console.info("Plugins installed")


async def main():
    await bot.start()
    console.info("Bot Running")
    await asyncio.gather(loadPlugins(), idle())


if __name__ == "__main__":
    LOOP.run_until_complete(main())
    console.info("Bot Stoped")
