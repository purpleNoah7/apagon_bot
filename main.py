import telebot
import os
import schedule
import threading
import time
from create_database import verify_database
from datetime import datetime, timedelta
from dotenv import load_dotenv
from functions_database import (
    create_user,
    get_user,
    delete_user,
    get_block_for_user,
    hay_apagon,
    get_apagones,
    clean_horarios,
    cambio_de_bloque,
    add_apagones,
    notificar,
    get_connection,
)

# Cargar variables del archivo .env
load_dotenv()

# Obtener el token del archivo .env

verify_database()
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
bot = telebot.TeleBot(TOKEN)

en_to_es_days = {
    "Monday": "lunes",
    "Tuesday": "martes",
    "Wednesday": "miércoles",
    "Thursday": "jueves",
    "Friday": "viernes",
    "Saturday": "sábado",
    "Sunday": "domingo",
}

es_to_en_days = {v: k for k, v in en_to_es_days.items()}


@bot.message_handler(commands=["send_db"])
def send_db(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return

    try:
        with open("apagones.db", "rb") as db_file:
            bot.send_document(message.chat.id, db_file)
    except Exception as e:
        bot.send_message(
            message.chat.id, f"No se pudo enviar la base de datos: {str(e)}"
        )


@bot.message_handler(commands=["add"])
def add(message):
    user_id_str = str(message.from_user.id)
    print(user_id_str)
    print(ADMIN_ID)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    bloques_list = ["B1", "B2", "B3", "B4"]
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    msg = bot.send_message(
        message.chat.id, "Por favor, selecciona tu bloque.", reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_bloque_step_add_apagon)


def process_bloque_step_add_apagon(message):
    bloque = message.text
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    day_list = list(en_to_es_days.values())
    for day in day_list:
        markup.add(telebot.types.KeyboardButton(text=day))

    msg = bot.send_message(
        message.chat.id, "Por favor, selecciona el día.", reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_dia_step, bloque)


def process_dia_step(message, bloque):
    dia = message.text
    msg = bot.send_message(message.chat.id, "Ingrese la hora de inicio (HH:MM):")
    bot.register_next_step_handler(msg, process_start_hour_step, bloque, dia)


def process_start_hour_step(message, bloque, dia):
    start_hour = message.text
    msg = bot.send_message(message.chat.id, "Ingrese la hora de fin (HH:MM):")
    bot.register_next_step_handler(msg, process_end_hour_step, bloque, dia, start_hour)


def process_end_hour_step(message, bloque, dia, start_hour):
    end_hour = message.text
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    emergencys_list = ["sí", "no"]
    for emergency in emergencys_list:
        markup.add(telebot.types.KeyboardButton(text=emergency))

    msg = bot.send_message(
        message.chat.id, "Seleccione si es emergencia (sí/no):", reply_markup=markup
    )

    bot.register_next_step_handler(
        msg, process_emergencia_step, bloque, dia, start_hour, end_hour
    )


def process_emergencia_step(message, bloque, dia, start_hour, end_hour):
    emergencia = message.text.lower() == "sí"
    add_apagones(bloque, dia, start_hour, end_hour, emergencia, message)
    bot.send_message(message.chat.id, "Apagón añadido exitosamente.")


@bot.message_handler(commands=["clean"])
def clean(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return
    clean_horarios()
    bot.send_message(message.chat.id, "Base de datos limpiada exitosamente.")


@bot.message_handler(commands=["apagon"])
def start(message):
    bloque = get_block_for_user(message.from_user.id)

    markup = telebot.types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=False
    )

    buttons = ["start", "cambio", "registrarse", "notificar"]

    for button in buttons:
        markup.add(telebot.types.KeyboardButton(text=button))

    if bloque is None:
        mensaje = f"¡Hola {message.from_user.first_name}! No estás registrado en ningún bloque. Por favor, usa el comando /registrarse para registrarte.\n\n"
        return bot.send_message(message.chat.id, mensaje)

    hoy = datetime.now().strftime("%A")
    apagon = hay_apagon(bloque, hoy)
    hoy_es = en_to_es_days.get(hoy, hoy)
    mensaje = f"📅 Hoy es {hoy_es}, {datetime.now().strftime('%d de %B %Y')}\n\n"
    mensaje += f"**Bloque {bloque}**:\n"

    if apagon:
        horarios = get_apagones(bloque, hoy)
        mensaje += "- **Apagones: **\n"
        for horario in horarios:
            emergencia = " es de emergencia" if horario.emergencia else ""
            dia_es = en_to_es_days.get(horario.dia, horario.dia)
            mensaje += f"- El {dia_es} desde las {horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        mensaje += "No hay apagones programados para hoy.\n"

    bot.send_message(message.chat.id, mensaje)


def send_notification(user_id, bloque):
    hoy = datetime.now().strftime("%A")
    manana = (datetime.now() + timedelta(days=1)).strftime("%A")
    hoy_es = en_to_es_days.get(hoy, hoy)
    manana_es = en_to_es_days.get(manana, manana)

    message = f"📅 Notificaciones de apagones para {bloque}\n\n"

    apagones_hoy = hay_apagon(bloque, hoy)
    if apagones_hoy:
        message += f"**Para hoy ({hoy_es}):**\n"
        for horario in get_apagones(bloque, hoy):
            emergencia = " es de emergencia" if horario.emergencia else ""
            dia_es = en_to_es_days.get(horario.dia, horario.dia)
            message += f"- El {dia_es} desde las {horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        message += f"No hay apagones programados para hoy ({hoy_es}).\n\n"

    apagones_manana = hay_apagon(bloque, manana)
    if apagones_manana:
        message += f"\n**Para mañana ({manana_es}):**\n"
        for horario in get_apagones(bloque, manana):
            emergencia = " es de emergencia" if horario.emergencia else ""
            dia_es = en_to_es_days.get(horario.dia, horario.dia)
            message += f"- El {dia_es} desde las {horario.start_hour} hasta las {horario.end_hour} {emergencia}\n"
    else:
        message += f"No hay apagones programados para mañana ({manana_es}).\n"

    bot.send_message(user_id, message)


@bot.message_handler(commands=["registrarse"])
def registrarse(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    existing_user = get_user(user_id)
    if existing_user:
        bot.send_message(
            chat_id,
            "Ya estás registrado en un bloque. Usa el comando /cambio si deseas cambiarlo.",
        )
        return

    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    bloques_list = ["B1", "B2", "B3", "B4"]
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))

    msg = bot.send_message(
        chat_id, "Por favor, selecciona tu bloque.", reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_bloque_step, user_id, username)


def process_bloque_step(message, user_id, username):
    bloque = message.text
    if bloque != "B1" and bloque != "B2" and bloque != "B3" and bloque != "B4":
        bot.send_message(message.chat.id, "El bloque seleccionado no es válido.")
        return
    create_user(user_id, username, bloque)
    bot.send_message(
        message.chat.id,
        f"Te has registrado con éxito en el bloque {bloque}.",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["clean"])
def clean(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return
    clean_horarios()
    bot.send_message(message.chat.id, "Base de datos limpiada exitosamente.")


@bot.message_handler(commands=["cambio"])
def cambio(message):
    bot.send_message(message.chat.id, "Por favor, selecciona tu bloque.")
    markup = telebot.types.ReplyKeyboardMarkup(
        one_time_keyboard=True, resize_keyboard=True
    )
    bloques_list = ["B1", "B2", "B3", "B4"]
    for bloque in bloques_list:
        markup.add(telebot.types.KeyboardButton(text=bloque))
    msg = bot.send_message(
        message.chat.id, "Por favor, selecciona tu bloque.", reply_markup=markup
    )
    bot.register_next_step_handler(msg, process_bloque_step_cambio, message)


def process_bloque_step_cambio(message, previous_message):
    bloque = message.text
    if bloque != "B1" and bloque != "B2" and bloque != "B3" and bloque != "B4":
        bot.send_message(message.chat.id, "El bloque seleccionado no es válido.")
        return
    cambio_de_bloque(bloque, previous_message.from_user.id)
    bot.send_message(
        previous_message.chat.id,
        f"Se ha cambiado tu bloque a {bloque}.",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )


@bot.message_handler(commands=["stop"])
def stop(message):
    delete_user(message.from_user.id)
    bot.send_message(message.chat.id, "Has cancelado tu inscripción.")


# Schedule tasks
schedule.every(6).hours.do(notificar, send_notification)


def run_schedule():
    while True:
        schedule.run_pending()
        print("Scheduler: Running...")
        time.sleep(60)


@bot.message_handler(commands=["notificar"])
def notificarMSG(message):
    bot.send_message(
        message.chat.id,
        "Este bot envia notificaciones de apagones a los usuarios registrados cada 6h.",
    )


@bot.message_handler(commands=["tiposdeapagones"])
def notificarMSG(message):
    bot.send_message(
        message.chat.id,
        "Existen 2 tipos de apagones según la UNE:\n\n- Programados: Por deficit de generacion\n- Emergencia: ante situaciones de emergencias por salidas imprevistas de plantas generadoras",
    )


@bot.message_handler(commands=["notificaradmin"])
def notificarMSG(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return
    notificar()
    bot.send_message(message.chat.id, "Notificaciones enviadas.")


@bot.message_handler(commands=["broadcast"])
def broadcast(message):
    user_id_str = str(message.from_user.id)
    if user_id_str != ADMIN_ID:
        bot.send_message(message.chat.id, "No eres el administrador.")
        return

    # Extract the text after the command
    broadcast_message = message.text.partition(" ")[2]

    if not broadcast_message:
        bot.send_message(
            message.chat.id, "Por favor, proporciona un mensaje para el broadcast."
        )
        return

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT telegram_id FROM usuarios")
            users = cursor.fetchall()

    for (user_id,) in users:
        bot.send_message(user_id, broadcast_message)

    bot.send_message(message.chat.id, "Notificaciones enviadas a todos los usuarios.")


# Start the scheduling thread
threading.Thread(target=run_schedule, daemon=True).start()


@bot.message_handler(commands=["help"])
def help(message):
    bot.send_message(
        message.chat.id,
        "Comandos disponibles:\n\n/start - Iniciar el bot\n/registrarse - Registrarse en un bloque\n/stop - Cancelar el registro de un bloque\n/apagon - Ver el horario de hoy de mi bloque\n, /notificar - Notificarme de los apagones programados\n/cambio - Cambiar de bloque\n/tiposdeapagones - Ver los tipos de apagones",
    )


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "¡Hola! Estoy aquí para ayudarte a conocer sobre el horario de los apagones. ¿Qué necesitas?\n\nComandos disponibles:\n\n/start - Iniciar el bot\n/registrarse - Registrarse en un bloque\n/stop - Cancelar el registro de un bloque\n/apagon - Ver el horario de hoy de mi bloque\n, /notificar - Notificarme de los apagones programados\n/cambio - Cambiar de bloque\n/tiposdeapagones - Ver los tipos de apagones",
    )


bot.polling()
