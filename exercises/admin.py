from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Exercise, Placeholder
from .widgets import SQLEditorWidget, JavaScriptEditorWidget, JsonEditorWidget


class PlaceholderInline(admin.TabularInline):
    """Inline admin for placeholders."""
    model = Placeholder
    extra = 1
    fields = ('name', 'type', 'regex_pattern', 'description')
    
    def get_extra(self, request, obj=None, **kwargs):
        """Dynamically set the number of empty forms."""
        if obj is None:
            return 3  # Show 3 empty forms for new exercises
        return 1  # Show 1 empty form for existing exercises


class PlaceholderSanitizeJsInline(admin.StackedInline):
    """Inline admin for placeholder sanitization JavaScript."""
    model = Placeholder
    extra = 0
    fields = ('name', 'sanitize_js')
    readonly_fields = ('name',)
    verbose_name = "Placeholder Sanitization"
    verbose_name_plural = "Placeholder Sanitization JavaScript"
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['sanitize_js'].widget = JavaScriptEditorWidget(
            attrs={'rows': 10, 'style': 'width: 100%;'}
        )
        return formset


class ExerciseAdminForm(forms.ModelForm):
    """Custom form for Exercise admin."""
    
    tables_list = forms.CharField(
        required=False,
        help_text="Comma-separated list of table names to display to user",
        label="Show Tables"
    )
    
    class Meta:
        model = Exercise
        fields = '__all__'
        widgets = {
            'setup_code': SQLEditorWidget(attrs={'rows': 10}),
            'base_query': SQLEditorWidget(attrs={'rows': 5}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
        exclude = ('placeholders',)  # Hide the JSONField since we use inlines
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate tables_list from instance.show_tables
        if self.instance.pk and self.instance.show_tables:
            self.initial['tables_list'] = ', '.join(self.instance.show_tables)
    
    def clean_tables_list(self):
        """Convert comma-separated string to list."""
        tables_text = self.cleaned_data.get('tables_list', '')
        if not tables_text:
            return []
        
        # Split by comma and strip whitespace
        tables = [table.strip() for table in tables_text.split(',')]
        # Remove empty entries
        tables = [table for table in tables if table]
        return tables
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Update show_tables from tables_list
        instance.show_tables = self.cleaned_data.get('tables_list', [])
        
        if commit:
            instance.save()
        
        return instance


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    form = ExerciseAdminForm
    list_display = ('title', 'difficulty_display', 'order', 'show_query', 'show_errors', 'allow_js')
    list_filter = ('difficulty', 'show_query', 'show_errors', 'allow_js')
    search_fields = ('title', 'description')
    ordering = ('order', 'difficulty')
    inlines = [PlaceholderInline, PlaceholderSanitizeJsInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'color', 'difficulty', 'order')
        }),
        ('SQL Configuration', {
            'fields': ('setup_code', 'base_query', 'expected_flag', 'anti_flag')
        }),
        ('Display Options', {
            'fields': ('tables_list', 'show_query', 'show_errors', 'allow_js')
        }),
    )
    
    class Media:
        css = {
            'all': (
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/codemirror.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/theme/monokai.min.css',
                'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/theme/dracula.min.css',
                'css/admin-customizations.css',
            )
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/codemirror.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/mode/sql/sql.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/mode/javascript/javascript.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/mode/clike/clike.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/edit/matchbrackets.min.js',
            'https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.9/addon/edit/closebrackets.min.js',
        )
    
    def difficulty_display(self, obj):
        colors = {
            1: '#28a745',  # Green for easy
            2: '#28a745',
            3: '#28a745',
            4: '#ffc107',  # Yellow for medium
            5: '#ffc107',
            6: '#ffc107',
            7: '#fd7e14',  # Orange for hard
            8: '#fd7e14',
            9: '#dc3545',  # Red for expert
            10: '#dc3545',
        }
        color = colors.get(obj.difficulty, '#007bff')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}/10</span>',
            color, obj.difficulty
        )
    
    difficulty_display.short_description = 'Difficulty'