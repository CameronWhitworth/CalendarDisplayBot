import discord
import os
from dotenv import load_dotenv
from discord import app_commands
from commands import CalendarCommand, SyncCommand

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

class CalendarBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guild_scheduled_events = True
        intents.guilds = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

        # Initialize and register commands
        self.calendar_cmd = CalendarCommand(self)
        self.sync_cmd = SyncCommand(self)

        self.calendar_cmd.register(self.tree)
        self.sync_cmd.register(self.tree)

    async def setup_hook(self):
        await self.tree.sync()

client = CalendarBot()
client.run(DISCORD_TOKEN)
