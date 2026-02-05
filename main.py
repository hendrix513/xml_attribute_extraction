#!/usr/bin/env python3
"""
XML Attribute Extraction for Patent Documents - CLI Entry Point

This script provides a command-line interface for extracting doc-number values
from XML patent documents. The actual extraction logic is in the extractor module.
"""

import sys
from pathlib import Path
from extractor import extract_doc_numbers_from_file


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <xml_file_path>")
        print("Example: python main.py sample_patent.xml")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    try:
        doc_numbers = extract_doc_numbers_from_file(file_path)
        
        if doc_numbers:
            print("Extracted doc-numbers (in priority order):")
            for doc_num in doc_numbers:
                print(f"  {doc_num}")
        else:
            print("No doc-numbers found in the XML file.")
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
