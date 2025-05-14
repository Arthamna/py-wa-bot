import logging
from flask import current_app, jsonify
import json
import requests
from app.database import ScheduleManager
import re
import sqlite3
from datetime import datetime 
from zoneinfo import ZoneInfo

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

def async_checking():
    try:
        current_time = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"{current_time} : Running schedule check ")
        
        schedule_data = manager.check_schedules()
        process_schedule_data(schedule_data)
        return jsonify({"status": "success", "message": "sending data"}), 200
        
    except Exception as e:
        logging.error(f"Error in async_checking: {str(e)}")
        return jsonify({"status": "error", "message": "check log"}), 400
    
def process_schedule_data(schedule_data):
        upcoming_schedules = schedule_data.get("upcoming", [])
        if not upcoming_schedules:
            logging.info("No schedules found, skipping notification")
            return
        
        logging.info(f"Found schedules - Upcoming: {len(upcoming_schedules)}")
        try:
            current_message = format_schedule_message(upcoming_schedules)
            logging.info(f"Sending notification for current schedules: {upcoming_schedules}")
            send_schedule_notification(current_message)
        except Exception as e:
            logging.error(f"Error processing current schedules: {str(e)}")

def format_schedule_message(schedules):
    header = "⚠️ *JADWAL MENDATANG :*\n\n"
    
    message = header
    for idx, schedule in enumerate(schedules, 1):
        activity = schedule.get("activity", "")
        time = schedule.get("time", "")
        message += f"{idx}. {activity} - {time}\n"
    
    return message
    
def send_schedule_notification(message):
    try:
        data = get_text_message_input(recipient=current_app.config['RECIPIENT_WAID'], text=message)
        send_message(data)
        # logging.info("Schedule notification sent successfully")
    except Exception as e:
        logging.error(f"Failed to send schedule notification: {str(e)}")



manager = ScheduleManager()
def generate_response(message_body: str) -> str:
    message_body = message_body.lower()

    if message_body.startswith('tambah'):
        return process_add_command(message_body, manager)
    if message_body.startswith(('jadwal hari ini', 'hari ini')):
        return today(manager)
    if message_body.startswith(('jadwal minggu ini', 'minggu ini')):
        return week(manager)
    if message_body.startswith(('ganti nama', 'update nama')):
        return update_name(message_body, manager)
    if message_body.startswith(('ganti tanggal', 'update tanggal')):
        return update_date(message_body, manager)
    if message_body.startswith('hapus'):
        return delete_activity(message_body, manager)
        


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

def process_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    response = generate_response(message_body)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )



# passing data
def process_add_command(message_body, manager):
    pattern = r'^tambah(\s+.+?)\s+jam\s+(\d{1,2}:\d{2})(?:\s+tanggal\s+(\d{1,2})(?:\s+(\w+))?)?$'
    match = re.match(pattern, message_body, re.IGNORECASE)
    
    if not match:
        return "Format pesan salah. Contoh: *Tambah [aktivitas] jam [HH:MM] tanggal [(Opsional)] [Bulan (Opsional)]*"
    
    activity = match.group(1).strip()
    time = match.group(2).strip()
    date = match.group(3).strip() if match.group(3) else None
    month = match.group(4).strip() if match.group(4) else None

    try:
        response = manager.add_schedule(time=time, date=date, month=month, activity=activity)
    except sqlite3.IntegrityError as e:
        response = f"DB constraint error: {e}"
    except ValueError as e:
        response = f"Validation error: {e}"
    except Exception as e:
        response = f"Unexpected error: {e}"
    
    return response

def today(manager): 
    day_info, schedules = manager.get_today_schedules()

    if schedules:
        response = f"Jadwal untuk {day_info}:\n"
        for time, activity in schedules:
            response += f"- {time}: {activity}\n"
    else:
        response = f"Tidak ada jadwal untuk {day_info}"
        
    return response

def week(manager): 
    all_schedules = manager.get_weekly_schedules()
        
    if not all_schedules:
        return "Tidak ada jadwal untuk minggu ini."
    
    grouped_schedules = {}
    for time, activity, date, month in all_schedules:
        day_key = f"{date} {month}"
        if day_key not in grouped_schedules:
            grouped_schedules[day_key] = []
        grouped_schedules[day_key].append((time, activity))
    
    # Menyusun respons
    response = "Jadwal minggu ini:\n\n"
    for day_key, schedules in grouped_schedules.items():
        response += f"🗓️ {day_key}:\n"
        for time, activity in schedules:
            response += f"⏰ {time} - {activity}\n"
        response += "\n"
    
    return response.strip()

def update_name(message_body, manager): 
    pattern = r'^(?:ganti nama|update nama)\s+(.+?)\s+menjadi\s+(.+?)(?:\s+tanggal\s+(\d{1,2})(?:\s+(\w+))?)?$'
    match = re.match(pattern, message_body, re.IGNORECASE)
    
    if not match:
        return "Format pesan salah. Contoh: *ganti nama [aktivitas lama] menjadi [aktivitas baru] tanggal [DD (Opsional)] [Bulan (Opsional)]*"
    
    old_activity = match.group(1).strip()
    new_activity = match.group(2).strip()
    date = match.group(3).strip() if match.group(3) else None
    month = match.group(4).strip() if match.group(4) else None
    
    try:
        success = manager.update_activity_name( activity=old_activity, date=date, month=month, new_activity=new_activity)
        if success:
            return f"Jadwal '{old_activity}' berhasil diubah menjadi '{new_activity}'."
        else:
            return f"Jadwal '{old_activity}' tidak ditemukan."
    except ValueError as e:
        return f"Validation error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def update_date(message_body, manager): 
    pattern = r'^(?:ganti tanggal|update tanggal)\s+(.+?)\s+dari\s+(\d{1,2})\s+menjadi\s+(\d{1,2})(?:\s+(\w+))?$'
    match = re.match(pattern, message_body, re.IGNORECASE)
    
    if not match:
        return "Format pesan salah. Contoh: *ganti tanggal [aktivitas] dari [tanggal lama] menjadi [tanggal baru] [Bulan (Opsional)]*"
    
    activity = match.group(1).strip()
    old_date = match.group(2).strip()
    new_date = match.group(3).strip()
    month = match.group(4).strip().lower() if match.group(4) else None
    
    try:
        success = manager.update_schedule_time(activity=activity, date=old_date, new_date=new_date, month=month)
        if success:
            return f"Jadwal '{activity}' berhasil diubah dari tanggal {old_date} ke tanggal {new_date}."
        else:
            return f"Jadwal '{activity}' pada tanggal {old_date} tidak ditemukan."
            
    except ValueError as e:
        return f"Validation error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"
    
def delete_activity(message_body, manager):
    pattern = r'^hapus\s+(.+?)(?:\s+tanggal\s+(\d{1,2})(?:\s+(\w+))?)?$'
    match = re.match(pattern, message_body, re.IGNORECASE)
    
    if not match:
        return "Format pesan salah. Contoh: *hapus [aktivitas] tanggal [(Opsional)] [Bulan (Opsional)]*"
    
    activity = match.group(1).strip()
    date = match.group(2).strip() if match.group(2) else None 
    month = match.group(3).strip() if match.group(3) else None

    try:
        success = manager.remove_activity(activity=activity, date=date, month=month)
        if success :
            result_message = f"Aktivitas '{activity}' berhasil dihapus."
            return result_message
        else:
            return f"Aktivitas '{activity}' tidak ditemukan."

    except sqlite3.IntegrityError as e:
        response = f"DB constraint error: {e}"
    except ValueError as e:
        response = f"Validation error: {e}"
    except Exception as e:
        response = f"Unexpected error: {e}"
    
    return response
