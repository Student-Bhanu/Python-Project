import mysql.connector as m
import time
import os
import sys
import re

conn = None
cur = None
password = None

NUMERIC_TYPES = {
    "bit", "tinyint", "smallint", "mediumint", "int", "integer",
    "bigint", "bool", "boolean", "float", "double", "decimal", "dec"
}

STRING_TYPES = {
    "char", "varchar", "binary", "varbinary", "tinytext", "text",
    "mediumtext", "longtext", "tinyblob", "blob", "mediumblob",
    "longblob", "enum", "set"
}

DATE_TYPES = {"date"}
DATETIME_TYPES = {"datetime", "timestamp"}
TIME_TYPES = {"time"}
YEAR_TYPES = {"year"}

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def valid_identifier(name):
    return bool(IDENTIFIER_RE.fullmatch(name))

def require_identifier(name, what="name"):
    if not valid_identifier(name):
        raise ValueError(f"Invalid {what}: use letters, digits and underscore only, "
                         f"and do not start with a digit.")

def table_exists(table_name):
    require_identifier(table_name, "table name")
    cur.execute("SHOW TABLES LIKE %s", (table_name,))
    return cur.fetchone() is not None

def get_columns(table_name):
    require_identifier(table_name, "table name")
    return cur.fetchall()

def get_column_names(table_name):
    return [row[0] for row in get_columns(table_name)]

def quote_identifier(name):
    require_identifier(name)
    return f"`{name}`"

def show_error(prefix="Operation failed"):
    print(f"{prefix}.")

def connect_to_mysql():
    global conn, cur, password

    while True:
        password = input("\nEnter your password: ")

        try:
            conn = m.connect(
                host="localhost",
                user="root",
                password=password
            )
            cur = conn.cursor()
            cur.execute("SHOW DATABASES")
            databases = cur.fetchall()

            print("\nAvailable databases:")
            for database in databases:
                print(database[0])

            conn.close()
            conn = None
            cur = None
            break

        except m.Error:
            print("Entered password is wrong or MySQL is unavailable. "
                  "Please re-enter the password.")

def select_database():
    global conn, cur

    while True:
        database_name = input("Enter your database: ").strip()

        if not valid_identifier(database_name):
            print("Invalid database name.")
            continue

        try:
            temp_conn = m.connect(
                host="localhost",
                user="root",
                password=password
            )
            temp_cur = temp_conn.cursor()
            temp_cur.execute("SHOW DATABASES LIKE %s", (database_name,))
            exists = temp_cur.fetchone() is not None
            temp_cur.close()
            temp_conn.close()

            if not exists:
                print("The database does not exist. Please type it again.")
                continue

            conn = m.connect(
                host="localhost",
                user="root",
                password=password,
                database=database_name
            )
            cur = conn.cursor()
            print(f"Connected to database: {database_name}")
            break

        except m.Error as e:
            print(f"Database connection failed: {e}")

def connection():
    if conn and conn.is_connected():
        print("Connection established successfully.")
        return True

    print("Connection is not active.")
    return False

def create_tb():
    try:
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()

        if not tables:
            print("This database is empty; no table created before.")
        else:
            print("Existing tables:")
            for row in tables:
                print(row[0].upper())

        table_name = input("Enter table name: ").strip()
        require_identifier(table_name, "table name")

        column_name = input("Enter name of column: ").strip()
        require_identifier(column_name, "column name")

        data_type = input("Enter datatype of column: ").strip().upper()

        constraint_choice = input(
            "If you want to add constraint press 1 otherwise press 2: "
        ).strip()

        if constraint_choice == "1":
            constraint = input("Enter constraint: ").strip()
            query = (
                f"CREATE TABLE {quote_identifier(table_name)} "
                f"({quote_identifier(column_name)} {data_type} {constraint})"
            )
        else:
            query = (
                f"CREATE TABLE {quote_identifier(table_name)} "
                f"({quote_identifier(column_name)} {data_type})"
            )

        cur.execute(query)
        conn.commit()
        print("Table created successfully.")

        while True:
            add_more = input(
                "For add more column in table press 1 otherwise press 2: "
            ).strip()

            if add_more != "1":
                break

            add_column(table_name)

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not create table: {e}")

def add_column(table_name):
    try:
        require_identifier(table_name, "table name")

        column_name = input("Enter column name: ").strip()
        require_identifier(column_name, "column name")

        data_type = input("Enter datatype of column: ").strip().upper()

        constraint_choice = input(
            "If you want to add constraint press 1 otherwise press 2: "
        ).strip()

        if constraint_choice == "1":
            constraint = input("Enter constraint: ").strip()
            query = (
                f"ALTER TABLE {quote_identifier(table_name)} "
                f"ADD {quote_identifier(column_name)} {data_type} {constraint}"
            )
        else:
            query = (
                f"ALTER TABLE {quote_identifier(table_name)} "
                f"ADD {quote_identifier(column_name)} {data_type}"
            )

        cur.execute(query)
        conn.commit()
        print("Column added successfully.")

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not add column: {e}")

def records_read():
    try:
        table_name = input("Enter table name from where you want all data: ").strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        columns = get_column_names(table_name)
        query = f"SELECT * FROM {quote_identifier(table_name)}"
        cur.execute(query)
        rows = cur.fetchall()

        if not rows:
            print("No records found.")
            return

        for row in rows:
            print(dict(zip(columns, row)))
            print()

    except (ValueError, m.Error) as e:
        print(f"Could not read records: {e}")

def records_wrt():
    try:
        table_name = input(
            "Enter table name in which you want to add records: "
        ).strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        columns = get_columns(table_name)

        while True:
            values = []

            for column_name, data_type in columns:
                if data_type in DATETIME_TYPES:
                    value = input(
                        f"Enter {column_name} (YYYY-MM-DD hh:mm:ss), "
                        f"or NULL: "
                    )
                elif data_type in DATE_TYPES:
                    value = input(
                        f"Enter {column_name} (YYYY-MM-DD), or NULL: "
                    )
                elif data_type in TIME_TYPES:
                    value = input(
                        f"Enter {column_name} (hh:mm:ss), or NULL: "
                    )
                elif data_type in YEAR_TYPES:
                    value = input(f"Enter {column_name} (YYYY), or NULL: ")
                else:
                    value = input(f"Enter {column_name}, or NULL: ")

                values.append(None if value.strip().upper() == "NULL" else value)

            names = ", ".join(quote_identifier(c[0]) for c in columns)
            placeholders = ", ".join(["%s"] * len(values))

            query = (
                f"INSERT INTO {quote_identifier(table_name)} "
                f"({names}) VALUES ({placeholders})"
            )

            cur.execute(query, tuple(values))
            conn.commit()
            print("Data entered successfully.")

            if input(
                "For add more records press 1 for stop press 2: "
            ).strip() != "1":
                break

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Data was not entered: {e}")

def _get_value_for_column(prompt, data_type):
    value = input(prompt)
    return None if value.strip().upper() == "NULL" else value

def update_rec():
    try:
        table_name = input(
            "Enter table name in which you want to update records: "
        ).strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        columns = get_columns(table_name)
        column_names = [c[0] for c in columns]

        print("Available columns:", ", ".join(column_names))

        update_column = input(
            "Which field do you want to update? "
        ).strip()

        if update_column not in column_names:
            print("Invalid update column.")
            return

        update_type = dict(columns)[update_column]

        search_column = input(
            "By which field do you want to find the record? "
        ).strip()

        if search_column not in column_names:
            print("Invalid search column.")
            return

        search_type = dict(columns)[search_column]

        search_value = _get_value_for_column(
            f"Enter {search_column} of the student: ",
            search_type
        )

        new_value = _get_value_for_column(
            f"Enter new {update_column}: ",
            update_type
        )

        if search_value is None:
            where_clause = f"{quote_identifier(search_column)} IS NULL"
            params = (new_value,)
        else:
            where_clause = f"{quote_identifier(search_column)} = %s"
            params = (new_value, search_value)

        query = (
            f"UPDATE {quote_identifier(table_name)} "
            f"SET {quote_identifier(update_column)} = %s "
            f"WHERE {where_clause}"
        )

        cur.execute(query, params)
        conn.commit()

        print(f"Data updated successfully. Rows affected: {cur.rowcount}")

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not update record: {e}")

def search_rec():
    try:
        table_name = input(
            "Enter table name in which you want to search records: "
        ).strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        columns = get_columns(table_name)
        column_names = [c[0] for c in columns]
        print("Available columns:", ", ".join(column_names))

        search_column = input(
            "Choose the field by which you want to search: "
        ).strip()

        if search_column not in column_names:
            print("Invalid search column.")
            return

        data_type = dict(columns)[search_column]

        search_value = _get_value_for_column(
            f"Enter {search_column}: ",
            data_type
        )

        if search_value is None:
            query = (
                f"SELECT * FROM {quote_identifier(table_name)} "
                f"WHERE {quote_identifier(search_column)} IS NULL"
            )
            cur.execute(query)
        else:
            query = (
                f"SELECT * FROM {quote_identifier(table_name)} "
                f"WHERE {quote_identifier(search_column)} = %s"
            )
            cur.execute(query, (search_value,))

        rows = cur.fetchall()

        if not rows:
            print("Sorry, no such data found.")
            return

        for row in rows:
            print(dict(zip(column_names, row)))
            print()

    except (ValueError, m.Error) as e:
        print(f"Could not search records: {e}")

def drop_tb():
    try:
        table_name = input("Enter table name which you want to delete: ").strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        confirm = input(
            f"WARNING: This will permanently delete '{table_name}'. "
            "Type YES to continue: "
        ).strip()

        if confirm != "YES":
            print("Operation cancelled.")
            return

        cur.execute(f"DROP TABLE {quote_identifier(table_name)}")
        conn.commit()
        print("Table deleted successfully.")

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not delete table: {e}")

def drop_rec():
    try:
        table_name = input(
            "Enter table name in which you want to delete records: "
        ).strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        columns = get_columns(table_name)
        column_names = [c[0] for c in columns]
        print("Available columns:", ", ".join(column_names))

        search_column = input(
            "Choose the field by which you want to find the record: "
        ).strip()

        if search_column not in column_names:
            print("Invalid search column.")
            return

        data_type = dict(columns)[search_column]
        search_value = _get_value_for_column(
            f"Enter {search_column}: ",
            data_type
        )

        if search_value is None:
            where_clause = f"{quote_identifier(search_column)} IS NULL"
            params = ()
        else:
            where_clause = f"{quote_identifier(search_column)} = %s"
            params = (search_value,)

        query = (
            f"DELETE FROM {quote_identifier(table_name)} "
            f"WHERE {where_clause}"
        )

        confirm = input(
            "Type YES to permanently delete matching records: "
        ).strip()

        if confirm != "YES":
            print("Operation cancelled.")
            return

        cur.execute(query, params)
        conn.commit()

        print(f"Record deletion completed. Rows affected: {cur.rowcount}")

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not delete records: {e}")

def rec_count():
    try:
        table_name = input("Enter table name: ").strip()

        if not table_exists(table_name):
            print("No such table found.")
            return

        query = f"SELECT COUNT(*) FROM {quote_identifier(table_name)}"
        cur.execute(query)
        count = cur.fetchone()[0]

        print("The number of records are:", count)

    except (ValueError, m.Error) as e:
        print(f"Could not count records: {e}")

def change_tb():
    try:
        table_name = input("Enter table name: ").strip()

        if not table_exists(table_name):
            print("Table does not exist.")
            return

        while True:
            print(
                "Existing columns:",
                ", ".join(get_column_names(table_name))
            )
            add_column(table_name)

            if input(
                "If you want to add more column press 1 otherwise press 2: "
            ).strip() != "1":
                break

    except (ValueError, m.Error) as e:
        conn.rollback()
        print(f"Could not alter table: {e}")

def close_connection():
    global cur, conn

    try:
        if cur:
            cur.close()
        if conn and conn.is_connected():
            conn.close()
    except m.Error:
        pass

def controller():
    while True:
        print("\n1. Check connection")
        print("2. Create table")
        print("3. See records")
        print("4. Add record")
        print("5. Update record")
        print("6. Search record")
        print("7. Delete table")
        print("8. Delete records")
        print("9. Count records")
        print("10. Add column")
        print("11. Exit")

        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Enter a valid number.")
            continue

        if choice == 1:
            connection()
        elif choice == 2:
            create_tb()
        elif choice == 3:
            records_read()
        elif choice == 4:
            records_wrt()
        elif choice == 5:
            update_rec()
        elif choice == 6:
            search_rec()
        elif choice == 7:
            drop_tb()
        elif choice == 8:
            drop_rec()
        elif choice == 9:
            rec_count()
        elif choice == 10:
            change_tb()
        elif choice == 11:
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    text = "*" * 10 + " Welcome to STUDENT RECORDS MANAGEMENT SYSTEM " + "*" * 10

    for character in text:
        sys.stdout.write(character)
        sys.stdout.flush()
        time.sleep(0.02)

    try:
        connect_to_mysql()
        select_database()
        controller()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    finally:
        close_connection()