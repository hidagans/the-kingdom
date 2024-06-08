import asyncio
from aiofiles.os import remove as aremove
from pyrogram import filters
from pyrogram.types import *
from kingdom import bot
from kingdom.core import KING, FILTERS
from kingdom.database import *
from config import ADMINS
from kingdom.decorators import *

@KING.CALL("cb_stats")
async def show_stats_command(client, callback_query):
    user_id = callback_query.from_user.id
    character_profile = await get_character_profile(user_id)
    buttons = [
        [InlineKeyboardButton("UPDATE STATS", callback_data="cb_update_stats"),
         InlineKeyboardButton("BACK", callback_data="my_profile")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    if character_profile:
        character_name = character_profile['name']
        character_stats = await get_character_stats(user_id)
        stats_text = '\n'.join([f"{stat}: {value}" for stat, value in character_stats.items()])
        reply_text = f"Nama: {character_name}\nStatistik Total:\n{stats_text}"
    else:
        reply_text = "Nama: Belum ditentukan\nBelum ada karakter yang dibuat."
    
    await callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

# Callback for showing user profile
@KING.CALL("my_profile")
async def my_profile(client, callback_query):
    user_id = callback_query.from_user.id
    user = await client.get_users(user_id)
    character_profile = await get_character_profile(user_id)
    
    if character_profile:
        character_name = character_profile['name']
        character_stats = await get_character_stats(user_id)
        character_wallet = await get_character_wallet(user_id)
        wallet_text = '\n'.join([f"{stat}: {value}" for stat, value in character_wallet.items()])
        stats_text = '\n'.join([f"{stat}: {value}" for stat, value in character_stats.items()])
        reply_text = f"Profil Karakter:\nNama: {character_name}\nWallet: \n{wallet_text}\nStatistik:\n{stats_text}"
    else:
        reply_text = "Profil Karakter:\nNama: Belum ditentukan\nBelum ada karakter yang dibuat."

    buttons = [
        [InlineKeyboardButton("TOKEN", callback_data="cb_token"),
         InlineKeyboardButton("STATS", callback_data="cb_stats")],
        [InlineKeyboardButton("INVENTORY", callback_data="cb_inventory"),
         InlineKeyboardButton("EQUIPMENT", callback_data="cb_equipment")],
        [InlineKeyboardButton("DELETE PROFILE", callback_data="cb_delete_char"),
         InlineKeyboardButton("BACK", callback_data="start")]
    ]

    if callback_query.from_user.photo:
        photos = await client.download_media(callback_query.from_user.photo.big_file_id)
        await bot.send_photo(user_id, photo=photos, caption=reply_text, reply_markup=InlineKeyboardMarkup(buttons))
        
        await aremove(photos)
    else:
        await bot.send_message(user_id, reply_text, reply_markup=InlineKeyboardMarkup(buttons))



# Command to handle /start
@KING.CMD("start")
async def start_command(client, message):
    user_id = message.from_user.id
    await add_served_user(user_id)
    character_profile = await get_character_profile(user_id)
    buttons = [
        [InlineKeyboardButton("MY PROFILE", callback_data="my_profile"),
         InlineKeyboardButton("KONTEN", callback_data="cb_konten")
        ],
        [
        InlineKeyboardButton("BLACK MARKET", callback_data="black_market"),
        ]
    ]

    if character_profile:
        await message.reply("Selamat datang kembali! Ini profil Anda:", reply_markup=InlineKeyboardMarkup (
                buttons
            ))
    else:
        await message.reply("Halo! Anda belum mendaftar. Silakan buat karakter Anda dengan mengirim pesan /daftar.")

# Callback to go back to start menu
@KING.CALL("start")
async def back_to_start(client, callback_query):
    user_id = callback_query.from_user.id
    character_profile = await get_character_profile(user_id)
    buttons = [
        [InlineKeyboardButton("MY PROFILE", callback_data="my_profile"),
         InlineKeyboardButton("KONTEN", callback_data="cb_konten")
        ],
        [
        InlineKeyboardButton("BLACK MARKET", callback_data="black_market"),
        ]
    ]
    if character_profile:
        await callback_query.edit_message_text("Selamat datang kembali! Ini profil Anda:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await callback_query.edit_message_text("Halo! Anda belum mendaftar. Silakan buat karakter Anda dengan mengirim pesan /daftar.")

# Command to create a character
@KING.CMD("daftar")
async def create_character(client, message):
    user_id = message.from_user.id
    character_profile = await get_character_profile(user_id)
    
    if len(message.command) < 2:
        await message.reply("Anda harus mengirimkan nama karakter Anda! Contoh: /daftar John Doe")
        return

    character_name = ' '.join(message.command[1:])
    
    if not character_profile:
        character_stats = {'EXP': 0, 'Fight': 0, 'Skill Points': 0, 'max_hp': 1200, 'max_mana': 10}
        profile = {'user_id': user_id, 'name': character_name}
        await save_character_profile(user_id, profile)
        await save_character_stats(user_id, character_stats)
        await give_starting_items(user_id)
        reply_text = f"Selamat! Karakter Anda dengan nama {character_name} telah dibuat. Anda mendapatkan senjata dan armor."
    else:
        reply_text = "Anda sudah memiliki karakter. Gunakan /start untuk melihat profil Anda."
    
    await message.reply(reply_text)

@KING.CALL("cb_delete_char")
async def yesno(client, callback_query):
    buttons = [
        [InlineKeyboardButton("IYA", callback_data="cb_delete"),
         InlineKeyboardButton("TIDAK", callback_data="start")]
    ]
    await callback_query.edit_message_text("Anda yakin ingin menghapus profil dan data Anda?", reply_markup=InlineKeyboardMarkup(buttons))

# Callback for deleting character
@KING.CALL("cb_delete")
async def delete_character(client, callback_query):
    user_id = callback_query.from_user.id
    character_profile = await get_character_profile(user_id)
    
    buttons = [[InlineKeyboardButton("BACK", callback_data="start")]]
    
    if character_profile:
        delete_result = await delete_character_profile(user_id)
        if delete_result:
            reply_text = "Karakter Anda telah dihapus."
        else:
            reply_text = "Maaf, terjadi kesalahan saat menghapus karakter Anda."
    else:
        reply_text = "Anda tidak memiliki karakter yang dapat dihapus."
    
    await callback_query.edit_message_text(reply_text, reply_markup=InlineKeyboardMarkup(buttons))
