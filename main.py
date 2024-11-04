import telebot
import sqlite3
import os
import locale
import schedule
import threading
import time
from create_database import verify_database
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functions_database import create_user, get_user, update_user, login, delete_user, get_block_for_user, hay_apagon, get_apagones, clean_database, clean_horarios

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token del archivo .env

verify_database()
TOKEN = os.getenv('TELEGRAM_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')
bot = telebot.TeleBot(TOKEN)

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')



def add_apagones(bloque, dia, start_hour, end_hour, emergencia, message):

    conn = sqlite3.connect('apagones.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO horarios (bloque, dia, start_hour, end_hour, emergencia) VALUES (?, ?, ?, ?, ?)",
                   (bloque, dia, start_hour, end_hour, emergencia))
    conn.commit()
    conn.close()
    return True


@bot.message_handler(commands=['add'])
def add(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    bloques_list = ['B1', 'B2', 'B3', 'B4']
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    msg = bot.send_message(
        message.chat.id, "Por favor, selecciona tu bloque.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_bloque_step_add_apagon)


def process_bloque_step_add_apagon(message):
    bloque = message.text
    print(bloque)
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    day_list = ["lunes", "martes", "miércoles",
                "jueves", "viernes", "sábado", "domingo"]
    for day in day_list:
        markup.add(telebot.types.KeyboardButton(text=day))

    msg = bot.send_message(
        message.chat.id, "Por favor, selecciona el día.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_dia_step, bloque)


def process_dia_step(message, bloque):
    print(bloque)
    dia = message.text
    msg = bot.send_message(
        message.chat.id, 'Ingrese la hora de inicio (HH:MM):')
    bot.register_next_step_handler(msg, process_start_hour_step, bloque, dia)


def process_start_hour_step(message, bloque, dia):
    start_hour = message.text
    msg = bot.send_message(message.chat.id, 'Ingrese la hora de fin (HH:MM):')
    bot.register_next_step_handler(
        msg, process_end_hour_step, bloque, dia, start_hour)


def process_end_hour_step(message, bloque, dia, start_hour):
    end_hour = message.text
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    emergencys_list = ["sí", "no"]
    for emergency in emergencys_list:
        markup.add(telebot.types.KeyboardButton(text=emergency))

    msg = bot.send_message(
        message.chat.id, 'Seleccione si es emergencia (sí/no):', reply_markup=markup)

    bot.register_next_step_handler(
        msg, process_emergencia_step, bloque, dia, start_hour, end_hour)


def process_emergencia_step(message, bloque, dia, start_hour, end_hour):
    emergencia = (message.text.lower() == 'sí')

    add_apagones(bloque, dia, start_hour, end_hour, emergencia, message)
    bot.send_message(message.chat.id, 'Apagón añadido exitosamente.')


@bot.message_handler(commands=['clean'])
def clean(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return
    clean_horarios()
    bot.send_message(message.chat.id, 'Base de datos limpiada exitosamente.')


@ bot.message_handler(commands=['apagon'])
def start(message):
    bloque = get_block_for_user(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False)

    buttons = ['start', 'cambio', 'registrarse', 'notificar']

    for button in buttons:
        markup.add(telebot.types.KeyboardButton(text=button))

    if bloque is None:
        mensaje = f"¡Hola {
            message.from_user.first_name}! No estás registrado en ningún bloque. Por favor, usa el comando /registrarse para registrarte.\n\n"
        return bot.send_message(message.chat.id, mensaje)

    apagon = hay_apagon(bloque, datetime.now().strftime("%A"))
    mensaje = f"📅 Hoy es {datetime.now().strftime('%A, %d de %B %Y')}\n\n"
    mensaje += f"**Bloque {bloque}**:\n"

    if apagon:
        horarios = get_apagones(bloque, datetime.now().strftime("%A"))
        mensaje += "- **Apagones: **\n"
        for horario in horarios:
            emergencia = ' es de emergencia' if horario.emergencia else ''
            mensaje += f"  - El {horario.dia} desde las {
                horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        mensaje += "No hay apagones programados para hoy.\n"

    bot.send_message(message.chat.id, mensaje)


@ bot.message_handler(commands=['registrarse'])
def registrarse(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    existing_user = get_user(user_id)
    if existing_user:
        bot.send_message(
            chat_id, "Ya estás registrado en un bloque. Usa el comando /cambio si deseas cambiarlo.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True)
    bloques_list = ['B1', 'B2', 'B3', 'B4']
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    msg = bot.send_message(
        chat_id, "Por favor, selecciona tu bloque.", reply_markup=markup)
    bot.register_next_step_handler(msg, process_bloque_step, user_id, username)


def process_bloque_step(message, user_id, username):
    bloque = message.text
    create_user(user_id, username, bloque)
    bot.send_message(
        message.chat.id, f"Te has registrado con éxito en el bloque {bloque}.", reply_markup=telebot.types.ReplyKeyboardRemove())


@ bot.message_handler(commands=['stop'])
def stop(message):
    delete_user(message.from_user.id)
    bot.send_message(message.chat.id, "Has cancelado tu inscripción.")


def send_notification(user_id, bloque):
    hoy = datetime.now().strftime("%A")
    manana = (datetime.now() + timedelta(days=1)).strftime("%A")
    message = f"📅 Notificaciones de apagones para {bloque}\n\n"

    apagones_hoy = hay_apagon(bloque, hoy)
    if apagones_hoy:
        message += f"**Para hoy ({hoy}):**\n"
        for horario in get_apagones(bloque, hoy):
            emergencia = ' es de emergencia' if horario.emergencia else ''
            message += f"  - El {horario.dia} desde las {
                horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        message += f"No hay apagones programados para hoy ({hoy}).\n\n"

    apagones_manana = hay_apagon(bloque, manana)
    if apagones_manana:
        message += f"\n**Para mañana ({manana}):**\n"
        for horario in get_apagones(bloque, manana):
            emergencia = ' es de emergencia' if horario.emergencia == 'sí' else ''
            message += f"  - El {horario.dia} desde las {
                horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
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
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return
    notificar()
    bot.send_message(message.chat.id, "Notificaciones enviadas.")


# Start the scheduling thread
threading.Thread(target=run_schedule, daemon=True).start()


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Comandos disponibles:\n\n/start - Iniciar el bot\n/registrarse - Registrarse en un bloque\n/stop - Cancelar el registro de un bloque\n/apagon - Ver el horario de hoy de mi bloque")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "¡Hola! Estoy aquí para ayudarte a conocer sobre el horario de los apagones. ¿Qué necesitas?\n\n/registrarse - Registrarse en un bloque\n/stop - Cancelar el registro de un bloque\n/apagon - Ver el horario de hoy de mi bloque\n/notificar - Notificarme de los apagones programados\n/clean - Limpiar la base de datos")


bot.polling()
