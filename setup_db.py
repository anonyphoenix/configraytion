from sqlite3 import connect

db = connect("configs.db")
cursor = db.cursor()

cursor.execute(f"CREATE TABLE IF NOT EXISTS config(url, in_channel, config_id)")
cursor.execute(f"ALTER TABLE config ADD text {None}")
# print(cursor.execute("SELECT * FROM config "))