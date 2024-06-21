from kingdom.core import *
from kingdom.database import *
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random
import asyncio

@KING.CALL("black_market")
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

# Fungsi untuk mendapatkan daftar item dari Black Market
async def get_blackmarket_items():
    try:
        cursor = blackmarket_items.find({})
        item_list = []
        
        async for item in cursor:
            item_name = item["name"]
            item_price = item["price"]
            item_button = InlineKeyboardButton(f"Sell {item_name} ({item_price} Silver)", callback_data=f"sell_item_{item['name']}")
            item_list.append([item_button])
        
        return item_list
    
    except Exception as e:
        print(f"Error in get_blackmarket_items: {e}")
        return []

@bot.on_message(filters.command("blackmarket_items") & filters.user(ADMINS))
async def blackmarket_items_command(client, message):
    try:
        item_list = await get_blackmarket_items()
        if item_list:
            for item in item_list:
                item_name = item[0].text.split(' ')[1]  # Extract item name from button text
                reply_markup = InlineKeyboardMarkup([item])
                await bot.send_message(-1002074292027, f"Item: {item_name}", message_thread_id=32, reply_markup=reply_markup)
                await asyncio.sleep(5)  # Tambahkan jeda 5 detik
        else:
            await message.reply_text("Tidak ada item yang tersedia di Black Market saat ini.")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text("Terjadi kesalahan dalam memuat daftar item Black Market.")

@KING.CALL(r"^sell_item_")
async def sell_item_callback(client, callback_query):
    try:
        item_name = callback_query.data.split("_", 2)[2]  # Ambil nama item dari callback_data
        user_id = callback_query.from_user.id
        
        # Ambil data karakter dan inventory
        character = await characters.find_one({"user_id": user_id})
        if not character:
            await callback_query.answer("Karakter tidak ditemukan.")
            return
        
        inventory = character.get("inventory", [])
        item_to_sell = next((item for item in inventory if item['name'].lower() == item_name.lower()), None)
        
        if not item_to_sell:
            await callback_query.answer(f"Anda tidak memiliki item '{item_name}' di inventory.")
            return
        
        # Mendapatkan harga dari item di blackmarket
        black_market_item = await blackmarket_items.find_one({"name": item_name})
        if not black_market_item:
            await callback_query.answer("Item tidak ditemukan di black market.")
            return
        
        price = black_market_item["price"]
        
        # Menghapus item dari inventory
        inventory.remove(item_to_sell)
        
        # Update inventory karakter di database
        await characters.update_one(
            {"user_id": user_id},
            {"$set": {"inventory": inventory}}
        )
        
        # Menambahkan silver ke karakter
        current_silver = character.get("currency", {}).get("silver", 0)
        new_silver = current_silver + price
        await characters.update_one(
            {"user_id": user_id},
            {"$set": {"currency.silver": new_silver}}
        )
        
        # Menambahkan item ke dalam reward dungeon
        await add_item_to_black_market(item_to_sell)
        
        await callback_query.answer(f"Item '{item_name}' berhasil dijual seharga {price} Silver.")
    
    except Exception as e:
        print(f"Error: {e}")
        await callback_query.answer("Terjadi kesalahan saat menjual item.")



@KING.CALL("travel_to_nightshade")
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
