import os

os.makedirs("project/data/files", exist_ok=True)
print("Nested directories created")





for item in os.listdir("."):
    print(item)

    import os

for file in os.listdir("."):
    if file.endswith(".txt"):
        print(file)