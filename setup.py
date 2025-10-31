"""
Package Name: agentic_bookkeeper
File Name: setup.py
Description: Package configuration and installation script
Author: Stephen Bogner, P.Eng.
LLM: claude-sonnet-4-5-20250929
Ownership: Stephen Bogner - All Rights Reserved.  See LICENSE
Date Created: 2025-10-24
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agentic_bookkeeper",
    version="0.2.0",
    author="Stephen Bogner, P.Eng.",
    author_email="stephenbogner@stephenbogner.com",
    description="An intelligent bookkeeping automation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StephenBogner/agentic_bookkeeper",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    license="Proprietary",
    python_requires=">=3.8",
    install_requires=[
        # Core GUI Framework
        "PySide6>=6.6.0",
        # File System Monitoring
        "watchdog>=3.0.0",
        # Configuration Management
        "python-dotenv>=1.0.0",
        # Document Processing
        "pypdf>=3.0.0",
        "Pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "pymupdf>=1.23.0",
        # LLM API Providers
        "requests>=2.31.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "google-generativeai>=0.3.0",
        # Report Generation
        "reportlab>=4.0.0",
        "pandas>=2.0.0",
        # Security (API key encryption)
        "cryptography>=41.0.0",
    ],
    package_data={
        "agentic_bookkeeper": ["py.typed"],
    },
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "agentic_bookkeeper=agentic_bookkeeper.main:main",
        ],
    },
)
