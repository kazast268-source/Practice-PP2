from config import DB_NAME, USER, PASSWORD, HOST, PORT
import psycopg2

def connect():
    return psycopg2.connect(
        host=HOST,
        database=DB_NAME,
        user=USER,
        password=PASSWORD,
        port=PORT
    )