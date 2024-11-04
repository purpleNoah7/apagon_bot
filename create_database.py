import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def verify_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id SERIAL PRIMARY KEY,
                bloque TEXT NOT NULL,
                dia TEXT NOT NULL,
                start_hour TEXT NOT NULL,
                end_hour TEXT NOT NULL,
                emergencia BOOLEAN NOT NULL
            )
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                bloque TEXT NOT NULL,
                telegram_id BIGINT
            )
            ''')
    print("Verificación de la base de datos exitosa.")