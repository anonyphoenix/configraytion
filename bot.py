import logging
from telethon import TelegramClient, Button, events
import config
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from pymongo import MongoClient, DESCENDING
import helper
import navlib
import i18n
import datetime

if config.LOG_TO_FILE:
    logging.basicConfig(filename=config.LOG_FILE, level=config.LOG_LEVEL)
else:
    logging.basicConfig(level=config.LOG_LEVEL)

db = MongoClient(config.MONGO_URL)
configs = db[config.MONGO_DB]['configs']
tokens = db[config.MONGO_DB]['tokens']
users = db[config.MONGO_DB]['users']

if config.PROXY:
    bot = TelegramClient(config.CONFIGRAYTION_BOT_SESSION, config.API_ID, config.API_HASH, proxy=config.PROXY_ADDRESS)
else:
    bot = TelegramClient(config.CONFIGRAYTION_BOT_SESSION, config.API_ID, config.API_HASH)

logging.info('configraytion bot is starting...')
bot.start(bot_token=config.BOT_TOKEN)
logging.info('configraytion bot started.')


@bot.on(events.NewMessage(incoming=True))
async def start(event):
    # join, entity = await helper.join_check(user_id, bot)
    # if join is False:
    #     full_info = await bot(GetFullChannelRequest(entity))
    #     chat_title = full_info.chats[0].title
    #     channel_username = full_info.chats[0].username
    #     if channel_username is None:
    #         channel_username = full_info.full_chat.exported_invite.link
    #     else:
    #         channel_username = f'https://t.me/{channel_username}'
    #     key = [
    #         [Button.url(text=chat_title, url=channel_username)],
    #         [Button.url(text=i18n.get('VERIFY_SUBSCRIPTION'), url=f"{config.BOT_ID}?start=check")]
    #     ]
    #     await event.reply(i18n.get('JOIN_FIRST_AND_THEN_RETRY'), buttons=key)
    #     return
    user = helper.bot_auth(event, users)
    if user['user_group'] == 'guest' or event.raw_text == "/language":
        await helper.bot_lang(event)
    else:
        text_spl = str(event.raw_text).split(' ')
        if len(text_spl) == 2:
            try:
                config_id = int(text_spl[1])
                config_find = configs.find_one({'config_id': config_id})
                if config_find:
                    await event.reply(config_find['url'], file=config_find['qrcode'])
                else:
                    await event.reply(i18n.get('CONFIG_NOT_FOUND', lang=user['lang']))
            except ValueError:
                if config_id == "check":
                    await event.reply()
        elif event.raw_text == "/start":
                await helper.bot_welcome(event, user['lang'])


@bot.on(events.CallbackQuery(pattern='LANG_(EN|FA)'))
async def lang_en_fa(event):
    lang_code = 'en' if 'LANG_EN' in event.data.decode() else 'fa'
    users.update_one({
        'user_id': event.sender_id
    }, { '$set': {
        'lang': lang_code,
    }, '$setOnInsert': {
        'user_id': event.sender_id,
        'user_type': helper.get_peer_type_from_event(event),
        'user_group': 'registered',
        'registration_time': datetime.datetime.now(),
        'last_config_request_time': datetime.datetime.min
    }}, upsert=True)
    await helper.bot_welcome(event, 'en')
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern='GET_CONFIG'))
async def get_config(event):
    user = helper.bot_auth(event, users)
    if user['last_config_request_time'] < datetime.datetime.now() - datetime.timedelta(minutes=15):
        find_configs = configs.find().sort('config_id', DESCENDING).limit(3)
        for c in find_configs:
            await event.respond('```' + c['url'] + '#' + c['country_emoji'] + ' t.me/' + config.CHANNEL_USERNAME + ' ' + c['country'] + '```',
                                file=c['qrcode'])
    else:
        wait_time_minute = (datetime.datetime.now() - user['last_config_request_time']).minute + 1
        await event.respond(i18n.get('WAIT_BETWEEN_REQUESTS_1', user['lang']) + str(wait_time_minute) +
                            i18n.get('WAIT_BETWEEN_REQUESTS_2', user['lang']))
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern='ADD_TOKEN'))
async def add_token(event):
    user = helper.bot_auth(event, users)

    if user['user_id'] in config.BOT_ADMINS:
        async with bot.conversation(event.sender_id) as conv:
            await conv.send_message(i18n.get('ENTER_TOKEN_CREDIT', user['lang']))
            response = await conv.get_response()
            try:
                token_credit = int(response.text)
            except ValueError:
                await conv.send_message(i18n.get('MUST_BE_INTEGER', user['lang']))
                return

            token_value = helper.generate_random_token()

            token_data = {
                'creator_id': user['user_id'],
                'token': token_value,
                'credit': token_credit,
                'date_created': datetime.datetime.now()
            }

            try:
                tokens.insert_one(token_data)
                logging.debug('token ' + token_value + ' inserted to DB.')
                await conv.send_message(f'{i18n.get('TOKEN_GENERATED_SUCCESSFULLY', user['lang'])}\n\n`{token_value}`')
            except Exception as e:
                await conv.send_message(i18n.get('ERROR', user['lang']))
    else:
        await event.respond(i18n.get('NOT_AUTHORIZED'), user['lang'])
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern='VIEW_TOKENS:.*'))
async def view_tokens(event):
    user = helper.bot_auth(event, users)

    if user['user_id'] in config.BOT_ADMINS:
        count_tokens = tokens.count_documents({})

        if count_tokens == 0:
            await event.reply(i18n.get('NO_TOKEN', user['lang']))
            return
        
        current_page = int(event.data.decode().split(":")[1])
        skip = (current_page * 10) - 10
        tokens_find = tokens.find({}).limit(10).skip(skip)
        
        if not tokens_find:
            await event.reply(i18n.get('NO_TOKEN_LEFT', user['lang']))
            return
        
        keys = []
        for token in tokens_find:
            keys.append([Button.inline(str(token['token']), str.encode('VIEW_TOKEN:' + str(token['token'])))])
        count = tokens.count_documents({})
        total_pages = count // 10
        if count % 10 != 0:
            total_pages += 1
        page_keys = navlib.paginate('VIEW_TOKENS', current_page, total_pages=total_pages)
        if len(page_keys) != 0:
            keys.append(page_keys)
        await event.respond(i18n.get('SELECT_TOKEN', user['lang']), buttons=keys)
    else:
        await event.respond(i18n.get('NOT_AUTHORIZED'), user['lang'])
    raise events.StopPropagation


@bot.on(events.CallbackQuery(pattern='VIEW_TOKEN:.*'))
async def view_token(event):
    user = helper.bot_auth(event, users)
    if user['user_id'] in config.BOT_ADMINS:
        token = event.data.decode().split(":")[1]
        token = tokens.find_one({"token": token})
        if token:
            message = (f"{i18n.get('CREATOR', user['lang'])}: `{token['creator_id']}`\n"
            f"{i18n.get('CREDIT', user['lang'])}: `{token['credit']}`\n"
            f"{i18n.get('TOKEN', user['lang'])}: `{token['token']}`")
            await event.reply(message)
        else:
            await event.respond(i18n.get('TOKEN_NOT_FOUND', user['lang']))
    raise events.StopPropagation

bot.run_until_disconnected()
