from django.test import TestCase, Client
from django.urls import reverse
from .models import Exercise
import json


class ExerciseModelTest(TestCase):
    """Tests for the Exercise model."""
    
    def setUp(self):
        """Set up test data."""
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="A test exercise",
            setup_code="CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            placeholders=json.dumps([{"name": "id", "type": "int"}]),
            expected_flag="TEST_FLAG",
            show_tables=json.dumps(["test"]),
            show_query=True,
            show_errors=True,
            difficulty=1,
            order=1
        )
    
    def test_exercise_creation(self):
        """Test that exercise is created correctly."""
        self.assertEqual(self.exercise.title, "Test Exercise")
        self.assertEqual(self.exercise.difficulty, 1)
        self.assertTrue(self.exercise.show_query)
        self.assertTrue(self.exercise.show_errors)
        self.assertEqual(json.loads(self.exercise.placeholders)[0]["name"], "id")
        self.assertEqual(json.loads(self.exercise.show_tables)[0], "test")


class ExerciseViewsTest(TestCase):
    """Tests for exercise views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="A test exercise",
            setup_code="CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            placeholders=json.dumps([{"name": "id", "type": "int"}]),
            expected_flag="TEST_FLAG",
            show_tables=json.dumps(["test"]),
            show_query=True,
            show_errors=True,
            difficulty=1,
            order=1
        )
    
    def test_exercise_list_view(self):
        """Test that exercise list view works correctly."""
        response = self.client.get(reverse('exercise_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Exercise")
        self.assertTemplateUsed(response, 'exercises/exercise_list.html')
    
    def test_exercise_detail_view(self):
        """Test that exercise detail view works correctly."""
        response = self.client.get(reverse('exercise_detail', args=[self.exercise.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Exercise")
        self.assertTemplateUsed(response, 'exercises/exercise_detail.html')
    
    def test_mark_exercise_solved(self):
        """Test marking an exercise as solved."""
        # Should only accept POST requests
        response = self.client.get(reverse('mark_exercise_solved', args=[self.exercise.id]))
        self.assertEqual(response.status_code, 405)
        
        # POST should work
        response = self.client.post(reverse('mark_exercise_solved', args=[self.exercise.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        
        # Check that the session contains the solved exercise
        session = self.client.session
        self.assertIn(self.exercise.id, session.get('solved_exercises', []))


class SessionStorageTest(TestCase):
    """Tests for session-based exercise progress tracking."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.exercise = Exercise.objects.create(
            title="Test Exercise",
            description="A test exercise",
            setup_code="CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT);",
            base_query="SELECT * FROM test WHERE id = :id",
            placeholders=json.dumps([{"name": "id", "type": "int"}]),
            expected_flag="TEST_FLAG",
            show_tables=json.dumps(["test"]),
            show_query=True,
            show_errors=True,
            difficulty=1,
            order=1
        )
    
    def test_session_persistence(self):
        """Test that solved exercises are persisted in the session."""
        # Mark exercise as solved
        self.client.post(reverse('mark_exercise_solved', args=[self.exercise.id]))
        
        # Visit the exercise list page and check that it shows as solved
        response = self.client.get(reverse('exercise_list'))
        self.assertContains(response, "Solved")
        
        # Visit the exercise detail page and check that it shows as solved
        response = self.client.get(reverse('exercise_detail', args=[self.exercise.id]))
        self.assertContains(response, "true") # "isSolved" in the JS
