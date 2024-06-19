from .__mongo import *
import random
async def get_random_black_market_item():
    try:
        items = await black_market.find().to_list(length=None)
        if items:
            return random.choice(items)
        else:
            return None
    except Exception as e:
        print(f"Error in get_random_black_market_item: {e}")
        return None

async def add_item_to_dungeon_rewards():
    item = await get_random_black_market_item()
    if item:
        # Tambahkan item ke pool hadiah dungeon
        await dungeon_rewards.insert_one(item)
        # Hapus item dari black market
        await black_market.delete_one({"_id": item["_id"]})
        print(f"Item '{item['name']}' telah ditambahkan ke pool hadiah dungeon.")
    else:
        print("Tidak ada item yang tersedia di black market.")

async def add_item_to_world_boss_rewards():
    item = await get_random_black_market_item()
    if item:
        # Tambahkan item ke pool hadiah world boss
        await world_boss_rewards.insert_one(item)
        # Hapus item dari black market
        await black_market.delete_one({"_id": item["_id"]})
        print(f"Item '{item['name']}' telah ditambahkan ke pool hadiah world boss.")
    else:
        print("Tidak ada item yang tersedia di black market.")

async def add_item_to_open_world_chess_rewards():
    item = await get_random_black_market_item()
    if item:
        # Tambahkan item ke pool hadiah open world chess
        await open_world_chess_rewards.insert_one(item)
        # Hapus item dari black market
        await black_market.delete_one({"_id": item["_id"]})
        print(f"Item '{item['name']}' telah ditambahkan ke pool hadiah open world chess.")
    else:
        print("Tidak ada item yang tersedia di black market.")
