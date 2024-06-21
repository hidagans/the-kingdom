from pyrogram import *
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from kingdom.core import *
from kingdom.database import *
from config import ADMINS
from kingdom.decorators import *

# Fungsi untuk menambahkan peta dan resource
@KING.CMD("add_map", FILTERS.OWNER)
async def add_map(client, message):
    if len(message.command) < 4:
        await message.reply_text("Contoh penggunaan /add_map <Zona> <Tier> <Type>")
        return
    
    location_name = message.chat.title
    zone = message.command[1]
    tier = int(message.command[2])
    map_type = message.command[3]
    group_id = message.chat.id
    url_grup = await client.export_chat_invite_link(group_id)
    
    # Cek apakah lokasi sudah ada
    existing_map = await maps.find_one({"location": group_id})
    if existing_map:
        await message.reply_text("Lokasi ini sudah ada.")
        return
    
    # Tambahkan lokasi baru ke database
    await maps.insert_one({"location": group_id, "name": location_name, "zona": zone, "tier": tier, "type": map_type, "link": url_grup})
    await message.reply_text(f"Lokasi '{location_name}' dengan ID {group_id} telah ditambahkan.")
    
    # Persentase resource berdasarkan tipe peta
    resource_percentages = {
        "Gurun": {"Ore": 0.3, "Fiber": 0.1, "Hide": 0.4},
        "Rawa": {"Kayu": 0.1, "Fiber": 0.3, "Hide": 0.3},
        "Pegunungan": {"Kayu": 0.1, "Ore": 0.3, "Stone": 0.4},
        "Hutan": {"Kayu": 0.4, "Stone": 0.1, "Hide": 0.3},
        "Salju": {"Ore": 0.4, "Fiber": 0.2, "Stone": 0.1}
    }
    
    if map_type in resource_percentages:
        percentages = resource_percentages[map_type]
        for resource_type, percentage in percentages.items():
            for resource_tier in range(max(1, tier - 2), tier + 1):
                material_info = await material.find_one({"type": resource_type, "Level": str(resource_tier)})
                
                if material_info:
                    resource_spot = {
                        "map_id": group_id,
                        "resource_type": resource_type,
                        "resource_name": material_info['name'],
                        "resource_tier": resource_tier,
                        "percentage": percentage,
                        "quantity": int(material_info['quantity'] * percentage),
                        "occupied_by": None  # Inisialisasi spot tidak ada yang menempati
                    }
                    await maps_resource.insert_one(resource_spot)
        await message.reply_text(f"Spot resource untuk '{location_name}' telah ditambahkan dengan persentase yang sesuai.")
    else:
        await message.reply_text(f"Type '{map_type}' tidak dikenali.")

# Fungsi untuk menambahkan spot pengumpulan
@KING.CMD("add_gathering_spot", FILTERS.OWNER)
async def add_gathering_spot_command(client, message):
    group_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("Penggunaan: /add_gathering_spot [resource_type]")
        return

    resource_type = message.command[1]
    
    # Cek tipe peta berdasarkan group_id
    map_data = await maps.find_one({"location": group_id})
    if not map_data:
        await message.reply_text("Lokasi tidak ditemukan.")
        return

    map_type = map_data.get("type")
    
    # Ambil resource yang sesuai dengan tipe peta dan resource_type
    resources = await maps_resource.find({"map_id": group_id, "resource_type": resource_type}).to_list(length=None)
    if not resources:
        await message.reply_text("Sumber daya tidak ditemukan. Pastikan tipe benar.")
        return
    
    for resource in resources:
        resource_name = resource["resource_name"]
        resource_tier = resource["resource_tier"]
        quantity = resource["quantity"]
        
        await maps.update_one(
            {"location": group_id},
            {"$push": {"spots": {"resource": f"{resource_name} Tier {resource_tier}", "quantity": quantity, "occupied_by": None}}},
            upsert=True
        )
    
    await message.reply_text(f"Spot pengumpulan untuk tipe '{resource_type}' berhasil ditambahkan di {map_data['name']}.")

@KING.CMD("show_maps")
async def show_maps(client, message):
    maps = await maps.find().to_list(length=None)
    if not maps:
        await message.reply_text("No map locations found.")
        return
    keyboard = create_map_list_inline_keyboard(maps)
    await message.reply_text("Here are the map locations:", reply_markup=keyboard)

@KING.CALL("maps")
async def mps(client, callback_query):
    maps = await maps.find().to_list(length=None)
    if not maps:
        await callback_query.reply_text("No map locations found.")
        return
    keyboard = create_map_list_inline_keyboard(maps)
    await callback_query.reply_text("Here are the map locations:", reply_markup=keyboard)

@KING.CALL(r"^location_")
async def on_location_callback(client, callback_query):
    location_id = int(callback_query.data.split("_")[1])
    map_entry = await maps.find_one({"location": location_id})
    
    if map_entry:
        await callback_query.edit_message_text(
            f"Details for location: {map_entry['name']} \nZona: {map_entry['zona']}\nType Map: {map_entry['type']}\n Link: {map_entry['link']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ZONE", callback_data=f"zone_{location_id}")],
                [InlineKeyboardButton("BACK", callback_data="show_maps")],
            ])
        )
    else:
        await callback_query.answer("Location not found.", show_alert=True)

# Callback handler for zone buttons
@KING.CALL(r"^zone_")
async def on_zone_callback(client, callback_query):
    user_id = callback_query.from_user.id
    location_id = int(callback_query.data.split("_")[1])
    zone_entry = await maps.find_one({"location": location_id})

    if zone_entry:
        await callback_query.edit_message_text(
            f"Details for zone: {zone_entry['name']}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("BACK", callback_data=f"location_{location_id}")]
            ])
        )
        
        # Update the character's location
        await characters.update_one(
            {"user_id": user_id}, 
            {"$set": {"location": location_id}}
        )
    else:
        await callback_query.answer("Zone not found.", show_alert=True)


# Handler to show the maps again when back is pressed
@KING.CALL("show_maps")
async def show_maps_callback(client, callback_query):
    maps = await maps.find().to_list(length=None)
    if not maps:
        await callback_query.message.edit_text("No map locations found.")
        return
    
    keyboard = create_map_list_inline_keyboard(maps)
    await callback_query.message.edit_text("Here are the map locations:", reply_markup=keyboard)

@KING.CMD("delete_maps", FILTERS.OWNER)
async def delete_maps(client, message):
    group_id = message.chat.id
    await maps.delete_one({"location": group_id})
    await message.reply_text("Location deleted successfully!")

@KING.CMD("add_royal", FILTERS.OWNER)
async def add_royal(client, message):
    location = message.chat.id
    link = await client.export_chat_invite_link(location)
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: /add_royal")
    
    zone_name = message.chat.title
    zone_entry = await maps.find_one({"location": location})
    if zone_entry:
        await message.reply_text("Location already exists!")
    
    zone_entry = {"location": location, "name": zone_name, "type": "Royal City","link":link, "description": "Royal Zone"}
    await maps.insert_one(zone_entry)

    await message.reply_text("Royal zone added successfully!")