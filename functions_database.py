import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

es_to_en_days = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

class Horario:
    def __init__(self, id, bloque, dia, start_hour, end_hour, emergencia):
        self.id = id
        self.bloque = bloque
        self.dia = dia
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.emergencia = emergencia

    def __repr__(self):
        return (f"Horario(id={self.id}, bloque={self.bloque}, dia='{self.dia}', "
                f"start_hour='{self.start_hour}', end_hour='{self.end_hour}', "
                f"emergencia={self.emergencia})")


def create_user(user_id, username, bloque):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO usuarios (telegram_id, nombre, bloque) VALUES (%s, %s, %s)",
                           (user_id, username, bloque))
    return True


def get_user(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE telegram_id=%s", (user_id,))
            result = cursor.fetchone()
    return result


def delete_user(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE telegram_id=%s", (user_id,))
    return True


def get_block_for_user(user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT bloque FROM usuarios WHERE telegram_id=%s", (user_id,))
            result = cursor.fetchone()
    return result[0] if result else None


def clean_horarios():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM horarios")
    return True


def hay_apagon(bloque, dia):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM horarios WHERE bloque=%s AND dia=%s", (bloque, dia))
            apagon_existe = cursor.fetchone()[0] > 0
    return apagon_existe


def get_apagones(bloque, dia):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, bloque, dia, start_hour, end_hour, emergencia FROM horarios WHERE bloque=%s AND dia=%s", (bloque, dia))
            rows = cursor.fetchall()
    apagones = [Horario(id=row[0], bloque=row[1], dia=row[2],
                        start_hour=row[3], end_hour=row[4], emergencia=row[5]) for row in rows]
    return apagones

def cambio_de_bloque(bloque, user_id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE usuarios SET bloque=%s WHERE telegram_id=%s", (bloque, user_id))
    return True

def eliminar_apagon(id):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM horarios WHERE id=%s", (id,))
    return True


def add_apagones(bloque, dia, start_hour, end_hour, emergencia, message):
    dia_ingles = es_to_en_days.get(dia.lower(), dia)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO horarios (bloque, dia, start_hour, end_hour, emergencia)
                VALUES (%s, %s, %s, %s, %s)
            """, (bloque, dia_ingles, start_hour, end_hour, emergencia))
    return True

def notificar(send_notification):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT telegram_id, bloque FROM usuarios")
            users = cursor.fetchall()
    for user_id, bloque in users:
        send_notification(user_id, bloque)