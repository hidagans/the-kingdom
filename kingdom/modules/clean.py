from kingdom import *
from kingdom.core import *
from pyrogram import *
from pyrogram.types import *

async def delete_service_message(message):
    if message.service == "MessageServiceType.NEW_CHAT_MEMBERS":
        await message.delete()
        print(f"Pesan {message.id} berhasil dihapus.")

@KING.CMD("clean")
async def clean_service(client, message):
    print("Proses gan...")
    await delete_service_message(message)
