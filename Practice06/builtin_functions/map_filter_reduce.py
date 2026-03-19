#map
nums = [1, 2, 3, 4]
squares = list(map(lambda x: x**2, nums))
print(squares)
#filder
nums = [1, 2, 3, 4, 5, 6]
evens = lis(filter(lambda x: x % 2 == 0, nums))
print(evens)
#reduce
from functools import reduce
nums = [1, 2, 3, 4]
total = reduce(lambda x, y: x + y, nums)
print(total)