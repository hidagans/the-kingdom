from .__mongo import *
from bson import ObjectId
from .charactersdb import *
import asyncio
from datetime import timedelta, datetime

outpost_last_attack_times = {}
outpost_attackers = {}

async def get_outpost(location):
    await outpost.find_one({"location": location})

async def get_faction(faction_name):
    await faction.find_one({"name": faction_name})

async def get_outpost(outpost_id):
    try:
        return await outpost.find_one({"_id": ObjectId(outpost_id)})
    except Exception as e:
        print(f"Error in get_outpost: {e}")
        return None

async def update_outpost_guard_hp(outpost_id, new_hp):
    try:
        await outpost.update_one({"_id": ObjectId(outpost_id)}, {"$set": {"guard_hp": new_hp}})
    except Exception as e:
        print(f"Error in update_outpost_guard_hp: {e}")

async def change_outpost_faction(outpost_id, new_faction_id):
    try:
        await outpost.update_one({"_id": ObjectId(outpost_id)}, {"$set": {"faction_id": ObjectId(new_faction_id), "guard_hp": 9000}})
    except Exception as e:
        print(f"Error in change_outpost_faction: {e}")

async def check_user_in_faction(user_id):
    try:
        character_profile = get_character_profile(user_id)
        if character_profile and "faction_id" in character_profile:
            return character_profile["faction_id"]
        return None
    except Exception as e:
        print(f"Error in check_user_in_faction: {e}")
        return None

async def update_user_hp(user_id, damage_taken):
    try:
        user = await get_character_profile(user_id)
        new_hp = user['stats']['max_hp'] - damage_taken
        if new_hp < 0:
            new_hp = 0
        await characters.update_one({"user_id": user_id}, {"$set": {"stats.max_hp": new_hp}})
    except Exception as e:
        print(f"Error in update_user_hp: {e}")

async def regen_guard_hp(outpost_id):
    while True:
        await asyncio.sleep(120)  # Wait for 2 minutes
        outpost = await get_outpost(outpost_id)
        if outpost:
            last_attack_time = outpost_last_attack_times.get(outpost_id)
            if last_attack_time and datetime.now() - last_attack_time >= timedelta(minutes=2):
                await update_outpost_guard_hp(outpost_id, 9000)