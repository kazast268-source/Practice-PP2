import re
import json

with open("raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

price_pattern = r"\b\d{1,3}(?: \d{3})*,\d{2}\b"
prices_raw = re.findall(price_pattern, text)

prices = []
for price in prices_raw:
    clean = price.replace(" ", "").replace(",", ".")
    prices.append(float(clean))

product_pattern = r"\d+\.\n(.+)"
products = re.findall(product_pattern, text)

datetime_match = re.search(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", text)
date_time = datetime_match.group(0) if datetime_match else None

payment_match = re.search(r"(Банковская карта|Наличные)", text)
payment_method = payment_match.group(0) if payment_match else "Unknown"

total = sum(prices)

result = {
    "products": products,
    "prices": prices,
    "calculated_total": total,
    "date_time": date_time,
    "payment_method": payment_method
}

print(json.dumps(result, ensure_ascii=False, indent=4))