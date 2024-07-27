from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from kingdom import bot
from kingdom.database import *
from kingdom.core import KING, FILTERS
from config import ADMINS
from datetime import datetime, timedelta

# Fungsi untuk menampilkan opsi crafting
@bot.on_message(filters.command("craft"))
async def craft_menu(client, message):
    buttons = [
        [InlineKeyboardButton("Craft Gathering Tool", callback_data="craft_gathering_tool")],
        [InlineKeyboardButton("BACK", callback_data="start")]
    ]
    await message.reply_text("Choose an item to craft:", reply_markup=InlineKeyboardMarkup(buttons))

# Fungsi untuk menampilkan opsi alat gathering
@KING.CALL("craft_gathering_tool")
async def craft_gathering_tool(client, callback_query):
    buttons = [
        [InlineKeyboardButton("Craft Pickaxe", callback_data="craft_tool:pickaxe")],
        [InlineKeyboardButton("Craft Axe", callback_data="craft_tool:axe")],
        [InlineKeyboardButton("Craft Sickle", callback_data="craft_tool:sickle")],
        [InlineKeyboardButton("BACK", callback_data="craft")]
    ]
    await callback_query.edit_message_text("Choose a gathering tool to craft:", reply_markup=InlineKeyboardMarkup(buttons))

# Fungsi untuk memulai crafting alat
@KING.CALL(r"craft_tool:(.+)")
async def craft_tool(client, callback_query):
    user_id = callback_query.from_user.id
    tool_type = callback_query.data.split(":")[1]
    
    # Data alat dan bahan yang diperlukan
    tools = {
        "pickaxe": {"Wood": 5, "Ore": 10},
        "axe": {"Wood": 10, "Hide": 5},
        "sickle": {"Fiber": 10, "Wood": 5}
    }
    
    if tool_type not in tools:
        await callback_query.answer("Tool type not recognized.", show_alert=True)
        return
    
    required_resources = tools[tool_type]
    
    # Cek apakah pemain memiliki sumber daya yang cukup
    inventory = await sumber_daya.find_one({"user_id": user_id})
    if not inventory:
        await callback_query.answer("You do not have enough resources.", show_alert=True)
        return
    
    # Cek apakah pemain memiliki semua bahan yang dibutuhkan
    for resource, quantity in required_resources.items():
        if inventory.get(resource, 0) < quantity:
            await callback_query.answer(f"You do not have enough {resource}.", show_alert=True)
            return
    
    # Kurangi bahan dari inventory pemain
    for resource, quantity in required_resources.items():
        await sumber_daya.update_one(
            {"user_id": user_id},
            {"$inc": {resource: -quantity}}
        )
    
    # Tambahkan alat ke inventory pemain
    await sumber_daya.update_one(
        {"user_id": user_id},
        {"$inc": {tool_type: 1}},
        upsert=True
    )
    
    await callback_query.message.reply_text(f"You have successfully crafted a {tool_type}!")
    
    # Kembali ke menu utama crafting
    buttons = [
        [InlineKeyboardButton("Craft Another Tool", callback_data="craft_gathering_tool")],
        [InlineKeyboardButton("BACK", callback_data="start")]
    ]
    await callback_query.edit_message_text("Crafting complete! What would you like to do next?", reply_markup=InlineKeyboardMarkup(buttons))

# Fungsi untuk menampilkan inventory pemain
@KING.CMD("inventory")
async def show_inventory(client, message):
    user_id = message.from_user.id
    inventory = await sumber_daya.find_one({"user_id": user_id})
    
    if not inventory:
        await message.reply_text("Your inventory is empty.")
        return
    
    inventory_text = "Your inventory:\n"
    for item, quantity in inventory.items():
        if item != "_id" and item != "user_id":
            inventory_text += f"{item}: {quantity}\n"
    
    await message.reply_text(inventory_text)

# Fungsi untuk menambahkan bahan ke inventory (untuk testing/admin)
@KING.LORD("add_resource")
async def add_resource(client, message):
    if len(message.command) < 3:
        await message.reply_text("Usage: /add_resource <resource_name> <quantity>")
        return
    
    user_id = message.from_user.id
    resource_name = message.command[1]
    try:
        quantity = int(message.command[2])
    except ValueError:
        await message.reply_text("Quantity must be a number.")
        return
    
    await sumber_daya.update_one(
        {"user_id": user_id},
        {"$inc": {resource_name: quantity}},
        upsert=True
    )
    
    await message.reply_text(f"Added {quantity} {resource_name} to your inventory.")

# Fungsi untuk menambahkan merchant
@KING.LORD("add_merchant")
async def add_merchant(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /add_merchant <merchant_name>")
        return
    
    merchant_name = message.command[1]
    group_id = message.chat.id
    url_grup = await client.export_chat_invite_link(group_id)
    
    existing_merchant = await merchants.find_one({"name": merchant_name})
    if existing_merchant:
        await message.reply_text("Merchant with this name already exists.")
        return
    
    # Tambahkan merchant baru ke database
    await merchants.insert_one({"name": merchant_name, "group_id": group_id, "link": url_grup, "owner": None, "lease_end": None})
    await message.reply_text(f"Merchant '{merchant_name}' telah ditambahkan dengan ID {group_id}.")

# Fungsi untuk memulai lelang merchant
@KING.LORD("start_auction")
async def start_auction(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /start_auction <merchant_name>")
        return
    
    merchant_name = message.command[1]
    merchant = await merchants.find_one({"name": merchant_name})
    
    if not merchant:
        await message.reply_text("Merchant not found.")
        return
    
    if merchant.get("owner"):
        await message.reply_text("This merchant is currently owned by another player.")
        return
    
    await pelelangan.insert_one({"merchant_name": merchant_name, "highest_bid": 0, "highest_bidder": None, "end_time": datetime.utcnow() + timedelta(days=2)})
    await message.reply_text(f"Auction for '{merchant_name}' has started. Use /bid <amount> to place a bid.")

@KING.CMD("bid")
async def place_bid(client, message):
    if len(message.command) < 2:
        await message.reply_text("Usage: /bid <amount>")
        return
    
    try:
        amount = int(message.command[1])
    except ValueError:
        await message.reply_text("Bid amount must be a number.")
        return

    user_id = message.from_user.id
    user = await get_character_profile(user_id)
    
    if not user or user.get("stats", {}).get("Gold", 0) < amount:
        await message.reply_text("You do not have enough gold.")
        return
    
    current_auction = await pelelangan.find_one({}, sort=[("end_time", -1)])
    
    if not current_auction or datetime.utcnow() > current_auction["end_time"]:
        await message.reply_text("No ongoing auction or the auction has ended.")
        return
    
    if amount <= current_auction["highest_bid"]:
        await message.reply_text("Your bid must be higher than the current highest bid.")
        return
    
    await characters.update_one({"user_id": user_id}, {"$inc": {"stats.Gold": -amount}})
    await pelelangan.update_one({"_id": current_auction["_id"]}, {"$set": {"highest_bid": amount, "highest_bidder": user_id}})
    await message.reply_text(f"Your bid of {amount} gold has been placed.")

@KING.LORD("end_auction")
async def end_auction(client, message):
    current_auction = await pelelangan.find_one({}, sort=[("end_time", -1)])
    
    if not current_auction or datetime.utcnow() < current_auction["end_time"]:
        await message.reply_text("The auction is still ongoing.")
        return
    
    highest_bidder = current_auction["highest_bidder"]
    merchant_name = current_auction["merchant_name"]
    
    if highest_bidder:
        await merchants.update_one({"name": merchant_name}, {"$set": {"owner": highest_bidder, "lease_end": datetime.utcnow() + timedelta(days=60)}})
        await message.reply_text(f"{merchant_name} has been leased to user {highest_bidder} for 2 months.")
    else:
        await message.reply_text("No bids were placed.")
    
    await pelelangan.delete_one({"_id": current_auction["_id"]})

@KING.CMD("refine")
async def refine_resource(client, message):
    user_id = message.from_user.id
    user = await get_character_profile(user_id)
    if not user:
        await message.reply_text("User not found.")
        return
    
    merchant = await merchants.find_one({"owner": user_id, "lease_end": {"$gt": datetime.utcnow()}})
    if not merchant:
        await message.reply_text("You do not own a merchant or your lease has expired.")
        return
    
    if len(message.command) < 3:
        await message.reply_text("Usage: /refine <resource_name> <quantity>")
        return
    
    resource_name = message.command[1]
    try:
        quantity = int(message.command[2])
    except ValueError:
        await message.reply_text("Quantity must be a number.")
        return
    
    inventory = await sumber_daya.find_one({"user_id": user_id})
    if not inventory or inventory.get(resource_name, 0) < quantity:
        await message.reply_text("You do not have enough resources.")
        return
    
    # Process refining (for simplicity, let's assume refining returns double the quantity)
    refined_quantity = quantity * 2
    
    await sumber_daya.update_one(
        {"user_id": user_id},
        {"$inc": {resource_name: -quantity, f"refined_{resource_name}": refined_quantity}},
        upsert=True
    )
    
    await message.reply_text(f"Successfully refined {quantity} {resource_name} into {refined_quantity} refined {resource_name}.")
