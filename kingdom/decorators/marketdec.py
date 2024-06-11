from kingdom.database import *
from pyrogram.types import *
import logging
from kingdom import bot

async def send_to_market(item_to_sell, price, item_type, object_id):
    button = [[InlineKeyboardButton("BUY", callback_data=f"buy_{object_id}")]]
    await bot.send_message(-1002179455095, f"""
                      
>ITEM READY TO BUY
Item name : {item_to_sell}
Price : {price} Silver
Kategori : {item_type}
""", reply_markup=InlineKeyboardMarkup(button), message_thread_id=2)


async def sell_item(user_id, item_type, item_name):
    try:
        character = await characters.find_one({"user_id": user_id})
        if character:
            inventory = characters.get("inventory", [])
            item_to_sell = next((item for item in inventory if item['name'] == item_name), None)
            if item_to_sell:
                await bot.send_message(user_id, "Masukkan harga jual untuk item ini:")
                price = await bot.listen(user_id)
                try:
                    price = int(price.text)
                except ValueError:
                    return "Harga yang dimasukkan tidak valid."

                inventory.remove(item_to_sell)
                result = await market.insert_one({
                    "user_id": user_id,
                    "item_name": item_to_sell['name'],
                    "price": price,
                    "item_type": item_type,
                    "item": item_to_sell
                })
                await characters.update_one(
                    {"user_id": user_id},
                    {"$set": {"inventory": inventory}}
                )
                await send_to_market(item_to_sell['name'], price, item_type, result.inserted_id)
                return f"Item {item_name} telah dijual seharga {price} silver dan masuk ke market."
                
            else:
                return f"Item {item_name} tidak ditemukan di inventory."
        else:
            return "Karakter tidak ditemukan."
    except Exception as e:
        logging.error(f"Error in sell_item: {e}")
        return "Terjadi kesalahan saat menjual item."

async def buy_item(user_id, item_id):
    try:
        item_in_market = await market.find_one({"_id": item_id})
        if item_in_market:
            character = await characters.find_one({"user_id": user_id})
            if character:
                price = item_in_market['price']
                if character.get('currency', {}).get('Silver', 0) >= price:
                    character['currency']['Silver'] -= price
                    character['inventory'].append(item_in_market['item'])
                    await characters.update_one(
                        {"user_id": user_id},
                        {"$set": {"inventory": character['inventory'], "currency.Silver": character['currency']['Silver']}}
                    )
                    await market.delete_one({"_id": item_id})

                    return f"Item {item_in_market['item']['name']} telah dibeli seharga {price} Silver."
                else:
                    return "Silver tidak cukup untuk membeli item ini."
            else:
                return "Karakter tidak ditemukan."
        else:
            return "Item tidak ditemukan di market."
    except Exception as e:
        logging.error(f"Error in buy_item: {e}")
        return "Terjadi kesalahan saat membeli item."
