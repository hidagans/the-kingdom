from pyrogram import *
from pyrogram.enums import ChatMemberStatus
from kingdom import bot
import asyncio

@bot.on_message(filters.command("ban_all"))
async def ban_all_members(client, message):
    chat_id = -1001637185367
    members = client.get_chat_members(chat_id)
    
    async for member in members:
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            try:
                await client.ban_chat_member(chat_id, member.user.id)
                await asyncio.sleep(1)  # Beri jeda 1 detik antara tiap ban
            except Exception as e:
                await message.reply(f"Gagal memban {member.user.first_name}: {str(e)}")
    
    await message.reply("Semua member telah berhasil di-ban, kecuali admin dan pemilik grup.")

@bot.on_message(filters.command("demote_admin"))
async def demote_admin(client, message):
    if len(message.command) < 2:
        await message.reply("Harap beri ID pengguna atau balas pesan dari admin yang ingin Anda turunkan.")
        return

    user_id = int(message.command[1]) if len(message.command) == 2 else message.reply_to_message.from_user.id
    chat_id = message.chat.id

    try:
        # Menurunkan admin ke level member biasa dengan hanya menggunakan argumen yang didukung
        await client.promote_chat_member(
            chat_id,
            user_id,
            can_change_info=False,
            can_invite_users=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_manage_video_chats=False
        )
        await message.reply("Admin telah berhasil diturunkan menjadi anggota biasa.")
    except Exception as e:
        await message.reply(f"Gagal menurunkan admin: {str(e)}")