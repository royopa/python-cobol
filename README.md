# Python COBOL Copybook Parser

[![PyPI version](https://badge.fury.io/py/python-cobol.svg)](https://badge.fury.io/py/python-cobol)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-green.svg)](https://opensource.org/licenses/GPL-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A modern, well-structured Python library for parsing and processing COBOL Copybook files. This library provides comprehensive support for COBOL data structures including REDEFINES, INDEXED BY, and OCCURS clauses, with robust error handling and extensive test coverage.

## ✨ Features

- **Complete COBOL Support**: Parse REDEFINES, INDEXED BY, and OCCURS statements
- **Modern Python**: Type hints, dataclasses, and modern Python patterns
- **Comprehensive Testing**: Extensive test suite with high coverage
- **CLI Interface**: Command-line tool for processing COBOL files
- **Library API**: Easy-to-use Python API for integration
- **Database Ready**: Generate database-safe field names
- **Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling with informative messages

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install python-cobol

# Install for development
git clone https://github.com/rodrigo/python-cobol.git
cd python-cobol
pip install -e ".[dev]"
```

### Basic Usage

#### Command Line Interface

```bash
# Process a COBOL file with all features enabled
python-cobol example.cbl

# Skip denormalization
python-cobol example.cbl --skip-denormalize

# Enable verbose logging
python-cobol example.cbl --verbose

# See all options
python-cobol --help
```

#### Python API

```python
from python_cobol import process_cobol

# Read and process a COBOL file
with open("example.cbl", "r") as f:
    fields = process_cobol(f.readlines())

# Access field information
for field in fields:
    print(f"Field: {field['name']}, Level: {field['level']}")
    if field['pic']:
        print(f"  PIC: {field['pic']}")
        print(f"  Type: {field['pic_info']['type']}")
        print(f"  Length: {field['pic_info']['length']}")
```

## 📖 Documentation

### Supported COBOL Features

#### PIC Clauses
- Character fields: `PIC X(10)`
- Numeric fields: `PIC 9(5)`
- Signed fields: `PIC S9(5)`
- Decimal fields: `PIC 9(5)V99`
- Signed decimal: `PIC S9(5)V99`

#### OCCURS Clauses
```cobol
05 FIELD-1 OCCURS 3 TIMES PIC X(10).
05 GROUP-1 OCCURS 2 TIMES.
   10 SUB-FIELD-1 PIC X(5).
   10 SUB-FIELD-2 PIC 9(3).
```

#### REDEFINES Clauses
```cobol
05 FIELD-1 PIC X(10).
05 FIELD-2 REDEFINES FIELD-1 PIC 9(10).
```

#### INDEXED BY Clauses
```cobol
05 FIELD-1 OCCURS 3 TIMES INDEXED BY IDX-1 PIC X(10).
```

### API Reference

#### Core Functions

##### `process_cobol(lines: List[str]) -> List[Dict]`
Complete processing pipeline that:
- Cleans COBOL lines
- Parses field definitions
- Handles REDEFINES
- Denormalizes OCCURS
- Cleans field names
- Makes names database-safe

##### `parse_pic_string(pic_str: str) -> PicInfo`
Parse a PIC clause and return structured information:
```python
pic_info = parse_pic_string('S9(5)V99')
# Returns: PicInfo(type='Signed Float', length=7, precision=2)
```

##### `clean_cobol(lines: List[str]) -> List[str]`
Convert multi-line COBOL statements to single lines.

##### `parse_cobol(lines: List[str]) -> List[Dict]`
Parse COBOL lines into structured dictionaries.

##### `denormalize_cobol(lines: List[Dict]) -> List[Dict]`
Expand OCCURS clauses into individual fields.

##### `clean_names(lines: List[Dict], **options) -> List[Dict]`
Clean field names with options:
- `ensure_unique_names`: Add suffixes for uniqueness
- `strip_prefix`: Remove prefixes before first dash
- `make_database_safe`: Replace dashes with underscores

### Data Models

#### `PicInfo`
```python
@dataclass
class PicInfo:
    type: str          # 'Char', 'Integer', 'Float', 'Signed Integer', etc.
    length: int        # Total field length
    precision: int     # Decimal places (for numeric fields)
```

#### `CobolField`
```python
@dataclass
class CobolField:
    level: int
    name: str
    pic: Optional[str] = None
    pic_info: Optional[PicInfo] = None
    occurs: Optional[int] = None
    indexed_by: Optional[str] = None
    redefines: Optional[str] = None
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/rodrigo/python-cobol.git
cd python-cobol

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
python -m pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Run all checks (format, lint, test)
make check
```

### Project Structure

```
python-cobol/
├── python_cobol/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── core.py            # Core parsing functions
│   ├── models.py          # Data models
│   ├── patterns.py        # Regular expression patterns
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
│   ├── test_core.py       # Core functionality tests
│   ├── test_example.py    # Integration tests
│   └── example.cbl        # Test COBOL file
├── pyproject.toml         # Project configuration
├── requirements.txt       # Runtime dependencies
├── requirements-dev.txt   # Development dependencies
├── Makefile              # Development tasks
├── .pre-commit-config.yaml # Code quality hooks
└── README.md             # This file
```

## 📋 Examples

### Example 1: Simple Field Processing

**Input COBOL:**
```cobol
01  CUSTOMER-RECORD.
    05  CUSTOMER-ID PIC 9(10).
    05  CUSTOMER-NAME PIC X(50).
    05  CUSTOMER-BALANCE PIC S9(10)V99.
```

**Python Code:**
```python
from python_cobol import process_cobol

cobol_lines = [
    "01  CUSTOMER-RECORD.",
    "    05  CUSTOMER-ID PIC 9(10).",
    "    05  CUSTOMER-NAME PIC X(50).",
    "    05  CUSTOMER-BALANCE PIC S9(10)V99."
]

fields = process_cobol(cobol_lines)

for field in fields:
    print(f"{field['name']}: {field['pic_info']['type']}")
```

**Output:**
```
CUSTOMER_RECORD: Group
CUSTOMER_ID: Integer
CUSTOMER_NAME: Char
CUSTOMER_BALANCE: Signed Float
```

### Example 2: OCCURS Processing

**Input COBOL:**
```cobol
01  ORDER-RECORD.
    05  ORDER-ITEMS OCCURS 5 TIMES.
        10  ITEM-CODE PIC X(10).
        10  ITEM-QUANTITY PIC 9(3).
        10  ITEM-PRICE PIC S9(7)V99.
```

**Python Code:**
```python
from python_cobol import process_cobol

cobol_lines = [
    "01  ORDER-RECORD.",
    "    05  ORDER-ITEMS OCCURS 5 TIMES.",
    "        10  ITEM-CODE PIC X(10).",
    "        10  ITEM-QUANTITY PIC 9(3).",
    "        10  ITEM-PRICE PIC S9(7)V99."
]

fields = process_cobol(cobol_lines)

# Print all denormalized fields
for field in fields:
    print(f"{field['name']}: {field['pic']}")
```

**Output:**
```
ORDER_RECORD: None
ITEM_CODE_1: X(10)
ITEM_QUANTITY_1: 9(3)
ITEM_PRICE_1: S9(7)V99
ITEM_CODE_2: X(10)
ITEM_QUANTITY_2: 9(3)
ITEM_PRICE_2: S9(7)V99
...
```

### Example 3: REDEFINES Processing

**Input COBOL:**
```cobol
01  DATA-RECORD.
    05  TEXT-FIELD PIC X(20).
    05  NUMERIC-FIELD REDEFINES TEXT-FIELD PIC 9(20).
```

**Python Code:**
```python
from python_cobol import process_cobol

cobol_lines = [
    "01  DATA-RECORD.",
    "    05  TEXT-FIELD PIC X(20).",
    "    05  NUMERIC-FIELD REDEFINES TEXT-FIELD PIC 9(20)."
]

fields = process_cobol(cobol_lines)

# Only NUMERIC-FIELD remains after REDEFINES processing
for field in fields:
    print(f"{field['name']}: {field['pic']}")
```

**Output:**
```
DATA_RECORD: None
NUMERIC_FIELD: 9(20)
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `make test`
5. Run linting: `make lint`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

All code should pass these tools before submission.

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original code by Paulus Schoutsen
- PIC parsing logic inspired by [pyCOBOL](https://sourceforge.net/projects/pycobol/)
- Community contributors and maintainers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/rodrigo/python-cobol/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rodrigo/python-cobol/discussions)
- **Documentation**: [GitHub Wiki](https://github.com/rodrigo/python-cobol/wiki)

## 🔄 Changelog

### Version 1.0.0
- Complete refactoring with modern Python practices
- Added type hints throughout
- Improved error handling and logging
- Enhanced CLI interface
- Comprehensive test suite
- Modern project structure with pyproject.toml
- Pre-commit hooks for code quality
- Detailed documentation and examples

### Version 0.1.4 (Original)
- Basic COBOL parsing functionality
- Support for REDEFINES, OCCURS, INDEXED BY
- Simple CLI interface