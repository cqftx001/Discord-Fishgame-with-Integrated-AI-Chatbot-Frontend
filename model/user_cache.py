import discord
from discord.ext import commands
from aiohttp import ClientSession
import asyncio
class UserCache:
    def __init__(self, expiry_time):
        self.cache = {}
        self.expiry_time = expiry_time

    def check_user(self, user_id):
        if user_id in self.cache:
            user_info, timestamp = self.cache[user_id]
            if (asyncio.get_event_loop().time() - timestamp) < self.expiry_time:
                return user_info
        return None

    def add_user(self, user_id, exists):
        self.cache[user_id] = (exists, asyncio.get_event_loop().time())

#

