import logging
from telethon import TelegramClient, events
import config
import qrcode
import time
from pymongo import MongoClient
import parser


if config.LOG_TO_FILE:
    logging.basicConfig(filename=config.LOG_FILE, level=config.LOG_LEVEL)
else:
    logging.basicConfig(level=config.LOG_LEVEL)

db = MongoClient(config.MONGO_URL)
configs = db[config.MONGO_DB]['configs']

if config.PROXY:
    user = TelegramClient(config.RECEIVER_SESSION, config.API_ID,
                          config.API_HASH, proxy=config.PROXY_ADDRESS)
else:
    user = TelegramClient(config.RECEIVER_SESSION, config.API_ID, config.API_HASH)

logging.info('receiver is connecting to Telegram...')
user.start(phone=config.PHONE, password=config.PASSWORD)
logging.info('receiver connected to Telegram.')


@user.on(events.NewMessage(chats=config.CHANNEL_LIST))
async def receive_config(event):
    logging.debug('new message received from CHANNEL_LIST.')
    xray_config, country, country_abbreviation, country_emoji = parser.parse_configshub(event.raw_text)
    logging.debug('config parsed: ' + xray_config + '.')
    find_config = configs.find_one({'url': xray_config})
    if find_config:
        logging.debug('duplicate config found config_id=' + str(find_config.get('config_id')) + '.')
    else:
        config_id = configs.count_documents({}) + 1
        qr_path = f'qrcode/{time.time()}.png'
        qr = qrcode.QRCode(
            version=12,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=2,
            border=8
        )
        qr.add_data(xray_config)
        qr.make()
        img = qr.make_image(fill_color='black', back_color='white')
        img.save(qr_path)
        logging.debug('qr code saved for config id=' + str(config_id))
        data = {
            'config_id': config_id,
            'url': xray_config,
            'in_channel': False,
            'qrcode': qr_path,
            'country': country,
            'country_abbreviation': country_abbreviation,
            'country_emoji': country_emoji,
            'text': event.raw_text
        }
        configs.insert_one(data)
        logging.info('config id=' + str(config_id) + ' saved to DB.')


if __name__ == '__main__':
    user.run_until_disconnected()
