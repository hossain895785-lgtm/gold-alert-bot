import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHAT_ID = os.environ.get("CHAT_ID", "")

TARGET_LOW_USD = 2600    # দাম এর নিচে নামলে মেসেজ আসবে
TARGET_HIGH_USD = 2800   # দাম এর ওপরে উঠলে মেসেজ আসবে
STATE_FILE = "state.json"


def fetch_json(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_gold_data():
    try:
        gold_json = fetch_json("https://api.gold-api.com/price/XAU")
        usd_per_ounce = float(gold_json.get("price", 0))
        if usd_per_ounce <= 0:
            return None

        fx_json = fetch_json("https://open.er-api.com/v6/latest/USD")
        usd_to_bdt = float(fx_json.get("rates", {}).get("BDT", 120))

        usd_per_gram = usd_per_ounce / 31.1035
        bdt_per_vori = round(usd_per_gram * 11.664 * usd_to_bdt)

        return usd_per_ounce, bdt_per_vori
    except Exception as e:
        print("Error fetching gold price:", e)
        return None


def send_telegram_message(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("BOT_TOKEN or CHAT_ID missing.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        resp.read()


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("alert_state", "NORMAL")
        except Exception:
            pass
    return "NORMAL"


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"alert_state": state}, f)


def dhaka_time():
    bd_tz = timezone(timedelta(hours=6))
    return datetime.now(bd_tz).strftime("%d/%m/%Y %I:%M %p")


def main():
    gold_data = get_gold_data()
    if not gold_data:
        return

    usd_per_ounce, bdt_per_vori = gold_data
    last_state = load_state()

    if usd_per_ounce <= TARGET_LOW_USD and last_state != "LOW_SENT":
        msg = (
            f"📉 *GOLD PRICE DROP ALERT!*\n\n"
            f"💰 স্পট গোল্ড: *${usd_per_ounce:.2f}* / আউন্স\n"
            f"🇧🇩 আনুমানিক ভরি: *৳{bdt_per_vori:,}* (২৪ ক্যারেট সমতুল্য)\n"
            f"🎯 লো-টার্গেট: ${TARGET_LOW_USD}\n"
            f"⏰ সময়: {dhaka_time()}"
        )
        send_telegram_message(msg)
        save_state("LOW_SENT")

    elif usd_per_ounce >= TARGET_HIGH_USD and last_state != "HIGH_SENT":
        msg = (
            f"📈 *GOLD PRICE PUMP ALERT!*\n\n"
            f"💰 স্পট গোল্ড: *${usd_per_ounce:.2f}* / আউন্স\n"
            f"🇧🇩 আনুমানিক ভরি: *৳{bdt_per_vori:,}* (২৪ ক্যারেট সমতুল্য)\n"
            f"🎯 হাই-টার্গেট: ${TARGET_HIGH_USD}\n"
            f"⏰ সময়: {dhaka_time()}"
        )
        send_telegram_message(msg)
        save_state("HIGH_SENT")

    elif TARGET_LOW_USD < usd_per_ounce < TARGET_HIGH_USD and last_state != "NORMAL":
        save_state("NORMAL")


if __name__ == "__main__":
    main()
