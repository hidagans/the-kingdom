from .__mongo import *
from .charactersdb import *

async def get_character_name(user_id):
    character_profile = await get_character_profile(user_id)
    if character_profile:
        return await character_profile.get("name")
    else:
        return

async def remove_user_from_guild(user_id, guild_id):
    await guild.update_one({"_id": guild_id}, {"$pull": {"Members": user_id}})
    await characters.update_one({"user_id": user_id}, {"$unset": {"Guild": ""}})

async def get_user_guild_id(user_id):
    character_profile = await get_character_profile(user_id)
    return character_profile.get("Guild", None)

async def does_guild_exist(user_id):
    # Implementasi kode untuk mengecek apakah pengguna telah membuat guild sebelumnya
    pass

async def is_in_guild(user_id):
    guild = await guild.find_one({"Members": user_id})
    return guild is not None

async def create_new_guild(user_id, guild_name):
    character_profile = await get_character_profile(user_id)
    if character_profile:
        result = await guild.insert_one({"name": guild_name, "Leader": user_id})
        await characters.update_one({"user_id": user_id}, {"$set": {"Guild": result.inserted_id}})
        return result
    
async def join_guild(user_id, guild_name):
    guild = await guild.find_one({"name": guild_name})
    if guild:
        await guild.update_one({"_id": guild["_id"]}, {"$addToSet": {"Members": user_id}})
        await characters.update_one({"user_id": user_id}, {"$set": {"Guild": guild["_id"]}})
    else:
        raise Exception("Guild not found")

async def get_guild_info(user_id):
    character = await get_character_profile(user_id)
    if character:
        guild_id = character.get("Guild")
        if guild_id:
            guild_info = await guild.find_one({"_id": guild_id})
            return guild_info
    return None