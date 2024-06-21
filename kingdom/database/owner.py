from .__mongo import *

async def add_potion_to_inventory(potion_name, quantity, user_id):
    # Cari potion berdasarkan nama
    characters_data = await characters.find_one({"user_id": user_id})
    potion = await potions.find_one({"name": potion_name})
    if potion:
        inventory = characters_data.get('inventory', [])
        inventory.append(potion)
        # Masukkan dokumen ke dalam koleksi inventory
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory}})
        print(f"{quantity} {potion_name} telah ditambahkan ke inventory user {user_id}.")
    else:
        print(f"Potion {potion_name} tidak ditemukan di database.")

async def add_item_to_inventory(name, type, user_id):
    # Cari item berdasarkan nama
    characters_data = await characters.find_one({"user_id": user_id})
    inventory_data = characters_data.get('inventory', [])
    if type == "weapons":
        item = await weapons.find_one({"name": name})
        await characters.up
        inventory_data.append(item)
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory_data}})
        print(f"{name} telah ditambahkan ke inventory user {user_id}.")
    elif type == "bodyarmors":
        item = await bodyarmors.find_one({"name": name})
        inventory_data.append(item)
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory_data}})
        print(f"{name} telah ditambahkan ke inventory user {user_id}.")
    elif type == "footarmors":
        item = await footarmors.find_one({"name": name})
        inventory_data.append(item)
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory_data}})
        print(f"{name} telah ditambahkan ke inventory user {user_id}.")
    elif type == "headarmors":
        item = await headarmors.find_one({"name": name})
        inventory_data.append(item)
        characters.update_one({"user_id": user_id}, {"$set": {"inventory": inventory_data}})
        print(f"{name} telah ditambahkan ke inventory user {user_id}.")
    else:
        print(f"Item {name} tidak ditemukan di database.")

#hehehe