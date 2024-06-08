from datetime import datetime, timedelta
from pyrogram import Client
from pyrogram.types import *
from kingdom.database import *
from kingdom.decorators import *
from kingdom.core import *

@KING.CALL("world_boss")
async def start_world_boss(client, callback_query):
    user_id = callback_query.from_user.id

    # Cek apakah pemain mencoba memulai pertempuran di luar waktu yang ditentukan
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    spawn_time = find_next_world_boss_spawn(now).strftime("%H:%M")
    buttons = [
        [
            InlineKeyboardButton("BACK", callback_data="cb_konten"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    if abs((datetime.strptime(current_time, "%H:%M") - datetime.strptime(spawn_time, "%H:%M")).total_seconds()) > 180:
        await callback_query.edit_message_text("Pertempuran World Boss hanya dapat dimulai dalam 3 menit setelah waktu spawn yang ditentukan.", reply_markup=reply_markup)
        return

    if await is_in_world_boss(user_id):
        await callback_query.edit_message_text("Anda masih dalam pertempuran world boss. Silakan tunggu sampai selesai sebelum memulai yang lain.", reply_markup=reply_markup)
        return

    if await has_completed_world_boss(user_id):
        await callback_query.edit_message_text("Anda sudah menyelesaikan pertempuran world boss sebelumnya. Silakan tunggu hingga pertempuran selesai sebelum Anda dapat memulai lagi.", reply_markup=reply_markup)
        return

    # Cek waktu saat ini dan cari waktu spawn World Boss berikutnya
    next_spawn_time = find_next_world_boss_spawn(now)

    # Hitung waktu hingga spawn berikutnya
    time_until_spawn = next_spawn_time - now

    # Simpan data pertempuran World Boss ke dalam database
    completion_time = now + timedelta(minutes=30)
    await save_world_boss_data(user_id, completion_time)

    # Kirim pesan bahwa pertempuran World Boss dimulai
    respon_message = f"Pertempuran world boss dimulai! Estimasi waktu selesai: {completion_time.strftime('%H:%M')} WIB"
    await callback_query.edit_message_text(respon_message, reply_markup=reply_markup)


@KING.CMD("collect_world_boss")
async def collect_world_boss_rewards(client: Client, message: Message):
    user_id = message.from_user.id
    if await has_completed_world_boss(user_id):
        await give_world_boss_rewards(user_id)
        await delete_world_boss_data(user_id)
        await send_world_boss_completion_message(user_id)
        await message.reply_text("Hadiah world boss telah dikumpulkan!")
    else:
        await message.reply_text("Anda belum menyelesaikan pertempuran world boss ini.")