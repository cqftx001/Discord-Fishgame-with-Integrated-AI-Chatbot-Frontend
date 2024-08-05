import hashlib
import time
import configparser

config = configparser.ConfigParser()
config.read('./config/config.ini')
password = config.get('PasswordSettings', 'Password')
def get_token(timestamp):
    token_string = f"{password}{timestamp}{password}"
    token = hashlib.md5(token_string.encode('utf-8')).hexdigest()
    return token
