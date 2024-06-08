from kingdom.core import *
from xendit import Xendit
from config import XENDIT_API
from pyrogram import filters
from kingdom.core import KING, FILTERS
from kingdom.database import *

xendit_client = Xendit(api_key=XENDIT_API)

@KING.CMD("topup")
async def topup(client, message):
    try:
        command_parts = message.text.split()
        if len(command_parts) != 2:
            await message.reply("Usage: /topup <amount>")
            return
        
        amount = int(command_parts[1])
        invoice = xendit_client.Invoice.create(
            external_id=f"invoice_{message.from_user.id}_{amount}",
            amount=amount,
            payer_email=message.from_user.username,
            description="Top-up Invoice",
        )

        invoice.insert_one({"_id": invoice.external_id, "user_id": message.from_user.id, "status": "PENDING"})
        await message.reply(f"Please complete your top-up by paying the invoice here: {invoice.invoice_url}")
    except Exception as e:
        print(f"Error: {e}")
        await message.reply("An error occurred while processing your top-up. Please try again later.")

@KING.CMD("status")
async def status(client, message):
    user_id = message.from_user.id
    user_invoices = invoice.find({"user_id": user_id})
    if not user_invoices:
        await message.reply("You have no pending invoices.")
        return

    status_messages = []
    for invoice_data in user_invoices:
        status_messages.append(f"Invoice {invoice_data['_id']}: {invoice_data['status']}")
    
    await message.reply("\n".join(status_messages))

