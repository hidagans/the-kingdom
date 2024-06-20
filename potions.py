import pymongo
from config import MONGO_URL

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["potions"]

potion_data = {
    'Regen HP': {
        0: {'name': 'Minor Healing Potion', 'item_power': 0, 'regen_hp': 5, 'duration': 1}
    }
}

# Meningkatkan stats sesuai dengan tier
for potion_type, tiers in potion_data.items():
    for tier in range(1, 9):
        tier_str = str(tier)
        potion_info = tiers[0]  # Gunakan stats dari tier 0 sebagai dasar
        # Tingkatkan stats berdasarkan tier
        potion_info['item_power'] += 5 * tier
        potion_info['regen_hp'] += 10 * tier
        potion_info['duration'] += 1 * tier

        # Buat dokumen untuk disimpan di database
        potion_document = {
            "type": potion_type,
            "name": f"{potion_info['name']} Tier {tier_str}",
            "Level": tier_str,
            "item_power": potion_info["item_power"],
            "regen_hp": potion_info["regen_hp"],
            "duration": potion_info["duration"],
            "potion_type": "Regen HP"
        }
        # Masukkan dokumen ke dalam koleksi potions
        collection.insert_one(potion_document)

print("Data POTIONS telah disimpan di database MongoDB.")
