# Student Records Management System

A console-based **Student Records Management System** built using **Python and MySQL**. The project allows users to manage database tables and student records through a simple menu-driven interface.

## Features

* Connect Python with MySQL
* Check database connection
* Create new tables
* Add columns to existing tables
* Insert records
* View all records
* Search records
* Update records
* Delete records
* Delete complete tables
* Count records
* Handle different MySQL data types
* Use parameterized queries for safer database operations
* Validate table and column names
* Commit and rollback database changes

## Technologies Used

* **Python**
* **MySQL**
* **mysql-connector-python**

## Project Structure

```text
Student-Records-Management/
│
├── main.py
├── python_mysql_connectivity.py
└── README.md
```

### `main.py`

Contains the menu and controls the flow of the program. It takes the user's choice and calls the appropriate database function.

### `python_mysql_connectivity.py`

Contains the functions responsible for connecting to MySQL and performing database operations such as creating tables, inserting records, updating records, searching, deleting, and counting records.

## Requirements

Make sure you have:

* Python 3.x
* MySQL Server
* A MySQL database
* `mysql-connector-python`

Install the required Python package:

```bash
pip install mysql-connector-python
```

## Database Setup

1. Install and start MySQL Server.
2. Create a database in MySQL.

For example:

```sql
CREATE DATABASE student_db;
```

3. Make sure MySQL is running on:

```text
localhost
```

4. The program will ask for your MySQL password when it starts.
5. Enter the database name when prompted.

## How to Run

Clone the repository:

```bash
git clone <your-repository-url>
```

Go into the project directory:

```bash
cd Student-Records-Management
```

Run the program:

```bash
python main.py
```

## Main Menu

The program provides options such as:

```text
1. Check connection
2. Create new table
3. See records
4. Add record
5. Update records
6. Search records
7. Delete table
8. Delete records
9. Count records
10. Add a column
11. Exit
```

Select an option by entering its corresponding number.

## Example Workflow

```text
Start Program
     ↓
Connect to MySQL
     ↓
Select Database
     ↓
Display Menu
     ↓
Choose Operation
     ↓
Perform Database Operation
     ↓
Return to Menu
     ↓
Exit
```

## Database Operations

### Create Table

The program allows the user to create a table by entering:

* Table name
* Column name
* Data type
* Optional constraint

Additional columns can also be added later.

### Insert Records

The program reads the table structure and asks the user to enter values for the available columns.

### Search Records

Records can be searched using a selected column and its value.

### Update Records

A particular record can be located using a column and then updated with a new value.

### Delete Records

Records can be deleted by selecting a column and providing the value used to identify the records.

### Count Records

The program uses SQL's `COUNT(*)` operation to determine the number of records in a table.

## Learning Objectives

This project was developed to practice:

* Python functions
* Loops and conditional statements
* Exception handling
* Python modules
* MySQL connectivity
* SQL queries
* CRUD operations
* Database table management
* Parameterized SQL queries
* Working with different database data types

## Future Improvements

Some possible improvements for future versions:

* Add a graphical user interface
* Add student-specific validation
* Add login/authentication
* Add proper student ID management
* Improve input validation
* Add pagination for large datasets
* Add reports and statistics
* Separate configuration from source code

## Author

**Bhanu Prabhat Suryavansham**
