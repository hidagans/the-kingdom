from .__mongo import *

async def get_maps(location):
   await maps.find_one({"location": location})