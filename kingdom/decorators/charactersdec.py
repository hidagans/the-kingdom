from kingdom.database import *
from bson.objectid import ObjectId

async def give_starting_items(user_id):
    # Ambil item dengan level 1 dari masing-masing koleksi
    level_1_weapons = await weapons.find({"Level": "1"}).to_list(None)
    level_1_headarmor = await headarmors.find({"Level": "1"}).to_list(None)
    level_1_bodyarmor = await bodyarmors.find({"Level": "1"}).to_list(None)
    level_1_footarmor = await footarmors.find({"Level": "1"}).to_list(None)
    
    # Simpan item awal karakter ke dalam starting_items
    starting_items = {
        "weapons": None,
        "headarmor": None,
        "bodyarmor": None,
        "footarmor": None
    }
    
    # Pilih satu item dari setiap kategori dan tambahkan ke starting_items
    if level_1_weapons:
        item = level_1_weapons[0]
        starting_items["weapons"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item.get("type"),
            "name": item.get("name"),
            "Level": item.get("Level"),
            "item_power": item.get("item_power"),
            "damage": item.get("damage"),
            "defense": item.get("defense"),
            "magic_attack": item.get("magic_attack"),
            "attack_speed": item.get("attack_speed"),
            "armor_type": item.get("armor_type")
        }
    
    if level_1_headarmor:
        item = level_1_headarmor[0]
        starting_items["headarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item.get("type"),
            "name": item.get("name"),
            "Level": item.get("Level"),
            "item_power": item.get("item_power"),
            "damage": item.get("damage"),
            "defense": item.get("defense"),
            "magic_attack": item.get("magic_attack"),
            "attack_speed": item.get("attack_speed"),
            "armor_type": item.get("armor_type")
        }
    
    if level_1_bodyarmor:
        item = level_1_bodyarmor[0]
        starting_items["bodyarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item.get("type"),
            "name": item.get("name"),
            "Level": item.get("Level"),
            "item_power": item.get("item_power"),
            "damage": item.get("damage"),
            "defense": item.get("defense"),
            "magic_attack": item.get("magic_attack"),
            "attack_speed": item.get("attack_speed"),
            "armor_type": item.get("armor_type")
        }
    
    if level_1_footarmor:
        item = level_1_footarmor[0]
        starting_items["footarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item.get("type"),
            "name": item.get("name"),
            "Level": item.get("Level"),
            "item_power": item.get("item_power"),
            "damage": item.get("damage"),
            "defense": item.get("defense"),
            "magic_attack": item.get("magic_attack"),
            "attack_speed": item.get("attack_speed"),
            "armor_type": item.get("armor_type")
        }
    
    # Perbarui equipment karakter dengan item awal
    await characters.update_one({"user_id": user_id}, {"$set": {"equipment": starting_items}})

