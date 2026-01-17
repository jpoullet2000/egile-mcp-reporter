"""Example: Create a professional investment report using the reporter."""

import asyncio
from pathlib import Path

from egile_mcp_reporter.report_service import ReportService


async def main():
    """Generate sample investment report in multiple formats."""
    
    # Initialize report service
    service = ReportService(output_dir="reports")
    
    # Sample portfolio data
    portfolio_data = {
        "summary": {
            "total_value": 125000.00,
            "total_cost": 100000.00,
            "profit_loss": 25000.00,
            "profit_loss_pct": 25.0,
        },
        "holdings": [
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "shares": 100,
                "purchase_price": 150.00,
                "current_price": 180.00,
                "current_value": 18000.00,
                "profit_loss": 3000.00,
                "profit_loss_pct": 20.0,
            },
            {
                "ticker": "MSFT",
                "company_name": "Microsoft Corporation",
                "shares": 50,
                "purchase_price": 300.00,
                "current_price": 350.00,
                "current_value": 17500.00,
                "profit_loss": 2500.00,
                "profit_loss_pct": 16.67,
            },
        ],
        "sell_recommendations": [
            {
                "ticker": "XYZ",
                "recommendation": "SELL",
                "sell_score": 7,
                "reasons": [
                    "Significant loss of -25%",
                    "Poor recent performance",
                    "High volatility",
                ],
            }
        ],
    }
    
    # Build report sections
    sections = []
    
    # Summary
    summary = portfolio_data["summary"]
    summary_text = f"""
**Portfolio Value:** ${summary['total_value']:,.2f}  
**Total Cost:** ${summary['total_cost']:,.2f}  
**Profit/Loss:** ${summary['profit_loss']:,.2f} ({summary['profit_loss_pct']:+.2f}%)

This report provides a comprehensive analysis of your investment portfolio as of today.
    """
    sections.append({
        "type": "text",
        "title": "Executive Summary",
        "content": summary_text.strip(),
    })
    
    # Holdings table
    sections.append({
        "type": "table",
        "title": "Portfolio Holdings",
        "data": portfolio_data["holdings"],
        "columns": [
            "ticker",
            "company_name",
            "shares",
            "current_price",
            "current_value",
            "profit_loss",
            "profit_loss_pct",
        ],
    })
    
    # Sell recommendations
    if portfolio_data["sell_recommendations"]:
        sell_text = "\n\n".join([
            f"**{rec['ticker']}** - {rec['recommendation']} (Score: {rec['sell_score']}/10)\n\n" +
            "\n".join([f"• {reason}" for reason in rec['reasons']])
            for rec in portfolio_data["sell_recommendations"]
        ])
        sections.append({
            "type": "text",
            "title": "⚠️ Sell Recommendations",
            "content": sell_text,
        })
    
    # Create reports in different formats
    print("\n" + "=" * 60)
    print("Creating Investment Portfolio Reports")
    print("=" * 60 + "\n")
    
    # PDF Report
    print("1. Creating PDF report...")
    pdf_result = service.create_report(
        title="Investment Portfolio Report",
        sections=sections,
        format="pdf",
    )
    print(f"   ✓ PDF created: {pdf_result['output_path']}")
    print(f"     Size: {pdf_result['size']:,} bytes\n")
    
    # PowerPoint Report
    print("2. Creating PowerPoint report...")
    pptx_result = service.create_report(
        title="Investment Portfolio Report",
        sections=sections,
        format="pptx",
    )
    print(f"   ✓ PowerPoint created: {pptx_result['output_path']}")
    print(f"     Slides: {pptx_result.get('slides', 'N/A')}\n")
    
    # HTML Report
    print("3. Creating HTML report...")
    html_result = service.create_report(
        title="Investment Portfolio Report",
        sections=sections,
        format="html",
    )
    print(f"   ✓ HTML created: {html_result['output_path']}")
    print(f"     Size: {html_result['size']:,} bytes\n")
    
    # Markdown Report
    print("4. Creating Markdown report...")
    md_result = service.create_report(
        title="Investment Portfolio Report",
        sections=sections,
        format="markdown",
    )
    print(f"   ✓ Markdown created: {md_result['output_path']}")
    print(f"     Size: {md_result['size']:,} bytes\n")
    
    print("=" * 60)
    print("All reports created successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
