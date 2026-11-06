import json
import os
import cloudscraper

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

API_URL = "https://www.voe.com.ua/disconnection/search.php"

PAYLOAD = {
    "csrf": "e09c1efcbee5f2fa39d462b972ea1e6eaf284cf022f9f566b8a290bf4040bbf7",
    "selected_eic": "",
    "website": "type",
    "address": "value",
    "city_id": "525610100",
    "city_label": "м.Ямпіль (Ямпільський Район/М.Ямпіль)",
    "street_id": "7730",
    "street_label": "вулиця Свободи",
    "house_id": "170637",
    "house_label": "140",
}

STATE_FILE = "last_data.json"


def send_telegram_message(text):
  if not TELEGRAM_TOKEN or not CHAT_ID:
    return
  url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
  cloudscraper.create_scraper().post(
      url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
  )


def check_schedule():
  # Создаем скрапер, который обходит защиту Cloudflare
  scraper = cloudscraper.create_scraper()

  try:
    response = scraper.post(API_URL, data=PAYLOAD, timeout=20)
    print(f"Статус ответа: {response.status_code}")

    # Пытаемся получить JSON
    current_data = response.json()
  except Exception as e:
    print(f"Ошибка: {e}")
    print(f"Ответ сервера: {response.text[:400]}")
    return

  previous_data = None
  if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as f:
      try:
        previous_data = json.load(f)
      except:
        pass

  if previous_data != current_data:
    msg = (
        "⚡ **ИЗМЕНЕНИЕ ГРАФИКА ОТКЛЮЧЕНИЙ!** ⚡\n\nЗафиксированы изменения по"
        " вашему адресу (ул. Свободы, 140)."
    )
    send_telegram_message(msg)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
      json.dump(current_data, f, ensure_ascii=False, indent+4 if 'indent+4' in globals() else 4) # исправлено на indent=4
    print("График изменился, уведомление отправлено!")
  else:
    print("Изменений нет.")


if __name__ == "__main__":
  check_schedule()
