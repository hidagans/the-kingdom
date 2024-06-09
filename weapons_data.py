import pymongo
from config import MONGO_URL

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["weapons"]

# Data senjata
weapons_data = {
    'Sword': {
        0: {'name': 'Metal Sword', 'item_power': 0, 'damage': 28, 'defense': 0, 'magic_attack': 0, 'attack_speed': 0.02}
    },
    'Axe': {
        0: {'name': 'Iron Axe', 'item_power': 0, 'damage': 28, 'defense': 0, 'magic_attack': 0, 'attack_speed': 0.02}
    },
    'Bow': {
        0: {'name': 'Oak Bow', 'item_power': 0, 'damage': 35, 'defense': 0, 'magic_attack': 0, 'attack_speed': 0.02}
    },
    'Dagger': {
        0: {'name': 'Bronze Dagger', 'item_power': 0, 'damage': 25, 'defense': 0, 'magic_attack': 0, 'attack_speed': 0.04}
    },
    'Crossbow': {
        0: {'name': 'Steel Crossbow', 'item_power': 0, 'damage': 40, 'defense': 0, 'magic_attack': 0, 'attack_speed': 0}
    },
    'Mace': {
        0: {'name': 'Silver Mace', 'item_power': 0, 'damage': 15, 'max_hp': 35, 'defense': 34, 'magic_attack': 0, 'attack_speed': 0}
    }
}

# Simpan data senjata ke dalam database MongoDB
for weapon_type, tiers in weapons_data.items():
    for tier in range(1, 9):
        tier_str = str(tier)
        weapon_info = tiers[0]  # Gunakan stats dari tier 0 sebagai dasar
        # Tingkatkan stats berdasarkan tier
        weapon_info['item_power'] += 5 * tier
        weapon_info['damage'] += 2 * tier
        weapon_info['defense'] += 1 * tier
        weapon_info['attack_speed'] += 0.1 * tier

        # Buat dokumen untuk disimpan di database
        weapon_document = {
            "type": weapon_type,
            "name": f"{weapon_info['name']} Tier {tier_str}",
            "Level": tier_str,
            "item_power": weapon_info["item_power"],
            "damage": weapon_info["damage"],
            "defense": weapon_info["defense"],
            "magic_attack": weapon_info.get("magic_attack", 0),
            "attack_speed": weapon_info["attack_speed"],
            "armor_type": "weapons"
        }
        # Masukkan dokumen ke dalam koleksi weapons
        collection.insert_one(weapon_document)

print("Data WEAPONS telah disimpan di database MongoDB.")
