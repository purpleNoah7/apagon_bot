import sqlite3


def add_apagones(bloque, dia, horario, emergencia):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO horarios (bloque, dia, horario, emergencia) VALUES (?, ?, ?, ?)",
                   (bloque, dia, horario, emergencia))
    conn.commit()
    conn.close()
    return True


add_apagones('B2', 'lunes', '10:00-14:00', True)
add_apagones('B2', 'domingo', '14:00-18:00', False)
add_apagones('B2', 'lunes', '18:00-22:00', False)
add_apagones('B2', 'martes', '10:00-14:00', False)