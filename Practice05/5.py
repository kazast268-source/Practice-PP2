import re

s = input()

if re.fullmatch(r"a.*b", s):
    print("Yes")
else:
    print("No")