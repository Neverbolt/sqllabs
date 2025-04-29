# Example Exercises for SQL Labs

This directory contains scripts to create example exercises for SQL Labs. These exercises range from basic SQL syntax to advanced SQL injection techniques, and they're designed to provide a comprehensive learning experience.

## Scripts Overview

- **`create_all_exercises.py`**: Creates all example exercises in a single script
- **`reset_exercises.py`**: Deletes all exercises and recreates them (useful for development)

## Exercise Types

The exercises are organized into several categories:

1. **Basic Sample Exercises**:
   - Basic SQL Injection - String Parameters
   - Error-Based SQL Injection
   - Blind SQL Injection

2. **SQL Learning Exercises**:
   - Introduction to SQL: SELECT Statements
   - SQL Comparison and Logical Operators
   - Pattern Matching with LIKE Operator
   - Basic SQL Injection: Authentication Bypass
   - UNION-Based SQL Injection
   - Error-Based SQL Injection
   - Blind SQL Injection
   - Time-Based Blind SQL Injection

3. **Anti-Flag Exercises**:
   - SQL Filtering: Exclude Sensitive Data
   - SQL JOIN: Access Without Exposing Passwords

## Creating Exercises

To create all example exercises, run:

```bash
python example_exercises/create_all_exercises.py
```

## Exercise Difficulty Levels

Exercises are categorized by difficulty level:

- **Level 1-2 (Green)**: Beginner exercises introducing basic SQL concepts
- **Level 3-5 (Yellow)**: Intermediate exercises introducing SQL injection techniques
- **Level 6-8 (Orange)**: Advanced exercises requiring more complex techniques
- **Level 9-10 (Red)**: Expert exercises that require creative problem-solving

## Adding New Exercises

To add new exercises, you can either:

1. Modify `create_all_exercises.py` to add more exercise definitions
2. Create a new script in this directory that uses the `create_exercise()` function

The `create_exercise()` function requires these parameters:

- `title`: Exercise title
- `description`: Markdown-formatted exercise description
- `setup_code`: SQL code to initialize the database
- `base_query`: SQL query template with placeholders
- `placeholders_data`: Information about query placeholders
- `expected_flag`: Flag text that should appear in results when solved
- `anti_flag` (optional): Text that must NOT appear in results
- `show_tables`: List of table names to display
- `difficulty`: Difficulty level (1-10)
- And more optional parameters