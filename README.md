# agentic_bookkeeper

An intelligent bookkeeping automation system.

## Description

agentic_bookkeeper is a Python package designed to automate bookkeeping tasks using intelligent agents.

## Installation

```bash
# Clone the repository
git clone https://github.com/StephenBogner/agentic_bookkeeper.git
cd agentic_bookkeeper

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements-dev.txt
```

## Usage

```bash
# Run the application
python src/agentic_bookkeeper/main.py

# Or use the installed console script
agentic_bookkeeper
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest -v --cov=agentic_bookkeeper

# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
agentic_bookkeeper/
├── src/
│   └── agentic_bookkeeper/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── docs/
│   └── README.md
├── specs/
├── requirements.txt
├── requirements-dev.txt
├── setup.py
└── README.md
```

## License

Proprietary - All Rights Reserved. See LICENSE.md for details.

## Author

Stephen Bogner, P.Eng.
