import discord
from discord.ext import commands
from discord.ui import View, Button, Select
import asyncio
import time
from datetime import datetime, timedelta
import random
import string


BLUE = "\033[94m"
RESET = "\033[0m"

print(f"{BLUE}"
      "$$$$$$$\\   $$$$$$\\  $$$$$$$\\  $$\\      $$\\ $$$$$$$$\\ $$$$$$$$\\  $$$$$$\\  $$\\   $$\\ \n"
      "$$  __$$\\ $$  __$$\\ $$  __$$\\ $$$\\    $$$ |$$  _____|\\__$$  __|$$  __$$\\ $$$\\  $$ |\n"
      "$$ |  $$ |$$ /  $$ |$$ |  $$ |$$$$\\  $$$$ |$$ |         $$ |   $$ /  $$ |$$$$\\ $$ |\n"
      "$$$$$$$\\ |$$$$$$$$ |$$ |  $$ |$$\\$$\\$$ $$ |$$$$$\\       $$ |   $$$$$$$$ |$$ $$\\$$ |\n"
      "$$  __$$\\ $$  __$$ |$$ |  $$ |$$ \\$$$  $$ |$$  __|      $$ |   $$  __$$ |$$ \\$$$$ |\n"
      "$$ |  $$ |$$ |  $$ |$$ |  $$ |$$ |\\$  /$$ |$$ |         $$ |   $$ |  $$ |$$ |\\$$$ |\n"
      "$$$$$$$  |$$ |  $$ |$$$$$$$  |$$ | \\_/ $$ |$$$$$$$$\\    $$ |   $$ |  $$ |$$ | \\$$ |\n"
      "\\_______/ \\__|  \\__|\\_______/ \\__|     \\__|\\________|   \\__|   \\__|  \\__|\\__|  \\__|\n"
      f"{RESET}")

TOKEN = "MTM1NTMwMDU2NzMzNzE0MDI4NQ.GthCI5.Tw1ZOgg28JgcbJw1JnDo98WFZdF36l99rqqROU"
GUILD_ID = 1341230221038452879 
ADMIN_ROLE_ID = 1341231407480967198  
REQUIRED_ROLE_ID = 1341231890014801959

CRYPTO_CONFIG = {
    "BTC": {
        "name": "Bitcoin",
        "address": "bc1qunllev4fz2q8vq3jwglrklqdrma7366tmxaeuv",
        "rate": 85000.00,
        "emoji_id": "1344677301383598173"
    },
    "ETH": {
        "name": "Ethereum",
        "address": "0xBa9062c942353c0Ea40d64dfA334fDecE300d9C5",
        "rate": 2100.00,
        "emoji_id": "1160945873652547584"
    },
    "LTC": {
        "name": "Litecoin",
        "address": "LLBZiu4DWjVWTbniDGFBPkev86scG7hcFk",
        "rate": 95.43,
        "emoji_id": "1344678874549850163"
    },
    "SOL": {
        "name": "Solana",
        "address": "F6W5rnpWPPWirmB8BeUxt7pEdKnqcYgFgQjjfQ2dv7TZ",
        "rate": 150.20,
        "emoji_id": "1344678838650798091"
    }
}

GREEN_COLOR = discord.Color.green()
RED_COLOR = discord.Color.red()

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="p", intents=intents)

async def safe_delete(message):
    try:
        await message.delete()
    except discord.errors.NotFound:
        
        pass
    except Exception as e:
        print(f"Error deleting message: {e}")

# --------------------------- [Close Button Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

class CloseButton(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(embed=discord.Embed(description="🗑️ This ticket will be deleted in 5 seconds.", color=RED_COLOR))
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --------------------------- [ Role Assignment Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

class RoleAssignment(View):
    def __init__(self, crypto_type):
        super().__init__()
        self.sender = None
        self.receiver = None
        self.crypto_type = crypto_type
        self.role_message = None 

    async def send_initial_embed(self, interaction):
        
        embed = discord.Embed(
            title="Role Assignment",
            description="Select one of the following buttons that corresponds to your role in this deal.\n"
                        "Once selected, both users must confirm to proceed.",
            color=GREEN_COLOR
        )
        embed.add_field(name="**Sender**", value="None", inline=True)
        embed.add_field(name="**Receiver**", value="None", inline=True)
        embed.set_footer(text="The ticket will be closed in 30 minutes if left unattended")

        self.role_message = await interaction.channel.send(embed=embed, view=self)

    async def update_embed(self, interaction):
        embed = discord.Embed(
            title="Role Assignment", 
            description="Select one of the following buttons that corresponds to your role in this deal.\nOnce selected, both users must confirm to proceed.", 
            color=GREEN_COLOR
        )
        embed.add_field(name="**Sender**", value=f"{self.sender.mention if self.sender else 'None'}", inline=True)
        embed.add_field(name="**Receiver**", value=f"{self.receiver.mention if self.receiver else 'None'}", inline=True)
        embed.set_footer(text="The ticket will be closed in 30 minutes if left unattended")
        
        # Update button states based on selected roles
        for child in self.children:
            if isinstance(child, Button):
                if child.custom_id == "sender":
                    child.disabled = bool(self.sender)
                elif child.custom_id == "receiver":
                    child.disabled = bool(self.receiver)
        
        # Store the message reference if not already stored
        if not self.role_message:
            self.role_message = interaction.message
            
        await interaction.message.edit(embed=embed, view=self)

        
        if self.sender and self.receiver:
            await asyncio.sleep(1)
            
            
            if self.role_message:
                await safe_delete(self.role_message)

            
            role_confirm = RoleConfirmation(self.sender, self.receiver, self.crypto_type)
            
            
            role_confirm.role_confirmation_message = await interaction.channel.send(
                embed=self.get_confirmation_embed(), 
                view=role_confirm
            )

    def get_confirmation_embed(self):
        
        confirmation_embed = discord.Embed(
            title="Role Confirmation", 
            description="Both roles are assigned. Please confirm to proceed.", 
            color=GREEN_COLOR
        )
        confirmation_embed.add_field(name="**Sender**", value=f"{self.sender.mention}", inline=True)
        confirmation_embed.add_field(name="**Receiver**", value=f"{self.receiver.mention}", inline=True)
        return confirmation_embed

    @discord.ui.button(label="Sender", style=discord.ButtonStyle.grey, custom_id="sender")
    async def sender_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user == self.receiver:
            await interaction.response.send_message("You cannot be both sender and receiver!", ephemeral=True)
            return
        self.sender = interaction.user
        await interaction.response.defer()
        await self.update_embed(interaction)

    @discord.ui.button(label="Receiver", style=discord.ButtonStyle.grey, custom_id="receiver")
    async def receiver_button(self, interaction: discord.Interaction, button: Button):
        
        warning_embed = discord.Embed(
            description="You selected receiver. Sending money to the bot will result in getting scammed.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=warning_embed, ephemeral=True)
        
        if interaction.user == self.sender:
            await interaction.followup.send("You cannot be both sender and receiver!", ephemeral=True)
            return
        self.receiver = interaction.user
        await self.update_embed(interaction)

    @discord.ui.button(label="Reset", style=discord.ButtonStyle.red, custom_id="reset")
    async def reset_button(self, interaction: discord.Interaction, button: Button):
        self.sender = None
        self.receiver = None
        await interaction.response.defer()
        await self.update_embed(interaction)

# --------------------------- [ RoleConfirmation Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

class RoleConfirmation(View):
    def __init__(self, sender, receiver, crypto_type):
        super().__init__()
        self.confirmed_users = set()
        self.sender = sender
        self.receiver = receiver
        self.crypto_type = crypto_type
        self.confirmation_messages = []
        self.amount_confirmed = False
        self.amount_embed_message = None  
        self.role_confirmation_message = None

        self.user_confirmed = {
            sender.id: False,
            receiver.id: False
        }

    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_role")
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in self.user_confirmed:
            await interaction.response.send_message("You are not part of this trade!", ephemeral=True)
            return

        if self.user_confirmed[interaction.user.id]:
            await interaction.response.send_message("You have already confirmed your role!", ephemeral=True)
            return

        
        self.user_confirmed[interaction.user.id] = True
        self.confirmed_users.add(interaction.user.id)

        
        if self.role_confirmation_message is None:
            self.role_confirmation_message = interaction.message

        
        await interaction.response.defer()

        
        confirm_embed = discord.Embed(description=f"{interaction.user.mention} has confirmed their role.", color=GREEN_COLOR)
        confirm_message = await interaction.followup.send(embed=confirm_embed)
        self.confirmation_messages.append(confirm_message)

        
        if len(self.confirmed_users) == 2:
            await asyncio.sleep(2) 

            
            for msg in self.confirmation_messages:
                await safe_delete(msg)

            
            if self.role_confirmation_message:
                await safe_delete(self.role_confirmation_message)
                self.role_confirmation_message = None  # Clear reference after deletion


            if not self.amount_confirmed:
                self.amount_confirmed = True  # Prevent duplicate amount requests

                # Ask for trade amount
                amount_embed = discord.Embed(
                    title="Deal Amount",
                    description="State the amount the bot is expected to receive in USD (e.g., 100.59)",
                    color=discord.Color(16776960)
                )
                amount_embed.set_footer(text="Ticket will be closed in 30 minutes if left unattended")
                self.amount_embed_message = await interaction.channel.send(f"{self.sender.mention}", embed=amount_embed)

                def check(m):
                    content = m.content.replace('$', '', 1).strip()
                    return (m.author == self.sender and
                            m.channel == interaction.channel and
                            content.replace('.', '', 1).isdigit() and content.count('.') <= 1)

                try:
                    amount_msg = await interaction.client.wait_for("message", timeout=120.0, check=check)

                    # Delete the amount embed message after sender inputs amount
                    await safe_delete(self.amount_embed_message)

                    amount = amount_msg.content.strip()
                    if not amount.startswith('$'):
                        amount = f"${amount}"

                    confirmation_embed = discord.Embed(
                        title="Amount Confirmation",
                        description="Confirm that the bot will receive the following USD value",
                        color=GREEN_COLOR
                    )
                    confirmation_embed.add_field(name="Amount", value=amount, inline=False)

                    # Transition to AmountConfirmation view
                    await interaction.channel.send(
                        embed=confirmation_embed,
                        view=AmountConfirmation(self.sender, self.receiver, amount, self.crypto_type)
                    )

                except asyncio.TimeoutError:
                    await interaction.channel.send(
                        embed=discord.Embed(
                            title="Timeout",
                            description="Trade amount not provided. Please restart the process.",
                            color=RED_COLOR
                        )
                    )

    @discord.ui.button(label="Incorrect", style=discord.ButtonStyle.grey, custom_id="incorrect_role")
    async def incorrect_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()

        # Delete previous confirmation messages
        for msg in self.confirmation_messages:
            await safe_delete(msg)

        # Delete previous role confirmation message
        if self.role_confirmation_message:
            print(f"Deleting previous role confirmation message: {self.role_confirmation_message.id}")  # Debugging
            await safe_delete(self.role_confirmation_message)
            self.role_confirmation_message = None  # Clear reference

        # Resend the role assignment embed
        embed = discord.Embed(
            title="Role Assignment",
            description="Select one of the following buttons that corresponds to your role in this deal.\n"
                        "Once selected, both users must confirm to proceed.",
            color=GREEN_COLOR
        )
        embed.add_field(name="**Sender**", value=f"{self.sender.mention if self.sender else 'None'}", inline=True)
        embed.add_field(name="**Receiver**", value=f"{self.receiver.mention if self.receiver else 'None'}", inline=True)
        
        # Store the new role confirmation message for deletion later
        self.role_confirmation_message = await interaction.channel.send(embed=embed, view=RoleAssignment(self.crypto_type))
        print(f"New role confirmation message set: {self.role_confirmation_message.id}")  # Debugging




class ReleaseView(discord.ui.View):
    def __init__(self, sender, receiver, channel, crypto_type, formatted_crypto_amount, amount_usd):
        super().__init__(timeout=None)
        self.sender = sender
        self.receiver = receiver
        self.channel = channel
        self.crypto_type = crypto_type
        self.formatted_crypto_amount = formatted_crypto_amount
        self.amount_usd = amount_usd
        self.deal_completed = False

    @discord.ui.button(label="Release", style=discord.ButtonStyle.green, custom_id="release_funds")
    async def release_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Only the sender can release funds
        if interaction.user.id != self.sender.id:
            await interaction.response.send_message("Only the sender can release the funds!", ephemeral=True)
            return

        # Prevent multiple releases
        if self.deal_completed:
            await interaction.response.send_message("This deal has already been completed!", ephemeral=True)
            return

        # Mark deal as completed to prevent duplicate releases
        self.deal_completed = True
        
        # Disable the button after it's clicked
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # Create and send payment released embed
        payment_released_embed = discord.Embed(
            title="Payment Released",
            description=f"The {self.crypto_type} has been released successfully to the address provided!",
            color=discord.Color.green()
        )
        
        payment_released_embed.add_field(
            name="Amount", 
            value=f"{self.formatted_crypto_amount} {self.crypto_type} ({self.amount_usd} USD)", 
            inline=False
        )
        
        transaction_id_release = "WTWYLu...ub2wH9"
        payment_released_embed.add_field(
            name="Transaction", 
            value="[View Transaction](https://live.blockcypher.com/ltc/tx/dc3bcc61de31d8b8bc6c6559f44e38b408cca48dc91578ba6b14b73ef181a41a)", 
            inline=False
        )
        
        
        payment_released_embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1153826027714379866/1264288617644163153/Money_release_Anim.gif?ex=67e64247&is=67e4f0c7&hm=a553081ec8870a169ba58ee8532908e3093a9613b852f2bdcf8b0122c9fb7579&=&width=510&height=510"
        )
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"View on {self.crypto_type} Explorer", url="https://blockchain.com"))
        await self.channel.send(embed=payment_released_embed, view=view)
        
        # Send "Deal Complete!" embed
        deal_complete_embed = discord.Embed(
            title="Deal Complete!",
            description="Thanks for using Halal! This deal is now marked as complete.\n\nWe hope you are satisfied with our service. If you would like to make your vouch public, use the command /setprivacy!\n\nThis ticket will be closed in 5 minutes",
            color=discord.Color.green()
        )
        
        deal_complete_view = discord.ui.View()
        deal_complete_view.add_item(discord.ui.Button(label="Close", style=discord.ButtonStyle.secondary, custom_id="close_ticket"))
        await self.channel.send(embed=deal_complete_embed, view=deal_complete_view)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_deal")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Anyone in the deal can cancel
        if interaction.user.id not in [self.sender.id, self.receiver.id]:
            await interaction.response.send_message("You are not part of this deal!", ephemeral=True)
            return
            
        # Confirm cancellation
        cancel_embed = discord.Embed(
            title="Deal Cancelled",
            description=f"{interaction.user.mention} has cancelled this deal. The funds will be returned to the sender.",
            color=discord.Color.red()
        )
        
        # Disable buttons after cancellation
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        
        # Send cancellation message
        await self.channel.send(embed=cancel_embed)
        
        
        close_view = discord.ui.View()
        close_view.add_item(discord.ui.Button(label="Close Ticket", style=discord.ButtonStyle.secondary, custom_id="close_ticket"))
        async def close_ticket(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message(embed=discord.Embed(description="🗑️ This ticket will be deleted in 5 seconds.", color=RED_COLOR))
            await asyncio.sleep(5)
            await interaction.channel.delete()
        await self.channel.send("This ticket will automatically close in 5 minutes or you can close it now.", view=close_view)

# --------------------------- [ AmountConfirmation Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------


class AmountConfirmation(View):
    def __init__(self, sender, receiver, amount, crypto_type):
        super().__init__()
        self.confirmed_users = set()
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.crypto_type = crypto_type
        self.confirmation_messages = []
        self.transaction_check_task = None
        self.deal_processed = False  # Flag to track if deal processing has started
        self.fee_payer = None  # Track who pays the fee
        self.fee_amount = 0  # Track fee amount
        self.fee_split = False  # Track if fee is split

        self.user_confirmed = {
            sender.id: False,
            receiver.id: False
        }

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_amount")
    async def confirm_amount_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in self.user_confirmed:
            await interaction.response.send_message("You are not part of this trade!", ephemeral=True)
            return

        if self.user_confirmed[interaction.user.id]:
            await interaction.response.send_message("You have already confirmed the amount!", ephemeral=True)
            return

        # Set user as confirmed
        self.user_confirmed[interaction.user.id] = True
        self.confirmed_users.add(interaction.user.id)
        
        # Don't disable the button - just send an ephemeral message confirming
        await interaction.response.send_message("You've confirmed the amount!", ephemeral=True)
        
        # Send confirmation message
        confirm_embed = discord.Embed(description=f"{interaction.user.mention} has confirmed the deal amount.", color=GREEN_COLOR)
        confirm_message = await interaction.channel.send(embed=confirm_embed)
        self.confirmation_messages.append(confirm_message)

        # Only process the deal once both users have confirmed and it hasn't been processed yet
        if len(self.confirmed_users) == 2 and not self.deal_processed:
            # Set flag to prevent duplicate processing
            self.deal_processed = True
            
            await asyncio.sleep(2)

            # Delete the confirmation message
            await safe_delete(interaction.message)

            # Delete confirmation messages
            for msg in self.confirmation_messages:
                await safe_delete(msg)

            # Calculate fee
            usd_amount = float(self.amount.replace('$', '').strip())
            if usd_amount < 50:
                # Skip fee selection for deals under $50 and proceed directly to deal summary
                self.fee_amount = 0  # FREE for deals under $50
                await self.process_deal_after_fee_selection(interaction)
            else:
                # For deals $50 and above, set the fee to a flat $2
                self.fee_amount = 2  
                
                # Create and send fee payment embed
                fee_embed = discord.Embed(
                    title="Fee Payment",
                    description="Select one of the corresponding buttons to select which user will be paying the Middleman fee.\n\nFee will be deducted from the balance once the deal is complete.",
                    color=discord.Color.light_gray()
                )
                
                fee_embed.add_field(
                    name="Fee",
                    value=f"${self.fee_amount:.2f}"
                )
                
                fee_embed.set_footer(text="Deals $50+: $2 | Deals under $50 are FREE.")
                
                # Create fee selection view with 4 buttons
                fee_view = FeeSelectionView(self)
                await interaction.channel.send(embed=fee_embed)
            
    async def process_deal_after_fee_selection(self, interaction):
        crypto_info = CRYPTO_CONFIG.get(self.crypto_type, CRYPTO_CONFIG["BTC"])
        
        sender_role_ids = [role.id for role in self.sender.roles]
        has_required_role = 1355172230048387072 in sender_role_ids
        
        deal_summary_embed = discord.Embed(
            title="📝 Deal Summary",
            description="Refer to this deal summary for any reaffirmations. Notify staff for any support required.",
            color=discord.Color.light_gray()
        ) 
        
        deal_summary_embed.add_field(name="Sender", value=f"{self.sender.mention}", inline=True)
        deal_summary_embed.add_field(name="Receiver", value=f"{self.receiver.mention}", inline=True)
        deal_summary_embed.add_field(name="Deal Value", value=f"{self.amount}", inline=True)
        deal_summary_embed.add_field(name="Coin", value=f"\n<:{self.crypto_type.lower()}:{crypto_info['emoji_id']}> {crypto_info['name']} ({self.crypto_type})", inline=False)
    
        if self.fee_amount > 0:
            if self.fee_split:
                fee_text = f"Split between {self.sender.mention} and {self.receiver.mention}"
            elif self.fee_payer == "sender":
                fee_text = f"Paid by {self.sender.mention}"
            elif self.fee_payer == "receiver":
                fee_text = f"Paid by {self.receiver.mention}"
            else:
                fee_text = "Fee payment method not selected"
        
            deal_summary_embed.add_field(name="Fee", value=f"${self.fee_amount:.2f} - {fee_text}", inline=False)
        else:
            deal_summary_embed.add_field(name="Fee", value="FREE", inline=False)
        
        deal_summary_embed.set_thumbnail(url="https://media.discordapp.net/attachments/1153826027714379866/1264288616801243156/Summary_Anim.gif?ex=67c15847&is=67c006c7&hm=758bdcde671ed4d8c11b1ffc2b14dabe1ed40470ec04a3931223aa6ce1fbd2f2&=&width=510&height=510")

        usd_amount = float(self.amount.replace('$', '').strip())
        crypto_rate = crypto_info['rate']  
        crypto_fee_amount = 0
        if self.fee_amount > 0:
            crypto_fee_amount = self.fee_amount / crypto_rate
        
        final_amount = usd_amount
        fee_description = ""
        
        if self.fee_amount > 0:
            if self.fee_payer == "sender":
                final_amount = usd_amount + self.fee_amount
                fee_description = f" (includes ${self.fee_amount:.2f} fee)"
            elif self.fee_split:
                final_amount = usd_amount + (self.fee_amount / 2)
                fee_description = f" (includes ${self.fee_amount/2:.2f} split fee)"
                       
        crypto_amount = final_amount / crypto_rate
        formatted_crypto_amount = f"{crypto_amount:.8f}"

    
        payment_invoice_embed = discord.Embed(
            title="💸 Payment Invoice",
            description="**Send the funds as part of the deal to the Middleman address specified below. Please copy the amount provided.**",
            color=discord.Color.light_gray()
        )

        payment_invoice_embed.add_field(
            name="Address",
            value=f"`{crypto_info['address']}`"  
        )
        
        payment_invoice_embed.add_field(
            name="Amount",
            value=f"`{formatted_crypto_amount}` {self.crypto_type} (${final_amount:.2f} USD{fee_description})"
        )

        payment_invoice_embed.set_footer(text=f"Exchange Rate: 1 {self.crypto_type} = ${crypto_rate:.2f} USD")

        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={crypto_info['address']}"
        payment_invoice_embed.set_thumbnail(url=qr_url)

        
        copy_view = CopyButton(crypto_info['address'], formatted_crypto_amount, self.crypto_type, crypto_info['emoji_id'])
    
    
        await interaction.channel.send(embeds=[deal_summary_embed, payment_invoice_embed], view=copy_view)

    
        await_embed = discord.Embed(
            description="<a:Loading:1354759378426925126> Awaiting transaction...", 
            color=discord.Color.dark_grey()
        )
        await_msg = await interaction.channel.send(embed=await_embed)

        if self.transaction_check_task is None:
            self.transaction_check_task = asyncio.create_task(self.check_transaction_timeout(interaction.channel, await_msg))

        
    async def check_transaction_timeout(self, channel, await_msg):
        try:
            crypto_info = CRYPTO_CONFIG.get(self.crypto_type, CRYPTO_CONFIG["BTC"])  
            sender_role_ids = [role.id for role in self.sender.roles]
            has_required_role = 1355172230048387072 in sender_role_ids
        
            if has_required_role:
                
            
                class SendTransactionView(discord.ui.View):
                    def __init__(self, sender, channel, crypto_info, receiver, amount, crypto_type):
                        super().__init__()
                        self.sender = sender
                        self.channel = channel
                        self.crypto_info = crypto_info
                        self.receiver = receiver
                        self.amount = amount
                        self.crypto_type = crypto_type
                
                    @discord.ui.button(label="Send", style=discord.ButtonStyle.green)
                    async def send_transaction(self, interaction: discord.Interaction, button: discord.ui.Button):
                        if interaction.user.id != self.sender.id:
                            await interaction.response.send_message("Only the sender can click this button.", ephemeral=True)
                            return
                        
                        await interaction.response.send_message("Transaction Sent", ephemeral=True)
                    
                        for item in self.children:
                            item.disabled = True
                        await interaction.message.edit(view=self)
                    
                        transaction_detected_embed = discord.Embed(
                            title=" <:checkmark:1354759510002241590> Transaction has been detected",
                            description="Wait for the transaction to receive the required number of confirmations.",
                            color=discord.Color.green()   
                        )
                        
                        
                        transaction_id = "2ZxTXY...2ATjwV"
                        transaction_detected_embed.add_field(name="Transaction", value="[View Transaction](https://live.blockcypher.com/ltc/tx/dc3bcc61de31d8b8bc6c6559f44e38b408cca48dc91578ba6b14b73ef181a41a)", inline=False)
                        transaction_detected_embed.add_field(name="Required Confirmations", value="1", inline=True)
                        
                        usd_amount = float(self.amount.replace('$', '').strip())
                        crypto_rate = self.crypto_info['rate']
                        crypto_amount = usd_amount / crypto_rate
                        formatted_crypto_amount = f"{crypto_amount:.8f}"
                    
                        transaction_detected_embed.add_field(
                            name="Amount Received", 
                            value=f"{formatted_crypto_amount} {self.crypto_type} ({self.amount} USD)", 
                            inline=True
                        )
                    
                        transaction_detected_embed.set_thumbnail(
                            url="https://media.discordapp.net/attachments/1153826027714379866/1264288618097278986/Money_Receive_Anim.gif?ex=67c35287&is=67c20107&hm=bb8b7ee3ee882a42256dbee3660d07f281b16e007b680d27cd03661695cba762&=&width=510&height=510"
                        )
                        await safe_delete(await_msg)
                        transaction_msg = await self.channel.send(embed=transaction_detected_embed)
                    
                    
                        await asyncio.sleep(20)
                        await safe_delete(transaction_msg)
                        
                    
                        release_embed = discord.Embed(
                            title="You may now proceed with the deal",
                            description=f"The receiver ({self.receiver.display_name}) may now provide the goods to the sender ({self.sender.display_name}) \n \n Once the deal is complete, the sender must click the \"Release\" button below to release the funds to the receiver & complete the deal",
                            color=discord.Color.green()
                        )
                        
                        release_view = ReleaseView(self.sender, self.receiver, self.channel, self.crypto_type, formatted_crypto_amount, self.amount)
                        
                        await self.channel.send(embed=release_embed, view=release_view)
            
            
                dm_embed = discord.Embed(
                    title="Send Transaction Confirmation",
                    description="Are you sure you want to send a Transaction to this ticket?",
                    color=discord.Color.blue()
                )

                dm_embed.add_field(
                    name="Sender",
                    value=f"{self.sender.mention}"
                )

                dm_embed.add_field(
                    name="Receiver",
                    value=f"{self.receiver.mention}"
                )

                dm_embed.add_field(
                    name="Ticket",
                    value=f"{channel}"
                )

                            
                send_button_view = SendTransactionView(
                    sender=self.sender, 
                    channel=channel, 
                    crypto_info=crypto_info, 
                    receiver=self.receiver,
                    amount=self.amount,
                    crypto_type=self.crypto_type
                )

            
                await self.sender.send(embed=dm_embed, view=send_button_view)
        
            else:
                await channel.send("Bro doesn't have roles lmao")
        
        except Exception as e:
            print(f"Error in transaction timeout: {e}")

class ReleaseConfirmation(View):
    def __init__(self, sender, receiver, crypto_type, formatted_crypto_amount, amount_usd):
        super().__init__()
        self.sender = sender
        self.receiver = receiver
        self.crypto_type = crypto_type
        self.formatted_crypto_amount = formatted_crypto_amount
        self.amount_usd = amount_usd
        self.deal_completed = False

    @discord.ui.button(label="Release", style=discord.ButtonStyle.green, custom_id="release_funds")
    async def release_button(self, interaction: discord.Interaction, button: Button):
        # Only the sender can release funds
        if interaction.user.id != self.sender.id:
            await interaction.response.send_message("Only the sender can release the funds!", ephemeral=True)
            return

        # Prevent multiple releases
        if self.deal_completed:
            await interaction.response.send_message("This deal has already been completed!", ephemeral=True)
            return

        # Mark deal as completed to prevent duplicate releases
        self.deal_completed = True
        
        # Disable the button after it's clicked
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # Create and send payment released embed
        payment_released_embed = discord.Embed(
            title="Payment Released",
            description=f"The {self.crypto_type} has been released successfully to the address provided!",
            color=discord.Color.green()
        )
        
        payment_released_embed.add_field(
            name="Amount", 
            value=f"{self.formatted_crypto_amount} {self.crypto_type} ({self.amount_usd} USD)", 
            inline=False
        )
        
        transaction_id_release = "WTWYLu...ub2wH9"
        payment_released_embed.add_field(
            name="Transaction", 
            value="[View Transaction](https://live.blockcypher.com/ltc/tx/dc3bcc61de31d8b8bc6c6559f44e38b408cca48dc91578ba6b14b73ef181a41a)", 
            inline=False
        )
        
        # Set the animated GIF for the thumbnail
        payment_released_embed.set_thumbnail(
            url="https://media.discordapp.net/attachments/1153826027714379866/1264288618097278986/Money_Receive_Anim.gif?ex=67c35287&is=67c20107&hm=bb8b7eb3ee882a42256dbee3660d07f281b16e007b680d27cd03661695cba762&=&width=510&height=510"
        )
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f"View on {self.crypto_type} Explorer", url="https://blockchain.com"))
        await interaction.channel.send(embed=payment_released_embed, view=view)
        
        # Send "Deal Complete!" embed
        deal_complete_embed = discord.Embed(
            title="Deal Complete!",
            description="Thanks for using Halal! This deal is now marked as complete.\n\nWe hope you are satisfied with our service. If you would like to make your vouch public, use the command /setprivacy!\n\nThis ticket will be closed in 5 minutes",
            color=discord.Color.green()
        )
        
        deal_complete_view = discord.ui.View()
        deal_complete_view.add_item(discord.ui.Button(label="Close", style=discord.ButtonStyle.secondary, custom_id="close_ticket"))
        async def close_ticket(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message(embed=discord.Embed(description="🗑️ This ticket will be deleted in 5 seconds.", color=RED_COLOR))
            await asyncio.sleep(5)
            await interaction.channel.delete()
        await interaction.channel.send(embed=deal_complete_embed, view=deal_complete_view)


# --------------------------- [ Fee Section Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

class FeeSelectionView(View):
    def __init__(self, amount_confirmation):
        super().__init__()
        self.amount_confirmation = amount_confirmation
        self.fee_amount = self.calculate_fee()

    def calculate_fee(self):
        amount = float(self.amount_confirmation.amount.replace("$", "").strip())  # Remove "$" and convert to float
        if amount < 50:
            return 0  # No fee for deals below $50
        elif amount < 250:
            return 2  # $2 flat fee for deals $50 - $249
        else:
            return round(amount * 0.01, 2)  # 1% fee for $250+

    async def disable_buttons(self, interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm_role")
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id not in self.user_confirmed:
            await interaction.response.send_message("You are not part of this trade!", ephemeral=True)
            return

        if self.user_confirmed[interaction.user.id]:
            await interaction.response.send_message("You have already confirmed the fee!", ephemeral=True)
            return

        
        self.user_confirmed[interaction.user.id] = True
        self.confirmed_users.add(interaction.user.id)

        
        if self.role_confirmation_message is None:
            self.role_confirmation_message = interaction.message

        
        await interaction.response.defer()

        
        confirm_embed = discord.Embed(description=f"{interaction.user.mention} has confirmed the fee", color=GREEN_COLOR)
        confirm_message = await interaction.followup.send(embed=confirm_embed)
        self.confirmation_messages.append(confirm_message)

    async def send_fee_embed(self, interaction, payer):
        """Send fee embed only if trade amount is $50 or more."""
        if self.fee_amount > 0:  # Only send embed if a fee applies
            fee_embed = discord.Embed(
                title="Fee Payment",
                description="Select one of the corresponding buttons to select which user will be paying the Middleman fee.\n\n"
                            "Fee will be deducted from the balance once the deal is complete.",
                color=discord.Color.green()
            )
            fee_embed.add_field(name="Fee", value=f"${self.fee_amount:.2f}", inline=False)
            await interaction.response.send_message(embed=fee_embed, view=self)
            self.amount_confirmation.fee_payer = payer
            await self.amount_confirmation.process_deal_after_fee_selection(interaction)
        else:
            await interaction.response.send_message("No fee required for this trade.", ephemeral=True)

    @discord.ui.button(label="Sender", style=discord.ButtonStyle.secondary, custom_id="fee_sender")
    async def fee_sender_button(self, interaction: discord.Interaction, button: Button):
        await self.disable_buttons(interaction)
        await self.send_fee_embed(interaction, "sender")

    @discord.ui.button(label="Receiver", style=discord.ButtonStyle.secondary, custom_id="fee_receiver")
    async def fee_receiver_button(self, interaction: discord.Interaction, button: Button):
        await self.disable_buttons(interaction)
        await self.send_fee_embed(interaction, "receiver")

    @discord.ui.button(label="Split Fee", style=discord.ButtonStyle.success, custom_id="fee_split")
    async def fee_split_button(self, interaction: discord.Interaction, button: Button):
        await self.disable_buttons(interaction)
        self.amount_confirmation.fee_payer = None
        self.amount_confirmation.fee_split = True
        await self.send_fee_embed(interaction, "split")

    @discord.ui.button(label="Use Pass", style=discord.ButtonStyle.primary, custom_id="fee_pass")
    async def fee_pass_button(self, interaction: discord.Interaction, button: Button):
        no_pass_embed = discord.Embed(
            title="No Fee Passes Available",
            description="You don't have any fee passes available.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=no_pass_embed, ephemeral=True)


def get_blockchain_explorer_url(crypto_type, transaction_id):
    """Returns the appropriate blockchain explorer URL based on cryptocurrency type"""
    explorers = {
        "BTC": f"https://www.blockchain.com/explorer/transactions/btc/{transaction_id}",
        "ETH": f"https://etherscan.io/tx/{transaction_id}",
        "SOL": f"https://solscan.io/tx/{transaction_id}",
        "LTC": f"https://live.blockcypher.com/ltc/tx/{transaction_id}"
    }
    return explorers.get(crypto_type, explorers["BTC"])

def get_explorer_name(crypto_type):
    """Returns the name of the blockchain explorer based on cryptocurrency type"""
    names = {
        "BTC": "Blockchain.com",
        "ETH": "Etherscan",
        "SOL": "Solscan",
        "LTC": "BlockCypher"
    }
    return names.get(crypto_type, "Blockchain Explorer")

# --------------------------- [ Close Button Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

class CopyButton(View):
    def __init__(self, address=None, amount=None, crypto_type=None, emoji_id=None):
        super().__init__()
        self.address = address
        self.amount = float(amount)
        self.crypto_type = crypto_type
        self.emoji_id = emoji_id

    @discord.ui.button(label="Copy Details", style=discord.ButtonStyle.grey, custom_id="copy_details")
    async def copy_details(self, interaction: discord.Interaction, button: Button):
        if self.address and self.amount and self.crypto_type:
            
            button.disabled = True
            await interaction.response.edit_message(view=self)
            
            
            await interaction.channel.send(f"{self.address}")
            await interaction.channel.send(f"{self.amount}")
        else:
            await interaction.response.send_message("Unable to get details. Please manually copy the address and amount from above.", ephemeral=True)

# --------------------------- [Ticket Panel Perfected, Don't change anything ] ---------------------------------------------------------------------------------------------------------

@bot.command()
async def lsworkmyfuckingwifi(ctx):
    print("Oh Boii")
    current_ticket_id = random.randint(1000, 9999)
    
    
    length = 25  # Change this to the desired length
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    
    
    embed = discord.Embed(
        title="Cryptocurrency",
        description="__Fees:__ \n \n Deals $250+: 1% \n Deals under $250: $2 \n __Deals under $50 are FREE__ \n \n "
                    "Press the dropdown below to select & initiate a deal involving either **Bitcoin, Ethereum, Litecoin, or Solana.**",
        color=GREEN_COLOR
    )

    view = discord.ui.View()
    select = discord.ui.Select(
        placeholder="Make a selection",
        options=[
            discord.SelectOption(label="BTC", emoji="<:h_btc:1345711016658341948>"),
            discord.SelectOption(label="ETH", emoji="<:h_eth:1345711216739352658>"),
            discord.SelectOption(label="LTC", emoji="<:h_ltc:1345711327489953833>"),
            discord.SelectOption(label="SOL", emoji="<:h_solana:1345711555626668056"),
        ],
        custom_id=f"crypto_select_{ctx.author.id}_{int(time.time())}"  
    )

    async def select_callback(interaction: discord.Interaction):
        crypto = select.values[0] 
        user = interaction.user  

        
        crypto_categories = {
            "BTC": "cryptocurrency1",
            "ETH": "cryptocurrency2",
            "LTC": "cryptocurrency3",
            "SOL": "cryptocurrency4"
        }
        category_name = crypto_categories.get(crypto, "Uncategorized")

        
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            category = await ctx.guild.create_category(name=category_name)

        
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            discord.Object(ADMIN_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        
        current_ticket_id = random.randint(100, 9999)
        channel = await ctx.guild.create_text_channel(f"ticket-pending", category=category, overwrites=overwrites)
        await asyncio.sleep(1)
        await channel.edit(name=f"ticket-{current_ticket_id}")

        
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send(
            embed=discord.Embed(
                title="Ticket Created",
                description=f"Ticket {channel.mention} created",
                color=GREEN_COLOR
            ),
            ephemeral=True
        )

        await channel.send(f"```{random_string}```")
        
        

        # Send welcome embeds
        embed1 = discord.Embed(
            title="Crypto Currency Middleman System",
            description=f"> {crypto} Middleman request created successfully! \n \n "
                        "Welcome to our automated cryptocurrency Middleman system! \n"
                        "Your cryptocurrency will be stored securely for the duration of this deal. "
                        "Please notify support for assistance.",
            color=GREEN_COLOR
        )
        embed1.set_thumbnail(url="https://media.discordapp.net/attachments/1153826027714379866/1264288616285212752/Welcome_Prompt.gif")
        embed1.set_footer(text=f"ticket-{current_ticket_id}")

        embed2 = discord.Embed(
            title="Security Notification",
            description="Our Bot and staff team will __NEVER__ direct message you. "
                        "Ensure all conversations related to the deal are done within this ticket. "
                        "Failure to do so may put you at risk of being scammed.",
            color=RED_COLOR
        )

        embed3 = discord.Embed(
            title="Who are you dealing with?",
            description="eg. @user \n eg. 123456789123456789",
            color=GREEN_COLOR
        )

        await channel.send(
            f"{user.mention}",
            embeds=[embed1, embed2], view=CloseButton()
            )
        user_prompt_message = await channel.send(embed=embed3)

        
        error_messages = []
        
        
        valid_trader_found = False
        
        while not valid_trader_found:
            def check(m):
                return m.channel == channel and m.author == user

            try:
                msg = await bot.wait_for("message", timeout=300.0, check=check)
                
                
                trader2 = None
                if msg.mentions:
                    trader2 = msg.mentions[0]
                elif msg.content.isdigit():
                    trader2 = ctx.guild.get_member(int(msg.content))
                
                if trader2:
                    
                    await channel.set_permissions(trader2, read_messages=True, send_messages=True)... (3 KB left)
