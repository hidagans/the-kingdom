from pyrogram import filters
from pyrogram.types import *
from kingdom.database import *
from kingdom.core import *

@KINGDOM.CALLBACK("dungeon_t3")
async def start_dungeon_t3(client, callback_query):
    await handle_dungeon(client, callback_query, tier=3, completion_time_minutes=3)

@KINGDOM.CALLBACK("dungeon_t4")
async def start_dungeon_t4(client, callback_query):
    await handle_dungeon(client, callback_query, tier=4, completion_time_minutes=4)

@KINGDOM.CALLBACK("dungeon_t5")
async def start_dungeon_t5(client, callback_query):
    await handle_dungeon(client, callback_query, tier=5, completion_time_minutes=5)

@KINGDOM.CALLBACK("dungeon_t6")
async def start_dungeon_t6(client, callback_query):
    await handle_dungeon(client, callback_query, tier=6, completion_time_minutes=6)

@KINGDOM.CALLBACK("dungeon_t7")
async def start_dungeon_t7(client, callback_query):
    await handle_dungeon(client, callback_query, tier=7, completion_time_minutes=7)

@KINGDOM.CALLBACK("dungeon_t8")
async def start_dungeon_t8(client, callback_query):
    await handle_dungeon(client, callback_query, tier=8, completion_time_minutes=8)

@KINGDOM.CALLBACK("cb_collect_t3")
async def collect_dungeon_t3_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=3)

@KINGDOM.CALLBACK("cb_collect_t4")
async def collect_dungeon_t4_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=4)

@KINGDOM.CALLBACK("cb_collect_t5")
async def collect_dungeon_t5_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=5)

@KINGDOM.CALLBACK("cb_collect_t6")
async def collect_dungeon_t6_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=6)

@KINGDOM.CALLBACK("cb_collect_t7")
async def collect_dungeon_t7_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=7)

@KINGDOM.CALLBACK("cb_collect_t8")
async def collect_dungeon_t8_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=8)