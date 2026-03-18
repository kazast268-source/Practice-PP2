import re
s = input()
result = re.split(r'(?=[A-Z])', s)
print(result)