#enumerate
names = ["Alice", "Bob", "Charlie"]
for i, name in enumerate(names):
    print(i, name)
#zip
names = ["Alice", "Bob"]
scores = [90, 85]
for name, score in zip(names, scores):
    print(name, score)
#enumerate+zip
names = ["Alice", "Bob"]
scores = [90, 85]
for i, (name, score) in enumerate(zip(names, scores)):
    print(i, name, score)