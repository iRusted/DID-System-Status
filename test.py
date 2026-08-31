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
from database_handling import get_alter_name_by_id
from database_handling import update_alter
from database_handling import get_alter_by_id
from helpers import confirmation
from helpers import alter_name_autocomplete


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