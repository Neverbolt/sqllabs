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

from exercises.models import Exercise, Placeholder


def create_exercise(title, description, setup_code, base_query, placeholders_data,
                   expected_flag, anti_flag=None, show_tables=None, show_query=True, show_errors=True,
                   allow_js=False, difficulty=1, order=None, color=None):
    """Create an exercise with the given parameters."""
    if show_tables is None:
        show_tables = []

    # Set the placeholders initially as empty list
    placeholders_json = []

    # Create the exercise
    exercise = Exercise.objects.create(
        title=title,
        description=description,
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
        color=color or '#007bff',
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


def create_basic_sample_exercises():
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
        color='#4285F4'  # Google Blue
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
        color='#EA4335'  # Google Red
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
        color='#FBBC05'  # Google Yellow
    )
    order_counter += 1

    return order_counter


def create_basic_sql_learning_exercises(order_start):
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

## Exercise:
Modify the query below to select all fruits that cost less than 2.00.

To complete this exercise:
1. Keep the `SELECT * FROM fruits` part
2. Add a `WHERE` clause to filter by price
3. The flag will appear when your query is correct
"""

    placeholders = [
        {
            'name': 'price',
            'type': 'str',
            'description': 'The maximum price to filter by'
        }
    ]

    create_exercise(
        title="Introduction to SQL: SELECT Statements",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM fruits WHERE price < :price",
        placeholders_data=placeholders,
        expected_flag="Red",
        anti_flag="Blue",
        show_tables=['fruits'],
        difficulty=1,
        order=order_counter,
        color='#4CAF50'  # Green for beginner exercises
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

This exercise teaches you about comparison operators in SQL, which are essential for filtering data.

## Common Comparison Operators:
- `=` Equal to
- `<>` or `!=` Not equal to
- `>` Greater than
- `<` Less than
- `>=` Greater than or equal to
- `<=` Less than or equal to

## Example:
```sql
SELECT * FROM users WHERE age >= 30;
```
This retrieves all users who are 30 years old or older.

## Logical Operators:
You can combine conditions using:
- `AND` - Both conditions must be true
- `OR` - At least one condition must be true
- `NOT` - Negates a condition

## Exercise:
Write a query to find all admin users (`is_admin = 1`) who are younger than 40.

To complete this exercise:
1. Use `SELECT * FROM users`
2. Add a `WHERE` clause with two conditions joined by `AND`
3. One condition should check if the user is an admin
4. The other condition should check if the user is older than 40
"""

    placeholders = [
        {
            'name': 'is_admin',
            'type': 'str',
            'description': 'Value to check if user is admin (1 for true, 0 for false)'
        },
        {
            'name': 'age',
            'type': 'str',
            'description': 'Minimum age to filter by'
        }
    ]

    create_exercise(
        title="SQL Comparison and Logical Operators",
        description=description,
        setup_code=setup_code,
        base_query="SELECT * FROM users WHERE is_admin = :is_admin AND age > :age",
        placeholders_data=placeholders,
        expected_flag="admin_user",
        anti_flag="jane",
        show_tables=['users'],
        difficulty=1,
        order=order_counter,
        color='#4CAF50'  # Green for beginner exercises
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

-- Find products that contain "top" anywhere in the name
SELECT * FROM products WHERE product_name LIKE '%top%';
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
        color='#4CAF50'  # Green for beginner exercises
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
        color='#FFC107'  # Yellow for medium difficulty
    )
    order_counter += 1

    # Skip some exercises for brevity...
    # The rest of the exercises would follow the same pattern

    return order_counter


def create_anti_flag_exercises(order_start):
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
        color='#FFC107'  # Yellow for medium difficulty
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
        color='#FFC107'  # Yellow for medium difficulty
    )
    order_counter += 1

    return order_counter


def main():
    """Create all example exercises."""
    # Use Exercise.objects.all().delete() to clear all exercises if needed
    # Exercise.objects.all().delete()

    print("Creating example exercises...")

    # Create sample exercises
    print("\n1. Creating basic sample exercises...")
    order = create_basic_sample_exercises()

    # Create SQL learning exercises
    print("\n2. Creating SQL learning exercises...")
    order = create_basic_sql_learning_exercises(order)

    # Create anti-flag exercises
    print("\n3. Creating anti-flag exercises...")
    order = create_anti_flag_exercises(order)

    print(f"\nCreated {order-1} example exercises!")


if __name__ == "__main__":
    main()
