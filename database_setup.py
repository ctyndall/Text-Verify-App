import sqlite3

DB_FILENAME = 'registration.db'

def setup_database():
	conn = sqlite3.connect(DB_FILENAME)
	c = conn.cursor()
	c.execute(''' CREATE TABLE students
				(
				phone_number INTEGER PRIMARY KEY,
				name 		TEXT,
				course		TEXT,
				pin			INTEGER,
				verified	INTEGER
				)
		''')

	conn.commit()
	conn.close()