import discord


class FishingPanelView(discord.ui.View):
    def __init__(self, session):
        super().__init__()
        self.add_item(ReturnButton(session))


class SellButton(discord.ui.Button):
    def __init__(self, session):
        super().__init__(label="fish_sell", style=discord.ButtonStyle.green, custom_id="fish_panel_sell")
        self.session = session

    async def callback(self, interaction: discord.Interaction):
        # 这里可以添加返回的逻辑
        await interaction.response.send_message("Fish sold!", ephemeral=True)


class ReturnButton(discord.ui.Button):
    def __init__(self, session):
        super().__init__(label="fish_return", style=discord.ButtonStyle.grey, custom_id="fish_panel_return")
        self.session = session

    async def callback(self, interaction: discord.Interaction):
        # 这里可以添加返回的逻辑
        pass
        await interaction.response.send_message("Return to the homepage!", ephemeral=True)
