from kingdom import *
from pyrogram import filters, types
from kingdom.core import KING, FILTERS
from kingdom.database import *
from config import ADMINS
import random
import string

async def create_redeem_code():
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return code

@KING.CMD("redeem")
async def redeem(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) == 1:
        await message.reply_text("Please provide the code to redeem")
    else:
        code = args[1]
        result = await redeemcode.find_one({"redeem_code": code})
        if result:
            if result.get("status") == "redeemed":
                await message.reply_text("This code has already been redeemed.")
            else:
                amount = result.get("amount", 0)
                # Update the character's gold
                await characters.update_one(
                    {"user_id": user_id},
                    {"$inc": {"stats.Gold": amount}}
                )
                # Update the status of the redeem code
                await redeemcode.update_one(
                    {"redeem_code": code},
                    {"$set": {"status": "redeemed"}}
                )
                await message.reply_text(f"Redeem code applied successfully! You've received {amount} gold.")
        else:
            await message.reply_text("Invalid redeem code.")


@KING.LORD("create_topup")
async def create_topup(client, message):
    user_id = message.from_user.id
    args = message.text.split()
    if len(args) == 1:
        await message.reply_text("Please provide the amount to topup")
        return

    amount = args[1]
    try:
        amount = float(amount)
        code = await create_redeem_code()
        await redeemcode.insert_one({"user_id": user_id, "redeem_code": code, "amount": amount})
        await message.reply_text(f"Your redeem code is {code} and you have to topup {amount} to redeem it")
    except ValueError:
        await message.reply_text("Invalid amount. Please provide a numerical value.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
