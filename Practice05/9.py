import re

s = input()
result = re.sub(r'(?<!^)(?=[A-Z])', ' ', s)
print(result)