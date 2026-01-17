"""FastMCP server for report generation."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from egile_mcp_reporter.report_service import ReportService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("egile-reporter", dependencies=["weasyprint", "python-pptx", "plotly"])

# Initialize services
output_dir = os.getenv("OUTPUT_DIR", "reports")
report_service = ReportService(output_dir=output_dir)


@mcp.tool()
def create_report(
    title: str,
    sections: List[Dict[str, Any]],
    format: str = "pdf",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a comprehensive report from structured data.

    Args:
        title: Report title
        sections: List of sections with type, title, content/data
        format: Output format (pdf, pptx, html, markdown)
        output_path: Optional custom output path

    Returns:
        Dictionary with report metadata and file path

    Example sections:
        [
            {"type": "text", "title": "Overview", "content": "Summary text..."},
            {"type": "table", "title": "Data", "data": [...], "columns": [...]},
            {"type": "list", "title": "Points", "items": ["Item 1", "Item 2"]},
            {"type": "chart", "title": "Graph", "chart_type": "bar", "data": {...}}
        ]
    """
    logger.info(f"Creating {format} report: {title}")
    
    try:
        result = report_service.create_report(
            title=title,
            sections=sections,
            format=format,
            output_path=output_path,
        )
        logger.info(f"Report created successfully: {result['output_path']}")
        return result
    except Exception as e:
        logger.error(f"Error creating report: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def markdown_to_pdf(
    markdown: str,
    output_path: str,
    title: Optional[str] = None,
    styles: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Convert markdown content to a styled PDF document.

    Args:
        markdown: Markdown formatted text
        output_path: Path for output PDF file
        title: Optional document title
        styles: Optional CSS style overrides

    Returns:
        Dictionary with file metadata

    Example:
        markdown_to_pdf(
            markdown="# Report\\n\\nContent here...",
            output_path="report.pdf",
            title="My Report"
        )
    """
    logger.info(f"Converting markdown to PDF: {output_path}")
    
    try:
        result = report_service.markdown_to_pdf(
            markdown=markdown,
            output_path=output_path,
            title=title,
            styles=styles,
        )
        return result
    except Exception as e:
        logger.error(f"Error converting markdown to PDF: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def markdown_to_pptx(
    markdown: str, output_path: str, title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert markdown to PowerPoint presentation.
    Use ## for new slides.

    Args:
        markdown: Markdown content (## headers create new slides)
        output_path: Path for output PPTX file
        title: Optional presentation title

    Returns:
        Dictionary with file metadata

    Example:
        markdown_to_pptx(
            markdown="# Title\\n\\n## Slide 1\\n\\nContent...\\n\\n## Slide 2\\n\\nMore...",
            output_path="presentation.pptx",
            title="My Presentation"
        )
    """
    logger.info(f"Converting markdown to PowerPoint: {output_path}")
    
    try:
        result = report_service.markdown_to_pptx(
            markdown=markdown, output_path=output_path, title=title
        )
        return result
    except Exception as e:
        logger.error(f"Error converting markdown to PPTX: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@mcp.tool()
def create_data_visualization(
    data: Dict[str, Any],
    chart_type: str,
    output_path: str,
    title: Optional[str] = None,
    width: int = 800,
    height: int = 600,
) -> Dict[str, Any]:
    """
    Generate a standalone chart/graph visualization.

    Args:
        data: Chart data (format depends on chart_type)
        chart_type: Type of chart (bar, line, pie, scatter)
        output_path: Path for output image file
        title: Optional chart title
        width: Chart width in pixels
        height: Chart height in pixels

    Returns:
        Dictionary with chart metadata

    Example for bar chart:
        create_data_visualization(
            data={"x": ["A", "B", "C"], "y": [10, 20, 15]},
            chart_type="bar",
            output_path="chart.png",
            title="Sales by Region"
        )

    Example for pie chart:
        create_data_visualization(
            data={"labels": ["Category A", "Category B"], "values": [30, 70]},
            chart_type="pie",
            output_path="pie.png"
        )
    """
    logger.info(f"Creating {chart_type} chart: {output_path}")
    
    try:
        result = report_service.create_data_visualization(
            data=data,
            chart_type=chart_type,
            output_path=output_path,
            title=title,
            width=width,
            height=height,
        )
        return result
    except Exception as e:
        logger.error(f"Error creating visualization: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


def main():
    """Run the MCP server."""
    logger.info("Starting Egile MCP Reporter server...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
