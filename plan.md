# SQL Labs Implementation Plan

## Overview
SQL Labs is a Django application designed to teach SQL injection techniques using SQL.js to execute SQL in the browser. The platform provides a series of exercises of increasing difficulty, from basic SQL queries to advanced injection techniques.

## Technology Stack
- Backend: Django
- Frontend SQL Engine: SQL.js
- Code Editor: CodeMirror (readonly for base query display)
- Frontend Framework: Minimal vanilla JS with Bootstrap for styling
- CSS: Custom styling inspired by Google's "Class Overview" slides

## Data Models

### Exercise
- `title`: String - Name of the exercise
- `description`: Text - Description and instructions
- `setup_code`: Text - SQL to initialize database (create tables, insert data)
- `base_query`: Text - Query with placeholders (`:name`)
- `placeholders`: JSONField - List of placeholder definitions:
  ```json
  [
    {
      "name": "name",
      "type": "str|int|regex",
      "regex_pattern": "optional pattern for regex type"
    }
  ]
  ```
- `expected_flag`: String - Flag that should appear in results when solved (case-insensitive check)
- `show_tables`: JSONField - List of table names to display to user
- `show_query`: Boolean - Whether to show the full query to user or just inputs
- `show_errors`: Boolean - Whether to display SQL error messages to user
- `difficulty`: Integer - Difficulty rating
- `order`: Integer - Display order in listing

## User Progress
- Store solved status in Django session
- No database persistence for user progress required
- Track exercises solved in current session

## Views/Pages

1. **Exercise List** - Homepage showing all available exercises with:
   - Exercise title and description
   - Difficulty indicator
   - Solved/unsolved status (for current session)

2. **Exercise Page** - Interface to solve a specific exercise:
   - Exercise description
   - SQL display (readonly CodeMirror) showing query with placeholders
   - Individual input fields for placeholders with type validation
   - Table definitions display (optional, based on show_tables)
   - Run button to execute query
   - Results display area
   - Success message when flag is found
   - Error display (configurable per exercise)

3. **Admin Interface** - Extended Django admin:
   - Form to create/edit exercises
   - Preview functionality to test exercises

## Implementation Phases

### Phase 1: Project Setup
- Initialize Django project and app
- Set up database models
- Configure session middleware
- Set up basic templates and static files

### Phase 2: Basic Exercise Management
- Implement admin interface for exercises
- Create data model for exercises
- Implement exercise listing view
- Basic session-based progress tracking

### Phase 3: SQL.js Integration
- Set up SQL.js in frontend
- Implement code for initializing database with setup_code
- Create SQL query execution system
- Implement placeholder handling and validation
- Add table schema extraction from database metadata

### Phase 4: CodeMirror Integration
- Set up CodeMirror for readonly SQL display
- Implement syntax highlighting
- Create input fields for placeholders with validation
- Update readonly editor with placeholder values on input

### Phase 5: Exercise Solving Experience
- Implement case-insensitive flag detection logic
- Create result display component
- Build table schema display component
- Add session-based progress tracking

### Phase 6: UI/UX Enhancements
- Implement Google "Class Overview" inspired styling
- Add animations and interactive elements
- Configure error display based on exercise settings
- Optimize mobile experience

### Phase 7: Testing and Refinement
- Write unit tests
- Perform user testing
- Fix bugs and improve UX based on feedback
- Performance optimization

## Next Steps

1. Set up the basic Django project structure
2. Create initial models
3. Implement the admin interface
4. Begin implementing the frontend views
5. Integrate SQL.js