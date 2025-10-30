# Linux Package Build Guide

**Package Name:** agentic_bookkeeper
**Version:** 0.1.0
**Author:** Stephen Bogner, P.Eng.
**Last Updated:** 2025-10-29

---

## Overview

This guide provides instructions for building and distributing Agentic Bookkeeper as a Linux package using Python's standard packaging tools (setuptools, pip, wheel).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Building Packages](#building-packages)
4. [Installation Methods](#installation-methods)
5. [Testing](#testing)
6. [Distribution](#distribution)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Operating System:** Ubuntu 20.04+, Debian 11+, or compatible Linux distribution
- **Python:** 3.8 or higher
- **pip:** 21.0 or higher (for proper dependency resolution)
- **System Tools:**
  - `python3-venv` (for virtual environment support)
  - `build-essential` (for compiling native dependencies)
  - `tesseract-ocr` (for OCR functionality)

### Install Prerequisites (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and build tools
sudo apt install -y python3 python3-pip python3-venv build-essential

# Install Tesseract OCR (required for document processing)
sudo apt install -y tesseract-ocr

# Install additional image processing libraries
sudo apt install -y libjpeg-dev zlib1g-dev
```text

### Install Prerequisites (CentOS/RHEL)

```bash
# Install Python and development tools
sudo yum install -y python3 python3-pip python3-devel gcc gcc-c++ make

# Install Tesseract OCR
sudo yum install -y tesseract

# Install image libraries
sudo yum install -y libjpeg-devel zlib-devel
```text

---

## Quick Start

### Automated Installation (Recommended)

The easiest way to install Agentic Bookkeeper is using the automated install script:

```bash
# Clone or extract the source code
cd agentic_bookkeeper_module/

# Run the installation script
./install.sh

# For development mode (includes dev dependencies and tests):
./install.sh --dev
```text

The script will:

1. Create a virtual environment
2. Install all dependencies
3. Set up application directories
4. Copy sample configuration
5. Test the installation

---

## Building Packages

### Build Source Distribution (sdist)

A source distribution contains all source files and can be installed on any platform:

```bash
# Ensure you have the latest build tools
pip install --upgrade build setuptools wheel

# Build source distribution
python -m build --sdist

# Output: dist/agentic_bookkeeper-0.1.0.tar.gz
```text

### Build Wheel Distribution (bdist_wheel)

A wheel is a built distribution that's faster to install:

```bash
# Build wheel
python -m build --wheel

# Output: dist/agentic_bookkeeper-0.1.0-py3-none-any.whl
```text

### Build Both Distributions

```bash
# Build both sdist and wheel
python -m build

# Output:
#   dist/agentic_bookkeeper-0.1.0.tar.gz
#   dist/agentic_bookkeeper-0.1.0-py3-none-any.whl
```text

### Using Legacy setup.py (Deprecated but Still Supported)

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Build both
python setup.py sdist bdist_wheel
```text

---

## Installation Methods

### Method 1: Install from Wheel (Recommended)

The wheel is the fastest installation method:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install from wheel
pip install dist/agentic_bookkeeper-0.1.0-py3-none-any.whl

# Verify installation
agentic_bookkeeper --version
```text

### Method 2: Install from Source Distribution

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install from source distribution
pip install dist/agentic_bookkeeper-0.1.0.tar.gz

# Verify installation
agentic_bookkeeper --version
```text

### Method 3: Install in Development Mode

For active development, install in editable mode:

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Verify installation
agentic_bookkeeper --version
```text

### Method 4: Install from PyPI (Future)

Once published to PyPI:

```bash
pip install agentic_bookkeeper
```text

---

## Testing

### Test Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test console script
agentic_bookkeeper --version
agentic_bookkeeper --help

# Test Python import
python3 -c "import agentic_bookkeeper; print('Import successful')"

# Run test suite
pytest

# Run with coverage
pytest --cov=agentic_bookkeeper --cov-report=html
```text

### Test Application Functionality

```bash
# Test GUI mode
agentic_bookkeeper

# Test CLI mode
agentic_bookkeeper --cli

# Process a sample document
agentic_bookkeeper --process samples/invoices/invoice_consulting.pdf
```text

### Verify Package Contents

```bash
# List files in wheel
unzip -l dist/agentic_bookkeeper-0.1.0-py3-none-any.whl

# List files in source distribution
tar -tzf dist/agentic_bookkeeper-0.1.0.tar.gz
```text

---

## Distribution

### Create Distribution Package

After building, create a distribution archive:

```bash
# Create distribution directory
mkdir -p agentic_bookkeeper_linux_dist

# Copy wheel and documentation
cp dist/agentic_bookkeeper-0.1.0-py3-none-any.whl agentic_bookkeeper_linux_dist/
cp README.md agentic_bookkeeper_linux_dist/
cp LICENSE agentic_bookkeeper_linux_dist/
cp install.sh agentic_bookkeeper_linux_dist/
cp -r docs/ agentic_bookkeeper_linux_dist/
cp -r samples/ agentic_bookkeeper_linux_dist/

# Create tarball for distribution
tar -czf agentic_bookkeeper_0.1.0_linux.tar.gz agentic_bookkeeper_linux_dist/

# Distribution package: agentic_bookkeeper_0.1.0_linux.tar.gz
```text

### Distribution Checklist

- [ ] Package builds without errors
- [ ] All tests pass
- [ ] Documentation is up-to-date
- [ ] LICENSE file is included
- [ ] README.md has installation instructions
- [ ] Sample documents are included
- [ ] install.sh script is executable
- [ ] Version numbers are correct in all files

### End-User Installation (from Distribution)

Users receiving the distribution package can install with:

```bash
# Extract distribution
tar -xzf agentic_bookkeeper_0.1.0_linux.tar.gz
cd agentic_bookkeeper_linux_dist/

# Run automated installer
./install.sh
```text

---

## Troubleshooting

### Build Issues

#### Issue: "ModuleNotFoundError: No module named 'setuptools'"

```bash
# Solution: Upgrade pip and install setuptools
pip install --upgrade pip setuptools wheel
```text

#### Issue: "error: invalid command 'bdist_wheel'"

```bash
# Solution: Install wheel package
pip install wheel
```text

#### Issue: Build fails with "gcc: command not found"

```bash
# Solution: Install build tools
sudo apt install build-essential  # Ubuntu/Debian
sudo yum install gcc gcc-c++       # CentOS/RHEL
```text

### Installation Issues

#### Issue: "No matching distribution found for PySide6>=6.6.0"

```bash
# Solution: Ensure pip is updated
pip install --upgrade pip

# Or use a different index
pip install --index-url https://pypi.org/simple/ PySide6
```text

#### Issue: "pytesseract.pytesseract.TesseractNotFoundError"

```bash
# Solution: Install Tesseract OCR
sudo apt install tesseract-ocr  # Ubuntu/Debian
sudo yum install tesseract       # CentOS/RHEL

# Verify installation
tesseract --version
```text

#### Issue: "ImportError: libGL.so.1: cannot open shared object file"

This is a common issue with PySide6 on headless servers.

```bash
# Solution: Install OpenGL libraries
sudo apt install -y libgl1-mesa-glx libglib2.0-0  # Ubuntu/Debian
sudo yum install -y mesa-libGL                     # CentOS/RHEL
```text

### Runtime Issues

#### Issue: "No such file or directory: ~/.config/agentic_bookkeeper/.env"

```bash
# Solution: Copy sample configuration
mkdir -p ~/.config/agentic_bookkeeper
cp samples/config/.env.sample ~/.config/agentic_bookkeeper/.env

# Edit and add your API keys
nano ~/.config/agentic_bookkeeper/.env
```text

#### Issue: "Permission denied" when running install.sh

```bash
# Solution: Make script executable
chmod +x install.sh
./install.sh
```text

### Testing Issues

#### Issue: Tests fail with "No module named 'pytest'"

```bash
# Solution: Install development dependencies
pip install -r requirements-dev.txt
```text

#### Issue: Import errors during tests

```bash
# Solution: Install package in development mode
pip install -e .
```text

---

## Advanced Topics

### Creating a DEB Package

For Debian/Ubuntu users, you can create a .deb package:

```bash
# Install dh-virtualenv
sudo apt install dh-virtualenv

# Create debian/ directory structure
mkdir -p debian
# (Additional configuration required - see dh-virtualenv documentation)
```text

### Creating an RPM Package

For RedHat/CentOS users, you can create a .rpm package:

```bash
# Install rpmbuild tools
sudo yum install rpm-build

# Create RPM spec file
# (Additional configuration required - see RPM packaging documentation)
```text

### Publishing to PyPI

To publish the package to Python Package Index (PyPI):

```bash
# Install twine
pip install twine

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Upload to production PyPI
twine upload dist/*
```text

**Note:** Publishing to PyPI requires an account and proper package configuration.

---

## File Structure

### Package Contents

text
agentic_bookkeeper_module/
├── setup.py                    # Package configuration
├── pyproject.toml             # Build system configuration
├── MANIFEST.in                # Files to include in distribution
├── install.sh                 # Linux installation script
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── README.md                  # Project documentation
├── LICENSE                    # License file
├── src/
│   └── agentic_bookkeeper/   # Source code
├── docs/                      # Documentation
├── samples/                   # Sample documents
└── dist/                      # Built distributions (created by build)
```text

---

## Maintenance

### Updating Dependencies

```bash
# Update requirements.txt
pip install pip-tools
pip-compile requirements.txt

# Update development dependencies
pip-compile requirements-dev.txt
```text

### Version Management

1. Update version in `setup.py`
2. Update version in `pyproject.toml`
3. Update version in `src/agentic_bookkeeper/__init__.py`
4. Update CHANGELOG.md
5. Create git tag: `git tag v0.1.0`
6. Rebuild packages

---

## Support

For issues, questions, or contributions:

- **Documentation:** docs/USER_GUIDE.md, docs/DEVELOPMENT.md
- **Issues:** (GitHub Issues URL when available)
- **Email:** stephenbogner@stephenbogner.com

---

## Additional Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [pip Documentation](https://pip.pypa.io/)
- [PEP 517: Build System Interface](https://peps.python.org/pep-0517/)
- [PEP 518: pyproject.toml](https://peps.python.org/pep-0518/)

---

**Last Updated:** 2025-10-29
**Version:** 1.0.0
