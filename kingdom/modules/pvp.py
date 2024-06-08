import random
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
from kingdom.core import *
from kingdom.database import *
from kingdom.decorators import *

@KING.CMD("pvp")
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


@KING.CMD("check_pvp")
async def check_pvp_command(client: Client, message: Message):
    user_id = message.from_user.id
    status_message = await check_pvp_status(user_id)
    await message.reply_text(status_message)

@KING.CMD("duel")
async def duel_command(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 3:
        await message.reply_text("Gunakan: /duel <user_id_target> <gold_amount>")
        return

    try:
        target_user = args[1]
        bet_amount = int(args[2])
        user = await client.get_users(target_user)
        target_user_id = user.id
    except ValueError:
        await message.reply_text("ID pengguna atau jumlah gold tidak valid.")
        return

    user_id = message.from_user.id
    target_user = await characters.find_one({"user_id": target_user_id})

    if not target_user:
        await message.reply_text("Pengguna target tidak ditemukan.")
        return

    await start_duel(user_id, target_user_id, bet_amount, message)

@KING.CMD("check_duel")
async def check_duel_command(client: Client, message: Message):
    user_id = message.from_user.id
    status_message = await check_duel_status(user_id)
    await message.reply_text(status_message)