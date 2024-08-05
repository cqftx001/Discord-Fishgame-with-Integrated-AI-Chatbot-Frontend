import logging

import discord
import asyncio
import api_services
from view import fishing_view
from logic.common import check_interaction


async def respond(obj, message, view, embed):
    if hasattr(obj, 'response'):
        await obj.response.send_message(message, view=view, embed=embed)
    else:
        await obj.respond(message, view=view, embed=embed)


async def fish(obj, session):
    if check_interaction(obj):
        user_id = obj.user.id
    else:
        user_id = obj.author.id

    fish_catch = await api_services.get_fish(user_id, session)
    embed = discord.Embed(title="Fishing Results", color=discord.Color.blue())
    for fish in fish_catch.show_item():
        # 添加鱼类信息
        embed.add_field(name="Type:", value=fish.type, inline=False)
        embed.add_field(name="Weight:", value=fish.weight, inline=False)
        embed.add_field(name="Description:", value=fish.description, inline=False)
        # 添加图片
        embed.set_image(url=fish.url)
        # 添加分隔符
        embed.add_field(name="\u200b", value="\u200b", inline=False)

    view = fishing_view.FishingPanelView(session)

    if check_interaction(obj):  # 是交互对象
        await obj.followup.send("Successfully started fishing!", view=view, embed=embed)
    else:  # 是普通消息对象
        await obj.send("Successfully started fishing!", view=view, embed=embed)



async def call_draw_api(prompt, session):
    url = 'http://localhost:8081/api/chat/draw'
    async with session.post(url, json={'prompt': prompt}) as resp:
        if resp.status != 200:
            raise ValueError(f"Unexpected response status: {resp.status}")
        data = await resp.json()

        return data


async def sell(obj, session):
    embed = discord.Embed(title="Fish Market", color=discord.Color.gold())
    embed.add_field(name="Sold Fish:", value=obj.type, inline=False)
    embed.add_field(name="Earned:", value=f"${obj.price}", inline=False)
    view = fishing_view.FishingPanelView(session)

    if hasattr(obj, 'response'):  # 是 Interaction 对象
        await obj.response.send_message("Welcome to fish market!", view=view, embed=embed)
    else:  # 是 Context 对象
        await obj.respond("Welcome to fish market!", view=view, embed=embed)
