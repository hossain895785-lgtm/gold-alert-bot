import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta

URL = "https://www.goldr.org/"
OUT_FILE = "bajus.json"


def parse_num(text):
    cleaned = re.sub(r"[^\d.]", "", text or "")
    return float(cleaned) if cleaned else 0.0


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
        # ক্যারেটের নামের পরবর্তী ৩০০ ক্যারেক্টারের মধ্যে থাকা সব টাকা ও ডলারের মান নেওয়া
        m_label = re.search(label_regex, plain, re.IGNORECASE)
        if not m_label:
            continue
        snippet = plain[m_label.end():m_label.end() + 300]

        bdt_matches = [parse_num(x) for x in re.findall(r"৳\s*([\d,]+(?:\.\d+)?)", snippet)]
        usd_matches = [parse_num(x) for x in re.findall(r"\$\s*([\d,]+(?:\.\d+)?)", snippet)]

        # প্রতি ভরি সোনার দাম সাধারণত ১০,০০০ টাকার বেশি এবং ১০০ ডলারের বেশি হয়
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


if __name__ == "__main__":
    try:
        fetch_goldr()
    except Exception as e:
        print("Error fetching goldr.org:", e)import json
import re
import urllib.request
from datetime import datetime, timezone, timedelta

URL = "https://www.goldr.org/"
OUT_FILE = "bajus.json"


def parse_num(text):
    cleaned = re.sub(r"[^\d.]", "", text or "")
    return float(cleaned) if cleaned else 0.0


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

    # টেবিল বা টেক্সট থেকে ক্যারেট অনুযায়ী BDT ও USD বের করার চেষ্টা
    rates = {}
    karats = ["22 Karat", "21 Karat", "18 Karat", "Traditional"]

    # HTML ট্যাগ সরিয়ে সহজ লাইনে আনা
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain)

    for k in karats:
        # উদাহরণ: "22 Karat Gold ... ৳... $..."
        pattern = re.compile(
            re.escape(k) + r".*?৳\s*([\d,]+(?:\.\d+)?)\s*\$\s*([\d,]+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        m = pattern.search(plain)
        if m:
            rates[k] = {
                "bdt": parse_num(m.group(1)),
                "usd": parse_num(m.group(2)),
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


if __name__ == "__main__":
    try:
        fetch_goldr()
    except Exception as e:
        print("Error fetching goldr.org:", e)
