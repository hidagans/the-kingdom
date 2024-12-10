from kingdom import *
from kingdom.core import *
from pyrogram import Client, filters
from pyrogram.types import Message

# Fungsi untuk menghapus pesan layanan
async def delete_service_message(message: Message):
    if message.service == "MessageServiceType.NEW_CHAT_MEMBERS":
        await message.delete()
        print(f"Pesan {message.id} berhasil dihapus.")

# Perintah untuk membersihkan pesan sebelumnya
@KING.CMD("clean")
async def clean_service(client: Client, message: Message):
    print("Memulai pembersihan pesan layanan...")
    
    async for msg in client.get_chat_history(message.chat.id, limit=100):
        await delete_service_message(msg)
    
    print("Pembersihan selesai.")
