import random
import sqlite3

import config
import database_setup
from twilio.rest import TwilioRestClient
from twilio.rest.exceptions import TwilioRestException

def send_pin(to_number, pin):
    body = 'Here is your pin: {}'.format(pin)
    account = config.twilio_account
    token = config.twilio_token
    client = TwilioRestClient(account, token)
    try:
        message = client.sms.messages.create(to=to_number,
                                         from_=config.twilio_number,
                                         body=body)
        return "pass"
    except TwilioRestException:
        return "fail"

def create_pin():
    forbidden = [123456, 111111, 222222, 333333, 444444, 666666, 777777, 888888, 999999]
    pin = random.randint(100001, 999998)
    if pin in forbidden:
        create_pin()  # skip numbers that could be accidently guessed
    return pin

def add_user(phone_number, name, course, pin):
    conn = sqlite3.connect(database_setup.DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO students VALUES (?, ?, ?, ?, 0)
        ''', (phone_number, name, course, pin)) # 0 means unverified
    conn.commit()
    conn.close()

def remove_user(phone_number):
    conn = sqlite3.connect(database_setup.DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        DELETE FROM students
        WHERE phone_number == ?''', (phone_number, ))
    conn.commit()
    conn.close()   


def check_user(phone_number):
    conn = sqlite3.connect(database_setup.DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        SELECT verified FROM students 
        WHERE phone_number == ?''', (phone_number,))
    res = c.fetchall()
    conn.commit()
    conn.close()
    return res

def update_pin(phone_number, new_pin):
    conn = sqlite3.connect(database_setup.DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        UPDATE students
        SET pin = ?
        WHERE phone_number == ?
        ''', (new_pin, phone_number))
    conn.commit()
    conn.close()    

def verify_pin(phone_number, pin):
    conn = sqlite3.connect(database_setup.DB_FILENAME)
    c = conn.cursor()
    c.execute('''
        SELECT pin FROM students WHERE phone_number == ?
        ''', (phone_number,))

    res = c.fetchall()[0][0]

    print pin, res
    if str(pin) == str(res):
        ans = True
        c.execute('''
            UPDATE students 
            SET verified = 1
            WHERE phone_number == ?''', (str(phone_number),))
    else:
        ans = False

    conn.commit()
    conn.close()

    print ans
    return ans

def get_info(phone_number):
    def dict_factory(cursor, row):
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conn = sqlite3.connect(database_setup.DB_FILENAME)
    conn.row_factory = dict_factory

    c = conn.cursor()
    c.execute('''
        SELECT phone_number, name, course FROM students WHERE phone_number == ?
        ''', (phone_number,))

    res = c.fetchall()
    conn.commit()
    conn.close()

    return res