numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_numbers = list(filter(lambda x: x % 2 != 0, numbers))
print(odd_numbers)


numbers = [1, 2, 3, 4, 5, 6]

result = list(filter(lambda x: x % 2 == 0, numbers))

print(result)


numbers = [5, 12, 8, 20, 3, 15]

result = list(filter(lambda x: x > 10, numbers))

print(result)


words = ["cat", "elephant", "dog", "tiger"]

result = list(filter(lambda x: len(x) > 4, words))

print(result)


numbers = [-5, 3, 0, -2, 8, 1]

result = list(filter(lambda x: x > 0, numbers))

print(result)

