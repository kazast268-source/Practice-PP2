import shutil

shutil.copy("a.txt", "b.txt")
print("Backup created.")

import os

if os.path.exists("b.txt"):
    os.remove("b.txt")
    print("b deleted.")
else:
    print("File not found.")