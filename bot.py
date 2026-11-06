import json
import os
import requests

# Настройки из секретов GitHub (или подставь свои для тестов)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# URL и параметры запроса к сайту Винницаоблэнерго
# (URL нужно взять из вкладки Headers -> Request URL твоего запроса search.php)
URL = "https://www.voe.com.ua/disconnection/detailed"  # или точный адрес search.php из Headers
API_URL = "https://www.voe.com.ua/disconnection/search.php"  # замени на точный URL из F12, если отличается

# Пример данных для отправки POST-запроса (подставь те параметры, которые уходят в Payload)
PAYLOAD = {
    # Сюда нужно перенести данные из вкладки Payload твоего запроса (город, улица, дом или ID)
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

STATE_FILE = "last_data.json"


def send_telegram_message(text):
  if not TELEGRAM_TOKEN or not CHAT_ID:
    print("Telegram token or Chat ID not set!")
    return
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Ошибка отправки в Telegram: {e}")


def check_schedule():
  try:
    # Делаем запрос к сайту
    response = requests.post(API_URL, data=PAYLOAD, headers=HEADERS, timeout=15)
    current_data = response.json()
  except Exception as e:
    print(f"Ошибка при запросе к сайту: {e}")
    return

  # Читаем предыдущее состояние, если оно есть
  previous_data = None
  if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
      try:
        previous_data = json.load(f)
      except:
        pass

  # Сравниваем текущие данные с прошлыми
  if previous_data != current_data:
    print("Обнаружены изменения в графике!")

    # Формируем уведомление
    msg = (
        "⚡ **ИЗМЕНЕНИЕ ГРАФИКА ОТКЛЮЧЕНИЙ!** ⚡\n\nПо вашему адресу зафиксированы"
        " изменения в графике Винницаоблэнерго."
    )
    send_telegram_message(msg)

    # Сохраняем новые данные как актуальные
    with open(STATE_FILE, "w", encoding="utf-8") as f:
      json.dump(current_data, f, ensure_ascii=False, indent=4)
  else:
    print("Изменений нет.")


if __name__ == "__main__":
  check_schedule()
