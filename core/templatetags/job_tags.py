from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import format_html, escape # <-- CORRECT
import re

register = template.Library()

# Keywords that often indicate a heading (case-insensitive)
HEADING_KEYWORDS = [
    'job summary', 'summary', 'overview', 'description',
    'responsibilities', 'key responsibilities', 'duties',
    'requirements', 'qualifications', 'skills', 'experience', 'education',
    'benefits', 'compensation', 'salary', 'pay',
    'location', 'company', 'about us',
    'how to apply', 'application instructions', 'to apply'
]

# Regex to match potential list item markers at the start of a line
# Allows *, -, +, numbers like 1., letters like a)
LIST_MARKER_RE = re.compile(r'^[ \t]*([\*\-\+]|\d+\.|[a-zA-Z]\))[ \t]+')
# Regex for lines that look like "Label: Value"
LABEL_VALUE_RE = re.compile(r'^([a-zA-Z\s]+):\s+(.*)')

@register.filter(name='parse_job_description', is_safe=True)
@stringfilter
def parse_job_description(value):
    """
    Attempts to parse a job description string into structured HTML.
    Looks for keywords to identify headings and common list patterns.
    WARNING: This parsing is based on assumptions and is inherently fragile.
             It may not work perfectly for all input formats.
    """
    html_output = ""
    lines = value.strip().splitlines()
    in_list = False
    current_buffer = [] # To collect lines that might form a paragraph

    def flush_buffer(force_paragraph=False):
        """Helper to render buffered lines as a paragraph."""
        nonlocal html_output, current_buffer
        content = '<br>'.join(escape(line.strip()) for line in current_buffer if line.strip())
        if content:
            # Only wrap non-empty buffer in <p> unless forced (rare)
             html_output += format_html('<p class="mb-2">{}</p>\n', format_html(content))
        current_buffer = []

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        # --- 1. Handle Blank Lines ---
        if not stripped_line:
            flush_buffer() # Render any preceding text as a paragraph
            if in_list:
                html_output += '</ul>\n' # Close list on blank line
                in_list = False
            continue

        # --- 2. Check for Keywords indicating a Heading ---
        # Check if line (or line ending with :) matches keywords
        potential_heading = stripped_line.lower().rstrip(':').strip()
        is_heading = potential_heading in HEADING_KEYWORDS

        if is_heading:
            flush_buffer() # Render preceding text
            if in_list:
                html_output += '</ul>\n' # Close previous list
                in_list = False
            # Use the original line's casing, remove trailing colon if present
            heading_text = stripped_line.rstrip(':').strip()
            html_output += format_html('<h5 class="mt-3 mb-2 fw-semibold text-primary">{}</h5>\n', escape(heading_text))
            continue # Move to next line after processing heading

        # --- 3. Check for List Items ---
        is_list_item = LIST_MARKER_RE.match(line) # Check original line for leading marker/indent

        if is_list_item:
            flush_buffer() # Render preceding text
            if not in_list:
                html_output += '<ul class="list-unstyled ps-3 mb-3">\n' # Use Bootstrap classes
                in_list = True
            # Clean the marker and create list item
            item_text = LIST_MARKER_RE.sub('', line).strip() # Use sub to remove marker
            html_output += format_html('<li class="mb-1"><i class="fas fa-check text-success me-2"></i>{}</li>\n', escape(item_text))
            continue # Move to next line

        # --- 4. Check for "Label: Value" Pattern ---
        label_match = LABEL_VALUE_RE.match(stripped_line)
        if label_match and label_match.group(1).lower() not in HEADING_KEYWORDS:
             flush_buffer()
             if in_list:
                 html_output += '</ul>\n'
                 in_list = False
             html_output += format_html('<p class="mb-2"><strong>{}:</strong> {}</p>\n',
                                        escape(label_match.group(1).strip()),
                                        escape(label_match.group(2).strip()))
             continue


        # --- 5. If none of the above, buffer the line for a potential paragraph ---
        # If we were in a list, but this line isn't a list item, close the list.
        if in_list:
             html_output += '</ul>\n'
             in_list = False
        current_buffer.append(line) # Add raw line to buffer

    # --- End of loop ---
    flush_buffer() # Render any remaining lines in the buffer
    if in_list: # Ensure any final list is closed
        html_output += '</ul>'

    # Return the final generated HTML, marked as safe
    if not html_output: # Handle empty input case
         return format_html('<p>{}</p>', escape(value)) # Fallback if parsing yielded nothing

    return format_html(html_output)