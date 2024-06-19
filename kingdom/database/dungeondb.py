from .__mongo import *
from .charactersdb import *
from pyrogram.types import *
import asyncio
from datetime import datetime, timedelta
from kingdom import bot
import random
from kingdom.decorators import *
import pymongo
import numpy as np

chests = [
    {"type": "Green", "silver_reward": 1000, "exp_reward": 50, "skill_point_reward": 0.1, "probability": 0.5},
    {"type": "Blue", "silver_reward": 2000, "exp_reward": 100, "skill_point_reward": 0.15, "probability": 0.3},
    {"type": "Purple", "silver_reward": 3000, "exp_reward": 150, "skill_point_reward": 0.2, "probability": 0.15},
    {"type": "Gold", "silver_reward": 5000, "exp_reward": 200, "skill_point_reward": 0.25, "probability": 0.05},
]

async def get_random_monster(tier):
    monsters = {
        3: [
            {   "photo": "./kingdom/monster/troll.jpeg",
                "name": "Troll",
                "level": 3,
                "max_hp": 300,
                "damage": 35,
                "defense": 20,
                "reward_exp": 90,
                "amount_silver": 300
            },
            {   "photo": "./kingdom/monster/darkelf.jpeg",
                "name": "Dark Elf",
                "level": 3,
                "max_hp": 250,
                "damage": 40,
                "defense": 25,
                "reward_exp": 100,
                "amount_silver": 350
            }
        ],
        4: [
            {   "photo": "./kingdom/monster/ogre.jpeg",
                "name": "Ogre",
                "level": 4,
                "max_hp": 400,
                "damage": 50,
                "defense": 30,
                "reward_exp": 130,
                "amount_silver": 500
            },
            {   "photo": "./kingdom/monster/necromancer.jpeg",
                "name": "Necromancer",
                "level": 4,
                "max_hp": 350,
                "damage": 55,
                "defense": 35,
                "reward_exp": 150,
                "amount_silver": 550
            }
        ],
        5: [
            {   "photo": "./kingdom/monster/dragonling.jpeg",   
                "name": "Dragonling",
                "level": 5,
                "max_hp": 500,
                "damage": 60,
                "defense": 40,
                "reward_exp": 180,
                "amount_silver": 700
            },
            {   "photo": "./kingdom/monster/vampirlord.jpeg",
                "name": "Vampire Lord",
                "level": 5,
                "max_hp": 450,
                "damage": 70,
                "defense": 45,
                "reward_exp": 200,
                "amount_silver": 750
            }
        ],
        6: [
            {   "photo": "./kingdom/monster/demon.jpeg",
                "name": "Demon",
                "level": 6,
                "max_hp": 600,
                "damage": 80,
                "defense": 50,
                "reward_exp": 230,
                "amount_silver": 900
            },
            {   "photo": "./kingdom/monster/ancientlich.jpeg",
                "name": "Ancient Lich",
                "level": 6,
                "max_hp": 550,
                "damage": 85,
                "defense": 55,
                "reward_exp": 250,
                "amount_silver": 950
            }
        ],
        7: [
            {   "photo": "./kingdom/monster/fireelemental.jpeg",
                "name": "Fire Elemental",
                "level": 7,
                "max_hp": 700,
                "damage": 100,
                "defense": 60,
                "reward_exp": 300,
                "amount_silver": 1200
            },
            {   "photo": "./kingdom/monster/icegolem.jpeg",
                "name": "Ice Golem",
                "level": 7,
                "max_hp": 650,
                "damage": 110,
                "defense": 65,
                "reward_exp": 320,
                "amount_silver": 1250
            }
        ],
        8: [
            {   "photo": "./kingdom/monster/ancientdragon.jpeg",
                "name": "Ancient Dragon",
                "level": 8,
                "max_hp": 800,
                "damage": 130,
                "defense": 70,
                "reward_exp": 400,
                "amount_silver": 1500
            },
            {   "photo": "./kingdom/monster/necromancer.jpeg",
                "name": "Titan",
                "level": 8,
                "max_hp": 750,
                "damage": 140,
                "defense": 75,
                "reward_exp": 450,
                "amount_silver": 1600
            }
        ]
    }
    return random.choice(monsters[tier])

def get_random_chest():
    chest_types = [chest['type'] for chest in chests]
    probabilities = [chest['probability'] for chest in chests]
    chosen_chest_type = np.random.choice(chest_types, p=probabilities)
    chosen_chest = next(chest for chest in chests if chest['type'] == chosen_chest_type)
    return chosen_chest

async def add_chest_to_inventory(user_id, chest_type):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            chests = character.get("chests", [])
            chests.append(chest_type)
            await characters.update_one(
                {"user_id": user_id},
                {"$set": {"chests": chests}}
            )
        else:
            await characters.insert_one({"user_id": user_id, "chests": [chest_type]})
    except Exception as e:
        print(f"Error adding chest to inventory: {e}")

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
            completion_status = document["status"]
            if completion_status == "completed":
                await dungeontime.delete_one({"user_id": user_id})
                await complete_dungeon(user_id)
        await asyncio.sleep(60)

async def save_dungeon_data(user_id, status):
    await dungeontime.update_one(
        {"user_id": user_id},
        {"$set": {"status": status}},
        upsert=True
    )

async def is_in_dungeon(user_id):
    completion_status = await get_dungeon_completion_time(user_id)
    current_status = "process"
    completion_status_aware = "completed" if completion_status else None
    current_status_aware = current_status
    if completion_status_aware:
        return completion_status_aware > current_status_aware
    return False

async def get_dungeon_completion_time(user_id):
    try:
        document = await dungeontime.find_one({"user_id": user_id})
        if document:
            return document["status"]
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
    random_chest = get_random_chest()
    
    message_text = f"Selamat! Anda telah menyelesaikan dungeon!\n"
    message_text += f"Anda mendapatkan chest: {random_chest['type']}\n"

    # Simpan chest ke inventaris pemain
    await add_chest_to_inventory(user_id, random_chest['type'])

    # Tambahkan tombol untuk membuka chest
    buttons = [
        [InlineKeyboardButton("Buka Chest", url="https://t.me/tkgame_bot/kingdom")]
    ]
    max_length = 1024
    for i in range(0, len(message_text), max_length):
        part = message_text[i:i+max_length]
        await bot.send_message(user_id, part, reply_markup=InlineKeyboardMarkup(buttons))

async def damage_log_dungeon(user_id):
    character = await characters.find_one({"user_id": user_id})
    await save_damage_log
    pass

async def save_damage_log(user_id):
    await logs_dungeon.insert_one ({"user_id": user_id})
    pass

async def cancel_dungeon(user_id):
    await delete_dungeon_data(user_id)

async def save_dungeon_rewards_to_character(user_id, silver_reward, exp_reward, skill_point_reward):
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
        character_profile['stats']['Exp'] = exp_new
        character_profile['stats']['Skill Points'] = skill_point_new

        await save_character_profile(user_id, character_profile)

async def has_completed_dungeon(user_id):
    dungeon = await dungeontime.find_one({"user_id": user_id})
    if dungeon and dungeon.get("status") == "completed":
        return True
    return False

    
async def set_complete_dungeon(user_id):
    await dungeontime.update_one(
        {"user_id": user_id},
        {"$set": {"status": "completed"}},
        upsert=True
    )

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
    current_hp = stats.get("current_hp")
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
        amount_exp = monster["reward_exp"]
        amount_silver = monster["amount_silver"]
        await add_exp(user_id, amount_exp)
        await add_silver(user_id, amount_silver)
        combat_result = f"Kamu mengalahkan {monster['name']}! Mendapatkan {amount_exp} EXP dan {amount_silver} Silver."
    else:
        combat_result = f"Kamu dikalahkan oleh {monster['name']}."

    character['stats']['current_hp'] = current_hp
    await characters.update_one({"user_id": user_id}, {"$set": character})

    return combat_result, battle_log



async def handle_dungeon(client, callback_query, tier):
    user_id = callback_query.from_user.id
    in_dungeon = await is_in_dungeon(user_id)
    buttons = [
        [
            InlineKeyboardButton("Attack", callback_data=f"attack {tier}"),
            InlineKeyboardButton("Kabur", callback_data="cancel_dungeon"),
        ]
    ]
    buttons_cancel = [
        [
            InlineKeyboardButton("Batal", callback_data="cancel_dungeon"),
        ]
    ]
    media = InputMediaPhoto(media="./kingdom/monster/dungeon.jpeg", caption="Dungeon akan segera dimulai")
    ya = await callback_query.edit_message_media(media=media, reply_markup=InlineKeyboardMarkup(buttons_cancel))
    await asyncio.sleep(5)

    status = "process"
    await save_dungeon_data(user_id, status)

    player_stats = await characters.find_one({"user_id": user_id})
    monster = await get_random_monster(tier)
    reply_text = f"Dungeon Tier {tier} dimulai! melawan Monster **{monster['name']}**."
    media = InputMediaPhoto(media=monster['photo'], caption=reply_text)
    await callback_query.edit_message_media(media=media, reply_markup=InlineKeyboardMarkup(buttons))

    

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

@KING.CALL("attack")
async def attack(client, callback_query):
    data = callback_query.data.split()
    user_id = callback_query.from_user.id
    await callback_query.edit_message_text("Bertarung")
    await callback_query.edit_message_text("⚔️ Attacking ⚔️")
    tier = int(data[1])

    player_stats = await characters.find_one({"user_id": user_id})
    monster = await get_random_monster(tier)
    combat_result, combat_log = await handle_combat(player_stats, monster)

    combat_log_text = "\n".join(combat_log)
    if combat_result:
        await set_complete_dungeon(user_id)
        reply_text = f"Anda telah menyelesaikan Dungeon Tier {tier}\n\n{combat_log_text}"
    else:
        reply_text = f"Anda kalah dalam Dungeon Tier {tier}\n\n{combat_log_text}"

    # Split the reply_text into multiple messages if it exceeds the limit
    max_length = 1024
    for i in range(0, len(reply_text), max_length):
        part = reply_text[i:i+max_length]
        await callback_query.edit_message_text(part)

loop = asyncio.get_event_loop()
loop.create_task(check_dungeon_completion())
