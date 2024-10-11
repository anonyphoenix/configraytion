from fastapi import FastAPI, Response
import json
from pymongo import MongoClient, DESCENDING
import config
import logging


if config.LOG_TO_FILE:
    logging.basicConfig(filename=config.LOG_FILE, level=config.LOG_LEVEL)
else:
    logging.basicConfig(level=config.LOG_LEVEL)

db = MongoClient(config.MONGO_URL)
configs = db[config.MONGO_DB]['configs']
tokens = db[config.MONGO_DB]['tokens']

app = FastAPI()


@app.get('/sub/')
async def get_sub_link(token: str):
    find_token = tokens.find_one({'token': token})
    if find_token is None:
        response = {
            'status': 403,
            'message': 'Token is invalid!'
        }
        return Response(json.dumps(response), 403)
    else:
        token_credit = find_token['credit']
        if token_credit <= 0:
            response = {
                'status': 403,
                'message': 'The user balance is not enough!'
            }
            return Response(json.dumps(response), 403)
        else:      
            response_text = ''
            find_configs = configs.find().sort('config_id', DESCENDING)
            for c in find_configs:
                response_text += c['url'] + '#' + c['country_emoji'] + ' ' + config.BOT_LINK + ' ' + c['country'] + '\n'
            tokens.update_one(find_token, {'$set': {'credit': int(token_credit) - 1}})
            return Response(response_text, 200)