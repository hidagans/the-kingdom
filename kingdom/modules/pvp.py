import random
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
from kingdom.core import *
from kingdom.database import *
from kingdom.decorators import *

@bot.on_message(filters.command("pvp"))
async def pvp_command(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Gunakan: /pvp <user_id_target>")
        return

    try:
        target_user = args[1]
        user = await client.get_users(target_user)
        target_user_id = user.id
    except ValueError:
        await message.reply_text("ID pengguna tidak valid.")
        return
    
    user_id = message.from_user.id
    target_user = await characters.find_one({"user_id": target_user_id})
    
    if target_user:
        await start_pvp(user_id, target_user_id, message)
    else:
        await message.reply_text("Pengguna target tidak ditemukan.")

@bot.on_message(filters.command("check_pvp"))
async def check_pvp_command(client: Client, message: Message):
    user_id = message.from_user.id
    status_message = await check_pvp_status(user_id)
    await message.reply_text(status_message)

@bot.on_message(filters.command("choose_attack"))
async def choose_attack_command(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Gunakan: /choose_attack <bagian_tubuh>")
        return

    part = args[1]
    user_id = message.from_user.id
    await choose_attack(user_id, part, message)

@bot.on_message(filters.command("choose_defense"))
async def choose_defense_command(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Gunakan: /choose_defense <bagian_tubuh>")
        return

    part = args[1]
    user_id = message.from_user.id
    await choose_defense(user_id, part, message)
