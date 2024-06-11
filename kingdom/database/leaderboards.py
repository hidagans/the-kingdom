from kingdom.database import *
from kingdom import bot
import asyncio

async def get_leaderboard(limit=10):
    try:
        # Mengambil karakter dan mengurutkan berdasarkan nilai EXP (descending)
        cursor = characters.find().sort("stats.Exp", -1).limit(limit)
        leaderboard = await cursor.to_list(length=limit)
        
        if not leaderboard:
            return "Tidak ada karakter yang ditemukan."
        
        # Membuat pesan leaderboard
        leaderboard_message = "🏆 Leaderboard EXP 🏆\n\n"
        for i, character in enumerate(leaderboard, start=1):
            user_id = character.get("user_id")
            username = await get_username(user_id)  # Fungsi untuk mendapatkan username dari user_id
            exp = character.get("stats", {}).get("Exp", 0)
            level = character.get("stats", {}).get("level", 1)
            leaderboard_message += f"{i}. @{username} - Level {level}, EXP {exp}\n"
        
        return leaderboard_message
    except Exception as e:
        logging.error(f"Error in get_leaderboard: {e}")
        return "Terjadi kesalahan saat mengambil leaderboard."

async def get_username(user_id):
    user = await bot.get_users(user_id)
    return user.username if user else "Unknown User"  # Jika user tidak ditemukan