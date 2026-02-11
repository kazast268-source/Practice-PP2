class A:
    def method_a(self):
        print("Method A")

class B:
    def method_b(self):
        print("Method B")

class C(A, B):   # ← наследуем от двух классов
    pass

obj = C()
obj.method_a()
obj.method_b()


class Father:
    def __init__(self):
        print("Father constructor")

class Mother:
    def __init__(self):
        print("Mother constructor")

class Child(Father, Mother):
    pass

c = Child()

class A:
    def greet(self):
        print("Hello from A")

class B:
    def greet(self):
        print("Hello from B")

class C(A, B):
    def greet(self):
        super().greet()

c = C()
c.greet()

class Engine:
    def start(self):
        print("Engine started")

class Wheels:
    def roll(self):
        print("Car is rolling")

class Car(Engine, Wheels):
    pass

c = Car()
c.start()
c.roll()

