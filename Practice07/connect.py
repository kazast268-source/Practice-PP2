import psycopg2

def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="phonebook",
        user="aktannurdaulet",
        password="astana2007"
    )
    return conn