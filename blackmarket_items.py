import pymongo
import random
from datetime import datetime, timedelta
from config import MONGO_URL

# Koneksi ke MongoDB
client = pymongo.MongoClient(MONGO_URL)
db = client["kingdom"]
collection = db["blackmarket_items"]

# Daftar jenis item dan tier yang ingin dimasukkan
item_types = ["weapon", "headarmor", "bodyarmor", "footarmor"]
tiers = range(2, 9)  # Tier dari 2 hingga 8

# Fungsi untuk menghasilkan harga berdasarkan tier
def generate_price(tier):
    return random.randint(tier * 500, tier * 1000)

# Memasukkan item ke dalam koleksi
for item_type in item_types:
    for tier in tiers:
        item_name = f"{item_type.capitalize()} Tier {tier}"
        price = generate_price(tier)
        update_time = datetime.utcnow() - timedelta(days=(tier - 1))  # Update harga semakin lama seiring naiknya tier

        item = {
            "name": item_name,
            "type": item_type,
            "tier": tier,
            "price": price,
            "update_time": update_time
        }

        collection.insert_one(item)

print("Data Black Market telah berhasil diisi.")
