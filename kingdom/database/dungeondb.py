from .__mongo import *
from .charactersdb import *
from pyrogram.types import *
import asyncio
from datetime import datetime, timedelta
from kingdom import bot
import random
from kingdom.decorators import *

async def get_random_item(collection_name):
    collection = getattr(mongodb, collection_name)
    random_item = await collection.aggregate([{ "$sample": { "size": 1 } }]).to_list(1)
    return random_item[0] if random_item else None

async def add_item_to_inventory(user_id, item):
    if item:
        item_type = item['armor_type'].lower()
        if item_type in ["headarmor", "bodyarmor", "footarmor", "weapons"]:
            character = await characters.find_one({"user_id": user_id})
            if character:
                inventory = character.get("inventory", [])
                inventory.append(item)
                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory}}
                )
            else:
                await characters.insert_one({"user_id": user_id, "inventory": [item]})
        else:
            print(f"Item {item['name']} tidak ditambahkan karena tipe tidak valid.")

async def get_users_in_dungeon():
    users_in_dungeon = []
    async for document in dungeontime.find({}):
        users_in_dungeon.append(document)
    return users_in_dungeon

async def check_dungeon_completion():
    while True:
        users_in_dungeon = await get_users_in_dungeon()
        for document in users_in_dungeon:
            user_id = document["user_id"]
            completion_time = document["completion_time"]
            current_time = datetime.now().astimezone()
            completion_time_aware = completion_time.astimezone() if completion_time else None
            if completion_time_aware and completion_time_aware < current_time:
                await complete_dungeon(user_id)
        await asyncio.sleep(60)

async def save_dungeon_data(user_id, completion_time):
    await dungeontime.update_one(
        {"user_id": user_id},
        {"$set": {"completion_time": completion_time}},
        upsert=True
    )

async def is_in_dungeon(user_id):
    completion_time = await get_dungeon_completion_time(user_id)
    current_time = datetime.now()
    completion_time_aware = completion_time.astimezone() if completion_time else None
    current_time_aware = current_time.astimezone()
    if completion_time_aware:
        return completion_time_aware > current_time_aware
    return False

async def get_dungeon_completion_time(user_id):
    try:
        document = await dungeontime.find_one({"user_id": user_id})
        if document:
            return document["completion_time"]
        return None
    except Exception as e:
        print(f"Error while fetching dungeon completion time: {e}")
        return None

async def delete_dungeon_data(user_id):
    await dungeontime.delete_one({"user_id": user_id})

async def complete_dungeon(user_id):
    await give_dungeon_rewards(user_id)
    await delete_dungeon_data(user_id)

async def give_dungeon_rewards(user_id):
    item_collections = ["bodyarmor", "headarmor", "footarmor", "weapons"]
    random_collection = random.choice(item_collections)
    random_item = await get_random_item(random_collection)
    silver_reward = 3000
    exp_reward = 100
    skill_point_reward = 0.25
    
    message_text = f"Selamat! Anda telah menyelesaikan dungeon!\n"
    message_text += f"Anda mendapatkan:\n"
    message_text += f"Silver: {silver_reward}\n"
    message_text += f"EXP: {exp_reward}\n"
    message_text += f"Skill Points: {skill_point_reward}\n"
    message_text += f"Item: ({random_item['type']})\n"

    await add_item_to_inventory(user_id, random_item)
    await add_silver(user_id, silver_reward)
    await add_exp(user_id, exp_reward)
    await add_skill_points(user_id, skill_point_reward)
    await save_dungeon_rewards_to_character(user_id, silver_reward, exp_reward, skill_point_reward, random_item)
    
    # Split the message text if it exceeds the limit
    max_length = 1024
    for i in range(0, len(message_text), max_length):
        part = message_text[i:i+max_length]
        await bot.send_message(user_id, part)

async def damage_log_dungeon(user_id):
    character = await characters.find_one({"user_id": user_id})
    await save_damage_log
    pass

async def save_damage_log(user_id):
    await logs_dungeon.insert_one ({"user_id": user_id})
    pass

async def cancel_dungeon(user_id):
    await delete_dungeon_data(user_id)

async def save_dungeon_rewards_to_character(user_id, silver_reward, exp_reward, skill_point_reward, item):
    character_profile = await get_character_profile(user_id)
    if character_profile:
        exp_previous = character_profile.get('stats', {}).get('Exp', 0)
        skill_point_previous = character_profile.get('stats', {}).get('Skill Points', 0)
        silver_previous = character_profile.get('currency', {}).get('Silver', 0)
        if 'stats' not in character_profile:
            character_profile['stats'] = {}
        if 'currency' not in character_profile:
            character_profile['currency'] = {}
        silver_new = silver_previous + silver_reward
        exp_new = exp_previous + exp_reward
        skill_point_new = skill_point_previous + skill_point_reward
        character_profile['currency']['Silver'] = silver_new
        character_profile['stats']['EXP'] = exp_new
        character_profile['stats']['Skill Points'] = skill_point_new

        if item:
            await add_item_to_inventory(user_id, item)

        await save_character_profile(user_id, character_profile)

async def has_completed_dungeon(user_id: int) -> bool:
    completion_time = await get_dungeon_completion_time(user_id)
    if completion_time:
        current_time = datetime.now(completion_time.tzinfo)
        if current_time > completion_time:
            return True
    return False

async def add_xp(user_id, xp):
    character = await characters.find_one({"user_id": user_id})
    if not character:
        return "Karakter tidak ditemukan."
    new_xp = character.get("xp", 0) + xp
    level = character.get("level", 1)
    level_up = False
    xp_for_next_level = 100 * level

    while new_xp >= xp_for_next_level:
        new_xp -= xp_for_next_level
        level += 1
        level_up = True
        xp_for_next_level = 100 * level

    await characters.update_one(
        {"user_id": user_id},
        {"$set": {"xp": new_xp, "level": level}}
    )

    if level_up:
        return f"Level up! Kamu sekarang level {level}."
    return f"XP bertambah! Kamu sekarang memiliki {new_xp} XP."

async def calculate_damage(attacker, defender):
    damage = max(0, attacker["damage"] - defender["defense"])
    return damage

async def handle_combat(player_stats, monster):
    user_id = player_stats['user_id']
    combat_result, combat_log = await combat(user_id, monster)
    return combat_result, combat_log

async def combat(user_id, monster):
    character = await get_character_profile(user_id)
    if not character:
        return "Karakter tidak ditemukan.", []

    stats = character.get("stats", {})
    max_hp = stats.get("max_hp")
    current_hp = character.get("characters_hp", max_hp)
    attack = stats.get("damage")
    defense = stats.get("defense")

    monster_hp = monster["max_hp"]
    monster_damage = monster["damage"]
    monster_defense = monster["defense"]

    battle_log = []

    while current_hp > 0 and monster_hp > 0:
        # Player attacks monster
        player_damage = max(0, attack - monster_defense)
        monster_hp -= player_damage
        battle_log.append(f"Kamu menyerang {monster['name']} dengan {player_damage} damage.")

        if monster_hp <= 0:
            break

        # Monster attacks player
        monster_attack = max(0, monster_damage - defense)
        current_hp -= monster_attack
        battle_log.append(f"{monster['name']} menyerang kamu dengan {monster_attack} damage.")

    # Determine the outcome
    combat_result = ""
    if current_hp > 0:
        reward_exp = monster["reward_exp"]
        reward_silver = monster["reward_silver"]
        await add_exp(user_id, reward_exp)
        await add_silver(user_id, reward_silver)
        combat_result = f"Kamu mengalahkan {monster['name']}! Mendapatkan {reward_exp} EXP dan {reward_silver} Silver."
    else:
        combat_result = f"Kamu dikalahkan oleh {monster['name']}."

    character['characters_hp'] = current_hp
    await characters.update_one({"user_id": user_id}, {"$set": character})

    return combat_result, battle_log

async def handle_dungeon(client, callback_query, tier, completion_time_minutes=5):
    user_id = callback_query.from_user.id
    in_dungeon = await is_in_dungeon(user_id)
    buttons = [
        [
            InlineKeyboardButton("AMBIL", callback_data=f"cb_collect_t{tier}"),
            InlineKeyboardButton("BACK", callback_data="dungeon_konten"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    if in_dungeon:
        await callback_query.edit_message_text("Anda masih dalam dungeon. Silakan tunggu sampai selesai sebelum memulai yang lain.", reply_markup=reply_markup)
        return

    dungeon_completed = await has_completed_dungeon(user_id)
    if dungeon_completed:
        await callback_query.edit_message_text("Anda sudah menyelesaikan dungeon sebelumnya. Silakan ambil item sebelum Anda dapat memulai lagi.", reply_markup=reply_markup)
        return

    current_time = datetime.now()
    completion_time = current_time + timedelta(minutes=completion_time_minutes)

    await save_dungeon_data(user_id, completion_time)

    reply_text = f"Dungeon Tier {tier} dimulai! Estimasi waktu selesai: {completion_time.strftime('%H:%M')} WIB"
    await callback_query.edit_message_text(reply_text, reply_markup=reply_markup)

    await asyncio.sleep(completion_time_minutes * 60)  # Menunggu waktu penyelesaian dungeon

    player_stats = await characters.find_one({"user_id": user_id})
    monster = await get_random_monster(tier)
    combat_result, combat_log = await handle_combat(player_stats, monster)

    combat_log_text = "\n".join(combat_log)
    if combat_result:
        reply_text = f"Anda telah menyelesaikan Dungeon Tier {tier}\n\n{combat_log_text}"
    else:
        reply_text = f"Anda kalah dalam Dungeon Tier {tier}\n\n{combat_log_text}"

    # Split the reply_text into multiple messages if it exceeds the limit
    max_length = 1024
    for i in range(0, len(reply_text), max_length):
        part = reply_text[i:i+max_length]
        await client.send_message(callback_query.message.chat.id, part)


async def handle_collect_rewards(client, callback_query, tier):
    user_id = callback_query.from_user.id
    dungeon_completed = await has_completed_dungeon(user_id)
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="dungeon_konten"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    if dungeon_completed:
        await give_dungeon_rewards(user_id)
        await delete_dungeon_data(user_id)
        await callback_query.edit_message_text(f"Hadiah dungeon Tier {tier} telah dikumpulkan!", reply_markup=reply_markup)
    else:
        await callback_query.edit_message_text("Anda belum menyelesaikan dungeon ini.", reply_markup=reply_markup)

loop = asyncio.get_event_loop()
loop.create_task(check_dungeon_completion())