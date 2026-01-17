# Egile MCP Reporter

MCP server for generating professional reports in multiple formats with data visualization support.

## Features

- **Multiple Output Formats**:
  - **PDF**: High-quality PDF reports via WeasyPrint (HTML→PDF with CSS)
  - **PowerPoint**: Professional presentations with python-pptx
  - **HTML**: Interactive reports with charts and styling
  - **Markdown**: Clean formatted markdown documents

- **Data Visualization**:
  - Tables with sorting and styling
  - Charts and graphs (bar, line, pie, scatter)
  - Interactive plots via Plotly
  - Support for pandas DataFrames

- **Professional Styling**:
  - Pre-built report templates
  - Custom CSS for HTML/PDF
  - PowerPoint themes and layouts
  - Responsive HTML design

- **Flexible Content**:
  - Markdown input with automatic conversion
  - Structured data (JSON, dicts, DataFrames)
  - Images and media embedding
  - Multi-section reports

## Installation

### Quick Install (Recommended)

**Windows**:
```bash
.\install.bat
```

**Linux/Mac**:
```bash
chmod +x install.sh
./install.sh
```

### Manual Install

```bash
# Install from source
pip install -e .
```

### Development Install

```bash
# Install with dev dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file based on `.env.example`:

```bash
# Output configuration
DEFAULT_FORMAT=pdf
OUTPUT_DIR=./reports

# PDF settings
PDF_PAGE_SIZE=A4
PDF_MARGINS=20mm

# PowerPoint settings
PPTX_THEME=default
PPTX_SLIDE_WIDTH=10
PPTX_SLIDE_HEIGHT=7.5

# Chart settings
CHART_THEME=plotly_white
CHART_DPI=300
```

## Usage

### As MCP Server

The server exposes the following tools:

#### 1. `create_report`
Generate a complete report from structured data.

```python
{
    "title": "Q4 Investment Report",
    "format": "pdf",  # pdf, pptx, html, markdown
    "sections": [
        {
            "title": "Portfolio Summary",
            "type": "text",
            "content": "Portfolio performance overview..."
        },
        {
            "title": "Holdings",
            "type": "table",
            "data": [...],  # List of dicts or DataFrame
            "columns": ["Ticker", "Shares", "Value", "P/L"]
        },
        {
            "title": "Performance Chart",
            "type": "chart",
            "chart_type": "bar",
            "data": {...}
        }
    ],
    "output_path": "reports/investment_report.pdf"
}
```

#### 2. `markdown_to_pdf`
Convert markdown content to PDF.

```python
{
    "markdown": "# Report Title\n\nContent...",
    "output_path": "report.pdf",
    "title": "My Report",
    "styles": {...}  # Optional CSS overrides
}
```

#### 3. `markdown_to_pptx`
Convert markdown to PowerPoint presentation.

```python
{
    "markdown": "# Slide 1\n\nContent...\n\n## Slide 2\n\nMore content...",
    "output_path": "presentation.pptx",
    "title": "My Presentation"
}
```

#### 4. `create_data_visualization`
Generate standalone chart/graph.

```python
{
    "data": {"labels": [...], "values": [...]},
    "chart_type": "bar",  # bar, line, pie, scatter, etc.
    "output_path": "chart.png",
    "title": "Performance Chart"
}
```

#### 5. `combine_reports`
Merge multiple reports into one.

```python
{
    "reports": ["report1.pdf", "report2.pdf"],
    "output_path": "combined.pdf",
    "format": "pdf"
}
```

### Programmatic Usage

```python
from egile_mcp_reporter.server import mcp

# Run via FastMCP
mcp.run(transport="stdio")
```

### Direct Service Usage

```python
from egile_mcp_reporter.report_service import ReportService

service = ReportService()

# Create PDF report
report = service.create_pdf_report(
    title="Investment Report",
    sections=[
        {"type": "text", "content": "Overview..."},
        {"type": "table", "data": holdings_data}
    ],
    output_path="report.pdf"
)

# Create PowerPoint
presentation = service.create_pptx_report(
    title="Quarterly Review",
    sections=sections,
    output_path="presentation.pptx"
)

# Generate chart
chart = service.create_chart(
    data={"x": [1, 2, 3], "y": [10, 20, 15]},
    chart_type="line",
    output_path="chart.png"
)
```

## Report Templates

### Investment Report Template
```python
{
    "template": "investment",
    "data": {
        "portfolio_summary": {...},
        "holdings": [...],
        "recommendations": [...]
    }
}
```

### Business Report Template
```python
{
    "template": "business",
    "data": {
        "executive_summary": "...",
        "metrics": {...},
        "insights": [...]
    }
}
```

## MCP Integration

Add to your MCP client config:

```json
{
  "mcpServers": {
    "reporter": {
      "command": "python",
      "args": ["-m", "egile_mcp_reporter.server"]
    }
  }
}
```

## Examples

See `tests/` directory for comprehensive examples:
- `test_pdf_generation.py` - PDF report examples
- `test_pptx_generation.py` - PowerPoint examples
- `test_chart_generation.py` - Data visualization
- `test_templates.py` - Using pre-built templates

## Architecture

```
egile-mcp-reporter/
├── src/egile_mcp_reporter/
│   ├── server.py           # FastMCP server
│   ├── report_service.py   # Core report generation
│   ├── pdf_generator.py    # PDF creation (WeasyPrint)
│   ├── pptx_generator.py   # PowerPoint creation
│   ├── html_generator.py   # HTML reports
│   ├── chart_service.py    # Data visualization
│   ├── templates/          # Report templates
│   │   ├── pdf/
│   │   ├── pptx/
│   │   └── html/
│   └── utils/
│       ├── markdown.py     # Markdown processing
│       └── styling.py      # CSS/theme management
└── tests/
```

## License

MIT License - see LICENSE file for details.
