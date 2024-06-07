from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL

# function database
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.kingdom

# variable mongo
userstartdb = db.userstart
characters = db.character_profile
maps = db.maps
black_market = db.blackmarketdb
world_boss = db.worldboss
sumber_daya = db.sumberdaya
merchants = db.merchant_ku
pelelangan = db.lelang
dungeontime = db.dungeontime
logs_dungeon = db.logsdungeon
outpost = db.outpost
faction = db.faction
gathering = db.gathering
material = db.material