import re
s = input()
if re.fullmatch(r"ab*", s):
    print("Yes")
else:
    print("No")