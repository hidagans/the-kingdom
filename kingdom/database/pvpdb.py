from .__mongo import *
import random
from datetime import timedelta, datetime
from pyrogram.types import *
import logging

async def check_pvp_status(user_id: int):
    pvp_data = await pvp_matches.find_one({"user_id": user_id, "status": "ongoing"})
    
    if pvp_data:
        current_time = datetime.utcnow()
        if current_time > pvp_data["completion_time"]:
            result_message = await complete_pvp(pvp_data)
            return result_message
        else:
            return f"Pertempuran PVP masih berlangsung. Estimasi waktu selesai: {pvp_data['completion_time'].strftime('%H:%M')} UTC"
    else:
        return "Anda tidak memiliki pertempuran PVP yang sedang berlangsung."

async def complete_pvp(pvp_data):
    user_id = pvp_data["user_id"]
    opponent_id = pvp_data["opponent_id"]

    user = await characters.find_one({"user_id": user_id})
    opponent = await characters.find_one({"user_id": opponent_id})

    user_power = 0
    opponent_power = 0
    for power_us in user['stats'].values():
        user_power += power_us
    for power_op in opponent['stats'].values():
        opponent_power += power_op

    if user_power > opponent_power:
        winner_id, loser_id = user_id, opponent_id
    elif opponent_power > user_power:
        winner_id, loser_id = opponent_id, user_id
    else:
        winner_id, loser_id = random.choice([(user_id, opponent_id), (opponent_id, user_id)])

    reward_gold = random.randint(50, 100)
    await characters.update_one({"user_id": winner_id}, {"$inc": {"stats.Gold": reward_gold}})
    
    winner = await characters.find_one({"user_id": winner_id})
    loser = await characters.find_one({"user_id": loser_id})


    loser_equipment = loser['equipment']
    winner_inventory = winner.get('inventory', [])

    for slot in ['weapons', 'headarmor', 'bodyarmor', 'footarmor']:
        item = loser_equipment.get(slot)
        if item:
            item_quantity = item.get('quantity', 1)
            if 'quantity' in item:
                winner_inventory.append(item)
                await characters.update_one(
                    {"user_id": loser_id}, 
                    {"$set": {f"equipment.{slot}": None}}
                )

    loser_inventory = loser.get('inventory', [])
    
    winner_inventory_dict = {item['_id']: item for item in winner_inventory}

    for item in loser_inventory:
        item_id = item['_id']
        if item_id in winner_inventory_dict:
            if 'quantity' in item:
                winner_inventory_dict[item_id]['quantity'] += item.get('quantity', 1)
        else:
            winner_inventory_dict[item_id] = item

    new_winner_inventory = list(winner_inventory_dict.values())
    
    await characters.update_one({"user_id": winner_id}, {"$set": {"inventory": new_winner_inventory}})
    await characters.update_one({"user_id": loser_id}, {"$set": {"inventory": []}})

    await pvp_matches.update_one({"_id": pvp_data["_id"]}, {"$set": {"status": "completed", "winner_id": winner_id}})
    
    pvp_data["completion_time"] = datetime.utcnow()
    pvp_data["winner_id"] = winner_id
    await pvp_history.insert_one(pvp_data)
    
    result_message = (
        f"Pertempuran PVP selesai!\n"
        f"Pemenang: Pengguna dengan ID {winner_id} (Mendapatkan {reward_gold} Gold dan item dari lawan)\n"
        f"Lawan: Pengguna dengan ID {loser_id}\n"
    )

    return result_message

async def is_in_pvp(user_id: int) -> bool:
    pvp_data = await pvp_matches.find_one({"user_id": user_id, "status": "ongoing"})
    return pvp_data is not None

async def start_duel(user_id: int, opponent_id: int, bet_amount: int, message: Message):
    if user_id == opponent_id:
        await message.reply_text("Anda tidak bisa menantang diri sendiri.")
        return

    user = await characters.find_one({"user_id": user_id})
    opponent = await characters.find_one({"user_id": opponent_id})

    if user['stats'].get('Gold', 0) < bet_amount:
        await message.reply_text("Anda tidak memiliki cukup gold untuk bertaruh.")
        return
    if opponent['stats'].get('Gold', 0) < bet_amount:
        await message.reply_text("Pengguna target tidak memiliki cukup gold untuk bertaruh.")
        return

    current_time = datetime.utcnow()
    completion_time = current_time + timedelta(minutes=5)
    
    duel_data = {
        "user_id": user_id,
        "opponent_id": opponent_id,
        "bet_amount": bet_amount,
        "start_time": current_time,
        "completion_time": completion_time,
        "status": "ongoing"
    }
    await duel_matches.insert_one(duel_data)

    reply_text = (
        f"Duel dimulai! Lawan Anda adalah pengguna dengan ID {opponent_id} dengan taruhan {bet_amount} Gold.\n"
        f"Estimasi waktu selesai: {completion_time.strftime('%H:%M')} UTC"
    )
    await message.reply_text(reply_text)

async def check_duel_status(user_id: int):
    duel_data = await duel_matches.find_one({"user_id": user_id, "status": "ongoing"})
    
    if duel_data:
        current_time = datetime.utcnow()
        if current_time > duel_data["completion_time"]:
            result_message = await complete_duel(duel_data)
            return result_message
        else:
            return f"Duel masih berlangsung. Estimasi waktu selesai: {duel_data['completion_time'].strftime('%H:%M')} UTC"
    else:
        return "Anda tidak memiliki duel yang sedang berlangsung."

async def complete_duel(duel_data):
    user_id = duel_data["user_id"]
    opponent_id = duel_data["opponent_id"]
    bet_amount = duel_data["bet_amount"]

    user = await characters.find_one({"user_id": user_id})
    opponent = await characters.find_one({"user_id": opponent_id})

    if not user or not opponent:
        logging.error(f"User or opponent not found. User ID: {user_id}, Opponent ID: {opponent_id}")
        return "Duel gagal: Pengguna atau lawan tidak ditemukan."

    user_power = sum(user['stats'].values())
    opponent_power = sum(opponent['stats'].values())

    if user_power > opponent_power:
        winner_id, loser_id = user_id, opponent_id
    elif opponent_power > user_power:
        winner_id, loser_id = opponent_id, user_id
    else:
        winner_id, loser_id = random.choice([(user_id, opponent_id), (opponent_id, user_id)])

    await characters.update_one({"user_id": winner_id}, {"$inc": {"stats.Gold": bet_amount}})
    await characters.update_one({"user_id": loser_id}, {"$inc": {"stats.Gold": -bet_amount}})

    await duel_matches.update_one({"_id": duel_data["_id"]}, {"$set": {"status": "completed", "winner_id": winner_id}})
    
    duel_data["completion_time"] = datetime.utcnow()
    duel_data["winner_id"] = winner_id
    await duel_history.insert_one(duel_data)
    
    result_message = (
        f"Duel selesai!\n"
        f"Pemenang: Pengguna dengan ID {winner_id} (Mendapatkan {bet_amount} Gold)\n"
        f"Lawan: Pengguna dengan ID {loser_id} (Kehilangan {bet_amount} Gold)\n"
    )

    return result_message

async def is_in_duel(user_id: int) -> bool:
    duel_data = await duel_matches.find_one({"user_id": user_id, "status": "ongoing"})
    return duel_data is not None