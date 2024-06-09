import pymongo
from config import MONGO_URL

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["headarmor"]

headarmor_data = {
    'Leather Hood': {
        0: {'name': 'Acolyte Hood', 'item_power': 0, 'max_hp': 10, 'max_mana': 5, 'defense': 2, 'damage': 0, 'damage_increase': 0.04, 'attack_speed': 0}
    },
    'Plate Helm': {
        0: {'name': 'Guardian Helm', 'item_power': 0, 'max_hp': 20, 'max_mana': 0, 'defense': 5, 'damage': 0,'damage_increase': 0.00, 'attack_speed': 0}
    },
    'Wizard Hat': {
        0: {'name': 'Mage Hat', 'item_power': 0, 'max_hp': 5, 'max_mana': 30, 'defense': 1, 'damage': 0,'damage_increase': 0.08, 'attack_speed': 0}
    },
    'Helmet of the Brave': {
        0: {'name': 'Warrior\'s Helmet', 'item_power': 0, 'max_hp': 15, 'max_mana': 0, 'defense': 3, 'damage': 0,'damage_increase': 0.02, 'attack_speed': 0}
    },
    'Hunter\'s Cap': {
        0: {'name': 'Ranger Cap', 'item_power': 0, 'max_hp': 10, 'max_mana': 10, 'defense': 2, 'damage': 0,'damage_increase': 0.04, 'attack_speed': 20}
    }
}

# Meningkatkan stats sesuai dengan tier
for equipment_type, tiers in headarmor_data.items():
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
            "armor_type": "headarmor"
        }
        # Masukkan dokumen ke dalam koleksi headarmor
        collection.insert_one(equipment_document)

print("Data HEAD ARMOR telah disimpan di database MongoDB.")
