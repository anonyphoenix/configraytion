import sys
sys.path.insert(0, '..')
from pymongo import MongoClient
import config


try:
    client = MongoClient(config.MONGO_URL)
    db = client[config.MONGO_DB]
    print(db.list_collection_names())
    user_rm = input('Enter a collection name to drop or * to drop all: ')
    if user_rm == '*':
        client.drop_database(config.MONGO_DB)
        print('Dropped all successfully.')
    else:
        result = db.drop_collection(user_rm)
        print(f'{result}')
except Exception as e:
    print(f'Error: {e}')
