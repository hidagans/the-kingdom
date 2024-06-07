import asyncio

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from kingdom.database import *
from kingdom.core import KINGDOM, FILTERS, subcribe


@KINGDOM.CMD("start", FILTERS.PRIVATE)
@subcribe
async def start(client, message):
    user_id = message.from_user.id
    await add_served_user(user_id)    
    character_profile = await get_character_profile(user_id)
    
    home_button = [
        [
             InlineKeyboardButton("MY PROFILE", callback_data="my_profile"),
             InlineKeyboardButton("KONTEN", callback_data="cb_konten")
        ],
        [
            InlineKeyboardButton("BLACK MARKET", callback_data="black_market"),
        ]
    ]
    if character_profile:
        await message.reply("Selamat datang kembali! Ini profil Anda:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply("Halo! Anda belum mendaftar. Silakan buat karakter Anda dengan mengirim pesan /daftar.")
    


@KINGDOM.CMD("daftar", FILTERS.PRIVATE)
@subcribe
async def daftar(client, message):
    user_id = message.from_user.id
    character_profile = await get_character_profile(user_id)
    
    if len(message.command) < 2:
        await message.reply("Anda harus mengirimkan nama karakter Anda! Contoh: /daftar John Doe")
        return

    character_name = ' '.join(message.command[1:])
    
    if not character_profile:
        character_stats = {'EXP': 0, 'Fight': 0, 'Skill Points': 0, 'max_hp': 1200, 'max_mana': 10}
        await save_character_profile(user_id, character_name)
        await save_character_stats(user_id, character_stats)
        #await give_starting_items(user_id)
        reply_text = f"Selamat! Karakter Anda dengan nama {character_name} telah dibuat. Anda mendapatkan senjata dan armor."
    else:
        reply_text = "Anda sudah memiliki karakter. Gunakan /start untuk melihat profil Anda."
    
    await message.reply(reply_text)  
