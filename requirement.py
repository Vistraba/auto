import discord
import asyncio
import random
import string
from datetime import datetime

# Bot token
TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual token
CHANNEL_ID = 1341230860854235177

# Color constants 
BLUE = "\033[94m"
RESET = "\033[0m"

# Crypto configurations
CRYPTO_CONFIG = {
    "BTC": {
        "address": "bc1qunllev4fz2q8vq3jwglrklqdrma7366tmxaeuv",
        "explorer": "https://www.blockchain.com/explorer/transactions/btc/"
    },
    "ETH": {
        "address": "0xBa9062c942353c0Ea40d64dfA334fDecE300d9C5",
        "explorer": "https://etherscan.io/tx/"
    },
    "LTC": {
        "address": "LLBZiu4DWjVWTbniDGFBPkev86scG7hcFk",
        "explorer": "https://live.blockcypher.com/ltc/tx/"
    },
    "SOL": {
        "address": "F6W5rnpWPPWirmB8BeUxt7pEdKnqcYgFgQjjfQ2dv7TZ",
        "explorer": "https://solscan.io/tx/"
    }
}

# Crypto Thumbnail URLs (Keeping from original code)
crypto_thumbnails = {
    "LTC": "https://media.discordapp.net/attachments/1271979893680246794/1271980697480855655/Groupe_22.png",
    "ETH": "https://media.discordapp.net/attachments/1271979893680246794/1271980639020908594/Groupe_21.png",
    "SOL": "https://media.discordapp.net/attachments/1271979893680246794/1271980590698336318/image.png",
    "BTC": "https://media.discordapp.net/attachments/1271979893680246794/1271980615981596764/Groupe_14.png",
}


# Transaction ID Generator (Keeping from original code)
def random_txid():
    return f"{random.randint(100000, 999999)}e0...{random.randint(100000, 999999)}d2"

# Generate Random Crypto Data (Modified to use CRYPTO_CONFIG)
def generate_crypto_data(crypto):
    amount = round(random.uniform(0.1, 2), 8)
    #  Price range is missing from edited code, keeping original logic for now
    price = random.uniform(85, 85000) #Using a broad range to cover all cryptos.  Ideally, this would be per crypto.

    usd_value = round(amount * price, 2)
    return amount, usd_value, random_txid()

# Weighted Crypto Selection (Keeping from original code)
embed_weights = ["LTC"] * 4 + ["ETH", "SOL"] * 2 + ["BTC"]

# Discord Bot Setup (Keeping from edited code, but adding necessary intents)
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
client = discord.Client(intents=intents)

class ViewButton(discord.ui.View):
    def __init__(self, crypto):
        super().__init__()
        label, url =  CRYPTO_CONFIG[crypto]["explorer"], CRYPTO_CONFIG[crypto]["explorer"] #Using explorer URL from CRYPTO_CONFIG.

        self.add_item(discord.ui.Button(label=label, url=url))

async def send_random_embed():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("Invalid channel ID!")
        return

    while not client.is_closed():
        crypto = random.choice(embed_weights)
        amount, usd_value, txid = generate_crypto_data(crypto)

        embed = discord.Embed(title=f"{crypto} Deal Complete", color=discord.Color.green())
        embed.add_field(name="Amount", value=f"`{amount}` {crypto} (${usd_value} USD)", inline=False)
        embed.add_field(name="Sender", value="``Anonymous``", inline=True)
        embed.add_field(name="Receiver", value="``Anonymous``", inline=True)
        embed.add_field(name="Transaction", value=f"{txid} [(View Transaction)]({CRYPTO_CONFIG[crypto]['explorer']})", inline=False) #Using CRYPTO_CONFIG for explorer URL.

        embed.set_thumbnail(url=crypto_thumbnails[crypto])
        await channel.send(embed=embed, view=ViewButton(crypto))
        print(f"Sent {crypto} embed with {amount} {crypto} (${usd_value} USD)")

        sleep_time = random.randint(240, 600)
        await asyncio.sleep(sleep_time)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    client.loop.create_task(send_random_embed())

client.run(TOKEN)