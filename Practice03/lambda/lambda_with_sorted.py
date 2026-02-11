students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
sorted_students = sorted(students, key=lambda x: x[1])
print(sorted_students)


words = ["apple", "pie", "banana", "cherry"]
sorted_words = sorted(words, key=lambda x: len(x))
print(sorted_words)


numbers = [5, 2, 9, 1, 7]

result = sorted(numbers, key=lambda x: -x)

print(result)


words = ["cat", "elephant", "dog", "tiger"]

result = sorted(words, key=lambda x: len(x))

print(result)

pairs = [(1, 3), (4, 1), (2, 5), (3, 2)]

result = sorted(pairs, key=lambda x: x[1])

print(result)


people = [
    {"name": "Ali", "age": 22},
    {"name": "Dana", "age": 19},
    {"name": "Mira", "age": 25}
]

result = sorted(people, key=lambda x: x["age"])

print(result)



