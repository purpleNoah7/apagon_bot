import sqlite3

def create_user(user_id, username, bloque):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (telegram_id, nombre, bloque) VALUES (?, ?, ?)", (user_id, username, bloque))
    conn.commit()
    conn.close()
    return True

def get_user(user_id):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user(user_id, username, telegram_id, bloque):
      conn = sqlite3.connect('apagones.db')
      cursor = conn.cursor()
      cursor.execute("UPDATE usuarios SET username=?, bloque=?, telegram_id=? WHERE id=?", (username, bloque, telegram_id, user_id))
      conn.commit()
      conn.close()
      return True

def login (user_id):
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
    cursor.execute("SELECT bloque FROM usuarios WHERE telegram_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None