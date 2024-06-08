from pyrogram.types import *
import asyncio
from kingdom.database import *
def create_map_list_inline_keyboard(maps):
    keyboard = []
    for map_entry in maps:
        button = InlineKeyboardButton(f"Location: {map_entry['name']}", callback_data=f"location_{map_entry['location']}")
        keyboard.append([button])
    keyboard.append([InlineKeyboardButton("BACK", callback_data="start")])
    return InlineKeyboardMarkup(keyboard)

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