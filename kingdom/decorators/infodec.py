from pyrogram.types import *
from kingdom.database import *
from pyromod import listen
import logging

async def show_inventory(user_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Head Armor", callback_data="inventory:headarmor")],
        [InlineKeyboardButton("Body Armor", callback_data="inventory:bodyarmor")],
        [InlineKeyboardButton("Foot Armor", callback_data="inventory:footarmor")],
        [InlineKeyboardButton("Weapons", callback_data="inventory:weapons")],
        [InlineKeyboardButton("Back", callback_data="my_profile")]
    ])
    return "Pilih kategori item:", keyboard

async def show_items(user_id, item_type, start=0, limit=1):
    try:
        inventory_data = await get_user_inventory(user_id)

        if not inventory_data or item_type not in inventory_data:
            return "Tidak ada item dalam kategori ini.", None

        items = inventory_data[item_type]
        if start >= len(items):
            return "Tidak ada item berikutnya.", None

        end = min(start + limit, len(items))
        keyboard = []

        for item in items[start:end]:
            item_buttons = []
            for action in ["use", "sell", "trash"]:
                callback_data = f"{action}:{item_type}:{item['name']}"
                item_buttons.append(InlineKeyboardButton(f"{action.capitalize()}", callback_data=callback_data))
            keyboard.append(item_buttons)

        navigation_buttons = []
        if end < len(items):
            navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"inventory:{item_type}:{end}"))
        navigation_buttons.append(InlineKeyboardButton("Back", callback_data="cb_inventory"))
        keyboard.append(navigation_buttons)

        return f"{item['name']}", InlineKeyboardMarkup(keyboard)
    except Exception as e:
        print(f"Error in show_items: {e}")
        return "Terjadi kesalahan dalam menampilkan item.", None

async def use_item(user_id, item_type, item_name):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })
            item_to_use = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_use:
                item_type = item_to_use.get("armor_type", "")
                if item_type in equipment:
                    equipment[item_type] = item_to_use
                    inventory.remove(item_to_use)
                    await characters.update_one(
                        {"user_id": user_id},
                        {"$set": {"inventory": inventory, "equipment": equipment}}
                    )
                    return f"{item_name} telah digunakan sebagai {item_type}."
                else:
                    return f"Tipe item {item_type} tidak dikenali."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in use_item: {e}")
        return "Terjadi kesalahan saat mencoba menggunakan item."
 

async def trash_item(user_id, item_type, item_name):
    try:
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            item_to_trash = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_trash:
                inventory.remove(item_to_trash)

                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory}}
                )
                return f"Item {item_name} telah dibuang."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in trash_item: {e}")
        return "Terjadi kesalahan saat mencoba membuang item."


async def show_equipment(user_id):
    try:
        equipment_data = await get_user_equipment(user_id)

        if not equipment_data:
            return "Equipment kamu kosong."

        equipment_message = "Equipment kamu:\n"
        for item_type, item_list in equipment_data.items():
            equipment_message += f"- {item_type.capitalize()}:\n"
            for item in item_list:
                equipment_message += f"  • {item['name']} (Level {item['Level']})\n"

        return equipment_message
    except Exception as e:
        print(f"Error in show_equipment: {e}")
        return "Terjadi kesalahan dalam menampilkan equipment."
    
async def equip_item(user_id, item_name):
    try:
        # Ambil data karakter dari MongoDB berdasarkan user_id
        character = await characters.find_one({"user_id": user_id})

        # Periksa apakah karakter ditemukan
        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })

            # Temukan item di inventory
            item_to_equip = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_equip:
                item_type = item_to_equip.get("armor_type", "")
                if item_type in equipment:
                    # Equip item
                    equipment[item_type] = item_to_equip

                    # Hapus item dari inventory
                    inventory.remove(item_to_equip)

                    # Perbarui data karakter di MongoDB
                    await characters.update_one(
                        {"user_id": user_id},
                        {"$set": {"inventory": inventory, "equipment": equipment}}
                    )
                    return f"{item_name} telah dipakai sebagai {item_type}."
                else:
                    return f"Tipe item {item_type} tidak dikenali."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in equip_item: {e}")
        return "Terjadi kesalahan saat mencoba memakai item."
    
async def unequip_item(user_id, item_type):
    try:
        # Ambil data karakter dari MongoDB berdasarkan user_id
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })

            # Temukan item di equipment
            item_to_unequip = equipment.get(item_type, None)

            if item_to_unequip:
                # Pindahkan item ke inventory
                inventory.append(item_to_unequip)

                # Hapus item dari equipment
                equipment[item_type] = None

                # Perbarui data karakter di MongoDB
                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory, "equipment": equipment}}
                )
                return f"{item_to_unequip['name']} telah dilepas dari {item_type}."
            else:
                return f"Tidak ada item yang dipakai di slot {item_type}."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in unequip_item: {e}")
        return "Terjadi kesalahan saat mencoba melepas item."

async def get_user_inventory(user_id):
    try:
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            inventory_data = {"headarmor": [], "bodyarmor": [], "footarmor": [], "weapons": []}

            for item in inventory:
                item_type = item.get("armor_type", "weapons")
                if item_type in inventory_data:
                    inventory_data[item_type].append(item)

            return inventory_data
        else:
            return {}
    except Exception as e:
        print(f"Error in get_user_inventory: {e}")
        return {}

    
async def get_user_equipment(user_id):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })
            equipment_data = {"headarmor": [], "bodyarmor": [], "footarmor": [], "weapons": []}

            # Kelompokkan item berdasarkan tipe
            for item_type, item in equipment.items():
                if item:
                    equipment_data[item_type].append(item)

            return equipment_data
        else:
            return {}
    except Exception as e:
        print(f"Error in get_user_equipment: {e}")
        return {}
    
async def calculate_total_stats(user_id):
    try:
        # Ambil data karakter dari MongoDB berdasarkan user_id
        character = await characters.find_one({"user_id": user_id})

        if character:
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })

            total_stats = {}

            # Jumlahkan semua statistik dari setiap item di equipment
            for item in equipment.values():
                if item:
                    for stat, value in item.items():
                        if stat not in ["_id", "type", "name", "Level", "armor_type"]:
                            if stat in total_stats:
                                total_stats[stat] += value
                            else:
                                total_stats[stat] = value

            # Perbarui total stats di dalam karakter
            await characters.update_one(
                {"user_id": user_id},
                {"$set": {"stats": total_stats}}
            )

            # Buat pesan hasil
            response_message = "Total stats kamu sekarang adalah:\n"
            for stat, value in total_stats.items():
                response_message += f"{stat.capitalize()}: {value}\n"

            return response_message
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in calculate_total_stats: {e}")
        return "Terjadi kesalahan saat menghitung total stats."