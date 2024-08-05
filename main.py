from typing import Final
import os
import asyncio
import aiohttp
import discord
from dotenv import load_dotenv
import time

import api_services
from logic import play_logic, fish_logic
from aiohttp import ClientSession


# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')


# STEP 1: BOT SETUP
class MyBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aiohttp_session = None

    async def setup_hook(self):
        # 在bot启动时初始化ClientSession
        if not self.aiohttp_session or self.aiohttp_session.closed:
            self.aiohttp_session = ClientSession()
        print("ClientSession has been created")
        self.http.timeout = 10.0  # 设置为10秒

    async def close(self):
        # 在bot关闭时关闭ClientSession
        if self.aiohttp_session and not self.aiohttp_session.closed:
            await self.aiohttp_session.close()
            print("ClientSession has been closed")
        await super().close()

client = MyBot(intents=discord.Intents.all())


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready():
    print(f'{client.user} is now running!')
    await client.sync_commands()


async def execute_command_logic(ctx, logic_function):
    try:
        if not ctx.response.is_done():
            await ctx.defer()

        # 确保会话有效
        if client.aiohttp_session is None or client.aiohttp_session.closed:
            await client.setup_hook()
        await api_services.ensure_user(ctx, client.aiohttp_session)
        await logic_function(ctx, client.aiohttp_session)
    except Exception as e:
        print(f"Error during command execution: {e}")

        if not ctx.response.is_done():
            await ctx.followup.send("An error occurred while processing your request.")



@client.slash_command(name="play", description="Start to play")
async def play(ctx):
    await execute_command_logic(ctx, play_logic.play)


@client.slash_command(name="sell", description="Sell fish")
async def sell(ctx):
    await execute_command_logic(ctx, fish_logic.sell)


@client.slash_command(name="fish", description="Fish")
async def fish(ctx):
    await execute_command_logic(ctx, fish_logic.fish)


@client.event
async def on_ready():
    print(f'{client.user} is now running!')


@client.slash_command(name="chatgpt_general", description="Start talk to your bot!")
async def chatgpt_general(ctx: discord.Interaction, message: str):
    if client.user is None:
        return

    if client.aiohttp_session is None or client.aiohttp_session.closed:
        client.aiohttp_session = aiohttp.ClientSession()

    response = await api_services.chatgptGeneral(message, client.aiohttp_session)
    if response['success']:
        await ctx.response.send_message(response['data'])
    else:
        await ctx.response.send_message(f"Error: {response['error']}")


@client.slash_command(name="chatgpt_command", description="Start talk to your bot!")
async def chatgpt_command(ctx: discord.Interaction, message: str):
    if client.user is None:
        return

    if client.aiohttp_session is None or client.aiohttp_session.closed:
        client.aiohttp_session = aiohttp.ClientSession()

    response = await api_services.chatgptCommand(message, client.aiohttp_session)
    if response['success']:
        command = response['data'].strip()
        if command == 'play':
            await play(ctx)
        elif command == 'sell':
            await sell(ctx)
        elif command == 'fish':
            await fish(ctx)
        else:
            await ctx.response.send_message(f"Unknown command: {command}")
    else:
        await ctx.response.send_message(f"Error: {response['error']}")


@client.slash_command(name="draw", description="Draw image")
async def draw(ctx: discord.Interaction, prompt: str):
    if client.user is None:
        return

    if client.aiohttp_session is None or client.aiohttp_session.closed:
        client.aiohttp_session = aiohttp.ClientSession()

    await ctx.response.defer()

    try:
        response = await api_services.draw(prompt, client.aiohttp_session)
        if response['success']:
            await ctx.followup.send(response['data'])
        else:
            await ctx.followup.send(f"Error: {response['error']}")
    except Exception as e:
        await ctx.followup.send(f"Error: {str(e)}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.aiohttp_session is None or client.aiohttp_session.closed:
        await client.setup_hook()

    response = await api_services.chatgpt(message.content, client.aiohttp_session)

    if response['success']:
        await message.channel.send(response['data']['choices'][0]['message']['content'])
    else:
        await message.channel.send(f"Error: {response['error']}")


# STEP 5: MAIN ENTRY POINT
def main():
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()
