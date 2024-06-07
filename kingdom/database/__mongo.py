from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL

# function database
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.kingdom

# variable mongo
userstartdb = db.userstart
character_profiledb = db.character_profiledb
character_statsdb = db.character_statsdb









#function async


#broadcast user database
async def is_served_user(user_id: int) -> bool:
    user = await userstartdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def get_served_users() -> list:
    users_list = []
    async for user in userstartdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await userstartdb.insert_one({"user_id": user_id})



#character profile database
async def get_character_profile(user_id):
    try:
        character_data = await character_profiledb.find_one({"user_id": user_id})
        return character_data
    except Exception as e:
        print(f"Error in get_character_profile function: {e}")
        return None

async def save_character_profile(user_id, profile_name):
    data = await get_character_profile(user_id)
    if not data:
        await character_profiledb.update_one({"user_id": user_id}, {"$set": {'profile_name': profile_name}}, upsert=True)


#chracter stats database
async def save_character_stats(user_id, stats):    
    await character_statsdb.update_one({"user_id": user_id}, {"$set": {"stats": stats}})




