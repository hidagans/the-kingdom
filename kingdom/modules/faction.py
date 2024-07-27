from pyrogram import filters
from kingdom.core import *
from kingdom.database import *
from bson import ObjectId
from datetime import datetime, timedelta
import asyncio
from pyrogram.types import *
from config import *

@KING.CALL("faction_konten")
async def outpost_konten(client, callback_query):
    location = callback_query.message.chat.id
    outposts_cursor = await get_outpost(location)
    
    outposts = await outposts_cursor.to_list(length=None)
    
    if not outposts:
        await callback_query.answer("Outpost tidak ditemukan!", show_alert=True)
        return

    total_outposts = len(outposts)
    
    buttons = [
        [InlineKeyboardButton(f"Outpost {outpost['outpost_number']}", callback_data=f"attack:{outpost['_id']}")] for outpost in outposts
    ]

    buttons.append([InlineKeyboardButton("Back", callback_data="cb_konten")])

    outpost_list_inline_keyboard = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_text(f"Total outposts available: {total_outposts}\n\nPilih Outpost:", reply_markup=outpost_list_inline_keyboard)

@KING.CMD("register_faction")
async def register_faction(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: /register_faction <faction_name>")
        return

    faction_name = " ".join(args[1:])
    in_faction = await check_user_in_faction(user_id)
    if in_faction:
        await message.reply_text("You are already registered in a faction.")
        return

    faction = await get_faction(faction_name)
    if not faction:
        await message.reply_text("Faction not found.")
        return

    faction_id = faction["_id"]

    try:
        await characters.update_one({"user_id": user_id}, {"$set": {"faction_id": faction_id}})
        await faction.update_one({"_id": faction_id}, {"$addToSet": {"members": user_id}})
        await message.reply_text(f"Successfully registered in faction {faction_name}.")
    except Exception as e:
        print(f"Error in register_faction: {e}")
        await message.reply_text("An error occurred while registering in the faction.")

@KING.CALL(r"attack:(.+)")
async def attack_outpost_command(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data.split(":")
    outpost_id = data[1]
    
    try:
        outpost_id = ObjectId(outpost_id)
    except:
        await callback_query.edit_message_text("Invalid outpost ID format.")
        return

    user = await get_character_profile(user_id)
    if not user:
        await callback_query.edit_message_text("User not found.")
        return

    outpost = await get_outpost(outpost_id)
    if not outpost:
        await callback_query.edit_message_text("Outpost not found.")
        return

    if user['faction_id'] == outpost['faction_id']:
        await callback_query.edit_message_text("You cannot attack your own faction's outpost.")
        return

    damage = user['stats'].get('damage', 0)
    if damage <= 0:
        await callback_query.edit_message_text("You do not have enough power to attack.")
        return

    new_guard_hp = outpost['guard_hp'] - damage

    if user_id not in outpost_attackers.get(outpost_id, []):
        new_guard_hp += int(outpost['guard_hp'] * 0.02)  # Increase guard HP by 2%
        if new_guard_hp > 9000:
            new_guard_hp = 9000  # Ensure HP does not exceed the maximum

        if outpost_id not in outpost_attackers:
            outpost_attackers[outpost_id] = []
        outpost_attackers[outpost_id].append(user_id)

    await update_outpost_guard_hp(outpost_id, new_guard_hp)
    outpost_last_attack_times[outpost_id] = datetime.now()
    await callback_query.edit_message_text(f"Outpost guard's HP is now {new_guard_hp}")

    # Update user HP
    await update_user_hp(user_id, damage // 10)  # Example: user takes 10% of the damage they deal

    # Start the regeneration process if not already started
    if outpost_id not in outpost_last_attack_times:
        asyncio.create_task(regen_guard_hp(outpost_id))

    if new_guard_hp <= 0:
        await change_outpost_faction(outpost_id, user['faction_id'])
        await callback_query.edit_message_text(f"Congratulations! You have successfully captured the outpost!")

@KING.CMD("outpost_status")
async def outpost_status_command(client, message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply_text("Usage: /outpost_status <outpost_id>")
        return

    outpost_id = args[1]
    try:
        outpost_id = ObjectId(outpost_id)
    except:
        await message.reply_text("Invalid outpost ID format.")
        return

    outpost = await get_outpost(outpost_id)
    if not outpost:
        await message.reply_text("Outpost not found.")
        return

    faction = await faction.find_one({"_id": outpost['faction_id']})
    faction_name = faction['name'] if faction else "Unknown"

    status_message = (
        f"Controlled by: {faction_name}\n"
        f"Guard HP: {outpost['guard_hp']}\n"
        f"Location: {outpost['location']}"
    )

    await message.reply_text(status_message)

@KING.CMD("add_outpost")
async def add_outpost_command(client, message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply_text("Usage: /add_outpost <outpost_number> <faction_name>")
        return

    location = message.chat.id
    outpost_number = args[1].strip()
    faction_name = args[2]

    # Periksa apakah nomor pos valid
    if not outpost_number.isdigit():
        await message.reply_text("Invalid outpost number. Please provide a valid number.")
        return

    faction_data = await faction.find_one({"name": faction_name})
    if not faction_data:
        await message.reply_text("Faction not found.")
        return

    faction_id = faction_data["_id"]

    outpost_data = {
        "location": location,
        "outpost_number": outpost_number,
        "guard_hp": 9000,
        "faction_id": faction_id
    }

    try:
        result = await outpost.insert_one(outpost_data)
        await message.reply_text(
            f"Outpost added successfully:\n"
            f"Outpost Number: {outpost_number}\n"
            f"Faction Name: {faction_name}\n"
            f"Outpost ID: {result.inserted_id}"
        )
    except Exception as e:
        print(f"Error in add_outpost_command: {e}")
        await message.reply_text("An error occurred while adding the outpost.")

