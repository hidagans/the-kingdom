from pyrogram import filters
from pyrogram.types import *
from kingdom import bot
from kingdom.core import KING, FILTERS
from kingdom.database import *

@KING.CALL("cb_token")
async def show_token(client, callback_query):
    user_id = callback_query.from_user.id
    character_profile = await get_character_profile(user_id)
    token = character_profile['tokentol']
    buttons = [
        [
            InlineKeyboardButton("CREATE TOKEN", callback_data="cb_create_token"),
            InlineKeyboardButton("UPDATE TOKEN", callback_data="cb_update_token")
        ],
        [
            InlineKeyboardButton("DELETE TOKEN", callback_data="cb_delete_token"),
            InlineKeyboardButton("BACK", callback_data="my_profile")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    if token:
        await callback_query.edit_message_text(token, reply_markup=reply_markup)
    
    if not token: 
        await callback_query.edit_message_text("kamu tidak punya token silahkan buat terlebih dahulu.", reply_markup=reply_markup)
# Fungsi handler untuk perintah /create_token
@KING.CALL("create_token")
async def create_token_handler(client, callback_query):
    user_id = callback_query.from_user.id
    new_token = await create_token(user_id)
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="my_profile"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_text(f"Token baru Anda: {new_token}", reply_markup=reply_markup)

# Fungsi handler untuk perintah /delete_token
@KING.CALL("cb_delete_token")
async def delete_token_handler(client, callback_query):
    user_id = callback_query.from_user.id
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="my_profile"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    if delete_token(user_id):
        await callback_query.edit_message_text("Token Anda berhasil dihapus.", reply_markup=reply_markup)
    else:
        await callback_query.edit_message_text("Anda tidak memiliki token untuk dihapus.", reply_markup=reply_markup)

# Fungsi handler untuk perintah /update_token
@KING.CALL("cb_update_token")
async def update_token_handler(client, callback_query):
    user_id = callback_query.from_user.id
    updated_token = update_token(user_id)
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="my_profile"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    if updated_token:
        await callback_query.edit_message_text(f"Token Anda berhasil diupdate menjadi: {updated_token}", reply_markup=reply_markup)
    else:
        await callback_query.edit_message_text("Anda tidak memiliki token untuk diupdate.", reply_markup=reply_markup)
