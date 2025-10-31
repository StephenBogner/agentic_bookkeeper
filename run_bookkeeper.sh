#!/bin/bash
# Agentic Bookkeeper Launcher Script (Linux/Mac)
# This script starts the Agentic Bookkeeper application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Agentic Bookkeeper Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found!${NC}"
    echo -e "${YELLOW}Please run the installation script first:${NC}"
    echo -e "  ${GREEN}./install.sh${NC}"
    echo ""
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if agentic_bookkeeper is installed
if ! python -c "import agentic_bookkeeper" 2>/dev/null; then
    echo -e "${RED}Error: Agentic Bookkeeper package not installed!${NC}"
    echo -e "${YELLOW}Please run the installation script:${NC}"
    echo -e "  ${GREEN}./install.sh${NC}"
    echo ""
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "${YELLOW}The application will start, but you'll need to configure API keys.${NC}"
    echo -e "${YELLOW}See docs/user/ENV_SETUP_GUIDE.md for details.${NC}"
    echo ""
fi

# Display startup information
echo -e "${GREEN}Starting Agentic Bookkeeper...${NC}"
echo ""
echo -e "${BLUE}Application Mode:${NC} GUI"
echo -e "${BLUE}Python Version:${NC} $(python --version 2>&1)"
echo -e "${BLUE}Working Directory:${NC} $SCRIPT_DIR"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo ""

# Start the application
python src/agentic_bookkeeper/main.py

# Cleanup message
echo ""
echo -e "${GREEN}Application closed successfully.${NC}"
