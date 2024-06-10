import pymongo
from config import MONGO_URL

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["bodyarmors"]

bodyarmor_data = {
    'Leather Jacket': {
        0: {'name': 'Acolyte Jacket', 'item_power': 0, 'max_hp': 10, 'max_mana': 5, 'defense': 3, 'damage': 0, 'damage_increase': 0.04, 'attack_speed': 0}
    },
    'Steel Plate': {
        0: {'name': 'Guardian Plate', 'item_power': 0, 'max_hp': 25, 'max_mana': 40, 'defense': 30, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Healer\'s Robe': {
        0: {'name': 'Healer\'s Robe', 'item_power': 0, 'max_hp': 5, 'max_mana': 15, 'defense': 2, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Sorcerer\'s Robe': {
        0: {'name': 'Mage\'s Robe', 'item_power': 0, 'max_hp': 5, 'max_mana': 20, 'defense': 2, 'damage': 0, 'damage_increase': 0.08, 'attack_speed': 0}
    },
    'Warrior\'s Armor': {
        0: {'name': 'Warrior\'s Armor', 'item_power': 0, 'max_hp': 15, 'max_mana': 0, 'defense': 4, 'damage': 0, 'damage_increase': 0.04, 'attack_speed': 0}
    },
    'Ranger\'s Tunic': {
        0: {'name': 'Ranger\'s Tunic', 'item_power': 0, 'max_hp': 10, 'max_mana': 10, 'defense': 3, 'damage': 0, 'damage_increase': 0.04, 'attack_speed': 10}
    }
}

# Simpan data armor ke dalam database MongoDB
for equipment_type, tiers in bodyarmor_data.items():
    for tier in range(1, 9):
        tier_str = str(tier)
        equipment_info = tiers[0]  # Gunakan stats dari tier 0 sebagai dasar
        # Tingkatkan stats berdasarkan tier
        equipment_info['item_power'] += 5 * tier
        equipment_info['max_hp'] += 8 * tier
        equipment_info['max_mana'] += 4 * tier
        equipment_info['defense'] += 3 * tier
        equipment_info['damage'] += 2 * tier
        equipment_info['damage_increase'] += 0.005 * tier
        equipment_info['attack_speed'] += 0.02 * tier

        # Buat dokumen untuk disimpan di database
        armor_document = {
            "type": equipment_type,
            "name": f"{equipment_info['name']} Tier {tier_str}",
            "Level": tier_str,
            "item_power": equipment_info["item_power"],
            "max_hp": equipment_info["max_hp"],
            "max_mana": equipment_info["max_mana"],
            "defense": equipment_info["defense"],
            "damage": equipment_info["damage"],
            "damage_increase": equipment_info["damage_increase"],
            "attack_speed": equipment_info["attack_speed"],
            "armor_type": "bodyarmor"  # Menambahkan informasi jenis armor
        }
        # Masukkan dokumen ke dalam koleksi armor
        collection.insert_one(armor_document)

print("Data BODY ARMOR telah disimpan di database MongoDB.")
