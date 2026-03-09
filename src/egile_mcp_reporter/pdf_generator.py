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
        Convert markdown to PDF using best available method.
        Priority: WeasyPrint (Linux/Mac) → ReportLab (Windows-friendly) → fpdf2 (fallback)

        Args:
            markdown: Markdown content
            output_path: Output PDF path
            title: Document title
            styles: Optional CSS style overrides

        Returns:
            Dictionary with file metadata
        """
        import datetime
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
        
        # Try WeasyPrint first (best quality, but requires GTK on Windows)
        try:
            from weasyprint import HTML, CSS
            
            # Convert markdown to HTML
            html_content = md.markdown(
                markdown,
                extensions=['extra', 'tables', 'fenced_code', 'nl2br']
            )
            
            # Build complete HTML document
            full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title or 'Report'}</title>
    <style>
        {self._get_default_css()}
        {styles.get('css', '') if styles else ''}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>{title or 'Report'}</h1>
        <p class="generated-date">Generated: {timestamp}</p>
    </div>
    <div class="content">
        {html_content}
    </div>
</body>
</html>
"""
            
            # Generate PDF using WeasyPrint
            HTML(string=full_html).write_pdf(str(output_path))
            
            logger.info(f"✅ Generated PDF with WeasyPrint: {output_path}")
            return {
                "status": "success",
                "format": "pdf",
                "output_path": str(output_path),
                "size": output_path.stat().st_size,
                "generator": "weasyprint"
            }
            
        except ImportError:
            logger.info("WeasyPrint not available, trying ReportLab")
        except Exception as e:
            logger.warning(f"WeasyPrint failed ({str(e)[:100]}), trying ReportLab")
        
        # Try ReportLab (Windows-friendly, good quality)
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
            import html as html_lib
            
            # Convert markdown to HTML first
            html_content = md.markdown(
                markdown,
                extensions=['extra', 'tables', 'fenced_code', 'nl2br']
            )
            
            # Create PDF document
            doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                                   leftMargin=0.75*inch, rightMargin=0.75*inch,
                                   topMargin=1*inch, bottomMargin=0.75*inch)
            
            # Build document content
            story = []
            styles = getSampleStyleSheet()
            
            # Add title if provided
            if title:
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=20,
                    textColor=colors.HexColor('#1e3a8a'),
                    spaceAfter=12,
                    alignment=TA_CENTER
                )
                story.append(Paragraph(html_lib.escape(title), title_style))
                
                # Add timestamp
                timestamp_style = ParagraphStyle(
                    'Timestamp',
                    parent=styles['Normal'],
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                    spaceAfter=20
                )
                story.append(Paragraph(f"Generated: {timestamp}", timestamp_style))
            
            # Parse HTML and convert to ReportLab elements
            self._html_to_reportlab(html_content, story, styles)
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"✅ Generated PDF with ReportLab (Windows-compatible): {output_path}")
            return {
                "status": "success",
                "format": "pdf",
                "output_path": str(output_path),
                "size": output_path.stat().st_size,
                "generator": "reportlab"
            }
            
        except ImportError:
            logger.warning("ReportLab not available, falling back to fpdf2")
        except Exception as e:
            logger.error(f"ReportLab generation failed: {e}, falling back to fpdf2")
        
        # Fallback: Use fpdf2 (original implementation)
        pdf = FPDF()
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_top_margin(15)
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add title if provided
        if title:
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, title, ln=True, align='C')
            pdf.ln(5)
            
            # Add generation timestamp
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 5, f'Generated: {timestamp}', ln=True, align='C')
            pdf.ln(10)
        
        # Process markdown line by line with error handling
        try:
            self._render_markdown(pdf, markdown)
        except Exception as e:
            logger.error(f"Error rendering markdown, using simplified mode: {e}")
            # Fallback: render as plain text
            pdf.set_font('Helvetica', '', 10)
            pdf.set_x(pdf.l_margin)
            # Split into manageable chunks
            simple_text = markdown.replace('#', '').replace('**', '').replace('|', ' ')
            for line in simple_text.split('\n')[:200]:  # Limit to 200 lines
                if line.strip():
                    try:
                        pdf.set_x(pdf.l_margin)
                        pdf.multi_cell(0, 5, line.strip()[:150])  # Max 150 chars
                    except:
                        pass  # Skip problematic lines
        
        # Save PDF
        pdf.output(str(output_path))
        
        logger.info(f"⚠️ Generated PDF with fpdf2 (limited formatting): {output_path}")
        return {
            "status": "success",
            "format": "pdf",
            "output_path": str(output_path),
            "size": output_path.stat().st_size,
            "generator": "fpdf2"
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
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 8, line[2:].strip())
                pdf.ln(3)
                i += 1
                continue
            elif line.startswith('## '):
                pdf.set_font('Helvetica', 'B', 12)
                pdf.ln(4)
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 7, line[3:].strip())
                pdf.ln(2)
                i += 1
                continue
            elif line.startswith('### '):
                pdf.set_font('Helvetica', 'B', 11)
                pdf.ln(3)
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 6, line[4:].strip())
                pdf.ln(2)
                i += 1
                continue
            
            # Tables (markdown format)
            if '|' in line and line.strip().startswith('|'):
                if not in_table:
                    # Table header
                    table_headers = [cell.strip() for cell in line.split('|')[1:-1]]
                    # Skip tables with too many columns (>6) - they're too complex
                    if len(table_headers) > 6:
                        logger.warning(f"Skipping complex table with {len(table_headers)} columns")
                        # Skip until end of table
                        i += 1
                        while i < len(lines) and '|' in lines[i]:
                            i += 1
                        continue
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
                    # Remove ** markers and render as regular text to avoid font width issues
                    text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                    pdf.set_font('Helvetica', 'B', 10)
                    pdf.set_x(pdf.l_margin)  # Reset X position
                    # Use write() instead of multi_cell() for bold text to avoid width calculation issues
                    pdf.write(5, text)
                    pdf.ln()
                except Exception as e:
                    logger.error(f"Failed to render bold text: {line[:50]}... Error: {e}")
                    # Fallback: render as regular text without bold
                    text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                    pdf.set_font('Helvetica', '', 10)
                    pdf.set_x(pdf.l_margin)
                    pdf.write(5, text)
                    pdf.ln()
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
                pdf.set_x(pdf.l_margin)  # Reset X position
                pdf.multi_cell(0, 5, line.strip())
            else:
                pdf.ln(2)
            
            i += 1
    
    def _render_table_row(self, pdf: FPDF, cells: List[str], is_header: bool = False):
        """Render a table row with proper column widths that fit the page."""
        if not cells:
            return
            
        num_cols = len(cells)
        
        # Skip tables that are too complex (>8 columns)
        if num_cols > 8:
            logger.warning(f"Skipping complex table with {num_cols} columns")
            return
        
        # Get effective page width (page width minus margins)
        effective_width = pdf.w - pdf.l_margin - pdf.r_margin
        col_width = effective_width / num_cols
        
        # Adjust font size based on column count to ensure content fits
        if num_cols <= 3:
            font_size = 9
            max_chars_per_col = int(col_width * 0.5)  # Rough estimate
        elif num_cols <= 5:
            font_size = 7
            max_chars_per_col = int(col_width * 0.6)
        else:
            font_size = 6
            max_chars_per_col = int(col_width * 0.7)
        
        # Ensure minimum column width
        min_col_width = 12
        if col_width < min_col_width:
            logger.warning(f"Table too wide ({num_cols} cols, {col_width:.1f}mm each), splitting into multiple tables")
            # Split table into chunks that fit
            chunk_size = max(1, int(effective_width / min_col_width))
            for i in range(0, num_cols, chunk_size):
                chunk_cells = cells[i:i + chunk_size]
                self._render_table_row(pdf, chunk_cells, is_header)
            return
        
        if is_header:
            pdf.set_font('Helvetica', 'B', font_size)
            pdf.set_fill_color(30, 64, 175)  # Blue header
            pdf.set_text_color(255, 255, 255)  # White text
        else:
            pdf.set_font('Helvetica', '', font_size)
            pdf.set_fill_color(255, 255, 255)  # White background
            pdf.set_text_color(0, 0, 0)  # Black text
        
        try:
            pdf.set_x(pdf.l_margin)  # Reset X position
            row_height = 6
            
            for i, cell in enumerate(cells):
                # Sanitize and intelligently truncate cell content
                display_text = self._sanitize_text(str(cell).strip())
                
                # Smart truncation - preserve important info
                if len(display_text) > max_chars_per_col:
                    # Try to truncate at word boundary
                    truncated = display_text[:max_chars_per_col-2]
                    last_space = truncated.rfind(' ')
                    if last_space > max_chars_per_col * 0.6:  # Only use word boundary if it's not too short
                        display_text = truncated[:last_space] + ".."
                    else:
                        display_text = truncated + ".."
                
                # Use multi_cell for text wrapping within cells
                x_position = pdf.get_x()
                y_position = pdf.get_y()
                
                # Draw cell with fill color
                pdf.cell(col_width, row_height, '', border=1, fill=True)
                pdf.set_xy(x_position, y_position)
                
                # Add text with proper clipping
                pdf.cell(col_width, row_height, display_text, border=1, align='L', fill=is_header)
            
            pdf.ln()
            
            # Reset colors
            pdf.set_fill_color(255, 255, 255)
            pdf.set_text_color(0, 0, 0)
            
        except Exception as e:
            logger.error(f"Error rendering table row: {e}")
            # Skip this row entirely
            try:
                pdf.ln(2)
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
    def _html_to_reportlab(self, html_content: str, story: list, styles):
        """Convert HTML content to ReportLab flowables."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_LEFT
        import html as html_lib
        from html.parser import HTMLParser
        
        class SimpleHTMLParser(HTMLParser):
            """Simple HTML parser for converting to ReportLab."""
            def __init__(self, story, styles):
                super().__init__()
                self.story = story
                self.styles = styles
                self.current_text = []
                self.in_table = False
                self.table_data = []
                self.current_row = []
                self.in_header = False
                self.list_items = []
                self.in_list = False
                
            def handle_starttag(self, tag, attrs):
                if tag in ['h1', 'h2', 'h3']:
                    self.flush_text()
                    self.in_header = tag
                elif tag == 'table':
                    self.flush_text()
                    self.in_table = True
                    self.table_data = []
                elif tag == 'tr':
                    self.current_row = []
                elif tag in ['th', 'td']:
                    pass  # Will collect text
                elif tag in ['ul', 'ol']:
                    self.flush_text()
                    self.in_list = True
                    self.list_items = []
                elif tag == 'li':
                    pass  # Will collect text
                elif tag == 'p':
                    self.flush_text()
                elif tag == 'br':
                    self.current_text.append('<br/>')
                elif tag == 'strong' or tag == 'b':
                    self.current_text.append('<b>')
                elif tag == 'em' or tag == 'i':
                    self.current_text.append('<i>')
                    
            def handle_endtag(self, tag):
                if tag in ['h1', 'h2', 'h3']:
                    text = ''.join(self.current_text)
                    if text.strip():
                        style_map = {'h1': 'Heading1', 'h2': 'Heading2', 'h3': 'Heading3'}
                        self.story.append(Paragraph(text, self.styles[style_map[tag]]))
                        self.story.append(Spacer(1, 12))
                    self.current_text = []
                    self.in_header = False
                elif tag == 'table':
                    if self.table_data:
                        # Calculate available width (A4 page with margins)
                        from reportlab.lib.pagesizes import A4
                        from reportlab.lib.units import inch
                        page_width = A4[0]
                        left_margin = 0.75 * inch
                        right_margin = 0.75 * inch
                        available_width = page_width - left_margin - right_margin
                        
                        # Calculate optimal column widths
                        num_cols = len(self.table_data[0]) if self.table_data else 0
                        if num_cols > 0:
                            # Wrap cell content in Paragraphs for proper text wrapping
                            wrapped_data = []
                            cell_style = ParagraphStyle('CellStyle', parent=self.styles['Normal'], fontSize=8, leading=10)
                            
                            for row_idx, row in enumerate(self.table_data):
                                wrapped_row = []
                                for cell in row:
                                    # Use smaller font for table cells
                                    if row_idx == 0:  # Header
                                        header_style = ParagraphStyle('HeaderStyle', parent=self.styles['Normal'], 
                                                                     fontSize=9, leading=11, textColor=colors.white)
                                        wrapped_row.append(Paragraph(str(cell), header_style))
                                    else:
                                        wrapped_row.append(Paragraph(str(cell), cell_style))
                                wrapped_data.append(wrapped_row)
                            
                            # Calculate column widths - distribute evenly but with smart adjustments
                            base_col_width = available_width / num_cols
                            col_widths = [base_col_width] * num_cols
                            
                            # Adjust for very wide tables - reduce font and padding
                            if num_cols > 6:
                                # For tables with many columns, use even smaller font
                                cell_style.fontSize = 7
                                cell_style.leading = 8
                            
                            # Create table with calculated widths
                            t = Table(wrapped_data, colWidths=col_widths, repeatRows=1)
                            
                            # Apply styles
                            table_style = [
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 9 if num_cols <= 6 else 7),
                                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                ('TOPPADDING', (0, 0), (-1, -1), 4),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 8 if num_cols <= 6 else 7),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                            ]
                            t.setStyle(TableStyle(table_style))
                            
                            self.story.append(t)
                            self.story.append(Spacer(1, 12))
                        else:
                            logger.warning("Empty table detected, skipping")
                    self.in_table = False
                    self.table_data = []
                elif tag == 'tr':
                    if self.current_row:
                        self.table_data.append(self.current_row)
                    self.current_row = []
                elif tag in ['th', 'td']:
                    text = ''.join(self.current_text).strip()
                    self.current_row.append(text)
                    self.current_text = []
                elif tag in ['ul', 'ol']:
                    # Add list items
                    for item in self.list_items:
                        self.story.append(Paragraph(f"• {item}", self.styles['Normal']))
                    self.story.append(Spacer(1, 6))
                    self.in_list = False
                    self.list_items = []
                elif tag == 'li':
                    text = ''.join(self.current_text).strip()
                    if text:
                        self.list_items.append(text)
                    self.current_text = []
                elif tag == 'p':
                    self.flush_text()
                elif tag == 'strong' or tag == 'b':
                    self.current_text.append('</b>')
                elif tag == 'em' or tag == 'i':
                    self.current_text.append('</i>')
                    
            def handle_data(self, data):
                if data.strip():
                    self.current_text.append(html_lib.escape(data))
                    
            def flush_text(self):
                text = ''.join(self.current_text).strip()
                if text and not self.in_table and not self.in_list and not self.in_header:
                    self.story.append(Paragraph(text, self.styles['Normal']))
                    self.story.append(Spacer(1, 6))
                self.current_text = []
        
        # Parse HTML
        parser = SimpleHTMLParser(story, styles)
        try:
            parser.feed(html_content)
            parser.flush_text()
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}")
            # Fallback: add as plain text
            plain_text = html_content.replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(plain_text, styles['Normal']))