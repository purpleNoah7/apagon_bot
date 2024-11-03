import telebot
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os
from functions_database import create_user, get_user, update_user, login, delete_user, get_block_for_user

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token del archivo .env
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Función para obtener los horarios de la base de datos


def obtener_horarios(bloque):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    hoy = datetime.now().strftime("%A")  # Día actual en inglés
    cursor.execute(
        "SELECT horario, emergencia FROM horarios WHERE bloque=? AND dia=?", (bloque, hoy))
    result = cursor.fetchall()
    conn.close()
    return result

# Comando /start para iniciar el bot


@bot.message_handler(commands=['start'])
def start(message):
    bloque = get_block_for_user(message.from_user.id)
    if bloque:
        mensaje = f"¡Hola {message.from_user.first_name}! Ya estás registrado en el bloque {bloque[0]}."
    else:
        mensaje = f"¡Hola {message.from_user.first_name}! No estás registrado en ningún bloque. Por favor, usa el comando /registrarse para registrarte."

    horarios = obtener_horarios(bloque)
    mensaje = f"📅 Hoy es {datetime.now().strftime('%A, %d de %B %Y')}\n\n"
    mensaje += f"**Bloque {bloque}**:\n"
    if horarios:
        for horario, emergencia in horarios:
            mensaje += f"- **Horario Programado:** {horario}\n"
            mensaje += f"- **Emergencia:** {emergencia}\n\n"
    else:
        mensaje += "No hay apagones programados para hoy.\n"

    bot.send_message(message.chat.id, mensaje)
    

@bot.message_handler(commands=['registrarse'])
def registrarse(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    # Crear un teclado personalizado con opciones de bloques
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # Añadir botones al teclado (debes especificar las opciones disponibles)
    bloques = ['B1', 'B2', 'B3', 'B4']
    for bloque in bloques:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    # Enviar el mensaje con el teclado
    msg = bot.send_message(
        chat_id, "Por favor, selecciona tu bloque.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_bloque_step, user_id, username)


def process_bloque_step(message, user_id, username):
    bloque = message.text
    create_user(user_id, username, bloque)
    bot.send_message(
        message.chat.id, f"Te has registrado con éxito en el bloque {bloque}.")


bot.polling()
