import pymongo
import random
from datetime import datetime, timedelta
from config import MONGO_URL

# Koneksi ke MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client["kingdom"]
collection = db["blackmarket_items"]

# Daftar jenis item yang ingin dimasukkan
item_collections = {
    "weapon": db.weapons,
    "bodyarmor": db.bodyarmors,
    "headarmor": db.headarmors,
    "footarmor": db.footarmors
}

tiers = range(2, 9)  # Tier dari 2 hingga 8

# Fungsi untuk menghasilkan harga berdasarkan tier
def generate_price(tier):
    return random.randint(tier * 500, tier * 1000)

# Memasukkan item ke dalam koleksi blackmarket_items
for item_type, item_collection in item_collections.items():
    for item in item_collection.find():
        for tier in tiers:
            item_name = f"{item_type.capitalize()} {item['name']} Tier {tier}"
            price = generate_price(tier)
            update_time = datetime.utcnow() - timedelta(days=(tier - 1))  # Update harga semakin lama seiring naiknya tier

            new_item = {
                "name": item_name,
                "type": item_type,
                "tier": tier,
                "price": price,
                "update_time": update_time
            }

            collection.insert_one(new_item)

print("Data Black Market telah berhasil diisi.")