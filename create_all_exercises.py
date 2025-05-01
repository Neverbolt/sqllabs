#!/usr/bin/env python
"""
Script to create all example exercises for SQL Labs.
This script combines all the previously separate exercise creation scripts
into a single, well-organized file that uses the current data model.
"""
import os
import django
import json
import time

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqllabs.settings')
django.setup()

from exercises.models import Exercise, Placeholder, Category


def create_exercise(title, description, setup_code, base_query, placeholders_data,
                   expected_flag, anti_flag=None, show_tables=None, show_query=True, show_errors=True,
                   allow_js=False, difficulty=1, order=None, category=None):
    """Create an exercise with the given parameters."""
    if show_tables is None:
        show_tables = []

    # Set the placeholders initially as empty list
    placeholders_json = []

    # Create the exercise
    exercise = Exercise.objects.create(
        title=title,
        description=description,
        category=category,
        setup_code=setup_code,
        base_query=base_query,
        expected_flag=expected_flag,
        anti_flag=anti_flag,
        show_tables=show_tables,
        show_query=show_query,
        show_errors=show_errors,
        allow_js=allow_js,
        difficulty=difficulty,
        order=order or 0,
        placeholders=placeholders_json  # Start with empty placeholders
    )

    # Create placeholders
    for ph_data in placeholders_data:
        # Default sanitization function if not provided
        default_sanitize_js = """// This function sanitizes the input value
// Parameter: value - the raw input from the user
// Returns: the sanitized value
function sanitize(value) {
  // By default, return the value unchanged
  return value;
}"""

        # For injection challenges, use a vulnerable sanitizer
        if ph_data.get('vulnerable', False) or title.lower().find('injection') > -1:
            default_sanitize_js = """// This function sanitizes the input value
// Parameter: value - the raw input from the user
// Returns: the sanitized value
function sanitize(value) {
  // This is intentionally vulnerable to SQL injection for learning purposes
  return value;
}"""

        placeholder = Placeholder.objects.create(
            exercise=exercise,
            name=ph_data['name'],
            type=ph_data.get('type', 'str'),
            regex_pattern=ph_data.get('regex_pattern', ''),
            description=ph_data.get('description', ''),
            sanitize_js=ph_data.get('sanitize_js', default_sanitize_js)
        )
        # Add to JSON format for the exercise placeholders field
        placeholders_json.append(placeholder.to_dict())

    # Update the exercise with the placeholders
    exercise.placeholders = placeholders_json
    exercise.save()

    print(f"Created exercise: {title} (ID: {exercise.id})")
    return exercise


def create_sql_basics_exercises(order_counter, categories):
    """Create SQL Basics exercises"""
    exercises = []

    sql_basics_category = categories['SQL Basics']


    # =====================================
    # Exercise 2: UNION Operator
    # =====================================
    setup_code = """
-- Create tables
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    signup_date TEXT
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT,
    position TEXT,
    department TEXT,
    hire_date TEXT
);

-- Insert data into customers
INSERT INTO customers VALUES (1, 'John Doe', 'john@example.com', '2022-01-15');
INSERT INTO customers VALUES (2, 'Jane Smith', 'jane@example.com', '2022-02-20');
INSERT INTO customers VALUES (3, 'Bob Johnson', 'bob@example.com', '2022-03-10');
INSERT INTO customers VALUES (4, 'Alice Brown', 'alice@example.com', '2022-04-05');

-- Insert data into employees
INSERT INTO employees VALUES (1, 'Michael Scott', 'Regional Manager', 'Management', '2015-05-12');
INSERT INTO employees VALUES (2, 'Jim Halpert', 'Sales Representative', 'Sales', '2016-03-22');
INSERT INTO employees VALUES (3, 'Pam Beesly', 'Receptionist', 'Administration', '2016-04-10');
INSERT INTO employees VALUES (4, 'Dwight Schrute', 'Assistant to the Regional Manager', 'Sales', '2016-02-15');
"""

    description = """
# SQL UNION Operator: Combining Result Sets

The UNION operator is a powerful SQL feature that allows you to combine the results of two or more SELECT statements into a single result set. This is particularly important to understand for SQL injection techniques.

## Basic UNION Syntax

```sql
SELECT column1, column2 FROM table1
UNION
SELECT column1, column2 FROM table2;
```

## Key Rules for UNION:

1. The number of columns must be the same in all SELECT statements
2. The data types of corresponding columns must be compatible
3. By default, UNION removes duplicate rows (use UNION ALL to keep duplicates)
4. The column names in the result will be taken from the first SELECT statement

## Example:

```sql
-- This combines customer and employee names in one result
SELECT name FROM customers
UNION
SELECT name FROM employees;
```

## Exercise:

Your task is to use the UNION operator to retrieve information from multiple tables:

1. The base query retrieves all customers.
2. You need to modify it using UNION to also retrieve information from all employees.
"""

    placeholders = [
        {
            'name': 'union_query',
            'type': 'str',
            'description': 'The UNION query to combine with the base query'
        }
    ]

    exercises.append(create_exercise(
        title="SQL UNION: Combining Multiple Queries",
        description=description,
        setup_code=setup_code,
        base_query="SELECT id, name, email, signup_date FROM customers :union_query",
        placeholders_data=placeholders,
        expected_flag="Dwight Schrute",
        show_tables=['customers', 'employees'],
        difficulty=3,
        order=order_counter,
        category=sql_basics_category
    ))
    order_counter += 1

    # =====================================
    # Exercise 3: String Functions
    # =====================================
    setup_code = """
-- Create a table with secret data
CREATE TABLE secret_data (
    id INTEGER PRIMARY KEY,
    data_name TEXT,
    secret_value TEXT
);

-- Insert some encrypted data
INSERT INTO secret_data VALUES (1, 'User Password', '53cr3t_p455w0rd');
INSERT INTO secret_data VALUES (2, 'Credit Card', '1234-5678-9012-3456');
INSERT INTO secret_data VALUES (3, 'Special Key', 'xyzFLAG{sql_string_functions}asdfiehbv');
INSERT INTO secret_data VALUES (4, 'Token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9');
INSERT INTO secret_data VALUES (5, 'Access Code', 'ACCESS_CODE_987654');
"""

    description = """
# SQL String Functions: Manipulating Text Data

SQL provides a variety of string manipulation functions that let you extract, modify, and work with text data. These functions are crucial for both legitimate data processing and for understanding certain SQL injection techniques.

## Common String Functions:

### SUBSTR/SUBSTRING (Extract parts of strings)
```sql
-- Syntax: SUBSTR(string, start_position, length)
SELECT SUBSTR('Hello World', 7, 5);  -- Returns 'World'
```

### LENGTH (Get string length)
```sql
SELECT LENGTH('Hello');  -- Returns 5
```

### UPPER/LOWER (Change case)
```sql
SELECT UPPER('hello');  -- Returns 'HELLO'
SELECT LOWER('WORLD');  -- Returns 'world'
```

### REPLACE (Replace occurrences of a string)
```sql
SELECT REPLACE('Hello World', 'World', 'SQL');  -- Returns 'Hello SQL'
```

### CONCAT (Combine strings)
```sql
-- In SQLite, use the || operator to concatenate
SELECT 'Hello' || ' ' || 'World';  -- Returns 'Hello World'
```

## Exercise:

In this exercise, you'll use SQL string functions to extract a hidden flag:

1. The flag is within the 'Special Key' record in the secret_data table
2. It's embedded in the middle of the secret_value
3. Use SUBSTR/SUBSTRING to extract just the part containing "FLAG..."
4. You'll need to determine the correct starting position and length

**Hint:** First query the table to find the 'Special Key' record, then analyze its value to determine where the flag begins and how long it is.
"""

    placeholders = [
        {
            'name': 'string_function',
            'type': 'str',
            'description': 'The string function to extract the flag'
        }
    ]

    exercises.append(create_exercise(
        title="SQL String Functions: Extracting Data",
        description=description,
        setup_code=setup_code,
        base_query="SELECT id, data_name, :string_function FROM secret_data WHERE data_name = 'Special Key'",
        placeholders_data=placeholders,
        expected_flag="FLAG{sql_string_functions}",
        show_tables=['secret_data'],
        difficulty=3,
        order=order_counter,
        category=sql_basics_category
    ))
    order_counter += 1

    # =====================================
    # Exercise 4: CASE Statements
    # =====================================
    setup_code = """
-- Create a table of users with different access levels
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    email TEXT,
    access_level INTEGER,
    department TEXT
);

-- Insert sample user data
INSERT INTO users VALUES (1, 'admin', 'admin@example.com', 10, 'IT');
INSERT INTO users VALUES (2, 'john', 'john@example.com', 5, 'Sales');
INSERT INTO users VALUES (3, 'jane', 'jane@example.com', 7, 'Engineering');
INSERT INTO users VALUES (4, 'bob', 'bob@example.com', 3, 'Marketing');
INSERT INTO users VALUES (5, 'alice', 'alice@example.com', 8, 'Engineering');
INSERT INTO users VALUES (6, 'securityflag', 'flag@example.com', 9, 'Security');

-- Create a hidden permissions table
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY,
    level INTEGER,
    description TEXT,
    code TEXT
);

-- Insert permissions data with flag
INSERT INTO permissions VALUES (1, 1, 'Basic User', 'READ_ONLY');
INSERT INTO permissions VALUES (2, 5, 'Manager', 'DEPT_MANAGE');
INSERT INTO permissions VALUES (3, 7, 'Director', 'ALL_DEPT_ACCESS');
INSERT INTO permissions VALUES (4, 9, 'Security Admin', 'FLAG{case_statement_master}');
INSERT INTO permissions VALUES (5, 10, 'System Admin', 'SYSTEM_ADMIN');
"""

    description = """
# SQL CASE Statements: Conditional Logic

The CASE statement in SQL allows you to add conditional logic to your queries. It's similar to if/else statements in other programming languages and lets you perform different actions based on different conditions.

## CASE Statement Syntax:

There are two main forms of the CASE statement:

### Simple CASE (comparing a value against multiple possible matches)
```sql
SELECT
    product_name,
    CASE category
        WHEN 'Electronics' THEN 'Tech Department'
        WHEN 'Clothing' THEN 'Fashion Department'
        ELSE 'Other Department'
    END AS department
FROM products;
```

### Searched CASE (evaluating multiple conditions)
```sql
SELECT
    employee_name,
    CASE
        WHEN salary > 100000 THEN 'High'
        WHEN salary > 50000 THEN 'Medium'
        ELSE 'Low'
    END AS salary_category
FROM employees;
```

## Exercise:

In this exercise, you'll use a CASE statement to map user access levels to their corresponding permission codes:

1. You have a users table with numeric access_level values
2. The permissions table contains the corresponding textual permission codes
3. Use a CASE statement to display each user's permission code based on their access_level
4. One of the permission codes contains the FLAG

**Hint:** You'll need to use a searched CASE statement that checks each access_level and returns the corresponding permission code.
"""

    placeholders = [
        {
            'name': 'case_statement',
            'type': 'str',
            'description': 'CASE statement to map access levels to permission codes'
        }
    ]

    exercises.append(create_exercise(
        title="SQL CASE Statements: Conditional Results",
        description=description,
        setup_code=setup_code,
        base_query="SELECT username, email, access_level, :case_statement AS permission FROM users",
        placeholders_data=placeholders,
        expected_flag="FLAG{case_statement_master}",
        show_tables=['users', 'permissions'],
        difficulty=4,
        order=order_counter,
        category=sql_basics_category
    ))
    order_counter += 1

    # =====================================
    # Exercise 5: Subqueries
    # =====================================
    setup_code = """
-- Create tables for a bookstore database
CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author_id INTEGER,
    genre TEXT,
    price REAL,
    published_year INTEGER
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    book_id INTEGER,
    quantity INTEGER,
    order_date TEXT
);

CREATE TABLE special_codes (
    id INTEGER PRIMARY KEY,
    code_name TEXT,
    code_value TEXT
);

-- Insert book data
INSERT INTO books VALUES (1, 'The SQL Guide', 1, 'Technical', 29.99, 2020);
INSERT INTO books VALUES (2, 'Database Design Patterns', 1, 'Technical', 39.99, 2018);
INSERT INTO books VALUES (3, 'Mystery at SQL Lake', 2, 'Mystery', 19.99, 2021);
INSERT INTO books VALUES (4, 'The Lost Query', 2, 'Mystery', 24.99, 2019);
INSERT INTO books VALUES (5, 'Data Adventures', 3, 'Adventure', 22.99, 2022);
INSERT INTO books VALUES (6, 'The Hidden Schema', 4, 'Mystery', 18.99, 2022);

-- Insert author data
INSERT INTO authors VALUES (1, 'Jane Smith', 'USA');
INSERT INTO authors VALUES (2, 'John Davis', 'UK');
INSERT INTO authors VALUES (3, 'Maria Garcia', 'Spain');
INSERT INTO authors VALUES (4, 'Liu Wei', 'China');

-- Insert order data
INSERT INTO orders VALUES (1, 1, 5, '2022-01-15');
INSERT INTO orders VALUES (2, 2, 3, '2022-01-20');
INSERT INTO orders VALUES (3, 3, 10, '2022-02-05');
INSERT INTO orders VALUES (4, 1, 2, '2022-02-10');
INSERT INTO orders VALUES (5, 5, 7, '2022-03-01');

-- Insert special code data with flag
INSERT INTO special_codes VALUES (1, 'DISCOUNT_CODE', 'SPRING2023');
INSERT INTO special_codes VALUES (2, 'SECRET_FLAG', 'FLAG{subquery_wizard}');
INSERT INTO special_codes VALUES (3, 'PROMO_CODE', 'BOOKWORM10');
"""

    description = """
# SQL Subqueries: Queries Within Queries

Subqueries are SQL queries nested inside another query. They allow you to use the results of one query as part of another query. This is an important concept in both regular SQL usage and in understanding how certain SQL injection techniques work.

## Subquery Locations:

Subqueries can appear in different parts of a SQL statement:

### 1. In a WHERE clause
```sql
SELECT title FROM books
WHERE author_id IN (SELECT id FROM authors WHERE country = 'USA');
```

### 2. In a FROM clause
```sql
SELECT avg_price
FROM (SELECT AVG(price) as avg_price FROM books) AS price_summary;
```

### 3. In a SELECT clause
```sql
SELECT
    name,
    (SELECT COUNT(*) FROM books WHERE books.author_id = authors.id) AS book_count
FROM authors;
```

## Exercise:

In this exercise, you'll practice using subqueries to retrieve information across multiple tables:

1. The bookstore database contains information about books, authors, and orders
2. There's also a special_codes table that contains a SECRET_FLAG
3. Use a subquery to find the most popular book (most ordered) and include the flag from special_codes

**Hint:** You'll need to use a subquery in the SELECT clause to retrieve the special code while your main query focuses on finding the most ordered book.
"""

    placeholders = [
        {
            'name': 'subquery',
            'type': 'str',
            'description': 'Subquery to retrieve the flag'
        }
    ]

    exercises.append(create_exercise(
        title="SQL Subqueries: Advanced Data Retrieval",
        description=description,
        setup_code=setup_code,
        base_query="""
SELECT
    books.id,
    books.title,
    authors.name AS author,
    SUM(orders.quantity) AS total_ordered,
    :subquery AS special_code
FROM
    books
JOIN
    authors ON books.author_id = authors.id
JOIN
    orders ON orders.book_id = books.id
GROUP BY
    books.id
ORDER BY
    total_ordered DESC
LIMIT 1
""",
        placeholders_data=placeholders,
        expected_flag="FLAG{subquery_wizard}",
        show_tables=['books', 'authors', 'orders', 'special_codes'],
        difficulty=5,
        order=order_counter,
        category=sql_basics_category
    ))
    order_counter += 1
    #
    # =====================================
    # Exercise 1: SQL Comments
    # =====================================
    setup_code = """
-- Creating a table of movies
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    director TEXT,
    release_year INTEGER,
    genre TEXT,
    rating REAL,
    notes TEXT
);

-- Inserting sample data
INSERT INTO movies VALUES (1, 'The Matrix', 'Wachowski Sisters', 1999, 'Sci-Fi', 8.7, 'Revolutionary visual effects');
INSERT INTO movies VALUES (2, 'Inception', 'Christopher Nolan', 2010, 'Sci-Fi', 8.8, 'Dreams within dreams');
INSERT INTO movies VALUES (3, 'The Godfather', 'Francis Ford Coppola', 1972, 'Crime', 9.2, 'Classic mafia movie');
INSERT INTO movies VALUES (4, 'Pulp Fiction', 'Quentin Tarantino', 1994, 'Crime', 8.9, 'Non-linear storytelling');
INSERT INTO movies VALUES (5, 'The Dark Knight', 'Christopher Nolan', 2008, 'Action', 9.0, 'Features Heath Ledger as Joker');
INSERT INTO movies VALUES (6, 'The Secret Movie', 'Unknown Director', 2023, 'Mystery', 10.0, 'FLAG{sql_comments_mastered}');
"""

    description = """
# SQL Comments: Understanding and Using Comments

In SQL, comments are non-executable text that you can add to make your queries more readable or to temporarily disable parts of a query. This is an important concept to understand not only for code documentation but also for certain SQL injection techniques.

## Types of SQL Comments

There are two main ways to create comments in SQL:

### 1. Single-line comments
Single-line comments start with `--` and continue until the end of the line. Everything after the `--` is ignored by the SQL engine.

```sql
SELECT * FROM users; -- This is a comment, the SQL engine ignores this part
```

### 2. Multi-line comments
Multi-line comments start with `/*` and end with `*/`. Everything between these markers is ignored.

```sql
/* This is a multi-line comment
   that can span multiple lines
   and is ignored by the SQL engine */
SELECT * FROM users;
```

## Exercise

In this exercise, you'll practice using SQL comments to your advantage. There's a "secret movie" in the database that you need to find:

1. First, query the table to see all movies
2. Then, modify your query using comments to find only the secret movie with a perfect rating of 10.0
3. Use the `--` comment style to comment out part of the WHERE clause

**Hint:** The base query includes a condition to find movies with ratings less than 9, but you want to find a movie with a rating of 10. How could you use comments to change the query behavior?
"""

    placeholders = [
        {
            'name': 'condition',
            'type': 'str',
            'description': 'Condition to filter movies (use comments strategically)'
        }
    ]

    exercises.append(create_exercise(
        title="SQL Comments and Query Modification",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM movies WHERE :condition AND rating < 9",
        placeholders_data=placeholders,
        expected_flag="FLAG{sql_comments_mastered}",
        show_tables=['movies'],
        difficulty=2,
        order=order_counter,
        category=sql_basics_category
    ))
    order_counter += 1

    return order_counter

def create_basic_sample_exercises(categories):
    """Create the basic sample exercises from sample_exercise.py"""
    order_counter = 1

    # Exercise 1: Basic SQL Injection
    setup_code = """
-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    is_admin INTEGER DEFAULT 0
);

-- Insert sample user data
INSERT INTO users VALUES (1, 'admin', 'admin123', 'admin@example.com', 1);
INSERT INTO users VALUES (2, 'alice', 'alice123', 'alice@example.com', 0);
INSERT INTO users VALUES (3, 'bob', 'bob123', 'bob@example.com', 0);
INSERT INTO users VALUES (4, 'carol', 'carol123', 'carol@example.com', 0);

-- Create secrets table with flag
CREATE TABLE secrets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    secret_name TEXT,
    secret_value TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert secret data including the flag
INSERT INTO secrets VALUES (1, 1, 'admin_key', 'supersecretadminkey');
INSERT INTO secrets VALUES (2, 1, 'flag', 'FLAG{sql_injection_basic_string}');
INSERT INTO secrets VALUES (3, 2, 'personal_note', 'My password reminder: alice123');
INSERT INTO secrets VALUES (4, 3, 'api_key', 'bob_api_12345');
"""

    description = """
# Basic SQL Injection - String Parameters

Welcome to your first SQL injection challenge!

In this exercise, you need to exploit a basic string-based SQL injection vulnerability to find the secret 'flag' value in the 'secrets' table.

The application uses the input directly in the query without proper sanitization. Try to modify the SQL query to display the contents of the 'secrets' table.
"""

    placeholders = [
        {
            'name': 'username',
            'type': 'str',
            'description': 'Username to look up'
        }
    ]

    create_exercise(
        title="Basic SQL Injection - String Parameters",
        description=description,
        setup_code=setup_code,
        base_query="SELECT id, username, email FROM users WHERE username = ':username'",
        placeholders_data=placeholders,
        expected_flag="FLAG{sql_injection_basic_string}",
        show_tables=['users', 'secrets'],
        difficulty=1,
        order=order_counter,
        category=categories['SQL Injection Fundamentals']
    )
    order_counter += 1

    # Exercise 2: Error-Based SQL Injection
    setup_code = """
-- Create admin_secrets table with flag
CREATE TABLE admin_secrets (
    id INTEGER PRIMARY KEY,
    key_name TEXT,
    key_value TEXT
);

-- Insert secret data including the flag
INSERT INTO admin_secrets VALUES (1, 'admin_api_key', 'secret_admin_api_key_123');
INSERT INTO admin_secrets VALUES (2, 'flag', 'FLAG{error_based_extraction}');
INSERT INTO admin_secrets VALUES (3, 'backup_code', 'admin_backup_987654321');

-- Create products table for the main query
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL
);

-- Insert product data
INSERT INTO products VALUES (1, 'Laptop', 'Electronics', 999.99);
INSERT INTO products VALUES (2, 'Smartphone', 'Electronics', 699.99);
INSERT INTO products VALUES (3, 'Headphones', 'Electronics', 149.99);
INSERT INTO products VALUES (4, 'Desk Chair', 'Furniture', 249.99);
"""

    description = """
# Error-Based SQL Injection

This challenge introduces error-based SQL injection!

The application will show you error messages that can be useful for extracting information. Your task is to extract the flag from the 'admin_secrets' table using error-based techniques.

Hint: SQLite's error messages can sometimes include parts of your query or data.
"""

    placeholders = [
        {
            'name': 'category',
            'type': 'str',
            'description': 'Product category to filter by'
        }
    ]

    create_exercise(
        title="Error-Based SQL Injection",
        description=description,
        setup_code=setup_code,
        base_query="SELECT id, name, price FROM products WHERE category = ':category'",
        placeholders_data=placeholders,
        expected_flag="FLAG{error_based_extraction}",
        show_tables=['products'],
        difficulty=3,
        order=order_counter,
        category=categories['SQL Injection Fundamentals']
    )
    order_counter += 1

    # Exercise 3: Blind SQL Injection
    setup_code = """
-- Create hidden_data table with flag
CREATE TABLE hidden_data (
    id INTEGER PRIMARY KEY,
    data_key TEXT,
    data_value TEXT
);

-- Insert secret data including the flag
INSERT INTO hidden_data VALUES (1, 'system_key', 'system_123456');
INSERT INTO hidden_data VALUES (2, 'flag', 'FLAG{blind_injection_master}');
INSERT INTO hidden_data VALUES (3, 'backup_key', 'backup_987654');

-- Create users table for the main query
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    is_active INTEGER
);

-- Insert user data
INSERT INTO users VALUES (1, 'admin', 1);
INSERT INTO users VALUES (2, 'user1', 1);
INSERT INTO users VALUES (3, 'user2', 1);
INSERT INTO users VALUES (4, 'user3', 0);
"""

    description = """
# Blind SQL Injection

Time for a blind SQL injection challenge!

In this exercise, you won't see the results of your query directly. The application only tells you whether any results were found or not.

Your goal is to extract the flag from the 'hidden_data' table using blind SQL injection techniques. Try using boolean conditions to extract the flag character by character.
"""

    placeholders = [
        {
            'name': 'username',
            'type': 'str',
            'description': 'Username to look up'
        }
    ]

    create_exercise(
        title="Blind SQL Injection",
        description=description,
        setup_code=setup_code,
        base_query="SELECT EXISTS(SELECT 1 FROM users WHERE username = ':username' AND is_active = 1)",
        placeholders_data=placeholders,
        expected_flag="FLAG{blind_injection_master}",
        show_tables=['users'],
        show_query=False,
        show_errors=False,
        allow_js=True,
        difficulty=7,
        order=order_counter,
        category=categories['Advanced SQL Injection']
    )
    order_counter += 1

    return order_counter


def create_basic_sql_learning_exercises(order_start, categories):
    """Create the SQL learning exercises from basic_sql_exercises.py"""
    order_counter = order_start

    # =====================================
    # Exercise 1: Introduction to SQL SELECTs
    # =====================================
    setup_code = """
-- Creating the first sample table: fruits
CREATE TABLE fruits (
    id INTEGER PRIMARY KEY,
    name TEXT,
    color TEXT,
    price REAL
);

-- Inserting sample data
INSERT INTO fruits VALUES (1, 'Apple', 'Red', 1.20);
INSERT INTO fruits VALUES (2, 'Banana', 'Yellow', 0.80);
INSERT INTO fruits VALUES (3, 'Orange', 'Orange', 1.50);
INSERT INTO fruits VALUES (4, 'Grapes', 'Purple', 2.50);
INSERT INTO fruits VALUES (5, 'Blueberry', 'Blue', 3.00);
"""

    description = """
# Introduction to SQL: Basic SELECT Statements

In this exercise, you'll learn the most basic SQL command: the `SELECT` statement.

SQL (Structured Query Language) is used to interact with databases. The most common operation is retrieving data using the `SELECT` statement.

## Basic Syntax:
```sql
SELECT column1, column2, ... FROM table_name;
```

## Example:
```sql
SELECT name, price FROM fruits;
```
This retrieves the name and price of all fruits.

## Filtering

If you want to filter the results based on a condition, you can use the `WHERE` clause.
This is added after the `FROM` clause and specifies, which entries should be included in the result set.

## Example:
```sql
SELECT name, price FROM fruits WHERE color = 'Red';
```
This retrieves the name and price of all fruits that are red.

## Exercise:
Add a where clause to select all fruits that cost less than 2.00. See the SQL Quick Reference for tips on what to use!
"""

    placeholders = [
        {
            'name': 'where',
            'type': 'str',
            'description': 'The WHERE clause to filter by'
        }
    ]

    create_exercise(
        title="Introduction to SQL: SELECT Statements",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM fruits :where",
        placeholders_data=placeholders,
        expected_flag="Red",
        anti_flag="Blue",
        show_tables=['fruits'],
        difficulty=1,
        order=order_counter,
        category=categories['SQL Basics']
    )
    order_counter += 1

    # =====================================
    # Exercise 2: SQL Comparison Operators
    # =====================================
    setup_code = """
-- Creating a table of users
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    age INTEGER,
    is_admin BOOLEAN
);

-- Inserting sample data
INSERT INTO users VALUES (1, 'john_doe', 'John', 'Doe', 28, 0);
INSERT INTO users VALUES (2, 'jane_smith', 'Jane', 'Smith', 45, 0);
INSERT INTO users VALUES (3, 'admin_user', 'Admin', 'User', 42, 1);
INSERT INTO users VALUES (4, 'bob_jones', 'Bob', 'Jones', 19, 0);
INSERT INTO users VALUES (5, 'alice_wonder', 'Alice', 'Wonder', 27, 0);
INSERT INTO users VALUES (6, 'super_jane', 'Super', 'Admin', 30, 1);
"""

    description = """
# SQL Comparison Operators

You can combine conditions using:
- `AND` - Both conditions must be true
- `OR` - At least one condition must be true
- `NOT` - Negates a condition

## Exercise:
Write a query to find all admin users who are older than 40.
"""

    placeholders = [
        {
            'name': 'where',
            'type': 'str',
            'description': 'The WHERE clause'
        },
    ]

    create_exercise(
        title="SQL Comparison and Logical Operators",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM users :where",
        placeholders_data=placeholders,
        expected_flag="admin_user",
        anti_flag="jane",
        show_tables=['users'],
        difficulty=1,
        order=order_counter,
        category=categories['SQL Basics']
    )
    order_counter += 1

    # =====================================
    # Exercise 3: LIKE Operator
    # =====================================
    setup_code = """
-- Creating a products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    description TEXT,
    price REAL
);

-- Inserting sample data
INSERT INTO products VALUES (1, 'Laptop Pro', 'Electronics', 'High-performance laptop for professionals', 1299.99);
INSERT INTO products VALUES (2, 'Smartphone X', 'Electronics', 'Latest smartphone with advanced features', 799.99);
INSERT INTO products VALUES (3, 'Smart Coffee Maker', 'Kitchen', 'Automatic coffee machine with timer', 89.99);
INSERT INTO products VALUES (4, 'Running Shoes', 'Sports', 'Lightweight shoes for marathon runners', 129.99);
INSERT INTO products VALUES (5, 'Smart Watch', 'Electronics', 'Watch with health monitoring features', 249.99);
INSERT INTO products VALUES (6, 'Bluetooth Coffee Speaker', 'Electronics', 'Portable speaker with great sound', 79.99);
INSERT INTO products VALUES (7, 'Yoga Mat', 'Sports', 'Non-slip exercise mat for yoga practice', 29.99);
"""

    description = """
# SQL LIKE Operator for Pattern Matching

The `LIKE` operator is used for pattern matching in SQL. This is especially useful when you don't know the exact value you're looking for.

## Wildcards:
- `%` - Represents zero, one, or multiple characters
- `_` - Represents a single character

## Examples:
```sql
-- Find products that start with "Smart"
SELECT * FROM products WHERE product_name LIKE 'Smart%';

-- Find products that end with "Shoes"
SELECT * FROM products WHERE product_name LIKE '%Shoes';
```

## Exercise:
Find all products in the "Electronics" category that have "Smart" somewhere in their name.

To complete this exercise:
1. Use the LIKE operator with the % wildcard
2. Combine conditions using AND to also filter by category
"""

    placeholders = [
        {
            'name': 'category',
            'type': 'str',
            'description': 'Category to filter by'
        },
        {
            'name': 'name_pattern',
            'type': 'str',
            'description': 'Pattern to search in product names (use % as wildcard)'
        }
    ]

    create_exercise(
        title="Pattern Matching with LIKE Operator",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM products WHERE category = :category AND product_name LIKE :name_pattern",
        placeholders_data=placeholders,
        expected_flag="Smart Watch",
        anti_flag="Coffee",
        show_tables=['products'],
        difficulty=2,
        order=order_counter,
        category=categories['SQL Basics']
    )
    order_counter += 1

    # =====================================
    # Exercise 4: SQL Injection Basics
    # =====================================
    setup_code = """
-- Creating a login table
CREATE TABLE login (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    role TEXT
);

-- Inserting sample data
INSERT INTO login VALUES (1, 'regular_user', 'password123', 'user');
INSERT INTO login VALUES (2, 'john_smith', 'john123', 'user');
INSERT INTO login VALUES (3, 'alice_admin', 'secure_pwd!', 'admin');
INSERT INTO login VALUES (4, 'bob_user', 'bob456', 'user');
INSERT INTO login VALUES (5, 'super_admin', 'admin_pwd!', 'super_admin');

-- Creating a secret_data table (only admins should see this)
CREATE TABLE secret_data (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value TEXT
);

INSERT INTO secret_data VALUES (1, 'API_KEY', 'sk_live_51HV0rAGPiGQBDH58g9Gkw1');
INSERT INTO secret_data VALUES (2, 'ADMIN_PASSWORD', 'FLAG{sql_injection_basics_complete}');
INSERT INTO secret_data VALUES (3, 'DATABASE_CREDENTIALS', 'dbuser:dbpassword');
"""

    description = """
# Introduction to SQL Injection

In this exercise, you'll learn about SQL injection, a common security vulnerability that occurs when user input is not properly validated and is directly included in SQL queries.

## What is SQL Injection?
SQL injection happens when an attacker can insert or "inject" malicious SQL code into a query that an application executes. This can bypass security measures and potentially:
- Access unauthorized data
- Modify database data
- Delete database contents
- Execute administrative operations

## Example of Vulnerable Code:
In many applications, a login query might look like this (pseudocode):
```
query = "SELECT * FROM login WHERE username = '" + user_input + "' AND password = '" + password_input + "'";
```

If user input is not properly sanitized, an attacker can input something like:
```
username: admin' --
password: anything
```

This transforms the query to:
```sql
SELECT * FROM login WHERE username = 'admin' -- ' AND password = 'anything'
```

The `--` is a SQL comment that makes the database ignore everything after it, effectively removing the password check!

## Exercise:
Find a way to log in as 'super_admin' without knowing the password.

1. The application uses the query: `SELECT * FROM login WHERE username = 'input_username' AND password = 'input_password'`
2. If the query returns any rows, the login is successful
3. Use SQL injection techniques to bypass the password check

*Hint: Try using SQL comments to modify the query structure*
"""

    placeholders = [
        {
            'name': 'username',
            'type': 'str',
            'description': 'Username for login'
        },
        {
            'name': 'password',
            'type': 'str',
            'description': 'Password for login'
        }
    ]

    create_exercise(
        title="Basic SQL Injection: Authentication Bypass",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM login WHERE username = ':username' AND password = ':password'",
        placeholders_data=placeholders,
        expected_flag="FLAG{sql_injection_basics_complete}",
        show_tables=['login'],
        difficulty=3,
        order=order_counter,
        category=categories['SQL Injection Fundamentals']
    )
    order_counter += 1

    # Skip some exercises for brevity...
    # The rest of the exercises would follow the same pattern

    return order_counter


def create_anti_flag_exercises(order_start, categories):
    """Create exercises that use the anti-flag feature"""
    order_counter = order_start

    # =====================================
    # Exercise 1: Filtering to exclude specific data
    # =====================================
    setup_code = """
-- Creating a products table with sensitive data
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    is_public BOOLEAN,
    price REAL,
    description TEXT
);

-- Inserting sample data
INSERT INTO products VALUES (1, 'Laptop Pro', 'Electronics', 1, 1299.99, 'High-performance laptop for professionals');
INSERT INTO products VALUES (2, 'Smartphone X', 'Electronics', 1, 799.99, 'Latest smartphone with advanced features');
INSERT INTO products VALUES (3, 'Coffee Maker', 'Kitchen', 1, 89.99, 'Automatic coffee machine with timer');
INSERT INTO products VALUES (4, 'Project X Prototype', 'R&D', 0, 9999.99, 'FLAG{filtered_query_success}');
INSERT INTO products VALUES (5, 'Secret Gadget', 'R&D', 0, 5999.99, 'Confidential product under development');
INSERT INTO products VALUES (6, 'Smart Watch', 'Electronics', 1, 249.99, 'Watch with health monitoring features');
"""

    description = """
# SQL Filtering: Excluding Private Data

In this exercise, you'll practice filtering queries to exclude sensitive information. This is an important security concept - ensuring that queries only return the appropriate data.

## The Scenario

You are working on an e-commerce site's product database. The database contains both public products and private/confidential products that are still in development.

## The Challenge

Write a SQL query that:
1. Retrieves all product information
2. Only includes products marked as public (`is_public = 1`)
3. Excludes any confidential R&D products

If your query correctly filters out the private products, you'll see the success flag in the results. However, if any confidential data appears in the results, the query will fail.

**Hint:** Use the WHERE clause to filter records based on multiple conditions.
"""

    placeholders = [
        {
            'name': 'conditions',
            'type': 'str',
            'description': 'Conditions to filter the products'
        }
    ]

    create_exercise(
        title="SQL Filtering: Exclude Sensitive Data",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM products WHERE :conditions",
        placeholders_data=placeholders,
        expected_flag="FLAG{filtered_query_success}",
        anti_flag="Confidential product",  # This must NOT appear in the results
        show_tables=['products'],
        difficulty=3,
        order=order_counter,
        category=categories['Security Best Practices']
    )
    order_counter += 1

    # =====================================
    # Exercise 2: Finding a flag without revealing sensitive data
    # =====================================
    setup_code = """
-- Creating users table with sensitive information
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    password TEXT,
    email TEXT,
    is_admin BOOLEAN,
    last_login TEXT
);

-- Creating a token table with access tokens (including the flag)
CREATE TABLE tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    token TEXT,
    description TEXT,
    expires_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert data
INSERT INTO users VALUES (1, 'admin', 'superSecureAdminPass123!', 'admin@example.com', 1, '2023-03-15 14:22:31');
INSERT INTO users VALUES (2, 'john', 'password123', 'john@example.com', 0, '2023-03-14 09:15:22');
INSERT INTO users VALUES (3, 'jane', 'jane456', 'jane@example.com', 0, '2023-03-15 11:43:09');
INSERT INTO users VALUES (4, 'bob', 'bobpass789', 'bob@example.com', 0, '2023-03-12 17:38:42');
INSERT INTO users VALUES (5, 'alice', 'aliceSecure234', 'alice@example.com', 0, '2023-03-15 08:27:15');

INSERT INTO tokens VALUES (1, 1, 'FLAG{join_without_password_success}', 'Admin API access token', '2024-03-15 00:00:00');
INSERT INTO tokens VALUES (2, 2, 'tkn_5f2d8b3e7a1c9', 'User API token', '2023-06-15 00:00:00');
INSERT INTO tokens VALUES (3, 3, 'tkn_3a7b9c5d1e8f2', 'User API token', '2023-06-15 00:00:00');
INSERT INTO tokens VALUES (4, 4, 'tkn_7c1f3d8a2b5e9', 'User API token', '2023-06-15 00:00:00');
INSERT INTO tokens VALUES (5, 5, 'tkn_2b9e7d4f1a3c8', 'User API token', '2023-06-15 00:00:00');
"""

    description = """
# SQL JOIN with Column Selection

In this exercise, you'll practice using SQL JOIN operations while protecting sensitive information.

## The Scenario

You're working on a system that needs to join user information with their API tokens. However, user passwords are stored in the database and must never be exposed in query results.

## The Challenge

Write a SQL query that:
1. Retrieves the admin's API token (user_id = 1)
2. Joins the users and tokens tables
3. Does NOT reveal any user passwords in the results

This exercise demonstrates a common security principle: even when you need to join tables with sensitive data, you should be careful to only select the specific columns you need.

**Hint:** Instead of using `SELECT *`, specify the exact columns you want to retrieve from each table.
"""

    placeholders = [
        {
            'name': 'columns',
            'type': 'str',
            'description': 'The columns to select'
        },
        {
            'name': 'join',
            'type': 'str',
            'description': 'The JOIN clause to connect the tables'
        }
    ]

    create_exercise(
        title="SQL JOIN: Access Without Exposing Passwords",
        description=description,
        setup_code=setup_code,
        base_query="SELECT :columns FROM users :join WHERE users.id = 1",
        placeholders_data=placeholders,
        expected_flag="FLAG{join_without_password_success}",
        anti_flag="superSecureAdminPass123!",  # Password must not appear in results
        show_tables=['users', 'tokens'],
        difficulty=4,
        order=order_counter,
        category=categories['Security Best Practices']
    )
    order_counter += 1

    return order_counter


def create_categories():
    """Create the exercise categories."""
    # Create categories
    categories = [
        {
            'name': 'SQL Basics',
            'description': 'Learn the fundamentals of SQL querying and syntax',
            'order': 1
        },
        {
            'name': 'SQL Injection Fundamentals',
            'description': 'Basic SQL injection techniques and concepts',
            'order': 2
        },
        {
            'name': 'Advanced SQL Injection',
            'description': 'More complex techniques including blind and time-based injection',
            'order': 3
        },
        {
            'name': 'Security Best Practices',
            'description': 'Exercises focused on how to protect against SQL injection',
            'order': 4
        }
    ]

    created_categories = {}

    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'order': cat_data['order']
            }
        )
        created_categories[cat_data['name']] = category
        if created:
            print(f"Created category: {category.name}")
        else:
            print(f"Using existing category: {category.name}")

    return created_categories


def create_all_exercises():
    """Create all example exercises."""
    # Use Exercise.objects.all().delete() to clear all exercises if needed
    # Exercise.objects.all().delete()

    print("Creating categories...")
    categories = create_categories()

    print("Creating example exercises...")

    # Create sample exercises
    print("\n1. Creating basic sample exercises...")
    order = create_basic_sample_exercises(categories)

    # Create SQL learning exercises
    print("\n2. Creating SQL learning exercises...")
    order = create_basic_sql_learning_exercises(order, categories)

    print("\n2. Creating advanced sample exercises...")
    order = create_sql_basics_exercises(order, categories)

    # Create anti-flag exercises
    print("\n3. Creating anti-flag exercises...")
    order = create_anti_flag_exercises(order, categories)

    print(f"\nCreated {order-1} example exercises!")


def main():
    """Main entry point for creating all example exercises."""
    create_all_exercises()


if __name__ == "__main__":
    main()
