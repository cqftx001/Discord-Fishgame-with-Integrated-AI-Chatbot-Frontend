import requests
from discord.ui import Item

from model.fish import Fish
from model.FishingCatch import FishingCatch
from model.user import User, UserInventory, UserProgress
import asyncio
import logging
import time
import configparser
from auth.get_token import get_token
from model.user_cache import UserCache

# 获取配置文件信息
config = configparser.ConfigParser()
config.read('./config/config.ini')
expiry_time = config.getint('CacheSettings', 'ExpiryTime', fallback=3600)



user_cache = UserCache(expiry_time)


async def get_fish(user_id, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    params = {'user_id': user_id}
    try:
        async with session.post("http://localhost:8081/api/fish/catch", params=params,
                                headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                fishing_catch = FishingCatch()
                fishing_catch.add_item(Fish(data['url'], data['type'], data['description'],data['weight']))
                return fishing_catch
            else:
                logging.error(f"Error retrieving fish data")
    except Exception as e:
        logging.exception(f"Exception occurred while fetching fish data: {str(e)}")
        return None

async def check_user_exists(session, user_id):
    cached_user = user_cache.check_user(user_id)
    if cached_user is not None:
        return cached_user
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    params = {'user_id': user_id}

    async with session.get("http://localhost:8081/api/user/is-exist",
                           params=params,
                           headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            if data.get('code') == 200:
                exists = data.get("data", {}).get("exist", 0)
                user_existence = exists != 0
                user_cache.add_user(user_id, user_existence)
                return user_existence
            else:
                logging.error(f"Error retrieving user exists: {data.get('msg')}")
        else:
            return False


async def chatgptGeneral(message_content,session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    params = {'message': message_content}
    try:
        async with session.post("http://localhost:8081/api/chat/general",
                                params=params,
                                headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                return {'success': True, 'data': response_data.get('data')}
            else:
                logging.error(f"HTTP Error: {response.status}")
                return {'success': False, 'error': f"HTTP Error: {response.status}"}
    except Exception as e:
        logging.exception(f"Error to connect to chatgpt: {e}")
        return {'success': False, 'error': str(e)}


async def chatgptCommand(message_content,session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    params = {'message': message_content}
    try:
        async with session.post("http://localhost:8081/api/chat/command",
                                params=params,
                                headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                return {'success': True, 'data': response_data.get('data')}
            else:
                logging.error(f"HTTP Error: {response.status}")
                return {'success': False, 'error': f"HTTP Error: {response.status}"}
    except Exception as e:
        logging.exception(f"Error to connect to chatgpt: {e}")
        return {'success': False, 'error': str(e)}


async def create_user(session, user_id, user_name):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "Content-Type": "application/json",
        "timestamp": timestamp,
        "token": token
    }
    payload = {
        "user_id": user_id,
        "user_name": user_name
    }

    async with session.post(f"http://localhost:8081/api/user/basic",
                            json=payload,
                            headers=headers) as response:
        if response.status == 200:
            response_data = await response.json()  # Assuming the response is JSON
            if response_data.get('code') == 200:
                return True
            else:
                return False
        else:
            return False


async def ensure_user(ctx, session):
    user_id = str(ctx.author.id)
    user_name = str(ctx.author.name)
    user_exists = await check_user_exists(session, user_id)
    if not user_exists:
        logging.info(f"User does not exist, creating: {user_id}")
        try:
            create_user_response = await create_user(session, user_id, user_name)
            if not create_user_response:
                logging.error("Error: Unable to create user.")
                return 'Error: Unable to create user.'
            else:
                user_cache.add_user(user_id, True)
                logging.info(f"User created successfully: {user_id}")
                return 'User created successfully.'
        except Exception as e:
            logging.exception(f"Exception while creating user: {e}")
            return 'Error: Unable to create user.'
    else:
        logging.info(f"User already exists: {user_id}")
        return 'User already exists.'


async def get_user_info(user_id, session):
    basic, finance, level, inventory = await asyncio.gather(
        get_user_basic(user_id, session),
        get_user_finance(user_id, session),
        get_user_level(user_id, session),
        get_user_inventory(user_id, session)
    )
    user = User(user_id, basic.get('user_name'), finance.get('coins'), finance.get('diamonds'),
                inventory.get('fish_inventory'), basic.get('rod_type'), level.get('level'),
                level.get('current_experience'), level.get('experience_for_next_level'))
    return user


async def get_user_basic(user_id, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }  #http://localhost:8081/api/user/is-exist
    url = f"http://localhost:8081/api/user/basic?user_id={user_id}"
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return response_data.get('data')
                else:
                    logging.error(f"Error: {response_data.get('msg')}")
            else:
                logging.error(f"HTTP Error: {response.status}")
    except Exception as e:
        logging.exception(f"Exception occurred while fetching user basic information: {e}")
    return None


async def get_user_finance(user_id, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    url = f"http://localhost:8081/api/user/finance?user_id={user_id}"
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return response_data.get('data')
                else:
                    logging.error(f"Error: {response_data.get('msg')}")
            else:
                logging.error(f"HTTP Error: {response.status}")
    except Exception as e:
        logging.exception(f"Exception occurred while fetching user basic information: {e}")
    return None


async def get_user_level(user_id, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    url = f"http://localhost:8081/api/user/level?user_id={user_id}"
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return response_data.get('data')
                else:
                    logging.error(f"Error: {response_data.get('msg')}")
            else:
                logging.error(f"HTTP Error: {response.status}")
    except Exception as e:
        logging.exception(f"Exception occurred while fetching user basic information: {e}")
    return None


async def get_user_inventory(user_id, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    url = f"http://localhost:8081/api/user/inventory?user_id={user_id}"
    try:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return response_data.get('data')
                else:
                    logging.error(f"Error: {response_data.get('msg')}")
            else:
                logging.error(f"HTTP Error: {response.status}")
    except Exception as e:
        logging.exception(f"Exception occurred while fetching user basic information: {e}")
    return None


async def chatgpt(message_content, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }
    params = {'message': message_content}
    try:
        async with session.post("http://localhost:8081/api/chat",
                                params=params,
                                headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return {'success': True, 'data': response_data.get('data')}
                else:
                    logging.error(f"Error to connect to chatgpt: {response_data.get('msg')}")
                    return {'success': False, 'error': response_data.get('msg')}
            else:
                logging.error(f"HTTP Error: {response.status}")
                return {'success': False, 'error': f"HTTP Error: {response.status}"}
    except Exception as e:
        logging.exception(f"Error to connect to chatgpt: {e}")
        return {'success': False, 'error': str(e)}


async def draw(message_content, session):
    timestamp = str(int(time.time()))
    token = get_token(timestamp)
    headers = {
        "timestamp": timestamp,
        "token": token
    }

    params = {'prompt': message_content}
    try:
        async with session.post("http://localhost:8081/api/chat/draw",
                                params=params,
                                headers=headers) as response:
            if response.status == 200:
                response_data = await response.json()
                if response_data.get('code') == 200:
                    return {'success': True, 'data': response_data.get('data')}
                else:
                    logging.error(f"Error to connect to chatgpt: {response_data.get('msg')}")
                    return {'success': False, 'error': response_data.get('msg')}
            else:
                logging.error(f"HTTP Error: {response.status}")
                return {'success': False, 'error': f"HTTP Error: {response.status}"}
    except Exception as e:
        logging.exception(f"Error to connect to chatgpt: {e}")
        return {'success': False, 'error': str(e)}