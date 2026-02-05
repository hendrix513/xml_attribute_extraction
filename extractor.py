"""
XML extraction module for patent documents.

This module provides functions to extract doc-number values from XML patent documents
in priority order based on the format attribute.
"""

import xml.etree.ElementTree as ET
from typing import List
from pathlib import Path


def extract_doc_numbers(xml_content: str) -> List[str]:
    """
    Extract doc-number values from XML content in priority order.
    
    Args:
        xml_content: String containing the XML document
        
    Returns:
        List of doc-number values, ordered by format priority (epo first, then patent-office)
        
    Raises:
        ValueError: If XML parsing fails
    """
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML: {e}")
    
    # Find all document-id elements
    document_ids = root.findall('.//document-id')
    
    # Separate by format and extract doc-numbers
    epo_doc_numbers = []
    patent_office_doc_numbers = []
    other_doc_numbers = []
    
    for doc_id in document_ids:
        format_attr = doc_id.get('format', '')
        doc_number_elem = doc_id.find('doc-number')
        
        # Skip if doc-number element doesn't exist or is empty
        if doc_number_elem is None or not doc_number_elem.text:
            continue
            
        doc_number = doc_number_elem.text.strip()
        
        # Categorize by format priority
        if format_attr == 'epo':
            epo_doc_numbers.append(doc_number)
        elif format_attr == 'patent-office':
            patent_office_doc_numbers.append(doc_number)
        else:
            # Handle other formats (lower priority)
            other_doc_numbers.append(doc_number)
    
    # Return in priority order: epo, patent-office, others
    return epo_doc_numbers + patent_office_doc_numbers + other_doc_numbers


def read_xml_file(file_path: Path) -> str:
    """
    Read XML content from a file with encoding fallback.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        String containing the XML content
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file cannot be read
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with a different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file with any encoding: {e}")
    except IOError as e:
        raise ValueError(f"Failed to read file: {e}")


def extract_doc_numbers_from_file(file_path: Path) -> List[str]:
    """
    Extract doc-number values from an XML file.
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        List of doc-number values in priority order
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If XML parsing fails or file cannot be read
    """
    xml_content = read_xml_file(file_path)
    return extract_doc_numbers(xml_content)
