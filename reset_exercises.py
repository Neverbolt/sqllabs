#!/usr/bin/env python
"""
Utility script to reset all exercises.
This script deletes all existing exercises and recreates the example exercises.
WARNING: This will delete ALL existing exercises!
"""
import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sqllabs.settings')
django.setup()

from exercises.models import Exercise, Placeholder


def reset_exercises():
    """Delete all existing exercises and placeholders."""

    # Get confirmation
    print("WARNING: This will delete ALL existing exercises and placeholders.")
    print("Enter 'yes' to continue, or anything else to cancel.")

    choice = input("> ")
    if choice.lower() != 'yes':
        print("Operation cancelled.")
        return

    # Delete all placeholders
    placeholder_count = Placeholder.objects.count()
    Placeholder.objects.all().delete()

    # Delete all exercises
    exercise_count = Exercise.objects.count()
    Exercise.objects.all().delete()

    print(f"Deleted {exercise_count} exercises and {placeholder_count} placeholders.")


if __name__ == "__main__":
    reset_exercises()

    # Run the create_all_exercises.py script if requested
    if len(sys.argv) > 1 and sys.argv[1] == '--recreate':
        print("\nRecreating example exercises...")
        # Use the current directory to find the create_all_exercises.py script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        create_script = os.path.join(current_dir, 'create_all_exercises.py')

        if os.path.exists(create_script):
            # Execute the create_all_exercises.py script
            exec(open(create_script).read())
        else:
            print(f"Error: Could not find {create_script}")
            print("Please run 'python example_exercises/create_all_exercises.py' manually.")
    else:
        print("\nTo recreate example exercises, run:")
        print("python example_exercises/reset_exercises.py --recreate")
