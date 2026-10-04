# تقویم شمسی برای آیفون

تقویم اشتراکی (ICS) با تاریخ شمسی و مناسبت‌های هر روز.

## اشتراک در آیفون
آدرس زیر را (USERNAME و REPO را عوض کنید) در
Settings ← Calendar ← Accounts ← Add Account ← Other ← Add Subscribed Calendar وارد کنید:

```
https://USERNAME.github.io/REPO/jalali.ics
```

## افزودن مناسبت
مناسبت‌های قمری را با تاریخ میلادی در `extra_events.json` بنویسید:

```json
[{"date": "2027-03-10", "title": "عید فطر", "holiday": true}]
```

بعد از ذخیره، به‌صورت خودکار `jalali.ics` دوباره ساخته می‌شود (GitHub Actions)؛
یا دستی: `python3 generate.py`
