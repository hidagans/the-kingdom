from datetime import timedelta, datetime
from kingdom.database import *
import asyncio
from kingdom.core import *

WORLD_BOSS_CHANNEL_ID = -1002083228353
WORLD_BOSS_SPAWN_TIMES = ["08:00", "12:00", "16:00", "20:00", "00:00"]
last_spawn_time = None

def find_next_world_boss_spawn(now):
    current_time = now.strftime("%H:%M")
    spawn_times = [datetime.strptime(time, "%H:%M") for time in WORLD_BOSS_SPAWN_TIMES]
    spawn_times = [time.replace(year=now.year, month=now.month, day=now.day) for time in spawn_times]

    for time in spawn_times:
        if time > now:
            return time

    return spawn_times[0] + timedelta(days=1)  # Waktu spawn pertama besok jika semua waktu telah berlalu hari ini

async def check_world_boss_completion():
    while True:
        users_in_world_boss = await get_users_in_world_boss()
        for document in users_in_world_boss:
            user_id = document["user_id"]
            completion_time = document["completion_time"]
            current_time = datetime.now()

            if completion_time and completion_time < current_time:
                await complete_world_boss(user_id)

        await asyncio.sleep(60)

async def schedule_world_boss():
    global last_spawn_time
    while True:
        now = datetime.now().strftime("%H:%M")
        for spawn_time in WORLD_BOSS_SPAWN_TIMES:
            if abs((datetime.strptime(now, "%H:%M") - datetime.strptime(spawn_time, "%H:%M")).total_seconds()) <= 180 and now != last_spawn_time:
                last_spawn_time = now
                await bot.send_message(WORLD_BOSS_CHANNEL_ID, "World Boss telah muncul! Bergabunglah dalam pertempuran dalam 3 menit ke depan!")
                await asyncio.sleep(60)
                await bot.send_message(WORLD_BOSS_CHANNEL_ID, "World Boss telah muncul! Bergabunglah dalam pertempuran dalam 2 menit ke depan!")
                await asyncio.sleep(60)
                await bot.send_message(WORLD_BOSS_CHANNEL_ID, "World Boss telah muncul! Bergabunglah dalam pertempuran dalam 1 menit ke depan!")
                await asyncio.sleep(60)
                await bot.send_message(WORLD_BOSS_CHANNEL_ID, "Pertempuran sudah dimulai! Pendaftaran telah ditutup.")
        
        await asyncio.sleep(30)

# Fungsi untuk mengirim pesan setelah menyelesaikan world boss
async def send_world_boss_completion_message(user_id):
    user = await get_character_profile(user_id)
    message = f"{user['name']} telah menyelesaikan pertempuran world boss dan mendapatkan hadiah!"
    await bot.send_message(WORLD_BOSS_CHANNEL_ID, message)
    await bot.send_message(user_id, message)  # Mengirim pesan ke chat pribadi pengguna

# Fungsi untuk menangani penyelesaian world boss
async def complete_world_boss(user_id):
    await give_world_boss_rewards(user_id)
    await delete_world_boss_data(user_id)
    await send_world_boss_completion_message(user_id)

asyncio.create_task(schedule_world_boss())
asyncio.create_task(check_world_boss_completion())
