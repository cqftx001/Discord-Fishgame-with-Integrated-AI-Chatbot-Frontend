import discord
import api_services
from view import play_view
import logic.common as common

async def play(obj, session):

    if common.check_interaction(obj):
        user_id = obj.user.id
    else:
        user_id = obj.author.id

    user_data = await api_services.get_user_info(user_id, session)
    embed = discord.Embed(title=f"Inventory of {user_data.name}", color=discord.Color.blue())
    embed.add_field(name="Coins", value=f"${user_data.inventory.coins}", inline=False)
    embed.add_field(name="Diamonds", value=f"${user_data.inventory.diamonds}", inline=False)
    embed.add_field(name="Level",
                    value=f"Level {user_data.progress.level}, {user_data.progress.current_experience}/{user_data.progress.experience_for_next_level} XP to next level",
                    inline=False)

    view = play_view.DashboradView(session)

    if hasattr(obj, 'response'):  # 是 Interaction 对象
        await obj.response.send_message("Welcome to Player Dashboard!", view=view, embed=embed)
    else:  # 是 Context 对象
        await obj.respond("Welcome to Player Dashboard!", view=view, embed=embed)

