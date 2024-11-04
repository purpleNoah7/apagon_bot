import telebot
import sqlite3
import os
import locale
import schedule
import threading
import time

from datetime import datetime, timedelta
from dotenv import load_dotenv
from functions_database import create_user, get_user, update_user, login, delete_user, get_block_for_user, hay_apagon, get_apagones

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token del archivo .env
TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)


locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')


def obtener_horarios(bloque):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    hoy = datetime.now().strftime("%A")  # Día actual en español
    cursor.execute(
        "SELECT horario, emergencia FROM horarios WHERE bloque=? AND dia=?", (bloque, hoy))
    result = cursor.fetchall()
    conn.close()
    return result


def obtener_horarios_por_dia(bloque, dia):
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT horario,  WHERE bloque=? AND dia=?", (bloque, dia))
    result = cursor.fetchall()
    conn.close()
    return result


@bot.message_handler(commands=['start'])
def start(message):
    bloque = get_block_for_user(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False)

    buttons = ['start', 'cambio', 'registrarse', 'notificar']

    for button in buttons:
        markup.add(telebot.types.KeyboardButton(text=button))

    if bloque == None:
        mensaje = f"¡Hola {message.from_user.first_name}! No estás registrado en ningún bloque. Por favor, usa el comando /registrarse para registrarte.\n\n"
        return bot.send_message(message.chat.id, mensaje)

    apagon = hay_apagon(bloque, datetime.now().strftime("%A"))
    if apagon:
        horario = get_apagones(bloque, datetime.now().strftime("%A"))
    mensaje = f"📅 Hoy es {datetime.now().strftime('%A, %d de %B %Y')}\n\n"
    mensaje += f"**Bloque {bloque}**:\n"
    if apagon:
        mensaje += "- **Apagones: **\n"
        for horario in horario:
            emergencia = ' es de emergencia' if horario else ''
            mensaje += f"  - El {horario.dia} desde las {horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        mensaje += "No hay apagones programados para hoy.\n"

    bot.send_message(message.chat.id, mensaje)


@bot.message_handler(commands=['registrarse'])
def registrarse(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    existing_user = get_user(user_id)
    if existing_user:
        bot.send_message(
            chat_id, "Ya estás registrado en un bloque. Usa el comando /cambio si deseas cambiarlo.")
        return

    # Crear un teclado personalizado con opciones de bloques
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    # Añadir botones al teclado (debes especificar las opciones disponibles)
    bloques_list = ['B1', 'B2', 'B3', 'B4']
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    # Enviar el mensaje con el teclado
    msg = bot.send_message(
        chat_id, "Por favor, selecciona tu bloque.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_bloque_step, user_id, username)


def process_bloque_step(message, user_id, username):
    bloque = message.text
    create_user(user_id, username, bloque)
    # Envía el mensaje de confirmación sin el teclado
    bot.send_message(
        message.chat.id, f"Te has registrado con éxito en el bloque {bloque}.", reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['stop'])
def stop(message):
    delete_user(message.from_user.id)
    bot.send_message(message.chat.id, "Has cancelado tu inscripción.")


def send_notification(user_id, bloque):
    hoy = datetime.now().strftime("%A")
    manana = (datetime.now() + timedelta(days=1)).strftime("%A")
    apagones_hoy = hay_apagon(bloque, hoy)
    apagones_manana = hay_apagon(bloque, manana)

    if apagones_hoy:
        message = f"📅 Notificaciones de apagones para {bloque}\n\n"
        message += f"**Para hoy ({hoy}):**\n"
        for horario in get_apagones(bloque, hoy):
            emergencia = ' es de emergencia' if horario.emergencia else ''
            message += f"  - El {horario.dia} desde las {
                horario.start_hour} hasta las {horario.end_hour} {emergencia}"
    else:
        message += f"No hay apagones programados para hoy ({hoy}).\n\n"

    if apagones_manana:
        message += f"\n**Para mañana ({manana}):**\n"
        for horario in get_apagones(bloque, manana):
            emergencia = ' es de emergencia' if horario.emergencia == 'sí' else ''
            message += f"  - El {horario.dia} desde las {
                horario.start_hour} hasta las {horario.end_hour} {emergencia}"
    else:
        message += f"No hay apagones programados para mañana ({manana}).\n"

    bot.send_message(user_id, message)


def notificar():
    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("SELECT telegram_id, bloque FROM usuarios")
    users = cursor.fetchall()
    conn.close()
    for user_id, bloque in users:
        send_notification(user_id, bloque)


# Schedule tasks
schedule.every().day.at("00:00").do(notificar)
schedule.every().day.at("06:00").do(notificar)


def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)


@bot.message_handler(commands=['notificar'])
def notificarMSG(message):
    notificar()
    bot.send_message(message.chat.id, "Notificaciones enviadas.")


# Start the scheduling thread
threading.Thread(target=run_schedule, daemon=True).start()


bot.polling()
