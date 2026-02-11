class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)

class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    def __init__(self, name, age):
        super().__init__(name)   # вызываем конструктор родителя
        self.age = age

s = Student("Nurdaulet", 18)
print(s.name, s.age)


class Animal:
    def speak(self):
        print("Animal speaks")

class Dog(Animal):
    def speak(self):
        super().speak()
        print("Dog barks")

d = Dog()
d.speak()


class A:
    def greet(self):
        print("Hello from A")

class B(A):
    def greet(self):
        super().greet()
        print("Hello from B")

b = B()
b.greet()


class Shape:
    def area(self):
        print("Calculating area")

class Rectangle(Shape):
    def area(self):
        super().area()
        print("Rectangle area = width * height")

r = Rectangle()
r.area()

