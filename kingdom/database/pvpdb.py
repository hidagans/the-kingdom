from .__mongo import *
import random
from datetime import timedelta, datetime
from pyrogram.types import *
import logging

# Part options
PARTS = ["head", "body", "arms", "legs"]

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

    # Power calculation based on selected attack and defense parts
    user_attack = pvp_data["user_attack"]
    user_defense = pvp_data["user_defense"]
    opponent_attack = pvp_data["opponent_attack"]
    opponent_defense = pvp_data["opponent_defense"]

    user_power = user['stats'][user_attack] - opponent['stats'][opponent_defense]
    opponent_power = opponent['stats'][opponent_attack] - user['stats'][user_defense]

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

async def start_pvp(user_id: int, opponent_id: int, message):
    if user_id == opponent_id:
        await message.reply_text("Anda tidak bisa menyerang diri sendiri.")
        return

    in_pvp = await is_in_pvp(user_id)
    if in_pvp:
        await message.reply_text("Anda masih dalam pertempuran PVP. Silakan tunggu sampai selesai sebelum memulai yang lain.")
        return

    current_time = datetime.utcnow()
    completion_time = current_time + timedelta(minutes=5)
    
    pvp_data = {
        "user_id": user_id,
        "opponent_id": opponent_id,
        "start_time": current_time,
        "completion_time": completion_time,
        "status": "awaiting_actions",
        "user_attack": None,
        "user_defense": None,
        "opponent_attack": None,
        "opponent_defense": None
    }
    await pvp_matches.insert_one(pvp_data)

    reply_text = (
        f"Pertempuran PVP dimulai! Lawan Anda adalah pengguna dengan ID {opponent_id}.\n"
        f"Silakan pilih bagian tubuh yang ingin Anda serang dan pertahankan.\n"
        f"Gunakan perintah /choose_attack <part> dan /choose_defense <part> untuk memilih bagian.\n"
        f"Estimasi waktu selesai: {completion_time.strftime('%H:%M')} UTC"
    )
    await message.reply_text(reply_text)

async def choose_attack(user_id: int, part: str, message: Message):
    if part not in PARTS:
        await message.reply_text("Bagian tubuh tidak valid. Gunakan: head, body, arms, legs.")
        return

    pvp_data = await pvp_matches.find_one({"user_id": user_id, "status": "awaiting_actions"})
    if not pvp_data:
        await message.reply_text("Anda tidak dalam pertempuran PVP atau pertempuran sudah dimulai.")
        return

    await pvp_matches.update_one({"_id": pvp_data["_id"]}, {"$set": {"user_attack": part}})
    await message.reply_text(f"Serangan dipilih: {part}")

    opponent_id = pvp_data["opponent_id"]
    opponent_data = await pvp_matches.find_one({"user_id": opponent_id, "status": "awaiting_actions"})
    if opponent_data and opponent_data["opponent_attack"] and opponent_data["opponent_defense"]:
        await start_battle(pvp_data)

async def choose_defense(user_id: int, part: str, message: Message):
    if part not in PARTS:
        await message.reply_text("Bagian tubuh tidak valid. Gunakan: head, body, arms, legs.")
        return

    pvp_data = await pvp_matches.find_one({"user_id": user_id, "status": "awaiting_actions"})
    if not pvp_data:
        await message.reply_text("Anda tidak dalam pertempuran PVP atau pertempuran sudah dimulai.")
        return

    await pvp_matches.update_one({"_id": pvp_data["_id"]}, {"$set": {"user_defense": part}})
    await message.reply_text(f"Pertahanan dipilih: {part}")

    opponent_id = pvp_data["opponent_id"]
    opponent_data = await pvp_matches.find_one({"user_id": opponent_id, "status": "awaiting_actions"})
    if opponent_data and opponent_data["opponent_attack"] and opponent_data["opponent_defense"]:
        await start_battle(pvp_data)

async def start_battle(pvp_data):
    await pvp_matches.update_one({"_id": pvp_data["_id"]}, {"$set": {"status": "ongoing"}})
    result_message = await complete_pvp(pvp_data)
    await pvp_matches.update_one({"_id": pvp_data["_id"]}, {"$set": {"completion_time": datetime.utcnow()}})
    return result_message
