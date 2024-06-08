from .__mongo import *
import random
import string

async def get_character_profile(user_id):
    try:
        character_data = await characters.find_one({"user_id": user_id})
        return character_data
    except Exception as e:
        print(f"Error in get_character_profile function: {e}")
        return None

async def save_character_profile(user_id, profile_name):
    data = await get_character_profile(user_id)
    if not data:
        await characters.update_one({"user_id": user_id}, {"$set": {'profile_name': profile_name}}, upsert=True)

async def save_character_stats(user_id, stats):    
    await characters.update_one({"user_id": user_id}, {"$set": {"stats": stats}})

async def add_gold_to_character(user_id, amount):
    characters.update_one({"user_id": user_id}, {"$inc": {"currency.Gold": amount}})

async def update_character_stats(user_id, stat_name, stat_value):
    character_profile = await get_character_profile(user_id)
    if character_profile:
        character_stats = character_profile['stats']
        character_stats[stat_name] = stat_value
        await save_character_profile(user_id, character_profile)

async def get_character_stats(user_id):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            characters_stats = character_profile.get('stats', {})
            return characters_stats
        else:
            return None
    except Exception as e:
        print(f"Error in get_character_stats function: {e}")
        return None

async def get_character_wallet(user_id):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            characters_wallet = character_profile.get('currency', {})
            return characters_wallet
        else:
            return None
    except Exception as e:
        print(f"Error in get_character_wallet function: {e}")
        return None
    
async def update_item_power(user_id, item_type, new_item_power):
    character = await characters.find_one({"user_id": user_id})
    
    if character:
        if item_type in character.get('items', {}):
            character['items'][item_type]['item_power'] = new_item_power
            await characters.replace_one({"user_id": user_id}, character)
            return True
        else:
            return False
    else:
        return False


async def get_total_fighters():
    all_characters = characters.find({}, {"stats.Fight": 1})
    total_fighter = 0
    async for character in all_characters:
        total_fighter += character['stats']['Fight']

    return total_fighter

async def get_total_workers():
    all_characters = characters.find({}, {"stats.Worker": 1})
    total_worker = 0
    async for character in all_characters:
        total_worker += character['stats']['Worker']

    return total_worker

async def get_total_skill():
    all_characters = characters.find({}, {"stats.Skill": 1})
    total_skill = 0
    async for character in all_characters:
        total_skill += character['stats']['Skill Points']

    return total_skill

async def get_total_exp():
    all_characters = characters.find({}, {"stats.Exp": 1})
    total_fame = 0
    async for character in all_characters:
        total_fame += character['stats']['EXP']

    return total_fame

async def get_total_silver():
    total_silver = 0
    all_characters = await characters.find().to_list(length=None)
    for character in all_characters:
        total_silver += character['stats'].get('Silver', 0)
    return total_silver

async def get_total_gold():
    total_gold = 0
    all_characters = await characters.find().to_list(length=None)
    for character in all_characters:
        total_gold += character['stats'].get('Gold', 0)
    return total_gold

async def delete_character_profile(user_id):
    result = await characters.delete_one({"user_id": user_id})
    return result.deleted_count > 0

async def get_total_item_power(user_id):
    character = await characters.find_one({"user_id": user_id})
    
    if character:
        items = character.get('items', {})
        total_item_power = sum(int(item.get('item_power', 0)) for item in items.values())
        
        return total_item_power
    else:
        return 0

async def add_item_power_to_profile(user_id, total_power):
    character_profile = await characters.find_one({"user_id": user_id})
    
    if character_profile:
        character_profile['stats']['item_power'] = total_power
        await characters.replace_one({"user_id": user_id}, character_profile)


async def add_silver(user_id, amount):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            silver_previous = character_profile.get('stats', {}).get('Silver', 0)
            silver_new = silver_previous + amount
            character_profile['stats']['Silver'] = silver_new
            await save_character_profile(user_id, character_profile)
            
            return True, silver_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in silver_gold function: {e}")
        return False, None

async def add_gold(user_id, amount):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            gold_previous = character_profile.get('stats', {}).get('Gold', 0)
            gold_new = gold_previous + amount
            character_profile['stats']['Gold'] = gold_new
            await save_character_profile(user_id, character_profile)
            
            return True, gold_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_gold function: {e}")
        return False, None

async def add_exp(user_id, amount):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            exp_previous = character_profile.get('stats', {}).get('Exp', 0)
            exp_new = exp_previous + amount
            character_profile['stats']['Exp'] = exp_new
            await save_character_profile(user_id, character_profile)
            
            return True, exp_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_exp function: {e}")
        return False, None

async def add_skill_points(user_id, amount):
    try:
        character_profile = await get_character_profile(user_id)
        
        if character_profile:
            skill_points_previous = character_profile.get('stats', {}).get('Skill Points', 0)
            skill_points_new = skill_points_previous + amount
            
            character_profile['stats']['Skill Points'] = skill_points_new
            await save_character_profile(user_id, character_profile)
            
            return True, skill_points_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_skill_points function: {e}")
        return False, None
    
async def create_token(user_id):
    character_profile = await get_character_profile(user_id)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    if character_profile:
        character_profile['tokentol'] = token

        await characters.update_one({"user_id": user_id}, character_profile)
    # Simpan token dalam dictionary tokens dengan user_id sebagai kuncinya
    return token

async def delete_token(user_id):
    character_profile = await get_character_profile(user_id)
    token = await characters.find_one({"user_id": user_id, "tokentol": token})
    if character_profile:
        await characters.delete_one()

async def update_token(user_id):
    characters_profile = await get_character_profile(user_id)
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    if characters_profile:
        characters_profile['tokentol'] = token
        await characters.replace_one({"user_id": user_id}, characters_profile)