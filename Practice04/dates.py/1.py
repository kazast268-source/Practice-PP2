from datetime import datetime, timedelta

current_date = datetime.now()
new_date = current_date - timedelta(days=5)
print(new_date)