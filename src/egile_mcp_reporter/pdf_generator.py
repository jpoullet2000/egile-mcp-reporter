"""PDF generation using fpdf2 (Python-based PDF library)."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from fpdf import FPDF
import markdown as md

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF reports using fpdf2."""

    def __init__(self):
        """Initialize PDF generator."""
        pass

    def _sanitize_text(self, text: str) -> str:
        """Remove or replace characters not supported by Helvetica font."""
        import unicodedata
        
        # Replace common Unicode characters with ASCII equivalents
        replacements = {
            '•': '-',  # Bullet point
            '→': '->',  # Right arrow
            '←': '<-',  # Left arrow
            '⚠': '!',   # Warning sign (changed to exclamation)
            '✓': 'v',   # Check mark
            '✗': 'x',   # X mark
            '💡': '*',  # Light bulb (changed to asterisk)
            '"': '"',   # Left double quote
            '"': '"',   # Right double quote
            ''': "'",   # Left single quote
            ''': "'",   # Right single quote
            '—': '-',   # Em dash
            '–': '-',   # En dash
            '…': '...',  # Ellipsis
        }
        
        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)
        
        # Normalize to decomposed form, then remove combining characters
        normalized = unicodedata.normalize('NFD', text)
        # Keep only ASCII-compatible characters
        ascii_text = normalized.encode('ascii', 'ignore').decode('ascii')
        return ascii_text


    def create_report(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        output_path: Path,
        styles: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a PDF report from structured sections.

        Args:
            title: Report title
            sections: List of section dictionaries
            output_path: Output PDF path
            styles: Optional (not used with fpdf2)

        Returns:
            Dictionary with file metadata
        """
        import datetime
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, title, ln=True, align='C')
        pdf.ln(5)
        
        # Add generation timestamp
        pdf.set_font('Helvetica', 'I', 10)
        timestamp = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
        pdf.cell(0, 5, f'Generated: {timestamp}', ln=True, align='C')
        pdf.ln(10)
        
        # Render sections
        for section in sections:
            self._render_section_fpdf(pdf, section)
        
        # Save PDF
        pdf.output(str(output_path))

        return {
            "status": "success",
            "format": "pdf",
            "output_path": str(output_path),
            "size": output_path.stat().st_size,
            "title": title,
            "sections": len(sections),
        }

    def from_markdown(
        self,
        markdown: str,
        output_path: str,
        title: Optional[str] = None,
        styles: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Convert markdown to PDF using fpdf2.

        Args:
            markdown: Markdown content
            output_path: Output PDF path
            title: Document title
            styles: Optional (not used with fpdf2)

        Returns:
            Dictionary with file metadata
        """
        import datetime
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF with proper margins
        pdf = FPDF()
        pdf.set_left_margin(10)
        pdf.set_right_margin(10)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title if provided
        if title:
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(5)
            
            # Add generation timestamp
            pdf.set_font('Helvetica', 'I', 10)
            timestamp = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
            pdf.cell(0, 5, f'Generated: {timestamp}', ln=True, align='C')
            pdf.ln(10)
        
        # Process markdown line by line
        self._render_markdown(pdf, markdown)
        
        # Save PDF
        pdf.output(str(output_path))
        
        return {
            "status": "success",
            "format": "pdf",
            "output_path": str(output_path),
            "size": output_path.stat().st_size,
        }
    
    def _render_markdown(self, pdf: FPDF, markdown_text: str):
        """Render markdown content to PDF."""
        # Sanitize the entire markdown text first
        markdown_text = self._sanitize_text(markdown_text)
        
        lines = markdown_text.split('\n')
        in_table = False
        table_headers = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if we need a new page (less than 20mm remaining)
            if pdf.get_y() > pdf.h - 30:
                pdf.add_page()
            
            # Headers
            if line.startswith('# '):
                pdf.set_font('Helvetica', 'B', 14)
                pdf.ln(5)
                pdf.multi_cell(0, 8, line[2:].strip())
                pdf.ln(3)
                i += 1
                continue
            elif line.startswith('## '):
                pdf.set_font('Helvetica', 'B', 12)
                pdf.ln(4)
                pdf.multi_cell(0, 7, line[3:].strip())
                pdf.ln(2)
                i += 1
                continue
            elif line.startswith('### '):
                pdf.set_font('Helvetica', 'B', 11)
                pdf.ln(3)
                pdf.multi_cell(0, 6, line[4:].strip())
                pdf.ln(2)
                i += 1
                continue
            
            # Tables (markdown format)
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    # Table header
                    table_headers = [cell.strip() for cell in line.split('|')[1:-1]]
                    if table_headers:  # Only start table if headers exist
                        in_table = True
                        try:
                            # Render header
                            self._render_table_row(pdf, table_headers, is_header=True)
                        except Exception as e:
                            logger.error(f"Failed to render table header, skipping table: {e}")
                            in_table = False
                            table_headers = []
                    i += 1
                    # Skip separator line
                    if i < len(lines) and ('---' in lines[i] or ':-:' in lines[i]):
                        i += 1
                    continue
                else:
                    # Table row
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]
                    if cells and len(cells) == len(table_headers):
                        try:
                            self._render_table_row(pdf, cells, is_header=False)
                        except Exception as e:
                            logger.error(f"Failed to render table row, skipping: {e}")
                    i += 1
                    continue
            else:
                in_table = False
                table_headers = []
            
            # List items (check BEFORE bold to handle bullets with bold text)
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                # Just render as plain text - don't try to handle bold inline
                content = line.strip()[2:]  # Remove list marker
                # Remove ** markers for bold text
                content = content.replace('**', '')
                try:
                    pdf.set_font('Helvetica', '', 10)
                    pdf.set_x(pdf.l_margin)  # Reset X position to left margin
                    pdf.multi_cell(0, 5, '- ' + content)
                except Exception as e:
                    logger.error(f"Failed to render list item: {content[:50]}... Error: {e}")
                    # Skip this line rather than crashing
                i += 1
                continue
            
            # Bold text **text**
            if '**' in line:
                try:
                    pdf.set_font('Helvetica', 'B', 10)
                    text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                    pdf.multi_cell(0, 5, text)
                except Exception as e:
                    logger.error(f"Failed to render bold text: {line[:50]}... Error: {e}")
                    # Try as regular text
                    pdf.set_font('Helvetica', '', 10)
                    pdf.multi_cell(0, 5, line)
                i += 1
                continue
            
            # Code blocks (skip)
            if line.strip().startswith('```'):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    i += 1
                i += 1
                continue
            
            # Regular text
            if line.strip():
                pdf.set_font('Helvetica', '', 10)
                pdf.multi_cell(0, 5, line.strip())
            else:
                pdf.ln(2)
            
            i += 1
    
    def _render_table_row(self, pdf: FPDF, cells: List[str], is_header: bool = False):
        """Render a table row with proper column widths."""
        if not cells:
            return
            
        num_cols = len(cells)
        
        # Get effective page width (page width minus margins)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        col_width = effective_width / num_cols
        
        # Adjust font size based on column count and width
        if num_cols <= 3:
            font_size = 10
        elif num_cols <= 6:
            font_size = 8
        else:
            font_size = 7
        
        # Ensure minimum column width
        min_col_width = 15
        if col_width < min_col_width:
            # Table too wide, use smaller font
            font_size = max(6, font_size - 1)
        
        if is_header:
            pdf.set_font('Helvetica', 'B', font_size)
        else:
            pdf.set_font('Helvetica', '', font_size)
        
        try:
            for i, cell in enumerate(cells):
                # Truncate very long cell values
                display_text = str(cell)
                max_chars = int(col_width / 2)  # Rough estimate: 2mm per char
                if len(display_text) > max_chars:
                    display_text = display_text[:max_chars-3] + "..."
                pdf.cell(col_width, 6, display_text, border=1)
            pdf.ln()
        except Exception as e:
            logger.error(f"Error rendering table row: {e}, num_cols={num_cols}, col_width={col_width}")
            # Try without borders as fallback
            try:
                pdf.ln()
            except:
                pass
    
    def _render_section_fpdf(self, pdf: FPDF, section: Dict[str, Any]):
        """Render a section to PDF using fpdf2."""
        section_type = section.get("type", "text")
        section_title = section.get("title", "")
        
        # Section title
        if section_title:
            pdf.set_font('Helvetica', 'B', 12)
            pdf.ln(3)
            pdf.multi_cell(0, 7, section_title)
            pdf.ln(2)
        
        # Section content based on type
        if section_type == "text":
            content = section.get("content", "")
            pdf.set_font('Helvetica', '', 10)
            pdf.multi_cell(0, 5, content)
            pdf.ln(3)
        
        elif section_type == "table":
            data = section.get("data", [])
            if data:
                columns = section.get("columns") or list(data[0].keys())
                
                # Table header
                self._render_table_row(pdf, columns, is_header=True)
                
                # Table rows
                for row in data:
                    values = [str(row.get(col, "")) for col in columns]
                    self._render_table_row(pdf, values, is_header=False)
                
                pdf.ln(3)
        
        elif section_type == "list":
            items = section.get("items", [])
            pdf.set_font('Helvetica', '', 10)
            for item in items:
                pdf.cell(10, 5, '')
                pdf.multi_cell(0, 5, f'\u2022 {item}')
            pdf.ln(3)

    def _generate_html(
        self, title: str, sections: List[Dict[str, Any]], custom_styles: Optional[Dict[str, str]]
    ) -> str:
        """Generate HTML content from sections."""
        import datetime

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
</head>
<body>
    <div class="report-header">
        <h1>{title}</h1>
        <p class="generated-date">Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    <div class="content">
"""

        for section in sections:
            html += self._render_section(section)

        html += """
    </div>
</body>
</html>
"""
        return html

    def _render_section(self, section: Dict[str, Any]) -> str:
        """Render a single section to HTML."""
        section_type = section.get("type", "text")
        section_title = section.get("title", "")

        html = "<div class='section'>\n"

        if section_title:
            html += f"<h2>{section_title}</h2>\n"

        if section_type == "text":
            content = section.get("content", "")
            # Convert markdown-like formatting
            import markdown as md

            html += f"<div class='text-content'>{md.markdown(content)}</div>\n"

        elif section_type == "table":
            html += self._render_table(section)

        elif section_type == "list":
            items = section.get("items", [])
            html += "<ul>\n"
            for item in items:
                html += f"<li>{item}</li>\n"
            html += "</ul>\n"

        elif section_type == "chart":
            # Placeholder for embedded chart
            html += f"<div class='chart-placeholder'>Chart: {section.get('title', 'Untitled')}</div>\n"

        html += "</div>\n"
        return html

    def _render_table(self, section: Dict[str, Any]) -> str:
        """Render table data to HTML."""
        data = section.get("data", [])
        if not data:
            return "<p>No data available</p>"

        columns = section.get("columns") or list(data[0].keys())

        html = "<table>\n<thead>\n<tr>\n"
        for col in columns:
            html += f"<th>{col}</th>"
        html += "\n</tr>\n</thead>\n<tbody>\n"

        for row in data:
            html += "<tr>\n"
            for col in columns:
                value = row.get(col, "")
                # Format numbers nicely
                if isinstance(value, float):
                    value = f"{value:,.2f}"
                html += f"<td>{value}</td>"
            html += "\n</tr>\n"

        html += "</tbody>\n</table>\n"
        return html

    def _get_default_css(self) -> str:
        """Get default CSS styles for PDF."""
        return """
@page {
    size: A4;
    margin: 20mm;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

.report-header {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #2563eb;
}

.report-header h1 {
    font-size: 28pt;
    color: #1e3a8a;
    margin: 0 0 10px 0;
}

.generated-date {
    color: #666;
    font-size: 9pt;
    margin: 5px 0;
}

.section {
    margin-bottom: 25px;
    page-break-inside: avoid;
}

.section h2 {
    font-size: 16pt;
    color: #1e40af;
    margin: 20px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 1px solid #ddd;
}

.section h3 {
    font-size: 13pt;
    color: #374151;
    margin: 15px 0 8px 0;
}

.text-content {
    margin: 10px 0;
}

.text-content p {
    margin: 8px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 10pt;
}

table thead {
    background-color: #1e40af;
    color: white;
}

table th {
    padding: 10px;
    text-align: left;
    font-weight: 600;
}

table td {
    padding: 8px 10px;
    border-bottom: 1px solid #e5e7eb;
}

table tbody tr:nth-child(even) {
    background-color: #f9fafb;
}

table tbody tr:hover {
    background-color: #f3f4f6;
}

ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
}

.chart-placeholder {
    background: #f3f4f6;
    border: 2px dashed #d1d5db;
    padding: 40px;
    text-align: center;
    color: #6b7280;
    margin: 15px 0;
}

strong, b {
    color: #1f2937;
}

code {
    background: #f3f4f6;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

pre {
    background: #1f2937;
    color: #f9fafb;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
}

pre code {
    background: transparent;
    color: #f9fafb;
}
"""
