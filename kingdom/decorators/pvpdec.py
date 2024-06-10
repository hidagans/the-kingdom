from kingdom.database import *
from datetime import *

async def start_pvp(user_id: int, opponent_id: int, message):
    if user_id == opponent_id:
        await message.reply_text("Anda tidak bisa menyerang diri sendiri.")
        return

    in_pvp = await is_in_pvp(user_id)
    if in_pvp:
        await message.reply_text("Anda masih dalam pertempuran PVP. Silakan tunggu sampai selesai sebelum memulai yang lain.")
        return

    current_time = datetime.utcnow()
    completion_time = current_time + timedelta(minutes=5)
    
    pvp_data = {
        "user_id": user_id,
        "opponent_id": opponent_id,
        "start_time": current_time,
        "completion_time": completion_time,
        "status": "ongoing"
    }
    await pvp_matches.insert_one(pvp_data)

    reply_text = (
        f"Pertempuran PVP dimulai! Lawan Anda adalah pengguna dengan ID {opponent_id}.\n"
        f"Estimasi waktu selesai: {completion_time.strftime('%H:%M')} UTC"
    )
    await message.reply_text(reply_text)
