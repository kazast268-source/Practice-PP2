import json
import csv
import psycopg2
from connect import connect

def export_to_json(filename="contacts_export.json"):
    conn = connect()
    cur = conn.cursor()
    query = """
        SELECT c.name, c.email, c.birthday, g.name, 
               array_agg(p.phone || ':' || p.type) as phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        GROUP BY c.id, g.name
    """
    cur.execute(query)
    rows = cur.fetchall()
    
    data = []
    for row in rows:
        data.append({
            "name": row[0], "email": row[1], 
            "birthday": str(row[2]), "group": row[3], "phones": row[4]
        })
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Exported to {filename}")
    cur.close()
    conn.close()

def import_from_json(filename):
    conn = connect()
    cur = conn.cursor()
    with open(filename, 'r') as f:
        contacts = json.load(f)
        
    for item in contacts:
        # Check for duplicate
        cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
        exists = cur.fetchone()
        
        if exists:
            choice = input(f"Contact {item['name']} exists. Overwrite? (y/n): ").lower()
            if choice != 'y': continue
            cur.execute("DELETE FROM contacts WHERE name = %s", (item['name'],))
        
        # Insert Logic (Simplified for brevity)
        cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name=EXCLUDED.name RETURNING id", (item['group'],))
        group_id = cur.fetchone()[0]
        
        cur.execute("INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id", 
                    (item['name'], item['email'], item['birthday'], group_id))
        contact_id = cur.fetchone()[0]
        
        for p_entry in item['phones']:
            if p_entry:
                p, t = p_entry.split(':')
                cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)", (contact_id, p, t))
    
    conn.commit()
    cur.close()
    conn.close()

def paginated_view():
    page = 0
    page_size = 5
    while True:
        conn = connect()
        cur = conn.cursor()
        # Using OFFSET for pagination
        cur.execute("SELECT name, email FROM contacts ORDER BY name LIMIT %s OFFSET %s", (page_size, page * page_size))
        rows = cur.fetchall()
        
        print(f"\n--- Page {page + 1} ---")
        for r in rows: print(f"{r[0]} | {r[1]}")
        
        cmd = input("\n[n]ext, [p]rev, [q]uit: ").lower()
        if cmd == 'n' and len(rows) == page_size: page += 1
        elif cmd == 'p' and page > 0: page -= 1
        elif cmd == 'q': break
        cur.close()
        conn.close()
def main_menu():
    while True:
        print("\n--- Меню PhoneBook ---")
        print("1. Показать контакты (Пагинация)")
        print("2. Поиск (Имя, Email, Телефон)")
        print("3. Добавить телефон существующему контакту (Procedure)")
        print("4. Сменить группу контакта (Procedure)")
        print("5. Экспорт в JSON")
        print("6. Импорт из JSON")
        print("0. Выйти")
        
        choice = input("\nВыберите действие: ")
        
        if choice == '1':
            paginated_view()
        elif choice == '2':
            query = input("Введите поисковый запрос (имя, почта или телефон): ")
            conn = connect()
            cur = conn.cursor()
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            results = cur.fetchall()
            if not results:
                print("Ничего не найдено.")
            else:
                print("\n--- Результаты поиска ---")
            for r in results:
                print(f"ID: {r[0]} | Имя: {r[1]} | Email: {r[2]} | Группа: {r[3]}")
                cur.close()
                conn.close()
        elif choice == '3':
            name = input("Имя контакта: ")
            phone = input("Новый телефон: ")
            p_type = input("Тип (home/work/mobile): ")
            conn = connect()
            cur = conn.cursor()
            cur.execute("CALL add_phone(%s::VARCHAR, %s::VARCHAR, %s::VARCHAR)", (name, phone, p_type))
            conn.commit()
            print("Готово.")
            cur.close()
            conn.close()
        elif choice == '4':
            name = input("Имя контакта: ")
            group = input("Новая группа: ")
            conn = connect()
            cur = conn.cursor()
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
            conn.commit()
            print("Группа обновлена.")
            cur.close()
            conn.close()
        elif choice == '5':
            export_to_json()
        elif choice == '6':
            filename = input("Введите имя файла (например, contacts.json): ")
            import_from_json(filename)
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный ввод, попробуйте снова.")

if __name__ == "__main__":
    print("PhoneBook Extended Edition")
    main_menu()
