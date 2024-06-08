from .__mongo import *

async def get_maps(location):
   await maps.find_one({"location": location})

async def show_gathering_spots(location):
    map_data = await maps.find_one({"location": location})
    return map_data.get("spots", []) if map_data else []