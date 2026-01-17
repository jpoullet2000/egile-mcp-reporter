"""Chart and data visualization service using Plotly."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ChartService:
    """Service for creating data visualizations."""

    def __init__(self):
        """Initialize chart service."""
        pass

    def create_chart(
        self,
        data: Dict[str, Any],
        chart_type: str,
        output_path: str,
        title: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a chart/graph visualization.

        Args:
            data: Chart data
            chart_type: Type of chart (bar, line, pie, scatter, etc.)
            output_path: Output path for chart image
            title: Chart title
            **kwargs: Additional chart options

        Returns:
            Dictionary with chart metadata
        """
        import plotly.graph_objects as go
        import plotly.io as pio

        chart_type = chart_type.lower()

        if chart_type == "bar":
            fig = self._create_bar_chart(data, title, **kwargs)
        elif chart_type == "line":
            fig = self._create_line_chart(data, title, **kwargs)
        elif chart_type == "pie":
            fig = self._create_pie_chart(data, title, **kwargs)
        elif chart_type == "scatter":
            fig = self._create_scatter_chart(data, title, **kwargs)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")

        # Save chart
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        pio.write_image(fig, str(output_path), width=kwargs.get("width", 800), height=kwargs.get("height", 600))

        return {
            "status": "success",
            "chart_type": chart_type,
            "output_path": str(output_path),
            "size": output_path.stat().st_size,
        }

    def _create_bar_chart(self, data: Dict[str, Any], title: Optional[str], **kwargs) -> Any:
        """Create a bar chart."""
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[go.Bar(x=data.get("x", data.get("labels", [])), y=data.get("y", data.get("values", [])))]
        )

        fig.update_layout(
            title=title or "Bar Chart",
            xaxis_title=kwargs.get("xlabel", "X Axis"),
            yaxis_title=kwargs.get("ylabel", "Y Axis"),
            template="plotly_white",
        )

        return fig

    def _create_line_chart(self, data: Dict[str, Any], title: Optional[str], **kwargs) -> Any:
        """Create a line chart."""
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[go.Scatter(x=data.get("x", []), y=data.get("y", []), mode="lines+markers")]
        )

        fig.update_layout(
            title=title or "Line Chart",
            xaxis_title=kwargs.get("xlabel", "X Axis"),
            yaxis_title=kwargs.get("ylabel", "Y Axis"),
            template="plotly_white",
        )

        return fig

    def _create_pie_chart(self, data: Dict[str, Any], title: Optional[str], **kwargs) -> Any:
        """Create a pie chart."""
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[go.Pie(labels=data.get("labels", []), values=data.get("values", []))]
        )

        fig.update_layout(title=title or "Pie Chart")

        return fig

    def _create_scatter_chart(self, data: Dict[str, Any], title: Optional[str], **kwargs) -> Any:
        """Create a scatter plot."""
        import plotly.graph_objects as go

        fig = go.Figure(
            data=[go.Scatter(x=data.get("x", []), y=data.get("y", []), mode="markers")]
        )

        fig.update_layout(
            title=title or "Scatter Plot",
            xaxis_title=kwargs.get("xlabel", "X Axis"),
            yaxis_title=kwargs.get("ylabel", "Y Axis"),
            template="plotly_white",
        )

        return fig
