import sqlite3


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
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (telegram_id, nombre, bloque) VALUES (?, ?, ?)",
                   (user_id, username, bloque))
    conn.commit()
    conn.close()
    return True


def get_user(user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE telegram_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def update_user(user_id, username, telegram_id, bloque):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET username=?, bloque=?, telegram_id=? WHERE id=?",
                   (username, bloque, telegram_id, user_id))
    conn.commit()
    conn.close()
    return True


def login(user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def delete_user(user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return True


def get_block_for_user(user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT bloque FROM usuarios WHERE telegram_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def clean_database():
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios")
    cursor.execute("DELETE FROM horarios")
    conn.commit()
    conn.close()
    return True


def clean_horarios():
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM horarios")
    conn.commit()
    conn.close()
    return True


def hay_apagon(bloque, dia):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM horarios WHERE bloque=? AND dia=?", (bloque, dia))
    apagon_existe = cursor.fetchone()[0] > 0
    conn.close()
    return apagon_existe


def get_apagones(bloque, dia):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, bloque, dia, start_hour, end_hour, emergencia FROM horarios WHERE bloque=? AND dia=?", (bloque, dia))
    rows = cursor.fetchall()
    conn.close()
    apagones = [Horario(id=row[0], bloque=row[1], dia=row[2],
                        start_hour=row[3], end_hour=row[4], emergencia=row[5]) for row in rows]
    return apagones

def cambio_de_bloque(bloque, user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET bloque=? WHERE telegram_id=?", (bloque, user_id))
    conn.commit()
    conn.close()
    return True

def eliminar_apagon(id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM horarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return True

