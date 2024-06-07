import random

async def get_random_monster(tier):
    monsters = {
        3: [
            {
                "name": "Troll",
                "level": 3,
                "max_hp": 300,
                "damage": 35,
                "defense": 20,
                "reward_exp": 90,
                "reward_silver": 300
            },
            {
                "name": "Dark Elf",
                "level": 3,
                "max_hp": 250,
                "damage": 40,
                "defense": 25,
                "reward_exp": 100,
                "reward_silver": 350
            }
        ],
        4: [
            {
                "name": "Ogre",
                "level": 4,
                "max_hp": 400,
                "damage": 50,
                "defense": 30,
                "reward_exp": 130,
                "reward_silver": 500
            },
            {
                "name": "Necromancer",
                "level": 4,
                "max_hp": 350,
                "damage": 55,
                "defense": 35,
                "reward_exp": 150,
                "reward_silver": 550
            }
        ],
        5: [
            {
                "name": "Dragonling",
                "level": 5,
                "max_hp": 500,
                "damage": 60,
                "defense": 40,
                "reward_exp": 180,
                "reward_silver": 700
            },
            {
                "name": "Vampire Lord",
                "level": 5,
                "max_hp": 450,
                "damage": 70,
                "defense": 45,
                "reward_exp": 200,
                "reward_silver": 750
            }
        ],
        6: [
            {
                "name": "Demon",
                "level": 6,
                "max_hp": 600,
                "damage": 80,
                "defense": 50,
                "reward_exp": 230,
                "reward_silver": 900
            },
            {
                "name": "Ancient Lich",
                "level": 6,
                "max_hp": 550,
                "damage": 85,
                "defense": 55,
                "reward_exp": 250,
                "reward_silver": 950
            }
        ],
        7: [
            {
                "name": "Fire Elemental",
                "level": 7,
                "max_hp": 700,
                "damage": 100,
                "defense": 60,
                "reward_exp": 300,
                "reward_silver": 1200
            },
            {
                "name": "Ice Golem",
                "level": 7,
                "max_hp": 650,
                "damage": 110,
                "defense": 65,
                "reward_exp": 320,
                "reward_silver": 1250
            }
        ],
        8: [
            {
                "name": "Ancient Dragon",
                "level": 8,
                "max_hp": 800,
                "damage": 130,
                "defense": 70,
                "reward_exp": 400,
                "reward_silver": 1500
            },
            {
                "name": "Titan",
                "level": 8,
                "max_hp": 750,
                "damage": 140,
                "defense": 75,
                "reward_exp": 450,
                "reward_silver": 1600
            }
        ]
    }
    return random.choice(monsters[tier])