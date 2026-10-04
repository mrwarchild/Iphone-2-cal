#!/usr/bin/env python3
"""
تولید تقویم شمسی (ICS) برای اشتراک در Calendar آیفون.
اجرا:  python3 generate.py            -> jalali.ics
گزینه‌ها: --from 1405 --to 1410
مناسبت‌های قمری (عید فطر، عاشورا و ...) هر سال جابه‌جا می‌شوند؛
آن‌ها را در extra_events.json (تاریخ میلادی) اضافه کنید.
"""
import argparse, datetime as dt, json, os, hashlib

# ---------- تبدیل میلادی -> شمسی ----------
def g2j(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = (355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
            + (gy2 + 399) // 400 + gd + g_d_m[gm - 1])
    jy = -1595 + 33 * (days // 12053); days %= 12053
    jy += 4 * (days // 1461); days %= 1461
    if days > 365:
        jy += (days - 1) // 365; days = (days - 1) % 365
    if days < 186:
        jm = 1 + days // 31; jd = 1 + days % 31
    else:
        jm = 7 + (days - 186) // 30; jd = 1 + (days - 186) % 30
    return jy, jm, jd

MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
WEEKDAYS = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"]  # Mon=0

def fa(n):
    return str(n).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

# ---------- مناسبت‌های ثابت شمسی: (ماه، روز): (عنوان، تعطیل؟) ----------
SOLAR_EVENTS = {
    (1, 1): ("جشن نوروز", True),
    (1, 2): ("تعطیلات نوروز", True),
    (1, 3): ("تعطیلات نوروز", True),
    (1, 4): ("تعطیلات نوروز", True),
    (1, 12): ("روز جمهوری اسلامی", True),
    (1, 13): ("روز طبیعت (سیزده‌به‌در)", True),
    (2, 1): ("بزرگداشت سعدی", False),
    (2, 11): ("روز کارگر", False),
    (2, 12): ("روز معلم", False),
    (2, 25): ("بزرگداشت فردوسی", False),
    (2, 28): ("بزرگداشت خیام", False),
    (3, 14): ("رحلت امام خمینی", True),
    (3, 15): ("قیام ۱۵ خرداد", True),
    (6, 1): ("روز پزشک (بوعلی سینا)", False),
    (7, 1): ("آغاز سال تحصیلی", False),
    (7, 20): ("بزرگداشت حافظ", False),
    (8, 13): ("روز دانش‌آموز", False),
    (9, 16): ("روز دانشجو", False),
    (9, 30): ("شب یلدا", False),
    (11, 22): ("پیروزی انقلاب اسلامی", True),
    (12, 29): ("ملی شدن صنعت نفت", True),
}

def esc(s):
    return s.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="y1", type=int, default=1405)
    ap.add_argument("--to", dest="y2", type=int, default=1410)
    ap.add_argument("--out", default="jalali.ics")
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    extra = {}
    p = os.path.join(here, "extra_events.json")
    if os.path.exists(p):
        for e in json.load(open(p, encoding="utf-8")):
            extra.setdefault(e["date"], []).append((e["title"], e.get("holiday", False)))

    # بازه میلادی: از 1 فروردین y1 (~20 مارس) تا پایان y2
    start = dt.date(a.y1 + 621, 3, 19)
    end = dt.date(a.y2 + 622, 3, 22)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//Jalali Calendar//FA//",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
             "X-WR-CALNAME:تقویم شمسی", "X-WR-TIMEZONE:Asia/Tehran",
             "REFRESH-INTERVAL;VALUE=DURATION:P1D", "X-PUBLISHED-TTL:P1D"]
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    d = start
    count = 0
    while d <= end:
        jy, jm, jd = g2j(d.year, d.month, d.day)
        if a.y1 <= jy <= a.y2:
            occ = []
            holiday = False
            if (jm, jd) in SOLAR_EVENTS:
                t, h = SOLAR_EVENTS[(jm, jd)]; occ.append(t); holiday |= h
            for t, h in extra.get(d.isoformat(), []):
                occ.append(t); holiday |= h
            date_txt = f"{fa(jd)} {MONTHS[jm-1]} {fa(jy)}"
            title = date_txt + (" | " + "، ".join(occ) if occ else "")
            if holiday:
                title += " (تعطیل)"
            desc = f"{WEEKDAYS[d.weekday()]} {date_txt}"
            if occ:
                desc += "\n" + "\n".join(occ)
            uid = hashlib.md5(d.isoformat().encode()).hexdigest() + "@jalali-cal"
            nxt = d + dt.timedelta(days=1)
            lines += ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
                      f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{nxt:%Y%m%d}",
                      f"SUMMARY:{esc(title)}", f"DESCRIPTION:{esc(desc)}",
                      "TRANSP:TRANSPARENT", "END:VEVENT"]
            count += 1
        d += dt.timedelta(days=1)
    lines.append("END:VCALENDAR")
    with open(os.path.join(here, a.out), "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")
    print(f"{count} روز نوشته شد -> {a.out}")

if __name__ == "__main__":
    main()
