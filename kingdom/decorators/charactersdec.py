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
            "type": item["type"],
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"],
            "damage": item["damage"],
            "defense": item["defense"],
            "magic_attack": item["magic_attack"],
            "attack_speed": item["attack_speed"],
            "armor_type": item["armor_type"]
        }
    
    if level_1_headarmor:
        item = level_1_headarmor[0]
        starting_items["headarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item["type"],
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"],
            "max_hp": item["max_hp"],
            "max_mana": item["max_mana"],
            "defense": item["defense"],
            "damage": item["damage"],
            "damage_increase": item["damage_increase"],
            "attack_speed": item["attack_speed"],
            "armor_type": item["armor_type"]
        }
    
    if level_1_bodyarmor:
        item = level_1_bodyarmor[0]
        starting_items["bodyarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item["type"],
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"],
            "max_hp": item["max_hp"],
            "max_mana": item["max_mana"],
            "defense": item["defense"],
            "damage": item["damage"],
            "damage_increase": item["damage_increase"],
            "attack_speed": item["attack_speed"],
            "armor_type": item["armor_type"]
        }
    
    if level_1_footarmor:
        item = level_1_footarmor[0]
        starting_items["footarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "type": item["type"],
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"],
            "max_hp": item["max_hp"],
            "max_mana": item["max_mana"],
            "defense": item["defense"],
            "damage": item["damage"],
            "damage_increase": item["damage_increase"],
            "attack_speed": item["attack_speed"],
            "armor_type": item["armor_type"]
        }
    
    # Perbarui equipment karakter dengan item awal
    await characters.update_one({"user_id": user_id}, {"$set": {"equipment": starting_items}})


