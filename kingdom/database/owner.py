from .__mongo import *

async def add_potion_to_inventory(potion_name, quantity, user_id):
    # Cari potion berdasarkan nama
    characters_data = await characters.find_one({"user_id": user_id})
    potion = await potions.find_one({"name": potion_name})
    
    if potion:
        # Mendapatkan inventory saat ini dari data karakter
        inventory = characters_data.get('inventory', [])
        
        # Cek apakah potion sudah ada dalam inventory
        potion_exists = False
        for item in inventory:
            if item['name'] == potion_name:
                item['quantity'] += quantity
                potion_exists = True
                break
        
        # Jika potion belum ada dalam inventory, tambahkan sebagai item baru
        if not potion_exists:
            inventory.append({"name": potion_name, "quantity": quantity})

        # Perbarui inventory karakter di database
        await characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory}})
        print(f"{quantity} {potion_name} telah ditambahkan ke inventory user {user_id}.")
    else:
        print(f"Potion {potion_name} tidak ditemukan di database.")
