import re

s = input()

matches = re.findall(r"[a-z]+_[a-z]+", s)

if matches:
    print(*matches)
else:
    print("No match")