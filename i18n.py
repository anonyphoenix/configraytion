import json

en_file = open('strings/en.json')
en_str = en_file.read()
en_file.close()
en = json.loads(en_str)

fa_file = open('strings/fa.json')
fa_str = fa_file.read()
fa_file.close()
fa = json.loads(fa_str)

def get(key, lang='en'):
    if lang == 'fa':
        return fa.get(key)
    else:
        return en.get(key)