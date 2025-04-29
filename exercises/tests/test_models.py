from django.test import TestCase
from exercises.models import Exercise, Placeholder


class ExerciseModelTest(TestCase):
    """Test case for the Exercise model."""
    
    def test_create_exercise(self):
        """Test creating an exercise."""
        exercise = Exercise.objects.create(
            title="Test Exercise",
            description="Test description",
            setup_code="CREATE TABLE test (id INT, value TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            expected_flag="FLAG{test}",
            difficulty=1,
            order=1
        )
        self.assertEqual(exercise.title, "Test Exercise")
        self.assertEqual(exercise.difficulty, 1)
    
    def test_create_exercise_with_anti_flag(self):
        """Test creating an exercise with an anti-flag."""
        exercise = Exercise.objects.create(
            title="Test Anti-Flag Exercise",
            description="Test description with anti-flag",
            setup_code="CREATE TABLE test (id INT, value TEXT, secret TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            expected_flag="FLAG{test_anti_flag}",
            anti_flag="SECRET_DATA",
            difficulty=3,
            order=2
        )
        self.assertEqual(exercise.title, "Test Anti-Flag Exercise")
        self.assertEqual(exercise.anti_flag, "SECRET_DATA")


class PlaceholderModelTest(TestCase):
    """Test case for the Placeholder model."""
    
    def setUp(self):
        """Set up test data."""
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="Test description",
            setup_code="CREATE TABLE test (id INT, value TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            expected_flag="FLAG{test}",
            difficulty=1,
            order=1
        )
    
    def test_create_placeholder(self):
        """Test creating a placeholder."""
        placeholder = Placeholder.objects.create(
            exercise=self.exercise,
            name="id",
            type="int",
            description="ID to filter by"
        )
        self.assertEqual(placeholder.name, "id")
        self.assertEqual(placeholder.type, "int")
    
    def test_placeholder_to_dict(self):
        """Test the to_dict method."""
        placeholder = Placeholder.objects.create(
            exercise=self.exercise,
            name="test",
            type="regex",
            regex_pattern="^test.*$",
            description="Test placeholder"
        )
        data = placeholder.to_dict()
        self.assertEqual(data["name"], "test")
        self.assertEqual(data["type"], "regex")
        self.assertEqual(data["regex_pattern"], "^test.*$")