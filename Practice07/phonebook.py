from connect import connect
import csv
def insert_user():
    name = input("Enter name: ")
    phone = input("Enter phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO nurdau (name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()
    cur.close()
    conn.close()
def insert_from_csv():
    conn = connect()
    cur = conn.cursor()

    with open("contacts.csv", newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            cur.execute(
                "INSERT INTO nurdau (name, phone) VALUES (%s, %s)",
                (row[0], row[1])
            )
    conn.commit()
    cur.close()
    conn.close()
def query_data():
    print("1. Show all")
    print("2. Search by name")
    print("3. Search by phone prefix")

    choice = input("Choose: ")

    conn = connect()
    cur = conn.cursor()

    if choice == "1":
        cur.execute("SELECT * FROM nurdau")

    elif choice == "2":
        name = input("Enter name: ")
        cur.execute("SELECT * FROM nurdau WHERE name=%s", (name,))

    elif choice == "3":
        prefix = input("Enter prefix: ")
        cur.execute("SELECT * FROM nurdau WHERE phone LIKE %s", (prefix + "%",))

    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()
def update_user():
    name = input("Enter name to update: ")
    new_name = input("New name (leave empty to skip): ")
    new_phone = input("New phone (leave empty to skip): ")

    conn = connect()
    cur = conn.cursor()

    if new_name:
        cur.execute(
            "UPDATE nurdau SET name=%s WHERE name=%s",
            (new_name, name)
        )

    if new_phone:
        cur.execute(
            "UPDATE nurdau SET phone=%s WHERE name=%s",
            (new_phone, name)
        )

    conn.commit()
    cur.close()
    conn.close()



def delete_user():
    print("1. Delete by name")
    print("2. Delete by phone")

    choice = input("Choose: ")

    conn = connect()
    cur = conn.cursor()

    if choice == "1":
        name = input("Enter name: ")
        cur.execute("DELETE FROM nurdau WHERE name=%s", (name,))

    elif choice == "2":
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM nurdau WHERE phone=%s", (phone,))

    conn.commit()
    cur.close()
    conn.close()
def main():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1. Insert from console")
        print("2. Insert from CSV")
        print("3. Query")
        print("4. Update")
        print("5. Delete")
        print("0. Exit")
        choice = input("Choose: ")
        if choice == "1":
            insert_user()
        elif choice == "2":
            insert_from_csv()
        elif choice == "3":
            query_data()
        elif choice == "4":
            update_user()
        elif choice == "5":
            delete_user()
        elif choice == "0":
            break
if __name__ == "__main__":
    main()