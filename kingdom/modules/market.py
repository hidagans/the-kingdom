from kingdom.core import *
from kingdom.database import *
from kingdom.decorators import *

@bot.on_callback_query(filters.regex(r"buy_(.*)"))
async def buy_item_callback(client, callback_query: CallbackQuery):
    item_id = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id
    result = await buy_item(user_id, ObjectId(item_id))
    await callback_query.message.delete()
    await bot.send_message(user_id, f"Kamu berhasil membeli {item_id} di market silahkan cek di inventory kamu")
    await callback_query.answer(result, show_alert=True)