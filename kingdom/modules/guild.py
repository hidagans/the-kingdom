from pyrogram import filters
from pyrogram.types import *
from kingdom.database import *
from kingdom.core import *
import asyncio

@KING.CMD("create_guild")
async def create_guild(client, message):
    user_id = message.from_user.id
    guild_exists = await does_guild_exist(user_id)
    if guild_exists:
        await message.reply_text("Anda telah menjadi anggota guild sebelumnya.")
        return
    
    in_guild = await is_in_guild(user_id)
    if in_guild:
        await message.reply_text("Anda telah menjadi anggota guild lain. Anda harus meninggalkan guild tersebut sebelum membuat yang baru.")
        return
    
    guild_name = message.text.split(" ", 1)[1]
    await create_new_guild(user_id, guild_name)

    await message.reply_text(f"guild '{guild_name}' telah berhasil dibuat!")

@KING.CMD("guild_info")
async def info_guild(client, message):
    user_id = message.from_user.id
    character_profile = await get_character_profile(user_id)
    guild_id = character_profile.get('Guild')
    if guild_id:
        guild_data = await guild.find_one({"_id": guild_id})
        if guild_data:
            user_names = {}
            for key, value in guild_data.items():
                if key != "_id" and key != "Leader":
                    user_names[key] = await get_character_name(value)

            for key, value in user_names.items():
                guild_data[key] = value

            guild_text = '\n'.join([f"{key}: {value}" for key, value in guild_data.items()])
            await message.reply_text(f"Info Guild:\n{guild_text}")
            return
    await message.reply_text("Anda tidak tergabung dalam guild manapun.")
    
@KING.CMD("join_guild")
async def join_guild(client, message):
    user_id = message.from_user.id
    in_guild = await is_in_guild(user_id)
    if in_guild:
        await message.reply_text("Anda telah menjadi anggota guild sebelumnya. Anda tidak dapat menjadi anggota guild lain.")
        return

    guild_name = message.text.split(" ", 1)[1]
    if guild_name :
        await join_guild(user_id, guild_name)
        await message.reply_text(f"Anda telah berhasil bergabung dengan guild '{guild_name}'!")
    
    await message.reply_text("Anda harus menentukan guild mana yang ingin Anda ikuti. Gunakan /join_guild <nama_guild>")

@KING.CMD("leave_guild")
async def leave_guild(client, message):
    user_id = message.from_user.id
    in_guild = await is_in_guild(user_id)
    if in_guild:
        guild_id = await get_user_guild_id(user_id)
        await remove_user_from_guild(user_id, guild_id)
        await message.reply_text("Anda telah berhasil keluar dari guild!")
    else:
        await message.reply_text("Anda tidak tergabung dalam guild manapun.")