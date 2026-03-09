"""Core report generation service with multi-format support."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from egile_mcp_reporter.pdf_generator import PDFGenerator
from egile_mcp_reporter.pptx_generator import PPTXGenerator
from egile_mcp_reporter.html_generator import HTMLGenerator
from egile_mcp_reporter.chart_service import ChartService

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating reports in multiple formats."""

    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report service.

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.pdf_generator = PDFGenerator()
        self.pptx_generator = PPTXGenerator()
        self.html_generator = HTMLGenerator()
        self.chart_service = ChartService()

        logger.info(f"Report service initialized with output dir: {self.output_dir}")

    def create_report(
        self,
        title: str,
        sections: List[Dict[str, Any]],
        format: str = "pdf",
        output_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a complete report from structured data.

        Args:
            title: Report title
            sections: List of section dictionaries
            format: Output format (pdf, pptx, html, markdown)
            output_path: Custom output path
            **kwargs: Additional format-specific options

        Returns:
            Dictionary with report metadata
        """
        format = format.lower()

        if not output_path:
            timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = title.replace(" ", "_").lower()
            ext = "pptx" if format == "pptx" else format
            output_path = str(self.output_dir / f"{safe_title}_{timestamp}.{ext}")

        # Handle path resolution: if path starts with / or \, treat as relative to output_dir
        output_path = Path(output_path)
        if not output_path.is_absolute() or str(output_path).startswith(('/', '\\')):
            # Remove leading slash/backslash and make relative to output_dir
            path_str = str(output_path).lstrip('/\\')
            output_path = self.output_dir / path_str

        try:
            if format == "pdf":
                result = self.pdf_generator.create_report(title, sections, output_path, **kwargs)
            elif format == "pptx":
                result = self.pptx_generator.create_report(title, sections, output_path, **kwargs)
            elif format == "html":
                result = self.html_generator.create_report(title, sections, output_path, **kwargs)
            elif format == "markdown":
                result = self._create_markdown_report(title, sections, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Created {format.upper()} report: {output_path}")
            return result

        except Exception as e:
            logger.error(f"Error creating {format} report: {e}")
            raise

    def markdown_to_pdf(
        self,
        markdown: str,
        output_path: str,
        title: Optional[str] = None,
        styles: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Convert markdown content to PDF.

        Args:
            markdown: Markdown content
            output_path: Output PDF path
            title: Document title
            styles: Optional CSS overrides

        Returns:
            Dictionary with file metadata
        """
        return self.pdf_generator.from_markdown(markdown, output_path, title, styles)

    def markdown_to_pptx(
        self, markdown: str, output_path: str, title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert markdown to PowerPoint presentation.

        Args:
            markdown: Markdown content (## for new slides)
            output_path: Output PPTX path
            title: Presentation title

        Returns:
            Dictionary with file metadata
        """
        return self.pptx_generator.from_markdown(markdown, output_path, title)

    def create_data_visualization(
        self,
        data: Dict[str, Any],
        chart_type: str,
        output_path: str,
        title: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate standalone chart/graph.

        Args:
            data: Chart data
            chart_type: Type of chart (bar, line, pie, scatter, etc.)
            output_path: Output path for chart image
            title: Chart title
            **kwargs: Additional chart options

        Returns:
            Dictionary with chart metadata
        """
        return self.chart_service.create_chart(data, chart_type, output_path, title, **kwargs)

    def _create_markdown_report(
        self, title: str, sections: List[Dict[str, Any]], output_path: Path
    ) -> Dict[str, Any]:
        """Create a markdown report."""
        import datetime

        content = f"# {title}\n\n"
        content += f"*Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}*\n\n"
        content += "---\n\n"

        for section in sections:
            section_title = section.get("title", "")
            section_type = section.get("type", "text")

            if section_title:
                content += f"## {section_title}\n\n"

            if section_type == "text":
                content += f"{section.get('content', '')}\n\n"

            elif section_type == "table":
                data = section.get("data", [])
                if data:
                    # Create markdown table
                    columns = section.get("columns") or list(data[0].keys())
                    content += "| " + " | ".join(columns) + " |\n"
                    content += "| " + " | ".join(["---"] * len(columns)) + " |\n"
                    for row in data:
                        values = [str(row.get(col, "")) for col in columns]
                        content += "| " + " | ".join(values) + " |\n"
                    content += "\n"

            elif section_type == "list":
                items = section.get("items", [])
                for item in items:
                    content += f"- {item}\n"
                content += "\n"

        output_path.write_text(content, encoding="utf-8")

        return {
            "status": "success",
            "format": "markdown",
            "output_path": str(output_path),
            "size": output_path.stat().st_size,
        }
