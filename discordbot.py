# =====================================================
# Copyright © 2026 Russell Rags. All Rights Reserved.
# Project: System Status Discord Bot
# =====================================================

import discord
from datetime import datetime, timezone
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks 
from botConfig import token  # imports bot token
from botConfig import superUserIDs # imports accepted super user IDs for bot
from botConfig import acceptedIDs # imports accepted super user IDs for bot
from botConfig import current_bot_host # imports the current bot hoster.
from botConfig import bot
from database_handling import get_current_fronter # Function to find the current alter
from database_handling import set_current_fronter # Function to Set Current Alter
from database_handling import get_alters # Function to pull the Alter List from the DB.
from database_handling import add_alter as db_add_alter # Function to add alters.
from database_handling import remove_alter as db_remove_alter # Function to REMOVE alters.
from database_handling import get_alter_name # Grabs an alters name based off the ID given. 
from database_handling import get_alter_by_id
from database_handling import update_alter
from database_handling import get_alter_id_by_name
from database_handling import create_new_message
from database_handling import set_host_id
from database_handling import read_host_id
from database_handling import read_message_user
from database_handling import read_message_alter
from helpers import confirmation
from helpers import alter_name_autocomplete
import traceback
import io

print("Bot Created and Developed by: Russell Rags.")
print("Copyright © 2026 Russell Rags. All Rights Reserved.")

acceptedUser = superUserIDs + acceptedIDs # Adds SuperUsers to AcceptedUsers to avoid checking every command for permission.
system_host = read_host_id()

intents = discord.Intents.default()
intents.message_content = True

# Command Extra

def build_alter_embed(data) -> discord.Embed: # Relates to /check_alters
    """
    Builds one alter's embed from a DB row.

    data is a tuple: (ID, Name, Pronouns, Role, Image_URL)
    """
    alter_id, name, pronouns, role, image_url = data

    embed = discord.Embed(
        title=f"Alter {alter_id} | {name}",
        colour=0xe400f5,
        timestamp=datetime.now(timezone.utc),
    )

    embed.set_author(name="System Status")

    embed.add_field(
        name="Alter Role",
        value=f"{name}'s Role is {role}",
        inline=False,
    )
    embed.add_field(
        name="Pronouns",
        value=f"{name} Pronouns Are {pronouns}",
        inline=False,
    )

    if image_url:
        embed.set_thumbnail(url=image_url)

    embed.set_footer(text="Alter Lookup Provided by SystemStatus")
    # icon_url left off for now — the old one was a webpage link, not a
    # direct image link, so Discord can't render it. Add a real image
    # URL here later if you want the footer icon back.

    return embed

class AlterBrowserView(discord.ui.View): # Relates to /check_alters
    def __init__(self, author_id: int, alter_ids: list):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.alter_ids = alter_ids
        self.page = 1

        self.previous_button.disabled = True
        if len(self.alter_ids) <= 1:
            self.next_button.disabled = True

    def current_embed(self) -> discord.Embed:
        current_id = self.alter_ids[self.page]
        data = get_alter_by_id(current_id)
        return build_alter_embed(data)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "These buttons aren't for you!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page -= 1
        self.previous_button.disabled = self.page == 0
        self.next_button.disabled = False
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page += 1
        self.next_button.disabled = self.page == len(self.alter_ids) - 1
        self.previous_button.disabled = False
        await interaction.response.edit_message(embed=self.current_embed(), view=self)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError
):
    import traceback
    import io

    tb = "".join(
        traceback.format_exception(
            type(error),
            error,
            error.__traceback__
        )
    )

    file = discord.File(
        io.BytesIO(tb.encode("utf-8")),
        filename="traceback.txt"
    )

    message = (
        f"❌ **Command failed**\n"
        f"Error: `{type(error).__name__}`"
    )

    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                message,
                file=file
            )
        else:
            await interaction.response.send_message(
                message,
                file=file
            )

    except discord.NotFound:
        # Interaction expired before we could respond.
        print("Interaction expired before the error message could be sent.")
        print(tb)

    except discord.HTTPException as e:
        print(f"Failed to send error message: {e}")
        print(tb)
#def build_message_embed(data) -> discord.Embed:


# Commands

@bot.tree.command(name="remove_alter", description="Remove an alter from the SQLite using the alters ID. Find IDs using /check_alters")
async def remove_alter(interaction: discord.Interaction, alter_id: int):

    if interaction.user.id not in superUserIDs: # Checks if the user is a Super User
        await interaction.response.send_message(
            "You are not allowed to run this command. You must be a SuperUser to run this command."
        )
        return

    alter_name = get_alter_name(alter_id) # Finds the name of the alter that is about to be deleted.

    await interaction.response.send_message( # Asks for confirmation about said alter.
        f"Are you sure you want to remove the alter with the ID: {alter_id}? "
        f"That alter is: {alter_name}! Respond with Yes/No to proceed."
    )

    confirmed = await confirmation(bot, interaction)

    if confirmed is True:
        db_remove_alter(alter_id) 

        await interaction.followup.send(
            f"The alter with the ID of {alter_id} has been deleted. That alter was: {alter_name}"
        )

    elif confirmed is False: # If user chooses no, then it doesn't delete alter.
        await interaction.followup.send(
            f"You have chosen NOT to remove the alter: {alter_name}."
        )

    else:
        await interaction.followup.send(
            "No valid response was received. The removal operation has been cancelled."
        )

@bot.tree.command(name="add_alter", description="Add an alter to the SQLite database to be stored.") # Adds a new alter to the DB using /add_alter <name> <pronouns> <role>
async def add_alter(interaction: discord.Interaction, alter_name: str, alter_pronouns: str, alter_role: str): 

    new_alter = f"The New Alters name is {alter_name}, Their set pronouns are {alter_pronouns}, and their role is, {alter_role}."
    if interaction.user.id in superUserIDs:
        db_add_alter(alter_name, alter_pronouns, alter_role)
        
        await interaction.response.send_message(
            f"Here is the info for the new alter: {new_alter}"
        )
    else:
        await interaction.response.send_message(
            "You are not allowed to run this command. You must be added to the Super Users ID list."
         )
        
@bot.tree.command(name="currentfront", description="Shows the current alter fronting") # /currentfront Shows the Current Fronting Alter
async def currentfront(interaction: discord.Interaction):

    # Checks if the person using the command is a SuperUser
    if interaction.user.id in acceptedUser:

        # Gets current fronter from the database
        current = get_current_fronter()

        # Sends response
        await interaction.response.send_message(
            f"The Current Alter Fronting is: {current}"
        )

    else:

        # User is not authorized
        await interaction.response.send_message(
            f"You are not allowed to run this command, You must be authorized first. Contact the bot host to fix."
        )

@app_commands.autocomplete(new_fronter=alter_name_autocomplete)
@bot.tree.command(name="setfronter", description="Set the currently fronting alter") # Sets the Current Fronter
async def newSetCurrentFront(interaction: discord.Interaction, new_fronter: str):

    if interaction.user.id in superUserIDs:

        set_current_fronter(new_fronter)

        await interaction.response.send_message(
            f"The Current Fronter has been changed to: {new_fronter}"
        )

    else:
        await interaction.response.send_message(
            "You are not allowed to run this command, you must be a SuperUser for this."
        )
       
@bot.tree.command(name="check_alters_old", description="Check the list of added alters.") # /check_alters Checks the list of alters in the database.
async def checkalterlist(interaction: discord.Interaction):
    
    alterList = get_alters()
    if interaction.user.id in acceptedUser: 
        message = "Current Alters:\n\n"
    
        for alter in alterList: 
            ID, name, pronouns, role = alter 
        
            message += (
                f"**{name}**\n"
                f"Pronouns: {pronouns}\n"
                f"Role: {role}\n"
                f"ID: {ID}\n\n"
            )
        
    await interaction.response.send_message(message)

@bot.tree.command(name="check_level", description="Check your ID level in with this bot.") # ID Check /Command with /check_level
async def checkID(interaction: discord.Interaction):

    if interaction.user.id in superUserIDs:
        await interaction.response.send_message(
            "Your ID is currently set to: Super User!"
        )
    elif interaction.user.id in acceptedIDs:
        await interaction.response.send_message(
            "Your ID is an Accepted User's ID!"
        )
    else:
        await interaction.response.send_message(
            "Your ID is not permitted to run commands."
        )

@app_commands.autocomplete(alter_name=alter_name_autocomplete)
@bot.tree.command(name="alter_name_to_id", description="Get an alters ID by their name.")
async def id_to_alter(interaction: discord.Interaction, alter_name: str):

    if interaction.user.id in superUserIDs:
        await interaction.response.defer()

        alter_id = get_alter_id_by_name(alter_name)

        await interaction.followup.send(
            f"The ID of {alter_name} is: {alter_id}"
        )
    else:
        await interaction.response.send_message(
            "You need to be a super user to use this command."
        )

@bot.tree.command(name="edit_alter_information", description="Edit an alters information") # Uses a Modal to edit an alters information. 
async def edit_alter_information(interaction: discord.Interaction, alter_id: int): 
    
    if interaction.user.id in superUserIDs: 
        
        alter_info = get_alter_by_id(alter_id)
        
        if alter_info == None: 
            await interaction.response.send_message(
                "Hey! That ID appears to be invalid. Please check your ID and try again."
            )
            return

        (ID, Name, Pronouns, Role, ImageURL) = alter_info
            
        alter_id = ID
        alter_name = Name 
        alter_pronouns = Pronouns 
        alter_role = Role 
        alter_image = ImageURL
       
        class MyModal(discord.ui.Modal, title="Edit Alter"):
            def __init__(self, alter_id, alter_name, alter_pronouns, alter_role, alter_image):
                super().__init__()

                self.alter_id = alter_id

                self.name_field = discord.ui.TextInput(
                    label="Name",
                    default=alter_name,
                    max_length=50,
                    required=True
                    )
                self.add_item(self.name_field)
                
                self.pronoun_field = discord.ui.TextInput(
                            label="Pronouns",
                            default= alter_pronouns,
                            max_length=20,
                            required=True,
                    )
                self.add_item(self.pronoun_field)
                
                self.role_field = discord.ui.TextInput(
                            label ="Role(s)", 
                            default= alter_role,
                            max_length=50,
                            required=True
                    )
                self.add_item(self.role_field)
                
                self.image_field = discord.ui.TextInput(
                            label ="Image URL",
                            default=alter_image,
                            placeholder="Optional URL Here.",
                            max_length=150,
                            required=False 
                )
                self.add_item(self.image_field)
                     
            async def on_submit(self, interaction):
                alter_id = self.alter_id
                name = self.name_field.value
                pronouns = self.pronoun_field.value
                role = self.role_field.value
                image_url = self.image_field.value

                if image_url == "":
                    image_url = None
                elif image_url and not image_url.startswith(("http://", "https://")):
                    image_url = None
            
                update_alter(alter_id, name=name, pronouns=pronouns, role=role, image_url=image_url)
                await interaction.response.send_message(
                    f"You have edited the alter with the ID of: {self.name_field.value}"
                )

        modal = MyModal(alter_id, alter_name, alter_pronouns, alter_role, alter_image)
        
        await interaction.response.send_modal(modal)

    else:
        await interaction.response.send_message(
            "You need to be a super user to use this command."
        )

@bot.tree.command(name="check_alters", description="The New way to Check Alters!")
async def check_alters(interaction: discord.Interaction):
    if interaction.user.id in acceptedUser:

        all_alters = get_alters()  # [(ID, Name, Pronouns, Role), ...]

        if not all_alters:
            await interaction.response.send_message("No alters found in the database.")
            return

        alter_ids = [row[0] for row in all_alters]

        view = AlterBrowserView(author_id=interaction.user.id, alter_ids=alter_ids)
        await interaction.response.send_message(embed=view.current_embed(), view=view)
    else: 
        await interaction.response.send_message("You must be an accepted user to run this command.")
    
@bot.tree.command(name="message", description="Message Anyone! Alter -> Person/Person -> Alter")
async def message_command(interaction: discord.Interaction, alter_id: int, message: str, alter_or_user: str, disct_id_recpt: str = None):

    if interaction.user.id in acceptedUser:
        current_time = datetime.now()

        if alter_or_user.lower() == "alter":
            alter_or_user = 1
        elif alter_or_user.lower() == "user":
            alter_or_user = 0
        else:
            await interaction.response.send_message(
                "Please enter either 'alter' or 'user' for alter_or_user.", ephemeral=True
            )
            return

        # Convert disct_id_recpt to int if provided
        if disct_id_recpt is not None:
            try:
                disct_id_recpt = int(disct_id_recpt)
            except ValueError:
                await interaction.response.send_message(
                    "disct_id_recpt must be a valid numeric Discord user ID.", ephemeral=True
                )
                return

        # alter -> user requires a Discord recipient ID
        if alter_or_user == 1 and disct_id_recpt is None:
            await interaction.response.send_message(
                "You must provide a Discord user ID (disct_id_recpt) to message as an alter.", ephemeral=True
            )
            return

        create_new_message(message, alter_id, disct_id_recpt, alter_or_user, current_time)

        if alter_or_user == 1:
            messaged_person = get_alter_name(alter_id)
        else:
            messaged_person = disct_id_recpt

        await interaction.response.send_message(
            f"Added a message to {messaged_person}"
        )

    else:
        await interaction.response.send_message(
            "You must be an accepted user to run this command.", ephemeral=True
        )
    
@bot.tree.command(
    name="check_for_messages",
    description="Read a message from an alter, or from a user as an alter!"
)
async def read_message(interaction: discord.Interaction):

    if interaction.user.id not in acceptedUser:
        await interaction.response.send_message(
            "You must be authorized to use this command."
        )
        return

    if interaction.user.id in system_host:

        current_fronter = get_current_fronter()
        alter_id = get_alter_id_by_name(current_fronter)
        alter_messages = read_message_alter(alter_id)

        if not alter_messages:
            await interaction.response.send_message(
                f"📭 No messages for **{current_fronter}**."
            )
            return

        message_info = "\n".join(
            f"**{message[3]}** — {message[1]}"
            for message in alter_messages
        )

        await interaction.response.send_message(message_info)

    else:
        user_id = interaction.user.id
        message_info = read_message_user(user_id)

        if not message_info:
            await interaction.response.send_message(
                "📭 You don't have any messages."
            )
            return

        message_text = "\n".join(
            f"**{message[3]}** — {message[1]}"
            for message in message_info
        )

        await interaction.response.send_message(message_text)
@bot.tree.command(name="system_set", description="Set the UserID of the System's Host")
async def set_system_host(interaction: discord.Interaction, host_id: str):
    if interaction.user.id in superUserIDs:
        try:
            host_id_int = int(host_id)
        except ValueError:
            await interaction.response.send_message(
                "That doesn't look like a valid ID.", ephemeral=True
            )
            return

        set_host_id(host_id_int,)
        await interaction.response.send_message(
            f"Set the ID of the System Host to {host_id_int}, that is <@{host_id_int}>!"
        )
    else:
        await interaction.response.send_message(
            "You don't have permission to do that.", ephemeral=True
        )
        


#Test Command

@bot.tree.command(name="test", description="Test Commands (Volitile, Changes Often)") # Testing Command, Use this to test new fetures before they get added.
async def test(interaction: discord.Interaction,):
    interaction.response.send_message(
        "Yeah, this does nothing right now. Go away."
    )

# Other Non Command Things

@bot.event
async def on_ready(): # Sends a Start Command, and defines the bot status.

    synced = await bot.tree.sync()

    print(f"Synced {len(synced)} slash commands")

    channel = await bot.fetch_channel(1534327053728481280) # Development Server ID
    await channel.send("Bot started", silent=True)

    print("Message sent!")
    if not check_alter_status.is_running():
        check_alter_status.start()
    
    print(f"Logged in as {bot.user}")

@tasks.loop(seconds=120)
async def check_alter_status(): # Changes the Alter Bot Status ever 120 Secons to reflect the current fronter.
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(f"The Current Fronter is: {get_current_fronter()}")
    )





print("Bot is running...")
bot.run(token)