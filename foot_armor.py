import pymongo
from config import MONGO_URL

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["footarmor"]

footarmor_data = {
    'Leather Shoes': {
        0: {'name': 'Acolyte Shoes', 'item_power': 0, 'max_hp': 5, 'max_mana': 2, 'defense': 1, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Steel Boots': {
        0: {'name': 'Guardian Boots', 'item_power': 0, 'max_hp': 15, 'max_mana': 20, 'defense': 10, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Sorcerer\'s Slippers': {
        0: {'name': 'Mage\'s Slippers', 'item_power': 0, 'max_hp': 2, 'max_mana': 15, 'defense': 1, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Warrior\'s Greaves': {
        0: {'name': 'Warrior\'s Greaves', 'item_power': 0, 'max_hp': 7, 'max_mana': 5, 'defense': 2, 'damage': 0, 'damage_increase': 0, 'attack_speed': 0}
    },
    'Ranger\'s Boots': {
        0: {'name': 'Ranger\'s Boots', 'item_power': 0, 'max_hp': 5, 'max_mana': 5, 'defense': 1, 'damage': 0, 'damage_increase': 0, 'attack_speed': 10}
    }
}

# Meningkatkan stats sesuai dengan tier
for equipment_type, tiers in footarmor_data.items():
    for tier in range(1, 9):
        tier_str = str(tier)
        equipment_info = tiers[0]  # Gunakan stats dari tier 0 sebagai dasar
        # Tingkatkan stats berdasarkan tier
        equipment_info['item_power'] += 5 * tier
        equipment_info['max_hp'] += 10 * tier
        equipment_info['max_mana'] += 5 * tier
        equipment_info['defense'] += 2 * tier
        equipment_info['damage_increase'] += 0.01 * tier
        equipment_info['attack_speed'] += 5 * tier

        # Buat dokumen untuk disimpan di database
        equipment_document = {
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
            "armor_type": "footarmor"
        }
        # Masukkan dokumen ke dalam koleksi footarmor
        collection.insert_one(equipment_document)

print("Data FOOT ARMOR telah disimpan di database MongoDB.")
