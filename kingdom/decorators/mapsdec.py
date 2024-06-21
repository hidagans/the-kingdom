from pyrogram.types import *
import asyncio
from kingdom.database import maps as map_collection, material
from datetime import timedelta, datetime

# Waktu respawn untuk setiap tier
RESPAWN_TIMES = {
    1: timedelta(minutes=3),  # Tier 1: 2-5 menit
    2: timedelta(minutes=3),  # Tier 2: 2-5 menit
    3: timedelta(minutes=15), # Tier 3: 10-20 menit
    4: timedelta(minutes=15), # Tier 4: 10-20 menit
    5: timedelta(minutes=45), # Tier 5: 30-60 menit
    6: timedelta(minutes=45), # Tier 6: 30-60 menit
    7: timedelta(hours=2.5),  # Tier 7: 2-3 jam
    8: timedelta(hours=7)     # Tier 8: 6-8 jam
}

def create_map_list_inline_keyboard(maps):
    keyboard = []
    for map_entry in maps:
        button = InlineKeyboardButton(f"Location: {map_entry['name']}", callback_data=f"location_{map_entry['location']}")
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("BACK", callback_data="start")])
    return InlineKeyboardMarkup(keyboard)

async def respawn_resources():
    while True:
        maps = await map_collection.find().to_list(length=None)  # Fetch the map data from the collection
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
                        
            await map_collection.update_one({"_id": map_data["_id"]}, {"$set": {"spots": map_data["spots"]}})
        
        await asyncio.sleep(60)  # Check every minute

asyncio.create_task(respawn_resources())
