from .__mongo import *
from kingdom.decorators import *
import datetime

async def get_users_in_world_boss():
    return await worldbosstime.find().to_list(length=None)

# Fungsi untuk menyimpan data world boss ke dalam database
async def save_world_boss_data(user_id, completion_time):
    await worldbosstime.update_one(
        {"user_id": user_id},
        {"$set": {"completion_time": completion_time}},
        upsert=True
    )

# Fungsi untuk memeriksa apakah pengguna sedang dalam world boss
async def is_in_world_boss(user_id):
    completion_time = await get_world_boss_completion_time(user_id)
    current_time = datetime.now()
    return completion_time and completion_time > current_time

# Fungsi untuk mendapatkan waktu estimasi selesai world boss
async def get_world_boss_completion_time(user_id):
    document = await worldbosstime.find_one({"user_id": user_id})
    return document["completion_time"] if document else None

# Fungsi untuk menghapus data world boss dari database
async def delete_world_boss_data(user_id):
    await worldbosstime.delete_one({"user_id": user_id})

# Fungsi untuk memberikan hadiah setelah menyelesaikan world boss
async def give_world_boss_rewards(user_id):
    silver_reward = 5000
    exp_reward = 200
    skill_point_reward = 0.5
    await characters.update_one(
        {"user_id": user_id},
        {"$inc": {"stats.Silver": silver_reward, "stats.Exp": exp_reward, "stats.SkillPoints": skill_point_reward}}
    )


# Fungsi untuk memeriksa apakah pengguna telah menyelesaikan world boss
async def has_completed_world_boss(user_id):
    document = await worldbosstime.find_one({"user_id": user_id})
    if document:
        completion_time = document["completion_time"]
        current_time = datetime.now()
        return completion_time and completion_time < current_time
    return False
