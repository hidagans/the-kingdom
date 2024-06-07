from pyrogram import filters
from config import ADMINS
from kingdom import bot


class FILTERS:
    ME = filters.me
    GROUP = filters.group
    PRIVATE = filters.private
    OWNER = filters.user(ADMINS)
    ME_PRIVATE = filters.me & filters.private
    ME_GROUP = filters.me & filters.group
    ME_OWNER = filters.me & filters.user(ADMINS)

class KINGDOM:
    def CMD(command, filter=FILTERS.ME):
        def wrapper(func):
            @bot.on_message(filters.command(command) & filter)
            async def wrapped_func(client, message):
                await func(client, message)

            return wrapped_func

        return wrapper

    def INLINE(command):
        def wrapper(func):
            @bot.on_inline_query(filters.regex(command))
            async def wrapped_func(client, message):
                await func(client, message)

            return wrapped_func

        return wrapper

    def CALLBACK(command):
        def wrapper(func):
            @bot.on_callback_query(filters.regex(command))
            async def wrapped_func(client, message):
                await func(client, message)

            return wrapped_func

        return wrapper
