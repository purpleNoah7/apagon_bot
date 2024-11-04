import sqlite3


def verify_database():
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bloque TEXT NOT NULL,
        dia TEXT NOT NULL,
        start_hour TEXT NOT NULL,
        end_hour TEXT NOT NULL,
        emergencia BOOLEAN NOT NULL
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        bloque TEXT NOT NULL,
        telegram_id INTEGER
    )
    ''')
    conn.commit()
    conn.close()
    print("Verificación de la base de datos exitosa.")
