import discord
from discord.ext import commands
import asyncio
import random
import string

# Color constants
GREEN_COLOR = discord.Color.green()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.sender = None
        self.receiver = None

    async def update_roles_embed(self, interaction):
        embed = discord.Embed(
            title="Role Assignment",
            description="Select your role in this transaction",
            color=GREEN_COLOR
        )
        embed.add_field(name="Sender", value=self.sender.mention if self.sender else "Not Selected", inline=True)
        embed.add_field(name="Receiver", value=self.receiver.mention if self.receiver else "Not Selected", inline=True)
        return embed

    @discord.ui.select(
        placeholder="Select cryptocurrency",
        options=[
            discord.SelectOption(label="BTC", emoji="<:h_btc:1345711016658341948>"),
            discord.SelectOption(label="ETH", emoji="<:h_eth:1345711216739352658>"),
            discord.SelectOption(label="LTC", emoji="<:h_ltc:1345711327489953833>"),
            discord.SelectOption(label="SOL", emoji="<:h_solana:1345711555626668056>"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        crypto = select.values[0]

        # Create ticket channel
        category = discord.utils.get(interaction.guild.categories, name=f"cryptocurrency-{crypto.lower()}")
        if not category:
            category = await interaction.guild.create_category(name=f"cryptocurrency-{crypto.lower()}")

        ticket_id = random.randint(1000, 9999)
        channel = await interaction.guild.create_text_channel(
            f"ticket-{ticket_id}",
            category=category,
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
        )

        await interaction.response.send_message(f"Created ticket: {channel.mention}", ephemeral=True)

        # Start inactivity timer
        async def check_inactivity():
            try:
                await asyncio.sleep(300)  # 5 minutes
                await channel.send("Ticket inactive for 5 minutes. Deleting in 5 seconds...")
                await asyncio.sleep(5)
                await channel.delete()
            except discord.NotFound:
                pass  # Channel already deleted

        asyncio.create_task(check_inactivity())

        trade_partner_embed = discord.Embed(
            title="Who are you dealing with?",
            description="Please mention the user or provide their ID",
            color=GREEN_COLOR
        )
        partner_msg = await channel.send(embed=trade_partner_embed)

        def check(m):
            return m.channel == channel and m.author == interaction.user

        try:
            msg = await bot.wait_for("message", timeout=300.0, check=check)
            trader2 = None
            if msg.mentions:
                trader2 = msg.mentions[0]
            elif msg.content.isdigit():
                trader2 = interaction.guild.get_member(int(msg.content))

            if trader2:
                await channel.set_permissions(trader2, read_messages=True, send_messages=True)
                await channel.send(f"{trader2.mention} has been added to the ticket!")
            else:
                await channel.send("Invalid user. Please try again with a valid mention or ID.")
        except asyncio.TimeoutError:
            await channel.send("Timed out. Please try again.")

        roles_embed = await self.update_roles_embed(interaction)
        role_view = RoleView()
        await channel.send(embed=roles_embed, view=role_view)

        # Send crypto address based on selection
        addresses = {
            "BTC": "bc1qunllev4fz2q8vq3jwglrklqdrma7366tmxaeuv",
            "ETH": "0xBa9062c942353c0Ea40d64dfA334fDecE300d9C5",
            "LTC": "LLBZiu4DWjVWTbniDGFBPkev86scG7hcFk",
            "SOL": "F6W5rnpWPPWirmB8BeUxt7pEdKnqcYgFgQjjfQ2dv7TZ"
        }

        welcome_embed = discord.Embed(
            title="Crypto Transaction",
            description=f"Welcome to your {crypto} transaction ticket!",
            color=GREEN_COLOR
        )

        address_embed = discord.Embed(
            title=f"{crypto} Address",
            description=f"```{addresses[crypto]}```",
            color=GREEN_COLOR
        )

        transaction_embed = discord.Embed(
            title="Cryptocurrency Transaction",
            description=f"You have initiated a {crypto} transaction.\nPlease follow the steps below to complete your trade.",
            color=GREEN_COLOR
        )
        transaction_embed.add_field(name="Step 1", value="Add your trade partner", inline=False)
        transaction_embed.add_field(name="Step 2", value="Select roles (Sender/Receiver)", inline=False)
        transaction_embed.add_field(name="Step 3", value="Describe the trade details", inline=False)

        await channel.send(embeds=[transaction_embed, welcome_embed, address_embed])
        await channel.send("Actions:", view=CopyCloseView(addresses[crypto]))


class RoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.sender = None
        self.receiver = None

    @discord.ui.button(label="Sender", style=discord.ButtonStyle.primary)
    async def sender_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.receiver == interaction.user:
            await interaction.response.send_message("You cannot be both sender and receiver!", ephemeral=True)
            return

        self.sender = interaction.user
        embed = discord.Embed(
            title="Role Assignment",
            description="Select your role in this transaction",
            color=GREEN_COLOR
        )
        embed.add_field(name="Sender", value=self.sender.mention, inline=True)
        embed.add_field(name="Receiver", value=self.receiver.mention if self.receiver else "Not Selected", inline=True)

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Receiver", style=discord.ButtonStyle.primary)
    async def receiver_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.sender == interaction.user:
            await interaction.response.send_message("You cannot be both sender and receiver!", ephemeral=True)
            return

        self.receiver = interaction.user
        embed = discord.Embed(
            title="Role Assignment",
            description="Select your role in this transaction",
            color=GREEN_COLOR
        )
        embed.add_field(name="Sender", value=self.sender.mention if self.sender else "Not Selected", inline=True)
        embed.add_field(name="Receiver", value=self.receiver.mention, inline=True)

        await interaction.response.edit_message(embed=embed, view=self)

        if self.sender and self.receiver:
            confirm_embed = discord.Embed(
                title="Roles Confirmed",
                description="Both roles have been assigned. Proceeding with transaction.",
                color=GREEN_COLOR
            )
            await interaction.message.channel.send(embed=confirm_embed)

            trade_details_embed = discord.Embed(
                title="Trade Details",
                description="Please describe what is being traded.\nFor example: 'Trading BTC for PayPal $50'",
                color=GREEN_COLOR
            )
            await interaction.message.channel.send(embed=trade_details_embed)

            def check(m):
                return m.channel == interaction.message.channel and m.author in [self.sender, self.receiver]

            try:
                msg = await bot.wait_for("message", timeout=300.0, check=check)
                trade_confirm_embed = discord.Embed(
                    title="Trade Confirmation",
                    description=f"Trade Details: {msg.content}",
                    color=GREEN_COLOR
                )
                trade_confirm_embed.add_field(name="Sender", value=self.sender.mention, inline=True)
                trade_confirm_embed.add_field(name="Receiver", value=self.receiver.mention, inline=True)
                await interaction.message.channel.send(embed=trade_confirm_embed)
            except asyncio.TimeoutError:
                await interaction.message.channel.send("No trade details provided within 5 minutes. Please try again.")

class CopyCloseView(discord.ui.View):
    def __init__(self, address):
        super().__init__()
        self.address = address

    @discord.ui.button(label="Copy Address", style=discord.ButtonStyle.primary)
    async def copy_address(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"```{self.address}```", ephemeral=True)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f"Bot is ready: {bot.user}")

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.TextChannel) and message.channel.name.startswith("ticket-"):
        # Reset inactivity timer by recreating the channel
        async def check_inactivity():
            try:
                await asyncio.sleep(300)  # 5 minutes
                await message.channel.send("Ticket inactive for 5 minutes. Deleting in 5 seconds...")
                await asyncio.sleep(5)
                await message.channel.delete()
            except discord.NotFound:
                pass  # Channel already deleted

        asyncio.create_task(check_inactivity())

    await bot.process_commands(message)

@bot.command()
async def setup(ctx):
    try:
        await ctx.message.delete()
    except:
        pass  # If message deletion fails, continue anyway

    embed = discord.Embed(
        title="Cryptocurrency Transaction",
        description="Select a cryptocurrency to start a transaction",
        color=GREEN_COLOR
    )
    await ctx.send(embed=embed, view=TicketView())

# Create a secret for BOT_TOKEN
import os
TOKEN = os.environ['DISCORD_TOKEN']
bot.run(TOKEN)