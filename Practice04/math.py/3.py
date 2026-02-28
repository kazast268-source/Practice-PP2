import math

n = int(input("Input number of sides: "))
side = float(input("Input the length of a side: "))

area = (n * side * side) / (4 * math.tan(math.pi / n))
print("The area of the polygon is:", int(area) if area.is_integer() else area)