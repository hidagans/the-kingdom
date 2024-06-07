from datetime import datetime, timedelta
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from kingdom import bot
from kingdom.database import *
import asyncio
from config import ADMINS

@bot.on_callback_query(filters.regex("cb_gathering_konten"))
async def cb_gathering_konten(client, callback_query):
    buttons = [
        [InlineKeyboardButton("SHOW RESOURCE", callback_data="show_resource")]
    ]
    await callback_query.edit_message_text("Show resource untuk melihat sumber daya yang tersedia di lokasi ini", reply_markup=InlineKeyboardMarkup(buttons))

@bot.on_callback_query(filters.regex(r"start_gathering:(.+)"))
async def gathering_konten(client, callback_query):
    location = callback_query.data.split(":")[1]
    spots = await show_gathering_spots(location)
    if not spots:
        await callback_query.answer("Tidak ada gathering spot yang ditemukan!", show_alert=True)
        return

    buttons = [
        [
            InlineKeyboardButton(
                f"{spot['resource']} {spot['quantity']}",
                callback_data=f"gather:{i}:{spot['resource']}:{spot['quantity']}"
            )
            for i, spot in enumerate(spots)
        ],
        [InlineKeyboardButton("BACK", callback_data="cb_konten")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    reply_text = "Pilih gathering spot yang ingin Anda kumpulkan:"
    await callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

@bot.on_callback_query(filters.regex(r"gather:(.+)"))
async def gather_action_callback(client, callback_query):
    data = callback_query.data.split(":")
    spot_index = int(data[1])
    resource = data[2]
    quantity = int(data[3])
    user_id = callback_query.from_user.id

    if await is_gathering(user_id):
        await callback_query.answer("Anda sedang dalam proses gathering. Silakan tunggu hingga selesai.", show_alert=True)
        return

    map_data = await maps.find_one({"location": callback_query.message.chat.id})
    if not map_data or spot_index >= len(map_data["spots"]):
        await callback_query.answer("Sumber daya tidak mencukupi di gathering spot ini.", show_alert=True)
        return

    spot = map_data["spots"][spot_index]
    if spot["quantity"] < quantity:
        await callback_query.answer("Sumber daya tidak mencukupi di gathering spot ini.", show_alert=True)
        return

    await callback_query.answer("Memulai gathering...")

    end_time = datetime.now() + timedelta(minutes=5)  # Gathering process takes 5 minutes
    await start_gathering(user_id, end_time, resource, quantity)
    map_data["spots"][spot_index]["quantity"] -= quantity
    await maps.update_one({"location": callback_query.message.chat.id}, {"$set": {"spots": map_data["spots"]}})

    await callback_query.message.reply_text(f"Gathering dimulai! Estimasi selesai: {end_time.strftime('%H:%M:%S')}")

    # Wait until gathering is complete
    await asyncio.sleep(5 * 60)  # 5 minutes in seconds

    resource, quantity = await complete_gathering(user_id)
    if resource and quantity:
        await bot.send_message(user_id, f"Gathering selesai! Anda mendapatkan {quantity} {resource}.")
        await callback_query.message.reply_text(f"Gathering selesai! Anda mendapatkan {quantity} {resource}.")
    else:
        await callback_query.message.reply_text("Terjadi kesalahan saat menyelesaikan gathering.")

@bot.on_callback_query(filters.regex("show_resource"))
async def show_gathering_spots_command(client, callback_query):
    location = callback_query.message.chat.id
    map_data = await maps.find_one({"location": location})
    
    if map_data:
        spots = map_data.get("spots", [])
        location_name = map_data.get("name", "Unknown Location")
        location_link = map_data.get("link", "")

        if spots:
            buttons = [
                [InlineKeyboardButton(f"{spot['resource']} {spot['quantity']}", callback_data=f"gather:{i}:{spot['resource']}:{spot['quantity']}")]
                for i, spot in enumerate(spots)
            ]
            buttons.append([InlineKeyboardButton("BACK", callback_data="cb_konten")])
            reply_markup = InlineKeyboardMarkup(buttons)
            response_message = f"Gathering spot di lokasi {location_name}:\n"
            if location_link:
                response_message += f"[{location_name}]({location_link})\n"
            for i, spot in enumerate(spots):
                resource = spot["resource"]
                quantity = spot["quantity"]
                response_message += f"ID: {i} Resource: {resource}, Quantity: {quantity}\n"
        else:
            response_message = "Grup ini tidak memiliki sumber daya yang tersedia."
            reply_markup = None
    else:
        response_message = "Lokasi tidak ditemukan."
        reply_markup = None

    await callback_query.edit_message_text(response_message, reply_markup=reply_markup)

# Fungsi untuk respawn sumber daya
async def respawn_resources():
    while True:
        maps = await maps.find().to_list(length=None)
        material_data = await material.find().to_list(length=None)
        quantity_items = {material['name']: material['quantity'] for material in material_data}
        
        for map_data in maps:
            for spot in map_data.get("spots", []):
                max_quantity = quantity_items.get(spot['resource'], spot.get('max_quantity', 10))  # Assume a default max quantity
                if spot['quantity'] < max_quantity:
                    # Determine respawn rate based on tier
                    resource_tier = spot.get('tier', 1)
                    respawn_time = RESPAWN_TIMES.get(resource_tier, timedelta(minutes=10))
                    last_gathered_time = spot.get('last_gathered_time', datetime.min)

                    if datetime.now() >= last_gathered_time + respawn_time:
                        spot['quantity'] = min(spot['quantity'] + 1, max_quantity)
                        spot['last_gathered_time'] = datetime.now()
                        
            await maps.update_one({"_id": map_data["_id"]}, {"$set": {"spots": map_data["spots"]}})
        
        await asyncio.sleep(60)  # Check every minute

asyncio.create_task(respawn_resources())