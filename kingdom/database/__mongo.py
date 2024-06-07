from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL

# function database
mongo_client = AsyncIOMotorClient(MONGO_TOPCMD
db = mongo_client.kingdom

# variable mongo
userstartdb = db.userstart










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
