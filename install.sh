#!/bin/bash
# Installation script for Egile MCP Reporter (Linux/Mac)

echo "========================================"
echo "Egile MCP Reporter - Installation"
echo "========================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Installing egile-mcp-reporter..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install egile-mcp-reporter"
    exit 1
fi

echo
echo "========================================"
echo "Additional Dependencies"
echo "========================================"
echo
echo "For PDF generation, you need WeasyPrint dependencies."
echo
echo "On Ubuntu/Debian:"
echo "  sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0"
echo
echo "On macOS:"
echo "  brew install pango"
echo
echo "For chart generation, install kaleido:"
echo "  pip install kaleido"
echo

echo
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo
echo "To test the installation:"
echo "  python example.py"
echo
echo "This will create sample reports in the 'reports' directory."
echo
