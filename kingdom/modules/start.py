import asyncio

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from kingdom.database import add_served_user
from kingdom.core import KINGDOM, FILTERS, subscribe


@KINGDOM.CMD("start", FILTERS.PRIVATE)
@subcribe
async def start(client, message):
    user_id = message.from_user.id
    await add_served_user(user_id)
    #character_profile = await get_character_profile(user_id)
    home_button = [
        [
             InlineKeyboardButton("MY PROFILE", callback_data="my_profile"),
             InlineKeyboardButton("KONTEN", callback_data="cb_konten")
        ],
        [
            InlineKeyboardButton("BLACK MARKET", callback_data="black_market"),
        ]
    ]
    await message.reply("Selamat datang kembali! Ini profil Anda:", reply_markup=InlineKeyboardMarkup(home_button))
  
  
