from kingdom.database import *
from bson.objectid import ObjectId

# Fungsi untuk menyimpan item karakter ke database
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
    
    # Iterasi melalui item dengan level 1 dan tambahkan ke starting_items
    for item in level_1_weapons:
        starting_items["weapons"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"]
        }
    for item in level_1_headarmor:
        starting_items["headarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"]
        }
    for item in level_1_bodyarmor:
        starting_items["bodyarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"]
        }
    for item in level_1_footarmor:
        starting_items["footarmor"] = {
            "_id": ObjectId(),  # Tambahkan ObjectId baru
            "name": item["name"],
            "Level": item["Level"],
            "item_power": item["item_power"]
        }
    
    # Perbarui equipment karakter dengan item awal
    await characters.update_one({"user_id": user_id}, {"$set": {"equipment": starting_items}})
