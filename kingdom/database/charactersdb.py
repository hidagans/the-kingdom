from .__mongo import *
import random
import string
from pyromod import listen
import logging
from pyrogram.types import *
from config import XP_PER_LEVEL, XP_INCREMENT

async def get_character_profile(user_id):
    try:
        character_data = await characters.find_one({"user_id": user_id})
        if character_data:
            # Inisialisasi nilai default jika currency tidak ada
            if 'currency' not in character_data:
                character_data['currency'] = {'Silver': 0, 'Gold': 0}
            return character_data
        return None
    except Exception as e:
        print(f"Error in get_character_profile function: {e}")
        return None

async def save_character_profile(user_id, profile_name):
    data = await get_character_profile(user_id)
    if not data:
        await characters.update_one({"user_id": user_id}, {"$set": {'profile_name': profile_name}}, upsert=True)

async def save_character_stats(user_id, stats):    
    await characters.update_one({"user_id": user_id}, {"$set": {"stats": stats}})

    #update user hp dengan menggabungkan 

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
        if item_type in character.get('equipment', {}):
            character['equipment'][item_type]['item_power'] = new_item_power
            await characters.replace_one({"user_id": user_id}, character)
            return True
        else:
            return False
    else:
        return False

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
        total_fame += character['stats']['Exp']

    return total_fame

async def get_total_silver():
    total_silver = 0
    all_characters = await characters.find().to_list(length=None)
    for character in all_characters:
        total_silver += character['currency'].get('Silver', 0)
    return total_silver

async def get_total_gold():
    total_gold = 0
    all_characters = await characters.find().to_list(length=None)
    for character in all_characters:
        total_gold += character['currency'].get('Gold', 0)
    return total_gold

async def delete_character_profile(user_id):
    result = await characters.delete_one({"user_id": user_id})
    return result.deleted_count > 0

async def get_total_item_power(user_id):
    character = await characters.find_one({"user_id": user_id})
    
    if character:
        items = character.get('equipment', {})
        total_item_power = sum(int(item.get('item_power', 0)) for item in items.values())
        
        return total_item_power
    else:
        return 0

async def add_item_power_to_profile(user_id, total_power):
    character_profile = await characters.find_one({"user_id": user_id})
    
    if character_profile:
        character_profile['stats']['item_power'] = total_power
        await characters.replace_one({"user_id": user_id}, character_profile)


async def add_silver(user_id, amount_silver):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            silver_previous = character_profile.get('currency', {}).get('Silver', 0)
            silver_new = (silver_previous if silver_previous is not None else 0) + amount_silver
            character_profile['currency']['Silver'] = silver_new
            await characters.update_one(
              {"user_id": user_id},
              {"$set": {"currency.Silver":  silver_new}}
              )
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_silver function: {e}")
        return False, None

async def add_gold(user_id, amount):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            gold_previous = character_profile.get('currency', {}).get('Gold', 0)
            gold_new = (gold_previous if gold_previous is not None else 0) + amount
            character_profile['currency']['Gold'] = gold_new
            await save_character_profile(user_id, character_profile)
            return True, gold_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_gold function: {e}")
        return False, None


async def add_exp(user_id, amount_exp):
    try:
        character_profile = await get_character_profile(user_id)
        if character_profile:
            # Mengambil nilai EXP dan level saat ini dengan nilai default jika tidak ada
            new_xp = character_profile.get("stats", {}).get("Exp", 0) + amount_exp
            level = character_profile.get("stats", {}).get("level", 1)
            level_up = False
            xp_for_next_level = XP_PER_LEVEL * level

            # Loop untuk menangani level up
            while new_xp >= xp_for_next_level:
                new_xp -= xp_for_next_level
                level += 1
                level_up = True
                xp_for_next_level = XP_PER_LEVEL + (XP_INCREMENT * level)

            # Pembaruan data di database
            await characters.update_one(
                {"user_id": user_id},
                {"$set": {"stats.Exp": new_xp, "stats.level": level}}
            )

            # Mengembalikan pesan berdasarkan apakah level up terjadi atau tidak
            if level_up:
                return f"Level up! Kamu sekarang level {level}."
            return f"EXP bertambah! Kamu sekarang memiliki {new_xp} EXP."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        logging.error(f"Error in add_exp: {e}")
        return "Terjadi kesalahan saat menambahkan EXP."

async def add_skill_points(user_id, amount_skill):
    try:
        character_profile = await get_character_profile(user_id)
        
        if character_profile:
            skill_points_previous = character_profile.get('stats', {}).get('Skill Points', 0)
            skill_points_new = skill_points_previous + amount_skill
            
            character_profile['stats']['Skill Points'] = skill_points_new
            await save_character_profile(user_id, character_profile)
            
            return True, skill_points_new
        else:
            return False, None
    except Exception as e:
        print(f"Error in add_skill_points function: {e}")
        return False, None
    
async def calculate_stats(character_profile):
    base_stats = character_profile.get('stats', {})
    equipment = character_profile.get('equipment', {})

    # Mulai dengan base stats
    total_stats = {
        'max_hp': base_stats.get('max_hp', 0),
        'max_mana': base_stats.get('max_mana', 0),
        'defense': 0,
        'damage': 0,
        'damage_increase': 0,
        'attack_speed': 0
    }

    # Tambahkan statistik dari setiap item
    for item_type in ['weapons', 'headarmor', 'bodyarmor', 'footarmor']:
        item = equipment.get(item_type)
        if item:
            total_stats['max_hp'] += item.get('max_hp', 0)
            total_stats['max_mana'] += item.get('max_mana', 0)
            total_stats['defense'] += item.get('defense', 0)
            total_stats['damage'] += item.get('damage', 0)
            total_stats['damage_increase'] += item.get('damage_increase', 0)
            total_stats['attack_speed'] += item.get('attack_speed', 0)

    return total_stats


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

async def collection_for_item_type(item_type):
    # Definisikan pemetaan antara jenis item dan nama koleksi di sini
    collections_mapping = {
        "weapons": weapons,
        "headarmor": headarmors,
        "bodyarmor": bodyarmors,
        "footarmor": footarmors
    }
    return collections_mapping.get(item_type)


async def show_inventory(user_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Head Armor", callback_data="inventory:headarmor")],
        [InlineKeyboardButton("Body Armor", callback_data="inventory:bodyarmor")],
        [InlineKeyboardButton("Foot Armor", callback_data="inventory:footarmor")],
        [InlineKeyboardButton("Weapons", callback_data="inventory:weapons")],
        [InlineKeyboardButton("Back", callback_data="my_profile")]
    ])
    return "Pilih kategori item:", keyboard

async def show_items(user_id, item_type, start=0, limit=1):
    try:
        inventory_data = await get_user_inventory(user_id)

        if not inventory_data or item_type not in inventory_data:
            return "Tidak ada item dalam kategori ini.", None

        items = inventory_data[item_type]
        if start >= len(items):
            return "Tidak ada item berikutnya.", None

        end = min(start + limit, len(items))
        keyboard = []

        for item in items[start:end]:
            item_buttons = []
            for action in ["use", "sell", "trash"]:
                callback_data = f"{action}:{item_type}:{item['name']}"
                item_buttons.append(InlineKeyboardButton(f"{action.capitalize()}", callback_data=callback_data))
            keyboard.append(item_buttons)

        navigation_buttons = []
        if end < len(items):
            navigation_buttons.append(InlineKeyboardButton("Next", callback_data=f"inventory:{item_type}:{end}"))
        navigation_buttons.append(InlineKeyboardButton("Back", callback_data="cb_inventory"))
        keyboard.append(navigation_buttons)

        return f"{item['name']}", InlineKeyboardMarkup(keyboard)
    except Exception as e:
        print(f"Error in show_items: {e}")
        return "Terjadi kesalahan dalam menampilkan item.", None

async def use_item(user_id, item_type, item_name):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })
            item_to_use = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_use:
                item_type = item_to_use.get("armor_type", "")
                if item_type in equipment:
                    equipment[item_type] = item_to_use
                    inventory.remove(item_to_use)
                    await characters.update_one(
                        {"user_id": user_id},
                        {"$set": {"inventory": inventory, "equipment": equipment}}
                    )
                    return f"{item_name} telah digunakan sebagai {item_type}."
                else:
                    return f"Tipe item {item_type} tidak dikenali."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in use_item: {e}")
        return "Terjadi kesalahan saat mencoba menggunakan item."
 

async def trash_item(user_id, item_type, item_name):
    try:
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            item_to_trash = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_trash:
                inventory.remove(item_to_trash)

                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory}}
                )
                return f"Item {item_name} telah dibuang."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in trash_item: {e}")
        return "Terjadi kesalahan saat mencoba membuang item."


async def show_equipment(user_id):
    try:
        equipment_data = await get_user_equipment(user_id)

        if not equipment_data:
            return "Equipment kamu kosong."

        equipment_message = "Equipment kamu:\n"
        for item_type, item_list in equipment_data.items():
            equipment_message += f"- {item_type.capitalize()}:\n"
            for item in item_list:
                equipment_message += f"  • {item['name']} (Level {item['Level']})\n"

        return equipment_message
    except Exception as e:
        print(f"Error in show_equipment: {e}")
        return "Terjadi kesalahan dalam menampilkan equipment."
    
async def equiped_item(user_id, item_type, item_id):
    character_profile = await get_character_profile(user_id)
    if character_profile:
        # Dapatkan item dari koleksi yang sesuai
        if item_type == 'weapons':
            item = await get_item(weapons, item_id)
        elif item_type == 'headarmor':
            item = await get_item(headarmors, item_id)
        elif item_type == 'bodyarmor':
            item = await get_item(bodyarmors, item_id)
        elif item_type == 'footarmor':
            item = await get_item(footarmors, item_id)
        else:
            return False

        if item:
            # Perbarui item yang dipakai
            character_profile['equipment'][item_type] = item

            # Hitung ulang statistik
            new_stats = calculate_stats(character_profile)
            character_profile['stats'] = new_stats

            # Simpan perubahan
            await characters.replace_one({"user_id": user_id}, character_profile)
            return True
    return False

    
async def equip_item(user_id, item_name):
    try:
        # Ambil data karakter dari MongoDB berdasarkan user_id
        character = await characters.find_one({"user_id": user_id})

        # Periksa apakah karakter ditemukan
        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })

            # Temukan item di inventory
            item_to_equip = next((item for item in inventory if item['name'] == item_name), None)

            if item_to_equip:
                item_type = item_to_equip.get("armor_type", "")
                if item_type in equipment:
                    # Equip item
                    equipment[item_type] = item_to_equip

                    # Hapus item dari inventory
                    inventory.remove(item_to_equip)

                    # Perbarui data karakter di MongoDB
                    await characters.update_one(
                        {"user_id": user_id},
                        {"$set": {"inventory": inventory, "equipment": equipment}}
                    )
                    return f"{item_name} telah dipakai sebagai {item_type}."
                else:
                    return f"Tipe item {item_type} tidak dikenali."
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in equip_item: {e}")
        return "Terjadi kesalahan saat mencoba memakai item."
    
async def unequip_item(user_id, item_type):
    try:
        # Ambil data karakter dari MongoDB berdasarkan user_id
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })

            # Temukan item di equipment
            item_to_unequip = equipment.get(item_type, None)

            if item_to_unequip:
                # Pindahkan item ke inventory
                inventory.append(item_to_unequip)

                # Hapus item dari equipment
                equipment[item_type] = None

                # Perbarui data karakter di MongoDB
                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory, "equipment": equipment}}
                )
                return f"{item_to_unequip['name']} telah dilepas dari {item_type}."
            else:
                return f"Tidak ada item yang dipakai di slot {item_type}."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in unequip_item: {e}")
        return "Terjadi kesalahan saat mencoba melepas item."

async def get_user_inventory(user_id):
    try:
        character = await characters.find_one({"user_id": user_id})

        if character:
            inventory = character.get("inventory", [])
            inventory_data = {"headarmor": [], "bodyarmor": [], "footarmor": [], "weapons": []}

            for item in inventory:
                item_type = item.get("armor_type", "weapons")
                if item_type in inventory_data:
                    inventory_data[item_type].append(item)

            return inventory_data
        else:
            return {}
    except Exception as e:
        print(f"Error in get_user_inventory: {e}")
        return {}

    
async def get_user_equipment(user_id):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            equipment = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapon": None
            })
            equipment_data = {"headarmor": [], "bodyarmor": [], "footarmor": [], "weapons": []}

            # Kelompokkan item berdasarkan tipe
            for item_type, item in equipment.items():
                if item:
                    equipment_data[item_type].append(item)

            return equipment_data
        else:
            return {}
    except Exception as e:
        print(f"Error in get_user_equipment: {e}")
        return {}
    
async def get_item(collection, item_id):
    item = await collection.find_one({"_id": item_id})
    return item

async def calculate_total_stats(user_id):
    try:
        character = await characters.find_one({"user_id": user_id})  # Menunggu hasil dari coroutine find_one
        if character:
            equip = character.get("equipment", {
                "headarmor": None,
                "bodyarmor": None,
                "footarmor": None,
                "weapons": None
            })

            max_hp_values = []

            for key, equipment in character['equipment'].items():
                if equipment and 'max_hp' in equipment:
                    max_hp_values.append(equipment['max_hp'])
                    

            total_stats = {
                'current_hp': character.get('stats', {}).get('current_hp', {}),
                'max_hp': character['stats']['characters_hp'] + sum(max_hp_values),
                'Exp': character.get('stats', {}).get('Exp', 0),
                'Skill Points': character.get('stats', {}).get('Skill Points', 0),
                'characters_hp': character.get('stats', {}).get('characters_hp', 0)
            }
           
            # Jumlahkan statistik dari setiap item
            for item in equip.values():
                if item:
                    for stat, value in item.items():
                        if stat not in ["_id", "type", "name", "Level", "armor_type"]:
                            if stat == 'max_hp':  # Tambahkan max_hp_values ke max_hp
                                total_stats[stat] = character['stats']['characters_hp'] + sum(max_hp_values)
                            else:
                                total_stats[stat] = value

            # Perbarui total stats di dalam karakter
            await characters.update_one(
                {"user_id": user_id},
                {"$set": {"stats": total_stats}}
            )

            # Buat pesan hasil
            response_message = "Total stats kamu sekarang adalah:\n"
            for stat, value in total_stats.items():
                response_message += f"{stat.capitalize()}: {value}\n"

            return response_message
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        print(f"Error in calculate_total_stats: {e}")
        return "Terjadi kesalahan saat menghitung total stats."
