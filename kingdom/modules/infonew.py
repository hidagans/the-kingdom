from pyrogram import filters
from pyrogram.types import *
from kingdom.core import *
from kingdom.database import *
from kingdom.decorators import *

@KING.CALL("cb_update_stats")
async def update_stats_command(client, callback_query):
    response_message = await calculate_total_stats(callback_query.from_user.id)
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="cb_stats"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_text(response_message, reply_markup=reply_markup)


@KING.CALL("cb_inventory")
async def inventory_command(client, callback_query):
    inventory_message, keyboard = await show_inventory(callback_query.from_user.id)
    await callback_query.edit_message_text(inventory_message, reply_markup=keyboard)

@KING.CALL(r"inventory:(headarmor|bodyarmor|footarmor|weapons)(:\d+)?")
async def category_items_command(client, callback_query):
    data = callback_query.data.split(":")
    item_type = data[1]
    start = int(data[2]) if len(data) > 2 else 0
    inventory_message, keyboard = await show_items(callback_query.from_user.id, item_type, start)
    if keyboard:
        await callback_query.edit_message_text(inventory_message, reply_markup=keyboard)
    else:
        await callback_query.answer(inventory_message)

@KING.CALL(r"(use|sell|trash):(headarmor|bodyarmor|footarmor|weapons):(.+)")
async def item_action_command(client, callback_query):
    data = callback_query.data.split(":")
    action = data[0]
    item_type = data[1]
    item_name = data[2]

    if action == "use":
        response_message = await use_item(callback_query.from_user.id, item_type, item_name)
    elif action == "sell":
        response_message = await sell_item(callback_query.from_user.id, item_type, item_name)
    elif action == "trash":
        response_message = await trash_item(callback_query.from_user.id, item_type, item_name)
    
    await callback_query.edit_message_text(response_message)

@KING.CALL("cb_konten")
async def konten_menu(client, callback_query):
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
    await callback_query.edit_message_text("Pilih menu konten:", reply_markup=reply_markup)


@KING.CALL("cb_equipment")
async def equipment_command(client, callback_query):
    equipment_message = await show_equipment(callback_query.from_user.id)
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="my_profile"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.edit_message_text(equipment_message, reply_markup=reply_markup)

@KING.CMD("unequip")
async def unequip_command(client, message):
    # Ambil tipe item dari argumen command
    item_type = message.text.split(' ', 1)[1] if len(message.text.split(' ')) > 1 else ""

    if item_type:
        # Memanggil fungsi unequip_item dengan tipe item yang diberikan
        response_message = await unequip_item(message.from_user.id, item_type)
    else:
        response_message = "Mohon berikan tipe item yang ingin dilepas (headarmor, bodyarmor, footarmor, weapon)."

    # Membalas pesan dengan hasil unequip item
    await message.reply_text(response_message)

@KING.CMD("trade_item")
async def trade_item(client, message):
    try:
        # Parsing pesan perintah untuk mendapatkan detail perdagangan
        command_parts = message.text.split(' ', 2)
        if len(command_parts) != 3:
            await message.reply_text("Gunakan: /trade_item <user_id_tujuan> <nama_item>")
            return

        target_user_id, item_name = command_parts[1], command_parts[2]
        
        # Cari karakter pengguna tujuan dalam database berdasarkan user_id
        target_character = await characters.find_one({"user_id": int(target_user_id)})
        if not target_character:
            await message.reply_text("Karakter pengguna tujuan tidak ditemukan.")
            return

        # Cek apakah pengguna memiliki item yang ingin diperdagangkan
        character = await characters.find_one({"user_id": message.from_user.id})
        if not character:
            await message.reply_text("Karakter tidak ditemukan.")
            return

        inventory = character.get("inventory", [])
        item_to_trade = next((item for item in inventory if item['name'].lower() == item_name.lower()), None)

        if not item_to_trade:
            await message.reply_text(f"Anda tidak memiliki item '{item_name}' di inventory.")
            return

        # Hapus item dari inventory pengguna
        inventory.remove(item_to_trade)

        # Perbarui inventory pengguna di database
        await characters.update_one(
            {"user_id": message.from_user.id},
            {"$set": {"inventory": inventory}}
        )

        # Tambahkan item ke inventory pengguna tujuan
        target_inventory = target_character.get("inventory", [])
        target_inventory.append(item_to_trade)

        # Perbarui inventory pengguna tujuan di database
        await characters.update_one(
            {"user_id": int(target_user_id)},
            {"$set": {"inventory": target_inventory}}
        )

        await message.reply_text(f"Item '{item_name}' berhasil diperdagangkan ke pengguna dengan ID {target_user_id}.")
    except Exception as e:
        print(f"Error in trade_item: {e}")
        await message.reply_text("Terjadi kesalahan saat melakukan perdagangan item.")