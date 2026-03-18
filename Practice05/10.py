import re
s = input()
result = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
print(result)