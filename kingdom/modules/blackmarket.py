from kingdom.core import *
from kingdom.database import *
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random

@KING.CALLBACK("black_market")
async def black_market(client, callback_query):
    user_id = callback_query.from_user.id
    character = await get_character_profile(user_id)
    black_market = -1002074292027
    
    if not character or character.get("location") != black_market:
        travel_to_nightshade_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Travel To Nightshade", callback_data="travel_to_nightshade")],
            [InlineKeyboardButton("BACK", callback_data="start")]
        ])
        await callback_query.message.reply_text("Anda harus berada di Nightshade City untuk mengakses Black Market.", reply_markup=travel_to_nightshade_markup)
        return

    black_market_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 Black Market", callback_data="black_market_menu")],
        [InlineKeyboardButton("BACK", callback_data="start")]
    ])
    
    await callback_query.edit_message_text("Black Market", reply_markup=black_market_markup)

@KING.CALLBACK("black_market_menu")
async def black_market_menu(client, callback_query):
    location = -1002074292027
    map_data = await get_maps(location)
    
    black_market_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Sell Item", callback_data="sell_item")],
        [InlineKeyboardButton("BACK", callback_data="start")]
    ])
    
    if map_data:
        await callback_query.edit_message_text("Welcome to the Black Market!", reply_markup=black_market_markup)
    else:
        back_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Go To Location", callback_data="travel_to_nightshade")],
            [InlineKeyboardButton("BACK", callback_data="start")]
        ])
        await callback_query.edit_message_text("You are not in the correct location.", reply_markup=back_markup)

@KING.CMD("sell_item")
async def sell_item(client, message):
    try:
        command_parts = message.text.split(' ', 1)
        if len(command_parts) != 2:
            await message.reply_text("Gunakan: /sell_item <nama_item>")
            return

        item_name = command_parts[1]
        
        character = await characters.find_one({"user_id": message.from_user.id})
        if not character:
            await message.reply_text("Karakter tidak ditemukan.")
            return

        inventory = characters.get("inventory", [])
        item_to_sell = next((item for item in inventory if item['name'].lower() == item_name.lower()), None)

        if not item_to_sell:
            await message.reply_text(f"Anda tidak memiliki item '{item_name}' di inventory.")
            return

        item_price = item_to_sell.get("price", 100)

        inventory.remove(item_to_sell)

        await characters.update_one(
            {"user_id": message.from_user.id},
            {"$set": {"inventory": inventory}}
        )

        await black_market.insert_one(item_to_sell)

        gold = character.get("gold", 0) + item_price
        await characters.update_one(
            {"user_id": message.from_user.id},
            {"$set": {"gold": gold}}
        )

        await message.reply_text(f"Item '{item_name}' berhasil dijual seharga {item_price} koin emas.")
    except Exception as e:
        print(f"Error in sell_item: {e}")
        await message.reply_text("Terjadi kesalahan saat menjual item.")

@KING.CALLBACK("travel_to_nightshade")
async def travel_to_nightshade(client, callback_query):
    user_id = callback_query.from_user.id
    character = await get_character_profile(user_id)
    starting = await maps.find_one({"type": "Royal City"})
    black_market = -1002074292027

    if not character:
        await callback_query.message.reply_text("Karakter tidak ditemukan.")
        return
    
    if character.get("location") != starting.get("location"):
        await callback_query.message.reply_text("Anda hanya bisa memulai perjalanan ke Nightshade City dari Starting City.")
        return

    success_chance = 0.7  
    if random.random() < success_chance:
        await characters.update_one(
            {"user_id": user_id},
            {"$set": {"location": black_market}}
        )
        await callback_query.message.reply_text("Anda berhasil melewati Red Zone dan tiba di Nightshade City.")
    else:
        # Perjalanan gagal
        await callback_query.message.reply_text("Anda gagal melewati Red Zone. Coba lagi nanti.")

    travel_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Coba Lagi", callback_data="travel_to_nightshade")],
        [InlineKeyboardButton("BACK", callback_data="start")]
    ])
    
    await callback_query.message.edit_reply_markup(reply_markup=travel_markup)