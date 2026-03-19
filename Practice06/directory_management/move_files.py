import shutil

shutil.copy("a.txt", "project/a.txt")
print("File copied")

shutil.move("a.txt", "project/a.txt")
print("File moved")