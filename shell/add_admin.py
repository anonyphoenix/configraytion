import sys
sys.path.insert(0, '..')
from pymongo import MongoClient
import config
import datetime


collection_name = 'users'

try:
    client = MongoClient(config.MONGO_URL)
    db = client[config.MONGO_DB]
    users = db[collection_name]
except ConnectionError:
    print('Error: Could not connect to MongoDB. Please check your connection settings.')

try:
    admin_id = int(input('Enter admin\'s ID: '))
except:
    print('Error: ID must be integer.')

try:
    users.update_one({
        'user_id': admin_id
    }, { '$set': {
        'user_group': 'admin'
    }, '$setOnInsert': {
        'user_id': admin_id,
        'user_type': 'user',
        'lang': 'en',
        'registration_time': datetime.datetime.now(),
        'last_config_request_time': datetime.datetime.min
    }}, upsert=True)
    print(f'Admin added.')
except Exception as e:
    print(f'Error: {e}')
