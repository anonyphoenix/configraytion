import sys
sys.path.insert(0, '..')
from pymongo import MongoClient
import config
import helper
import datetime


collection_name = 'tokens'

try:
    client = MongoClient(config.MONGO_URL)
    db = client[config.MONGO_DB]
    collection = db[collection_name]
except ConnectionError:
    print('Error: Could not connect to MongoDB. Please check your connection settings.')

try:
    token_credit = int(input('Enter token\'s credit: '))
except:
    print('Error: Credit must be integer.')

token_value = helper.generate_random_token()

token_data = {
    'creator_id': 0,
    'credit': token_credit,
    'token': token_value,
    'date_created': datetime.datetime.now()
}

try:
    result = collection.insert_one(token_data)
    print(f'Token inserted with id: {result.inserted_id}')
    print(f'Generated token: {token_value}')
except Exception as e:
    print(f'Error: {e}')

