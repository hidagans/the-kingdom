from .__mongo import *
from datetime import timedelta

# Waktu respawn untuk setiap tier
RESPAWN_TIMES = {
    1: timedelta(minutes=3),  # Tier 1: 2-5 menit
    2: timedelta(minutes=3),  # Tier 2: 2-5 menit
    3: timedelta(minutes=15), # Tier 3: 10-20 menit
    4: timedelta(minutes=15), # Tier 4: 10-20 menit
    5: timedelta(minutes=45), # Tier 5: 30-60 menit
    6: timedelta(minutes=45), # Tier 6: 30-60 menit
    7: timedelta(hours=2.5),  # Tier 7: 2-3 jam
    8: timedelta(hours=7)     # Tier 8: 6-8 jam
}

# Fungsi untuk mengecek apakah user sedang dalam proses gathering
async def is_gathering(user_id):
    gathering = await gathering.find_one({"user_id": user_id})
    return gathering is not None

# Fungsi untuk memulai proses gathering
async def start_gathering(user_id, end_time, resource, quantity):
    await gathering.insert_one({
        "user_id": user_id,
        "end_time": end_time,
        "resource": resource,
        "quantity": quantity
    })

# Fungsi untuk menyelesaikan proses gathering dan memperbarui inventory
async def complete_gathering(user_id):
    gathering = await gathering.find_one({"user_id": user_id})
    if gathering:
        resource = gathering["resource"]
        quantity = gathering["quantity"]
        await gathering.delete_one({"user_id": user_id})
        await sumber_daya.update_one(
            {"user_id": user_id},
            {"$inc": {resource: quantity}},
            upsert=True
        )
        return resource, quantity
    return None, None

# Fungsi untuk menampilkan spot gathering yang tersedia di lokasi tertentu
async def show_gathering_spots(location):
    map_data = await maps.find_one({"location": location})
    return map_data.get("spots", []) if map_data else []