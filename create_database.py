import sqlite3

# Conexión a la base de datos
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
    telefono TEXT,
    telegram_id INTEGER
)
''')


# Insertar datos de ejemplo
datos = [
    ('B1', 'Lunes', '10:00', '14:00', False),
    ('B1', 'Martes', '14:00', '18:00', True),
    ('B2', 'Lunes', '18:00', '22:00', False),
    ('B2', 'Martes', '10:00', '14:00', True),
    ('B1', 'Domingo', '14:00', '18:00', False),

]

cursor.executemany(
    "INSERT INTO horarios (bloque, dia, start_hour, end_hour, emergencia) VALUES (?, ?, ?, ?, ?)", datos)

# Confirmar la inserción
conn.commit()
print("Datos de ejemplo insertados correctamente.")

# Cerrar la conexión
conn.close()
