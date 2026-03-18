import re
s = input()
matches = re.findall(r"[A-Z][a-z]+", s)
if matches:
    print(*matches)
else:
    print("No match")