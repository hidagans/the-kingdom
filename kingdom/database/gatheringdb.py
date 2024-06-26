from .__mongo import *
from datetime import timedelta

# Fungsi untuk mengecek apakah user sedang dalam proses gathering
async def is_gathering(user_id):
    is_gathering = await gathering.find_one({"user_id": user_id})
    return is_gathering is not None

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
    is_gathering = await gathering.find_one({"user_id": user_id})
    if is_gathering:
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