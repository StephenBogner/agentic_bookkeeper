#!/bin/bash

# Package Name: agentic_bookkeeper
# File Name: install.sh
# Description: Linux installation script for Agentic Bookkeeper
# Author: Stephen Bogner, P.Eng.
# Created: 2025-10-29
# Usage: ./install.sh [--dev]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PYTHON_MIN_VERSION="3.8"
VENV_DIR="venv"
APP_NAME="agentic_bookkeeper"
CONFIG_DIR="$HOME/.config/$APP_NAME"
DATA_DIR="$HOME/.local/share/$APP_NAME"
LOG_DIR="$HOME/.local/share/$APP_NAME/logs"

# Functions
print_header() {
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Agentic Bookkeeper Installer${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "  $1"
}

check_python_version() {
    print_info "Checking Python version..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

    if [ "$(printf '%s\n' "$PYTHON_MIN_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$PYTHON_MIN_VERSION" ]; then
        print_error "Python $PYTHON_MIN_VERSION or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi

    print_success "Python $PYTHON_VERSION detected"
}

check_system_dependencies() {
    print_info "Checking system dependencies..."

    # Check for tesseract-ocr (required by pytesseract)
    if ! command -v tesseract &> /dev/null; then
        print_warning "Tesseract OCR is not installed."
        print_info "  Install it with: sudo apt-get install tesseract-ocr (Ubuntu/Debian)"
        print_info "                  or: sudo yum install tesseract (CentOS/RHEL)"
        print_info "  OCR functionality will not work without it."
    else
        print_success "Tesseract OCR detected"
    fi
}

create_virtual_environment() {
    print_info "Creating virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to remove it and create a fresh one? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi

    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
}

install_dependencies() {
    print_info "Installing dependencies..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    print_info "  Upgrading pip..."
    pip install --upgrade pip > /dev/null 2>&1

    # Install wheel for faster builds
    print_info "  Installing wheel..."
    pip install wheel > /dev/null 2>&1

    # Install production dependencies
    print_info "  Installing production dependencies..."
    pip install -r requirements.txt

    # Install development dependencies if --dev flag is present
    if [ "$1" == "--dev" ]; then
        print_info "  Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi

    # Install the package in editable mode
    print_info "  Installing $APP_NAME in editable mode..."
    pip install -e .

    print_success "Dependencies installed successfully"
}

create_directories() {
    print_info "Creating application directories..."

    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"

    print_success "Application directories created:"
    print_info "  Config: $CONFIG_DIR"
    print_info "  Data:   $DATA_DIR"
    print_info "  Logs:   $LOG_DIR"
}

setup_configuration() {
    print_info "Setting up configuration..."

    # Copy sample .env if it doesn't exist
    if [ ! -f "$CONFIG_DIR/.env" ]; then
        if [ -f "samples/config/.env.sample" ]; then
            cp "samples/config/.env.sample" "$CONFIG_DIR/.env"
            print_success "Configuration template copied to $CONFIG_DIR/.env"
            print_warning "Please edit $CONFIG_DIR/.env and add your API keys"
        else
            print_warning "Sample configuration not found. You'll need to create .env manually."
        fi
    else
        print_info "Configuration file already exists at $CONFIG_DIR/.env"
    fi
}

copy_sample_documents() {
    print_info "Copying sample documents..."

    if [ -d "samples" ]; then
        SAMPLES_DIR="$DATA_DIR/samples"
        mkdir -p "$SAMPLES_DIR"

        if [ -d "samples/invoices" ]; then
            cp -r samples/invoices "$SAMPLES_DIR/"
            print_success "Sample invoices copied"
        fi

        if [ -d "samples/receipts" ]; then
            cp -r samples/receipts "$SAMPLES_DIR/"
            print_success "Sample receipts copied"
        fi

        if [ -f "samples/README.md" ]; then
            cp samples/README.md "$SAMPLES_DIR/"
        fi

        print_info "  Samples location: $SAMPLES_DIR"
    else
        print_warning "Sample documents not found"
    fi
}

test_installation() {
    print_info "Testing installation..."

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Test console script
    if command -v $APP_NAME &> /dev/null; then
        VERSION=$($APP_NAME --version 2>&1 || echo "unknown")
        print_success "Console script '$APP_NAME' is available"
        print_info "  Version: $VERSION"
    else
        print_error "Console script '$APP_NAME' not found"
        print_info "  You may need to activate the virtual environment first:"
        print_info "  source $VENV_DIR/bin/activate"
        return 1
    fi

    # Test Python import
    if python3 -c "import agentic_bookkeeper" 2>/dev/null; then
        print_success "Python package imports successfully"
    else
        print_error "Python package import failed"
        return 1
    fi

    print_success "Installation test passed"
}

print_next_steps() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    print_info "Next steps:"
    echo ""
    print_info "1. Activate the virtual environment:"
    print_info "   source $VENV_DIR/bin/activate"
    echo ""
    print_info "2. Configure your API keys:"
    print_info "   Edit $CONFIG_DIR/.env"
    print_info "   Add your OpenAI, Anthropic, XAI, or Google API key"
    echo ""
    print_info "3. Run the application:"
    print_info "   $APP_NAME                  # GUI mode (recommended)"
    print_info "   $APP_NAME --cli            # CLI mode"
    print_info "   $APP_NAME --help           # Show help"
    echo ""
    print_info "4. Try the sample documents:"
    print_info "   $DATA_DIR/samples/"
    echo ""
    print_info "Documentation:"
    print_info "  User Guide:     docs/USER_GUIDE.md"
    print_info "  Developer Docs: docs/DEVELOPMENT.md"
    echo ""
}

# Main installation flow
main() {
    print_header

    # Check if --dev flag is present
    DEV_MODE=""
    if [ "$1" == "--dev" ]; then
        DEV_MODE="--dev"
        print_info "Installing in development mode..."
        echo ""
    fi

    check_python_version
    check_system_dependencies
    echo ""

    create_virtual_environment
    echo ""

    install_dependencies "$DEV_MODE"
    echo ""

    create_directories
    echo ""

    setup_configuration
    echo ""

    copy_sample_documents
    echo ""

    test_installation

    print_next_steps
}

# Run main installation
main "$@"
