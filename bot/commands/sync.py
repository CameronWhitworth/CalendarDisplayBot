from discord import app_commands, Interaction
import discord

class SyncCommand:
    def __init__(self, client: discord.Client):
        self.client = client

    def register(self, tree: app_commands.CommandTree):
        @tree.command(name="sync", description="Sync application commands")
        async def sync(interaction: Interaction):
            await interaction.response.defer(thinking=True)
            await self.client.tree.sync()
            await interaction.followup.send("✅ Slash commands synced.")
