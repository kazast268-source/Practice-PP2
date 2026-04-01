"""from config import DB_NAME, USER, PASSWORD, HOST, PORT
import psycopg2
def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="phonebook",
        user="aktannurdaulet",
        password="astana2007"
    )
    return conn
from config import DB_NAME, USER, PASSWORD, HOST, PORT
import psycopg2

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

cur = conn.cursor()
print("Connected successfully")"""