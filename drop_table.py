import sqlite3
conn = sqlite3.connect('Database/Scrapped_data.db')
c = conn.cursor()
c.execute("DROP TABLE IF EXISTS  amdocs")
# c.execute("DROP TABLE IF EXISTS output_amazon_01")
# c.execute("DROP TABLE IF EXISTS output_asianpaints_01")
# c.execute("DROP TABLE IF EXISTS output_apple_01")
# conn.commit()
conn.close()