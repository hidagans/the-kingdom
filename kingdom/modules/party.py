from pyrogram import filters
from pyrogram.types import *
from kingdom.database import *
from kingdom.core import *

@KING.CMD("create_party")
async def create_party_command(client, message):
    user_id = message.from_user.id
    if not party_group.find_one({"leader_id": user_id}):
        party_group.insert_one({"leader_id": user_id, "members": [user_id]})
        await message.reply_text("Party created successfully!")
    else:
        await message.reply_text("You already have a party!")

@KING.CMD("join_party")
async def join_party_command(client, message):
    user_id = message.from_user.id
    leader_id = message.text.split()[1]  # Assumes the command is in the format /join_party leader_id
    party = party_group.find_one({"leader_id": leader_id})
    if party:
        party_group.update_one({"leader_id": leader_id}, {"$addToSet": {"members": user_id}})
        await message.reply_text("You have joined the party successfully!")
    else:
        await message.reply_text("Failed to join the party!")

@KING.CMD("invite_party")
async def invite_party_command(client, message):
    user_id = message.from_user.id
    invited_user_id = message.text.split()[1]  # Assumes the command is in the format /invite_party invited_user_id
    party = party_group.find_one({"leader_id": user_id})
    if party:
        party_group.update_one({"leader_id": user_id}, {"$addToSet": {"members": invited_user_id}})
        await message.reply_text("Invitation sent successfully!")
    else:
        await message.reply_text("Failed to send invitation!")

@KING.CMD("disband_party")
async def disband_party_command(client, message):
    user_id = message.from_user.id
    party = party_group.find_one({"leader_id": user_id})
    if party:
        party_group.delete_one({"leader_id": user_id})
        await message.reply_text("Party disbanded successfully!")
    else:
        await message.reply_text("You don't have a party or you are not the leader!")

@KING.CMD("leave_party")
async def leave_party_command(client, message):
    user_id = message.from_user.id
    party = party_group.find_one({"members": user_id})
    if party:
        party_group.update_one({"members": user_id}, {"$pull": {"members": user_id}})
        await message.reply_text("You have left the party!")
    else:
        await message.reply_text("You are not in any party!")