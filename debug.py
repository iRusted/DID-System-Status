import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks 
from botConfig import token  # imports bot token
from botConfig import superUserIDs # imports accepted super user IDs for bot
from botConfig import acceptedIDs # imports accepted super user IDs for bot
# from botConfig import current_bot_host # imports the current bot hoster.
from database_handling import get_current_fronter # Function to find the current alter
from database_handling import set_current_fronter # Function to Set Current Alter
from database_handling import get_alters # Imports Alter List
from database_handling import add_alter # Unused, can be used to add alters. Will add later
from database_handling import remove_alter # Unused, can be used to remove alters. Will add later


# Put Code to Debug Under Here -------------------------------------------------------------------------------

developer = "rusty"

if developer == "rusty":
    print("Time for python to error out 20 million times for no reason")
else:
    print("Have a great time coding and may any errors make complete sense")
    
    


