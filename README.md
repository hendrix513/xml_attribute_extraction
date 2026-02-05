# XML Attribute Extraction - Patent Doc-Number Extractor

This Python program extracts `doc-number` values from patent XML documents in priority order based on the `format` attribute of `document-id` elements.

## Overview

The program processes XML patent documents and extracts `doc-number` values according to the following priority:
1. `document-id` elements with `format="epo"` (highest priority)
2. `document-id` elements with `format="patent-office"` (second priority)
3. Any other `document-id` elements (lowest priority)

## Architecture

The application follows a modular design for testability:

- **`extractor.py`**: Core extraction logic (fully unit tested)
  - `extract_doc_numbers()`: Parses XML and extracts doc-numbers in priority order
  - `read_xml_file()`: Handles file reading with encoding fallback
  - `extract_doc_numbers_from_file()`: Combines file reading and extraction
  
- **`main.py`**: Minimal CLI entry point that delegates to extractor module

- **`tests/`**: Comprehensive unit tests covering all logic paths
  - Priority ordering
  - Error handling
  - Edge cases (empty values, missing elements, malformed XML)

## Assumptions

The implementation makes the following assumptions about the XML structure:

1. **Element Hierarchy**: `document-id` elements can appear anywhere in the document tree (using XPath `//document-id`)

2. **Format Attribute**: The `format` attribute on `document-id` elements determines extraction priority:
   - `format="epo"` → highest priority
   - `format="patent-office"` → second priority
   - Other or missing format values → lowest priority

3. **Doc-Number Elements**: Each `document-id` contains a `doc-number` child element with the value to extract

4. **Multiple Occurrences**: Multiple `document-id` elements may exist within a single `application-reference`, and multiple `application-reference` elements may exist in the document

5. **Encoding**: The XML file is assumed to be UTF-8 encoded, with a fallback to Latin-1 if UTF-8 fails

6. **Malformed Data**: Empty or missing `doc-number` elements are gracefully skipped without raising errors

## Error Handling

The program handles the following error cases:

- **Missing File**: Exits with a clear error message if the specified XML file doesn't exist
- **Malformed XML**: Catches XML parsing errors and reports them clearly
- **Missing Elements**: Skips `document-id` elements that lack a `doc-number` child
- **Empty Values**: Ignores `doc-number` elements with empty or whitespace-only content
- **Encoding Issues**: Attempts multiple encodings (UTF-8, then Latin-1) if reading fails
- **Unexpected Errors**: Catches and reports any unexpected exceptions

All errors are written to stderr with descriptive messages, and the program exits with appropriate non-zero status codes.

## Installation and Setup

### Option 1: Using Docker (Recommended)

Docker provides a consistent environment and is the easiest way to run the application.

#### Prerequisites
- Docker and Docker Compose installed on your system

#### Running with Docker Compose

```bash
# Run the application with the sample XML file
docker-compose up app

# Run with your own XML file (just place it in the project directory!)
docker-compose run --rm app python main.py your-file.xml

# Run unit tests
docker-compose up test

# Open an interactive shell for development
docker-compose up shell
```

The current directory is automatically mounted, so you can place any XML file in the project folder and reference it by name - no manual volume binding needed!

#### Building and Running Manually

```bash
# Build the Docker image
docker build -t xml-extractor .

# Run with the built-in sample file
docker run --rm xml-extractor

# Run with a custom file from your host machine
docker run --rm -v $(pwd):/app xml-extractor python main.py your-file.xml

# Run tests
docker run --rm xml-extractor pytest tests/ -v
```

### Option 2: Local Installation with uv

This project uses [uv](https://github.com/astral-sh/uv) for dependency management and virtual environment handling.

#### Prerequisites

1. Install `uv`:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Ensure Python 3.8+ is installed on your system

#### Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd xml_attribute_extraction
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

## Usage

### Running the Application

#### With Docker (Easiest!)
```bash
# Run with the built-in sample file
docker-compose up app

# Run with your own XML file (just put it in the project directory!)
docker-compose run --rm app python main.py your-file.xml
```

#### Local (after uv setup)
```bash
# Basic usage
python main.py <path_to_xml_file>

# Using uv run
uv run python main.py <path_to_xml_file>
```

### Quick Start with Sample Data

The easiest way to see the application in action is with Docker:

```bash
docker-compose up app
```

For local development, a sample XML file (`sample_patent.xml`) is also included:

```bash
python main.py sample_patent.xml
```

**Expected Output (both methods):**
```
Extracted doc-numbers (in priority order):
  999000888
  66667777
```

## Running Tests

Comprehensive unit tests cover all extraction logic, error handling, and edge cases.

### With Docker

```bash
# Run all tests
docker-compose up test

# Run with coverage report
docker run --rm xml-extractor pytest tests/ -v --cov=extractor --cov-report=term-missing
```

### Local

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=extractor --cov-report=term-missing

# Run specific test file
pytest tests/test_extractor.py -v

# Run specific test
pytest tests/test_extractor.py::TestExtractDocNumbers::test_extract_with_priority_order -v
```

### Test Coverage

The test suite includes:
- **Priority ordering tests**: Verifying epo > patent-office > others
- **Error handling tests**: Malformed XML, missing files, encoding issues
- **Edge case tests**: Empty values, whitespace, missing elements
- **Integration tests**: End-to-end file reading and extraction
- **Sample verification**: Testing with the exact challenge sample data

## Project Structure

```
xml_attribute_extraction/
├── README.md              # This file
├── challenge_description  # Original challenge requirements
├── main.py               # Minimal CLI entry point
├── extractor.py          # Core extraction logic module
├── sample_patent.xml     # Sample XML file for testing
├── pyproject.toml        # Project configuration and dependencies
├── Dockerfile            # Docker image definition
├── docker-compose.yml    # Docker Compose services configuration
└── tests/
    ├── __init__.py
    └── test_extractor.py # Comprehensive unit tests
```

## Development

### Running Interactively

```bash
# Docker shell
docker-compose up shell

# Inside the container, you can:
python main.py sample_patent.xml
pytest tests/ -v
python -m extractor  # etc.
```

### Code Organization

The codebase follows best practices for testability:

1. **Separation of Concerns**: CLI logic (main.py) is separate from business logic (extractor.py)
2. **Pure Functions**: Core extraction functions have no side effects and are easily testable
3. **Error Handling**: All error cases are handled gracefully with clear messages
4. **Type Hints**: Functions include type hints for better IDE support and documentation
5. **Comprehensive Tests**: 100% coverage of extraction logic with edge cases

## Implementation Details

- **Language**: Python 3.8+
- **XML Parsing**: Uses Python's built-in `xml.etree.ElementTree` library (no external dependencies for core functionality)
- **Testing**: pytest framework with comprehensive coverage
- **Priority Sorting**: Doc-numbers are collected by format type and concatenated in priority order
- **CLI Interface**: Simple command-line interface accepting a file path as argument
- **Containerization**: Docker and Docker Compose for consistent deployment

## License

This is a challenge implementation for Cypris.
