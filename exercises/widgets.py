from django import forms
from django.forms.widgets import Textarea
from django.utils.safestring import mark_safe


class CodeEditorWidget(Textarea):
    """Widget for code editor using CodeMirror."""
    
    def __init__(self, mode='text/x-sql', theme='monokai', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.theme = theme
        
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Add unique ID if not provided
        if 'id' not in attrs:
            attrs['id'] = f"id_{name}"
        
        # Get the ID to reference it in JavaScript
        element_id = attrs['id']
        
        # Generate a unique ID for the editor instance
        editor_id = f"editor_{element_id}"
        
        # Render the textarea
        output = super().render(name, value, attrs, renderer)
        
        # Add the CodeMirror initialization
        output += f"""
        <div id="{editor_id}" style="border: 1px solid #ccc; margin-top: 10px;"></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // Initialize CodeMirror
                var {editor_id} = CodeMirror(document.getElementById('{editor_id}'), {{
                    value: document.getElementById('{element_id}').value,
                    mode: '{self.mode}',
                    theme: '{self.theme}',
                    lineNumbers: true,
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    indentUnit: 2,
                    viewportMargin: Infinity
                }});
                
                // Update textarea when CodeMirror changes
                {editor_id}.on('change', function() {{
                    document.getElementById('{element_id}').value = {editor_id}.getValue();
                }});
                
                // Hide the original textarea
                document.getElementById('{element_id}').style.display = 'none';
            }});
        </script>
        """
        
        return mark_safe(output)


class SQLEditorWidget(CodeEditorWidget):
    """CodeMirror widget specifically for SQL."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(mode='text/x-sql', theme='monokai', *args, **kwargs)


class JavaScriptEditorWidget(CodeEditorWidget):
    """CodeMirror widget specifically for JavaScript."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(mode='javascript', theme='dracula', *args, **kwargs)


class JsonEditorWidget(CodeEditorWidget):
    """CodeMirror widget specifically for JSON."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(mode='application/json', theme='monokai', *args, **kwargs)