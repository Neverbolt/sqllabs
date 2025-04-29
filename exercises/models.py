from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from colorfield.fields import ColorField


class Placeholder(models.Model):
    """Model for placeholders used in SQL exercises."""
    
    PLACEHOLDER_TYPES = [
        ('str', 'String'),
        ('int', 'Integer'),
        ('regex', 'Regular Expression'),
    ]
    
    exercise = models.ForeignKey(
        'Exercise', 
        on_delete=models.CASCADE, 
        related_name='placeholder_set'
    )
    name = models.CharField(
        max_length=50,
        help_text="Placeholder name (without the colon)"
    )
    type = models.CharField(
        max_length=10,
        choices=PLACEHOLDER_TYPES,
        default='str',
        help_text="Data type for validation"
    )
    regex_pattern = models.CharField(
        max_length=255,
        blank=True,
        help_text="Pattern to validate input (only for regex type)"
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of the placeholder for the admin interface"
    )
    sanitize_js = models.TextField(
        blank=True,
        null=False,
        help_text="JavaScript function to sanitize input (parameter: 'value', returns sanitized value)",
        default="""// This function sanitizes the input value
// Parameter: value - the raw input from the user
// Returns: the sanitized value
function sanitize(value) {
  // By default, return the value unchanged
  return value;
}"""
    )
    
    class Meta:
        ordering = ['name']
        unique_together = ['exercise', 'name']
    
    def __str__(self):
        return f":{self.name} ({self.get_type_display()})"
    
    def to_dict(self):
        """Convert placeholder to dictionary format for JSON."""
        data = {
            'name': self.name,
            'type': self.type,
        }
        if self.type == 'regex' and self.regex_pattern:
            data['regex_pattern'] = self.regex_pattern
        return data


class Exercise(models.Model):
    """Model for SQL exercises with placeholders for injection training."""
    
    title = models.CharField(max_length=100)
    description = models.TextField(help_text="Exercise description and instructions")
    setup_code = models.TextField(
        help_text="SQL to initialize database (create tables, insert data)"
    )
    base_query = models.TextField(
        help_text="Query with placeholders (e.g., 'SELECT * FROM users WHERE name = :name')"
    )
    placeholders = models.JSONField(
        help_text=(
            "List of placeholder definitions. Format: "
            "[{'name': 'name', 'type': 'str|int|regex', 'regex_pattern': 'optional pattern'}]"
        ),
        default=list,
        blank=True,
        editable=False  # We'll manage this through the placeholder_set
    )
    expected_flag = models.CharField(
        max_length=255,
        help_text="Flag that should appear in results when solved (case-insensitive check)"
    )
    anti_flag = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Text that must NOT appear in results for the query to be successful (case-insensitive check)"
    )
    show_tables = models.JSONField(
        help_text="List of table names to display to user",
        blank=True,
        default=list
    )
    show_query = models.BooleanField(
        default=True,
        help_text="Whether to show the base query to user or just inputs"
    )
    show_errors = models.BooleanField(
        default=True,
        help_text="Whether to display SQL error messages to user"
    )
    allow_js = models.BooleanField(
        default=False,
        help_text="Enable JavaScript mode for interactive SQL execution"
    )
    difficulty = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Difficulty rating from 1 (easiest) to 10 (hardest)"
    )
    order = models.IntegerField(
        default=0,
        help_text="Display order in listing"
    )
    color = ColorField(
        default='#007bff',
        help_text="Color to represent this exercise"
    )
    
    def save(self, *args, **kwargs):
        # First save to get a primary key
        super().save(*args, **kwargs)
        
        # Then update placeholders if needed (only for existing models with placeholder_set)
        if hasattr(self, 'placeholder_set') and self.pk is not None:
            try:
                self.placeholders = [p.to_dict() for p in self.placeholder_set.all()]
                # Save again if placeholders were updated
                super().save(update_fields=['placeholders'])
            except Exception:
                pass  # Skip this part if no placeholder_set exists yet
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return self.title
