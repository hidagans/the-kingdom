import os

# Bot and API settings
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7177790604:AAFT6fiTEkPAEucGOKmAOKhpDKxRyXNxyoA")
API_ID = int(os.environ.get("API_ID", "21445722"))
API_HASH = os.environ.get("API_HASH", "710f18f90849255dd85837d00d5fe85f")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://tititgoreng:Mantulx10@cluster0.5odosuy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
ADMINS = [int(x) for x in os.environ.get("ADMINS", "6696975845 7091183397 1784606556 1351391711").split()]

# Payment API
XENDIT_API = os.environ.get("XENDIT_API", "xnd_production_YvvvtTET0A7JpHP38jnLgYrMQiw9CttvrKSUe94V2qHaMudck0RVN5qit2XliE")
XENDIT_CALLBACK_TOKEN = '6AwHb7Sv0D1q8YbimDKkXsSU3vOPdTVffmuJSXfkUltc0gkF'

# Groups and channels to join
MUST_JOIN = os.environ.get("MUST_JOIN", "thekingdom_official")
CHANNEL = os.environ.get("CHANNEL_ID", "-1002083228353")

# GAME CONFIGURATION
XP_PER_LEVEL = 800
XP_INCREMENT = 200
