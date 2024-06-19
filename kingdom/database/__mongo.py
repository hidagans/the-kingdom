from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGO_URL

# function database
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client.kingdom

# variable mongo
userstartdb = db.userstartdb
characters = db.characters
maps = db.maps
black_market = db.black_market
black_market_items = db.black_market_items
world_boss = db.world_boss
sumber_daya = db.sumberdaya
merchants = db.merchants
pelelangan = db.pelelangan
dungeontime = db.dungeontime
logs_dungeon = db.logs_dungeon
outpost = db.outpost
faction = db.faction
gathering = db.gathering
material = db.material
guild = db.guild
guild_wars = db.guild_wars
market = db.market
maps_resource = db.maps_resource
party_group = db.party_group
pvp_matches = db.pvp_matches
pvp_history = db.pvp_history
duel_matches = db.duel_matches
duel_history = db.duel_history
redeemcode = db.redeemcode
weapons = db.weapons
headarmors = db.headarmors
bodyarmors = db.bodyarmors
footarmors = db.footarmors
invoice = db.invoice
worldbosstime = db.worldbosstime
world_boss_rewards = db.world_boss_rewards
open_world_chess_rewards = db.open_world_chess_rewards
dungeon_rewards = db.dungeon_rewards