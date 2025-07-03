import discord
import os
from discord.ext import commands
from slash_command import Slash_command
from commands import Commands
from event import Event
from test import Test
from stock_command import Stock_command
import threading

TOKEN = os.getenv("DISCOED_TOKEN")
intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)

_1A2B_lst = []
command_lst = []
client_cmd_lst = [i.name for i in client.commands]
mutex = threading.Lock()
client.add_cog(Slash_command(client, _1A2B_lst, command_lst, client_cmd_lst, mutex))
client.add_cog(Commands(client, _1A2B_lst, command_lst, client_cmd_lst, mutex))
client.add_cog(Event(client, _1A2B_lst, command_lst, client_cmd_lst, mutex))
#client.add_cog(Test(client, _1A2B_lst, command_lst, client_cmd_lst, mutex))
client.add_cog(Stock_command(client, _1A2B_lst, command_lst, client_cmd_lst, mutex))
client.run(TOKEN)