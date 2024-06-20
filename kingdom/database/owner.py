import .__mongo

async def add_potion_to_inventory(potion_name, quantity, user_id):
    # Cari potion berdasarkan nama
    characters_data = await characters.find_one({"user_id": user_id})
    potion = potions.find_one({"name": potion_name})
    if potion:
        inventory = characters_data.get('inventory', [])
        inventory.append(potion)
        # Masukkan dokumen ke dalam koleksi inventory
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory}})
        print(f"{quantity} {potion_name} telah ditambahkan ke inventory user {user_id}.")
    else:
        print(f"Potion {potion_name} tidak ditemukan di database.")
