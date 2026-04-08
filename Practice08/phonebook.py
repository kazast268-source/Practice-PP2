from connect import connect

conn = connect()
cur = conn.cursor()


def add_contact(name, surname, phone):
    cur.execute("CALL upsert_contact(%s, %s, %s)", (name,surname, phone))
    conn.commit()


def print_rows(rows):
    if not rows:
        print("No contacts found")
        return

    for i, row in enumerate(rows, start=1):
        name, surname, phone = row
        print(f"{i}. Name: {name} | Surname: {surname} | Phone: {phone}")


def show():
    limit = int(input("Limit: "))
    offset = int(input("Offset: "))
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s, %s)", (limit, offset))
    rows = cur.fetchall()
    print_rows(rows)


def insert_many():
    names = ["Aydyn", "Azamat", "Nurdaulet"]
    surnames = ["Darkhanuly", "Esbol", "Aktan"]
    phones = ["10000", "20000", "30000"]

    cur.execute("CALL insert_m(%s, %s, %s)", (names, surnames, phones))
    conn.commit()

    print("Inserted successfully")


def update_phone(name, new_phone):
    cur.execute("CALL upsert_contact(%s, %s)", (name, new_phone))
    conn.commit()


def update_name(old_name, new_name):
    cur.execute("UPDATE contacts SET name=%s WHERE name=%s", (new_name, old_name))
    conn.commit()


def search_pattern(pattern):
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    rows = cur.fetchall()
    print_rows(rows)


def delete_contact(value):
    cur.execute("CALL delete_contact(%s)", (value,))
    conn.commit()


# MENU
while True:
    print("\n1)Add 2)Show 3)Update phone 4)Update name 5)Delete 6)Search 8)Insert many 10)Exit")
    n = input("Choose: ")

    if n == "1":
        name = input("Name: ")
        phone = input("Phone: ")
        add_contact(name, phone)

    elif n == "2":
        show()

    elif n == "3":
        name = input("Name: ")
        phone = input("New phone: ")
        update_phone(name, phone)

    elif n == "4":
        old = input("Old name: ")
        new = input("New name: ")
        update_name(old, new)

    elif n == "5":
        val = input("Enter name or phone: ")
        delete_contact(val)

    elif n == "6":
        pattern = input("Enter pattern: ")
        search_pattern(pattern)

    elif n == "8":
        insert_many()

    elif n == "10":
        break