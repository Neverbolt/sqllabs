# WARNING: this is (to )

# SQL Labs

A Django application for learning SQL injection techniques with practical exercises.

## Overview

SQL Labs is a web application designed to help users learn and practice SQL injection techniques in a safe, controlled environment. It uses SQL.js to execute SQL queries entirely in the browser, making it safe and easy to deploy without requiring a real database server.

This application is perfect for educational purposes, workshops, and cybersecurity training sessions.

## Features

- 🔄 Interactive SQL exercises with real-time feedback
- 🔒 Browser-based execution using SQL.js (no server-side execution)
- 🎨 Syntax highlighting with CodeMirror (SQL and JavaScript)
- 📊 Session-based progress tracking
- 📱 Responsive, mobile-friendly design
- ♿ Accessibility features for all users
- 🚦 Exercises with varying difficulty levels
- 🎯 Flag-based challenge completion
- 🛡️ Anti-flag feature to teach proper data filtering
- 💻 JavaScript mode for advanced blind injection challenges
- 📝 Support for different SQL injection techniques:
  - Basic string-based injections
  - UNION-based injections
  - Error-based injections
  - Blind SQL injections
  - Time-based injections

## Screenshots

<details>
<summary>Click to see screenshots</summary>

### Exercise Listing
![Exercise Listing](docs/images/exercise-list.png)

### Challenge Interface
![Challenge Interface](docs/images/challenge-interface.png)

### Success Feedback
![Success Feedback](docs/images/success-feedback.png)

</details>

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sqllabs.git
cd sqllabs
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. (Optional) Create example exercises:
```bash
python create_all_exercises.py
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

8. Access the application at http://localhost:8000/ and the admin interface at http://localhost:8000/admin/

## Creating Exercises

Exercises can be created through the admin interface or programmatically. Each exercise includes:

- **Title and description**: Explain the challenge to users
- **SQL setup code**: Creates tables and inserts data
- **Base query with placeholders**: The query template with `:name` placeholders
- **Placeholder definitions**: List of placeholders with types (string, integer, regex)
- **Expected flag**: What users need to find to complete the challenge
- **Display options**: Control what information is shown (tables, query, errors)
- **Difficulty**: Rate from 1-10 to indicate challenge complexity

### Example Exercise Definition

```python
def create_exercise(
    title="Basic SQL Injection",
    description="Find the flag in the secrets table",
    setup_code="""
        CREATE TABLE users (id INT, username TEXT, password TEXT);
        INSERT INTO users VALUES (1, 'admin', 'admin123');
        CREATE TABLE secrets (id INT, flag TEXT);
        INSERT INTO secrets VALUES (1, 'FLAG{sql_injection_basic}');
    """,
    base_query="SELECT * FROM users WHERE username = ':username'",
    placeholders_data=[
        {
            "name": "username",
            "type": "str",
            "description": "Username to look up"
        }
    ],
    expected_flag="FLAG{sql_injection_basic}",
    anti_flag=None,  # Optional: text that must NOT appear in results
    show_tables=['users'],
    show_query=True,
    show_errors=True,
    allow_js=False,  # Enable for blind injection challenges
    difficulty=1,
    order=1,
    color="#4285F4"
)
```

See `create_all_exercises.py` for many more examples of different types of exercises.

## Running Tests

To run the test suite:
```bash
python manage.py test
```

## License

This project is open-source software licensed under the MIT license.

## Example Exercises

The repository includes a collection of example exercises:

### Types of Exercises

1. **Basic SQL Concepts**:
   - SELECT statements with WHERE clauses
   - Comparison operators and logical conditions
   - Pattern matching with LIKE

2. **SQL Injection Techniques**:
   - Basic authentication bypass
   - UNION-based SQL injection
   - Error-based SQL injection
   - Blind SQL injection (with JavaScript mode)
   - Time-based blind SQL injection

3. **Security Concepts**:
   - Anti-flag challenges that teach filtering out sensitive data
   - JOIN operations without revealing protected information
   - Column selection to hide sensitive fields

### Creating and Managing Exercises

- To create all example exercises:
```bash
python create_all_exercises.py
```

- To reset all exercises and start fresh:
```bash
python reset_exercises.py --recreate
```

## Advanced Features

- **JavaScript Mode**: For blind injection challenges, enables writing JavaScript code to automate detection
- **Anti-Flag**: Ensures queries properly filter out sensitive data before revealing the success flag
- **Parameter Sanitization**: Custom JavaScript functions to process query parameters before execution
- **Admin Interface**: Enhanced interface with syntax highlighting for SQL and JavaScript editing

## Acknowledgments

- [SQL.js](https://github.com/sql-js/sql.js) for browser-based SQL execution
- [CodeMirror](https://codemirror.net/) for SQL and JavaScript syntax highlighting
- [Django](https://www.djangoproject.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for styling
- [Canvas Confetti](https://github.com/catdad/canvas-confetti) for success animations
- [Marked.js](https://marked.js.org/) for Markdown rendering
