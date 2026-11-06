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

# Расширенные заголовки настоящего браузера Chrome
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.voe.com.ua/disconnection/detailed",
    "Origin": "https://www.voe.com.ua",
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
  # Создаем скрапер с имитацией браузера
  scraper = cloudscraper.create_scraper(
      browser={"custom": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}
  )

  try:
    response = scraper.post(API_URL, data=PAYLOAD, headers=HEADERS, timeout=20)
    print(f"Статус ответа: {response.status_code}")

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
      json.dump(current_data, f, ensure_ascii=False, indent=4)
    print("График изменился, уведомление отправлено!")
  else:
    print("Изменений нет.")


if __name__ == "__main__":
  check_schedule()
