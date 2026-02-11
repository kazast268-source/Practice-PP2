class Animal:
    def speak(self):
        print("Animal makes sound")


class Dog(Animal):   # ← Dog наследует Animal
    pass


d = Dog()
d.speak()


class Person:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print("Hello", self.name)


class Student(Person):
    def study(self):
        print(self.name, "is studying")


s1 = Student("Nurdaulet")
s1.greet()
s1.study()

class Person:
  def __init__(self, fname, lname):
    self.firstname = fname
    self.lastname = lname

  def printname(self):
    print(self.firstname, self.lastname)

#Use the Person class to create an object, and then execute the printname method:

x = Person("John", "Doe")
x.printname()



class Animal:
    def eat(self):
        print("Animal is eating")

class Cat(Animal):
    def meow(self):
        print("Meow")

c = Cat()
c.eat()
c.meow()

class Person:
    def __init__(self, name):
        self.name = name

class Student(Person):
    pass

s = Student("Nurdaulet")
print(s.name)


