import json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

URL = "https://www.goldr.org/"
OUT_FILE = "bajus.json"
VORI_GRAMS = 11.664


def parse_num(text):
    cleaned = re.sub(r"[^\d.]", "", text or "")
    return float(cleaned) if cleaned else 0.0


def send_telegram_message(payload):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Telegram secrets not set; skipping message.")
        return

    rates = payload.get("rates", {})
    r22 = rates.get("22 Karat", {})
    r21 = rates.get("21 Karat", {})
    r18 = rates.get("18 Karat", {})

    def fmt_line(label, item):
        gram_bdt = float(item.get("bdt", 0) or 0)
        vori_bdt = gram_bdt * VORI_GRAMS
        usd = float(item.get("usd", 0) or 0)
        return (
            f"• *{label}:*\n"
            f"  ├ ভরি: *৳{vori_bdt:,.0f}*\n"
            f"  └ গ্রাম: *৳{gram_bdt:,.0f}* (${usd:.2f})"
        )

    lines = [
        "🪙 *BAJUS গোল্ড রেট আপডেট (GoldR)*",
        f"🕒 সময়: {payload.get('updated_at', '')}",
        "",
        fmt_line("২২ ক্যারেট", r22),
        fmt_line("২১ ক্যারেট", r21),
        fmt_line("১৮ ক্যারেট", r18),
    ]
    text = "\n".join(lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        print("Telegram response status:", resp.status)


def fetch_goldr():
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain)

    rates = {}
    karat_labels = {
        "22 Karat": r"22\s*Karat\s*Gold",
        "21 Karat": r"21\s*Karat\s*Gold",
        "18 Karat": r"18\s*Karat\s*Gold",
        "Traditional": r"Traditional",
    }

    for key, label_regex in karat_labels.items():
        m_label = re.search(label_regex, plain, re.IGNORECASE)
        if not m_label:
            continue
        snippet = plain[m_label.end():m_label.end() + 300]

        bdt_matches = [parse_num(x) for x in re.findall(r"৳\s*([\d,]+(?:\.\d+)?)", snippet)]
        usd_matches = [parse_num(x) for x in re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", snippet)]

        valid_bdt = [v for v in bdt_matches if v > 10000]
        valid_usd = [u for u in usd_matches if u > 100]

        if valid_bdt:
            rates[key] = {
                "bdt": valid_bdt[0],
                "usd": valid_usd[0] if valid_usd else 0.0,
            }

    bd_tz = timezone(timedelta(hours=6))
    updated_at = datetime.now(bd_tz).strftime("%d %b %Y, %I:%M %p")

    payload = {
        "source": URL,
        "updated_at": updated_at,
        "rates": rates,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("Saved bajus.json:", json.dumps(payload, ensure_ascii=False))
    send_telegram_message(payload)


if __name__ == "__main__":
    try:
        fetch_goldr()
    except Exception as e:
        print("Error fetching goldr.org:", e) json
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

URL = "https://www.goldr.org/"
OUT_FILE = "bajus.json"


def parse_num(text):
    cleaned = re.sub(r"[^\d.]", "", text or "")
    return float(cleaned) if cleaned else 0.0


def send_telegram_message(payload):
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        print("Telegram secrets not set; skipping message.")
        return

    rates = payload.get("rates", {})
    r22 = rates.get("22 Karat", {})
    r21 = rates.get("21 Karat", {})
    r18 = rates.get("18 Karat", {})

    lines = [
        "🪙 *BAJUS গোল্ড রেট আপডেট (GoldR)*",
        f"🕒 সময়: {payload.get('updated_at', '')}",
        "",
        f"• ২২ ক্যারেট: *৳{r22.get('bdt', 0):,.0f}* (${r22.get('usd', 0):.2f})",
        f"• ২১ ক্যারেট: *৳{r21.get('bdt', 0):,.0f}* (${r21.get('usd', 0):.2f})",
        f"• ১৮ ক্যারেট: *৳{r18.get('bdt', 0):,.0f}* (${r18.get('usd', 0):.2f})",
    ]
    text = "\n".join(lines)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        print("Telegram response status:", resp.status)


def fetch_goldr():
    req = urllib.request.Request(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain)

    rates = {}
    karat_labels = {
        "22 Karat": r"22\s*Karat\s*Gold",
        "21 Karat": r"21\s*Karat\s*Gold",
        "18 Karat": r"18\s*Karat\s*Gold",
        "Traditional": r"Traditional",
    }

    for key, label_regex in karat_labels.items():
        m_label = re.search(label_regex, plain, re.IGNORECASE)
        if not m_label:
            continue
        snippet = plain[m_label.end():m_label.end() + 300]

        bdt_matches = [parse_num(x) for x in re.findall(r"৳\s*([\d,]+(?:\.\d+)?)", snippet)]
        usd_matches = [parse_num(x) for x in re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", snippet)]

        valid_bdt = [v for v in bdt_matches if v > 10000]
        valid_usd = [u for u in usd_matches if u > 100]

        if valid_bdt:
            rates[key] = {
                "bdt": valid_bdt[0],
                "usd": valid_usd[0] if valid_usd else 0.0,
            }

    bd_tz = timezone(timedelta(hours=6))
    updated_at = datetime.now(bd_tz).strftime("%d %b %Y, %I:%M %p")

    payload = {
        "source": URL,
        "updated_at": updated_at,
        "rates": rates,
    }

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print("Saved bajus.json:", json.dumps(payload, ensure_ascii=False))
    send_telegram_message(payload)


if __name__ == "__main__":
    try:
        fetch_goldr()
    except Exception as e:
        print("Error fetching goldr.org:", e)
