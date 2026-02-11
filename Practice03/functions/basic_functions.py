def my_function():
  print("Hello from a function")

  def my_function():
    print("Hello from a function")

my_function()


def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()


temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)

def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9
  print(fahrenheit_to_celsius(77))
  print(fahrenheit_to_celsius(95))
  print(fahrenheit_to_celsius(50))



def get_greeting():
  return "Hello from a function"

message = get_greeting()
print(message)


def myfunc():
  x = 300
  print(x)

myfunc()

def myfunc():
  x = 300
  def myinnerfunc():
    print(x)
  myinnerfunc()

myfunc()

x = 300

def myfunc():
  print(x)

myfunc()

print(x)


