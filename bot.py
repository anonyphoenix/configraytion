import logging
from telethon import TelegramClient, Button, events
import config
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerUser, PeerChat, PeerChannel
from os.path import exists
from pymongo import MongoClient
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

if config.PROXY:
    bot = TelegramClient(config.CONFIGRAYTION_BOT_SESSION, config.API_ID, config.API_HASH, proxy=config.PROXY_ADDRESS)
else:
    bot = TelegramClient(config.CONFIGRAYTION_BOT_SESSION, config.API_ID, config.API_HASH)

logging.info('configraytion bot is starting...')
bot.start(bot_token=config.BOT_TOKEN)
logging.info('configraytion bot started.')


@bot.on(events.NewMessage(incoming=True))
async def start(event):
    text = event.raw_text
    user_id = event.sender_id
    if type(event.message.peer_id) == PeerChannel:
        chat_type = 'channel'
    elif type(event.message.peer_id) == PeerChat:
        chat_type = 'group'
    elif type(event.message.peer_id) == PeerUser:
        chat_type = 'user'
    else:
        chat_type = None
    if chat_type == "user":
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
        text_spl = str(text).split(' ')
        text_len = len(text_spl)
        if text_len == 2:
            try:
                config_id = text_spl[1]
                print(config_id)
                config_id = int(config_id)
                config_find = configs.find_one({'config_id': config_id})
                if config_find is None:
                    await event.reply(i18n.get('CONFIG_NOT_FOUND'))
                else:
                    qr = config_find[1]
                    await event.reply(config_find[0], file=qr)
            except ValueError:
                if config_id == "check":
                    await event.reply()
        if text == "/start":
            if user_id in config.BOT_ADMINS:
                await event.respond(
                    i18n.get('WELCOME'),
                    buttons=[
                        [Button.inline(i18n.get('ADD_TOKEN'), b'ADD_TOKEN')],
                        [Button.inline(i18n.get('VIEW_TOKEN'), b'VIEW_TOKENS')]
                    ]
                )
            else:
                await event.reply(i18n.get('WELCOME'))


@bot.on(events.CallbackQuery(pattern="ADD_TOKEN"))
async def add_token(event):
    user_id = event.sender_id

    if user_id not in config.BOT_ADMINS:
        await event.respond("You are not authorized to add token.")
        return

    # Start a conversation
    async with bot.conversation(user_id) as conv:
        # Request token plan
        await conv.send_message("Please enter token\'s credit:")
        response = await conv.get_response()
        try:
            token_credit = int(response.text)
        except ValueError:
            await conv.send_message("Invalid input. Please enter an integer.")
            return

        token_value = helper.generate_random_token()

        token_data = {
            "creator_id": user_id,
            "token": token_value,
            "credit": token_credit,
            'date_created': datetime.datetime.now()
        }

        try:
            result = tokens.insert_one(token_data)
            await conv.send_message(f"Token registered successfully!\nGenerated token: {token_value}")
        except Exception as e:
            await conv.send_message(f"Error: {e}")


@bot.on(events.CallbackQuery(pattern="VIEW_TOKENS"))
async def view_tokens(event):
    user_id = event.sender_id
    if user_id not in config.BOT_ADMINS:
        await event.respond("You are not authorized to view tokens.")
        return

    # Initialize page_number and store it in a dict to be used later
    tokens = tokens.find({}).limit(10)
    if not tokens:
        await event.respond("No more tokens to display.")
        return
    
    keys = []
    for token in tokens:
        keys.append([Button.inline(str(token["token"]), str.encode("find_token:" + str(token["token"])))])
    count = tokens.count_documents({})
    total_pages = count // 10
    if count % 10 != 0:
        total_pages += 1
    page_keys = navlib.paginate("tokens_list", 1, total_pages=total_pages)
    if len(page_keys) != 0:
        keys.append(page_keys)
    await event.reply("select token:", buttons=keys)


@bot.on(events.CallbackQuery(pattern="tokens_list:*"))
async def tokens_list(event):
    user_id = event.sender_id
    if user_id not in config.BOT_ADMINS:
        await event.respond("You are not authorized to view tokens.")
        return
    count_tokens = tokens.count_documents({})
    if count_tokens == 0:
        await event.reply("Tokens not found!")
        return
    current_page = int(event.data.decode().split(":")[1])
    skip = (current_page * 10) - 10
    # Initialize page_number and store it in a dict to be used later
    tokens = tokens.find({}).limit(10).skip(skip)
    if not tokens:
        await event.respond("No more tokens to display.")
        return
    
    keys = [

    ]
    for token in tokens:
        keys.append([Button.inline(str(token["token"]), str.encode("find_token:" + str(token["token"])))])
    count = tokens.count_documents({})
    total_pages = count // 10
    if count % 10 != 0:
        total_pages += 1
    page_keys = navlib.paginate("tokens_list", current_page, total_pages=total_pages)
    if len(page_keys) != 0:
        keys.append(page_keys)
    await event.reply("select token:", buttons=keys)


@bot.on(events.CallbackQuery(pattern="find_token:*"))
async def find_token(event):
    user_id = event.sender_id
    if user_id in config.BOT_ADMINS:
        token = event.data.decode().split(":")[1]
        token = tokens.find_one({"token": token})
        if token is None:
            await event.reply("Token not found!")
        else:
            message = (f"Creator ID: {token['creator_id']}\n"
            f"Token: {token['token']}\n"
            f"Credit: {token['credit']}\n\n")
            await event.reply(message)


bot.run_until_disconnected()
