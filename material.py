import pymongo
import logging
from config import MONGO_URL

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = pymongo.MongoClient(MONGO_URL)
database = client["kingdom"]
collection = database["material"]

# Define enchantment levels and material data
enchantment_levels = ['Uncommon', 'Rare', 'Exceptional', 'Pristine']

material_data = {
    'Kayu': {
        1: {'name': 'Rough Logs', 'quantity': 6},
        2: {'name': 'Birch Logs', 'quantity': 6},
        3: {'name': 'Chesnut Logs', 'quantity': 6},
        4: {'name': 'Pine Logs', 'quantity': 5},
        5: {'name': 'Cedar Logs', 'quantity': 5},
        6: {'name': 'Bloodoak Logs', 'quantity': 5},
        7: {'name': 'Ashenbark Logs', 'quantity': 8},
        8: {'name': 'Whitewood Logs', 'quantity': 10},
    },
    'Ore': {
        2: {'name': 'Copper Ore', 'quantity': 6},
        3: {'name': 'Tin Ore', 'quantity': 6},
        4: {'name': 'Iron Ore', 'quantity': 6},
        5: {'name': 'Titanium Ore', 'quantity': 5},
        6: {'name': 'Runite Ore', 'quantity': 5},
        7: {'name': 'Meteorite Ore', 'quantity': 8},
        8: {'name': 'Adamantium Ore', 'quantity': 10},
    },
    'Fiber': {
        2: {'name': 'Cotton', 'quantity': 6},
        3: {'name': 'Flax', 'quantity': 6},
        4: {'name': 'Hemp', 'quantity': 6},
        5: {'name': 'Skyflower', 'quantity': 5},
        6: {'name': 'Amberleaf', 'quantity': 5},
        7: {'name': 'Sunflax', 'quantity': 8},
        8: {'name': 'Ghost Hemp', 'quantity': 10},
    },
    'Stone': {
        1: {'name': 'Rough Stone', 'quantity': 6},
        2: {'name': 'Lime Stone', 'quantity': 6},
        3: {'name': 'Sand Stone', 'quantity': 6},
        4: {'name': 'Travertine', 'quantity': 6},
        5: {'name': 'Granite', 'quantity': 5},
        6: {'name': 'Slate', 'quantity': 5},
        7: {'name': 'Basalt', 'quantity': 8},
        8: {'name': 'Marble', 'quantity': 10},
    },
    'Hide': {
        1: {'name': 'Scraps of Hide', 'quantity': 6},
        2: {'name': 'Rugged Hide', 'quantity': 6},
        3: {'name': 'Thin Hide', 'quantity': 6},
        4: {'name': 'Medium Hide', 'quantity': 6},
        5: {'name': 'Heavy Hide', 'quantity': 5},
        6: {'name': 'Robust Hide', 'quantity': 5},
        7: {'name': 'Thick Hide', 'quantity': 8},
        8: {'name': 'Resilient Hide', 'quantity': 10},
    }
}

# Function to create material documents
def create_material_documents():
    for material_type, tiers in material_data.items():
        for tier, material_info in tiers.items():
            tier_str = str(tier)
            
            # Create base material document
            base_document = {
                "type": material_type,
                "name": f"{material_info['name']} Tier {tier_str}",
                "Level": tier_str,
                "quantity": material_info['quantity'],
                "armor_type": "material_data",
                "enchantment": None
            }
            
            try:
                # Insert base material
                collection.insert_one(base_document)
                logger.info(f"Inserted base material: {base_document['name']}")
            except Exception as e:
                logger.error(f"Error inserting base material: {e}")

            # Create enchanted materials
            if tier > 3:  # Enchantment starts from tier 2
                for enchantment in enchantment_levels:
                    enchanted_document = {
                        "type": material_type,
                        "name": f"{enchantment} {material_info['name']} Tier {tier_str}",
                        "Level": tier_str,
                        "quantity": material_info['quantity'],
                        "armor_type": "material_data",
                        "enchantment": enchantment
                    }
                    
                    try:
                        collection.insert_one(enchanted_document)
                        logger.info(f"Inserted enchanted material: {enchanted_document['name']}")
                    except Exception as e:
                        logger.error(f"Error inserting enchanted material: {e}")

# Run the function to create and insert documents
create_material_documents()

print("Data MATERIAL telah disimpan di database MongoDB.")