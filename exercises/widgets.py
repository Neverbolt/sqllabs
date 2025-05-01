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
        
        # Generate a safe JS variable name by replacing invalid characters
        js_var_name = f"editor_{element_id.replace('-', '_').replace('.', '_')}"
        
        # Render the textarea
        output = super().render(name, value, attrs, renderer)
        
        # Add the CodeMirror initialization
        output += f"""
        <div id="{editor_id}" style="margin-top: 10px;"></div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // Initialize CodeMirror
                var {js_var_name} = CodeMirror(document.getElementById('{editor_id}'), {{
                    value: document.getElementById('{element_id}').value,
                    mode: '{self.mode}',
                    theme: '{self.theme}',
                    lineNumbers: true,
                    matchBrackets: true,
                    autoCloseBrackets: true,
                    indentUnit: 2,
                    viewportMargin: Infinity,
                    scrollbarStyle: 'simple',
                    styleActiveLine: true
                }});
                
                // Update textarea when CodeMirror changes
                {js_var_name}.on('change', function() {{
                    document.getElementById('{element_id}').value = {js_var_name}.getValue();
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


class MarkdownEditorWidget(CodeEditorWidget):
    """CodeMirror widget specifically for Markdown with preview."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(mode='markdown', theme='monokai', *args, **kwargs)
        
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        
        # Add unique ID if not provided
        if 'id' not in attrs:
            attrs['id'] = f"id_{name}"
        
        # Get the ID to reference it in JavaScript
        element_id = attrs['id']
        
        # Generate a unique ID for the editor instance and preview
        editor_id = f"editor_{element_id}"
        preview_id = f"preview_{element_id}"
        
        # Generate a safe JS variable name by replacing invalid characters
        js_var_name = f"editor_{element_id.replace('-', '_').replace('.', '_')}"
        
        # Render the textarea
        output = super(CodeEditorWidget, self).render(name, value, attrs, renderer)
        
        # Add the CodeMirror initialization with preview
        output += f"""
        <div style="display: flex; flex-direction: column; margin-top: 10px;">
            <div class="markdown-tabs">
                <button type="button" id="tab_edit_{element_id}" class="button active">Edit</button>
                <button type="button" id="tab_preview_{element_id}" class="button">Preview</button>
            </div>
            <div id="{editor_id}"></div>
            <div id="{preview_id}" class="markdown-preview" style="display: none;"></div>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // Check if marked.js is loaded, if not, load it
                if (typeof marked === 'undefined') {{
                    var script = document.createElement('script');
                    script.src = 'https://cdn.jsdelivr.net/npm/marked/marked.min.js';
                    script.onload = initializeEditor;
                    document.head.appendChild(script);
                }} else {{
                    initializeEditor();
                }}
                
                function initializeEditor() {{
                    // Initialize CodeMirror
                    var {js_var_name} = CodeMirror(document.getElementById('{editor_id}'), {{
                        value: document.getElementById('{element_id}').value,
                        mode: 'markdown',
                        theme: 'monokai',
                        lineNumbers: true,
                        matchBrackets: true,
                        autoCloseBrackets: true,
                        indentUnit: 2,
                        lineWrapping: true,
                        viewportMargin: Infinity,
                        scrollbarStyle: 'simple',
                        styleActiveLine: true
                    }});
                    
                    // Update textarea when CodeMirror changes
                    {js_var_name}.on('change', function() {{
                        document.getElementById('{element_id}').value = {js_var_name}.getValue();
                        updatePreview();
                    }});
                    
                    // Function to update the preview
                    function updatePreview() {{
                        var content = {js_var_name}.getValue();
                        var preview = document.getElementById('{preview_id}');
                        if (typeof marked !== 'undefined') {{
                            preview.innerHTML = marked.parse(content);
                        }} else {{
                            preview.innerHTML = content;
                        }}
                    }}
                    
                    // Initialize preview
                    updatePreview();
                    
                    // Tab switching
                    document.getElementById('tab_edit_{element_id}').addEventListener('click', function() {{
                        document.getElementById('{editor_id}').style.display = 'block';
                        document.getElementById('{preview_id}').style.display = 'none';
                        this.classList.add('active');
                        document.getElementById('tab_preview_{element_id}').classList.remove('active');
                    }});
                    
                    document.getElementById('tab_preview_{element_id}').addEventListener('click', function() {{
                        document.getElementById('{editor_id}').style.display = 'none';
                        document.getElementById('{preview_id}').style.display = 'block';
                        updatePreview(); // Update preview before showing
                        this.classList.add('active');
                        document.getElementById('tab_edit_{element_id}').classList.remove('active');
                    }});
                    
                    // Hide the original textarea
                    document.getElementById('{element_id}').style.display = 'none';
                }}
            }});
        </script>
        """
        
        return mark_safe(output)