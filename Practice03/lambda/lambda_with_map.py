numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)

numbers = [1, 2, 3, 4]

result = list(map(lambda x: x * 2, numbers))

print(result)

numbers = [2, 3, 4, 5]

result = list(map(lambda x: x ** 2, numbers))

print(result)


words = ["apple", "banana", "cherry"]

result = list(map(lambda x: x.upper(), words))

print(result)


numbers = ["10", "20", "30"]

result = list(map(lambda x: int(x), numbers))

print(result)


