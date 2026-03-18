import re

s = input()
result = re.sub(r"_([a-zA-Z])", lambda x: x.group(1).upper(), s)
print(result)