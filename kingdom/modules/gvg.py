from pyrogram import *
from kingdom.core import *
from config import ADMINS
from kingdom.database import *
from pyrogram.types import *

    
@KING.CMD("declarewar")
async def declare_war(message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Gunakan: /declarewar <nama_guild_target>")
        return

    target_guild_name = " ".join(args[1:])
    target_guild = await guild.find_one({"name": target_guild_name})
    if not target_guild:
        await message.reply_text("Guild target tidak ditemukan.")
        return

    user_id = message.from_user.id
    user_guild = await get_guild_info(user_id)
    
    if not user_guild:
        await message.reply_text("Anda tidak berada dalam guild.")
        return

    if user_guild["Leader"] != user_id:
        await message.reply_text("Hanya pemimpin guild yang dapat mendeklarasikan perang.")
        return

    war_data = {
        "guild1_id": user_guild,
        "guild2_id": target_guild["_id"],
        "status": "ongoing",
        "start_time": datetime.utcnow(),
        "completion_time": datetime.utcnow() + timedelta(minutes=30),
        "guild1_points": 0,
        "guild2_points": 0
    }
    await guild_wars.insert_one(war_data)
    await message.reply_text(f"Guild {user_guild['name']} telah mendeklarasikan perang terhadap Guild {target_guild_name}!")

@KING.CMD("guildattack")
async def guild_attack(message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Gunakan: /guildattack <user_id_target>")
        return

    try:
        target_user_id = int(args[1])
    except ValueError:
        await message.reply_text("ID pengguna tidak valid.")
        return

    user_id = message.from_user.id

    user_guild = await guild.find_one({"Members": user_id})
    target_guild = await guild.find_one({"Members": target_user_id})
    if not user_guild or not target_guild:
        await message.reply_text("Anda atau target tidak berada dalam guild.")
        return

    current_war = await guild_wars.find_one({
        "guild1_id": {"$in": [user_guild["_id"], target_guild["_id"]]},
        "guild2_id": {"$in": [user_guild["_id"], target_guild["_id"]]},
        "status": "ongoing"
    })

    if not current_war:
        await message.reply_text("Tidak ada perang yang sedang berlangsung antara guild Anda dan guild target.")
        return

    user_power = sum((await characters.find_one({"user_id": user_id}))["stats"].values())
    target_power = sum((await characters.find_one({"user_id": target_user_id}))["stats"].values())
    damage = random.randint(0, user_power)

    if user_guild["_id"] == current_war["guild1_id"]:
        await guild_wars.update_one(
            {"_id": current_war["_id"]},
            {"$inc": {"guild1_points": damage}}
        )
    else:
        await guild_wars.update_one(
            {"_id": current_war["_id"]},
            {"$inc": {"guild2_points": damage}}
        )

    await message.reply_text(f"Anda menyerang pengguna dengan ID {target_user_id} dan memberikan {damage} kerusakan!")



@KING.CMD("check_war")
async def check_war_command(message):
    user_id = message.from_user.id
    user_guild = await guild.find_one({"Members": user_id})
    if not user_guild:
        await message.reply_text("Anda tidak berada dalam guild.")
        return

    current_war = await guild_wars.find_one({
        "guild1_id": user_guild["_id"],
        "guild2_id": user_guild["_id"],
        "status": "ongoing"
    })

    if not current_war:
        await message.reply_text("Tidak ada perang guild yang sedang berlangsung.")
        return

    current_time = datetime.utcnow()
    if current_time > current_war["completion_time"]:
        result_message = await complete_guild_war(current_war)
        await message.reply_text(result_message)
    else:
        await message.reply_text(f"Perang guild masih berlangsung. Estimasi waktu selesai: {current_war['completion_time'].strftime('%H:%M')} UTC")
