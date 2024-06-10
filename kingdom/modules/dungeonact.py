import asyncio
from pyrogram import filters
from pyrogram.types import *
from kingdom.database import *
from kingdom.core import *

@KING.CALL("dungeon_t3")
async def start_dungeon_t3(client, callback_query):
    await handle_dungeon(client, callback_query, tier=3, completion_time_minutes=3)

@KING.CALL("dungeon_t4")
async def start_dungeon_t4(client, callback_query):
    await handle_dungeon(client, callback_query, tier=4, completion_time_minutes=4)

@KING.CALL("dungeon_t5")
async def start_dungeon_t5(client, callback_query):
    await handle_dungeon(client, callback_query, tier=5, completion_time_minutes=5)

@KING.CALL("dungeon_t6")
async def start_dungeon_t6(client, callback_query):
    await handle_dungeon(client, callback_query, tier=6, completion_time_minutes=6)

@KING.CALL("dungeon_t7")
async def start_dungeon_t7(client, callback_query):
    await handle_dungeon(client, callback_query, tier=7, completion_time_minutes=7)

@KING.CALL("dungeon_t8")
async def start_dungeon_t8(client, callback_query):
    await handle_dungeon(client, callback_query, tier=8, completion_time_minutes=8)

@KING.CALL("cb_collect_t3")
async def collect_dungeon_t3_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=3)

@KING.CALL("cb_collect_t4")
async def collect_dungeon_t4_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=4)

@KING.CALL("cb_collect_t5")
async def collect_dungeon_t5_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=5)

@KING.CALL("cb_collect_t6")
async def collect_dungeon_t6_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=6)

@KING.CALL("cb_collect_t7")
async def collect_dungeon_t7_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=7)

@KING.CALL("cb_collect_t8")
async def collect_dungeon_t8_rewards(client, callback_query):
    await handle_collect_rewards(client, callback_query, tier=8)

@KING.CALL("cancel_dungeon")
async def cancel_dungeon(client, callback_query):
    await callback_query.message.delete()
    await client.send_message(callback_query.from_user.id, "Dungeon dibatalkan")
    await asyncio.sleep(2)
    buttons = [
        [
            InlineKeyboardButton("DUNGEON", callback_data="dungeon_konten"),
            InlineKeyboardButton("WORLD BOSS", callback_data="world_boss"),
        ],
        [
            InlineKeyboardButton("FACTION", callback_data="faction_konten"),
            InlineKeyboardButton("PVP", callback_data="pvp_konten"),
        ],
        [
            InlineKeyboardButton("GVG", callback_data="gvg_konten"),
            InlineKeyboardButton("GATHERING", callback_data="cb_gathering_konten"),
        ],
        [
            InlineKeyboardButton("MAPS", callback_data="^maps"),
            InlineKeyboardButton("BACK", callback_data="start")
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(callback_query.from_user.id, "Pilih menu konten:", reply_markup=reply_markup)
    pass