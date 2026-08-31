# =====================================================
# Copyright © 2026 Russell Rags. All Rights Reserved.
# Project: System Status Discord Bot
# =====================================================

import discord
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
from database_handling import get_alter_names
import asyncio

async def confirmation(bot, interaction, timeout=60):
    def check(message):
        return (
            message.author == interaction.user
            and message.channel == interaction.channel
        )

    try:
        response = await bot.wait_for(
            "message",
            timeout=timeout,
            check=check
        )

        answer = response.content.lower()

        if answer == "yes":
            return True

        elif answer == "no":
            return False

        else:
            return None

    except TimeoutError:
        return None
    
import asyncio

async def alter_name_autocomplete(interaction, current):
    alter_names = await asyncio.to_thread(get_alter_names)

    choices = []

    for alter in alter_names:
        name = alter[0]

        if name and current.lower() in name.lower():
            choices.append(
                app_commands.Choice(
                    name=name,
                    value=name
                )
            )

    return choices[:25]


