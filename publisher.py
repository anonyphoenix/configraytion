import logging
from telethon.sync import TelegramClient
import config
import random
import time
import os
from pymongo import MongoClient


if config.LOG_TO_FILE:
    logging.basicConfig(filename=config.LOG_FILE, level=config.LOG_LEVEL)
else:
    logging.basicConfig(level=config.LOG_LEVEL)

db = MongoClient(config.MONGO_URL)
configs = db[config.MONGO_DB]['configs']

if config.PROXY:
    publisher_client = TelegramClient(config.PUBLISHER_BOT_SESSION, config.API_ID,
                          config.API_HASH, proxy=config.PROXY_ADDRESS)
else:
    publisher_client = TelegramClient(config.PUBLISHER_BOT_SESSION, config.API_ID, config.API_HASH)


logging.info('publisher is starting...')
publisher_client.start(bot_token=config.BOT_TOKEN)
logging.info('publisher started.')


while True:
    configs_len = configs.count_documents({'in_channel': False})
    if configs_len > 10:
        configs_list = configs.find({'in_channel': False}).limit(10)
        logging.debug(f'publisher fetched {configs_len} new configs from database.')
        full_text = ''
        for c in configs_list:
            config_id = c['config_id']
            url = c['url']
            config_type = url.split(':')[0]
            country = c['country']
            config_link = f'<a href="{config.BOT_LINK.format(id=config_id)}">{config_type + ' ' + country}</a>'
            full_text += config_link + '\n'
            configs.update_one(c, {'$set': {'in_channel': True}})

        emoji_list = ['🤑', '💵', '🛜', '🔗', '⛓‍💥', '⛓', '✅', '❤️', '💰', '🗿', '💣', '📱', '🛒', '👓',
                       '🎈', '🎊', '🧨', '✨', '🎉', '🎀', '🎁', '❤️‍🔥', '🤍', '💜', '🩵', '💙', '💚', '💛',
                         '🧡', '🩷', '💶', '💳', '🚀', '🔖', '🧪', '🍕', '🪙', '💻', '💵', '💸']
        post_emoji = random.choice(emoji_list)
        full_text += '\n\n' + post_emoji + f'{config.CHANNEL_USERNAME}' + post_emoji
        # pic is for future versions
        pic = None
        publisher_client.send_message(config.CHANNEL_ID, full_text, parse_mode='html', file=pic)
        if pic:
            os.remove(pic)

    time.sleep(5)
