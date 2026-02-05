"""
XML extraction module for patent documents.

This module provides functions to extract doc-number values from XML patent documents
in priority order based on the format attribute. Handles XML embedded within larger text documents.
"""

import xml.etree.ElementTree as ET
import re
from typing import List
from pathlib import Path


def extract_xml_from_text(content: str) -> List[str]:
    """
    Extract XML content from a text document that may contain other content.
    
    Looks for <root>...</root> tags and extracts all XML portions.
    
    Args:
        content: String that may contain XML along with other text
        
    Returns:
        List of extracted XML strings. Returns list with original content if it appears to be pure XML.
    """
    # First, try to see if the whole content is valid XML
    content_stripped = content.strip()
    if content_stripped.startswith('<?xml') or content_stripped.startswith('<root'):
        return [content]
    
    # Try to extract all XML snippets using regex - look for <root> tags
    pattern = r'(<root[\s>].*?</root>)'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        return matches
    
    # If no <root> tag, return original content and let XML parser handle it
    return [content]


def extract_doc_numbers(xml_content: str) -> List[str]:
    """
    Extract doc-number values from XML content in priority order.
    
    Handles XML embedded within larger text documents by first extracting the XML portion.
    If multiple XML snippets are found, aggregates results from all of them.
    
    Args:
        xml_content: String containing XML document (may be embedded in other text, may contain multiple snippets)
        
    Returns:
        List of doc-number values, ordered by format priority (epo first, then patent-office)
        
    Raises:
        ValueError: If XML parsing fails
    """
    # Extract XML snippets from text
    xml_snippets = extract_xml_from_text(xml_content)
    
    # Collect doc-numbers from all snippets
    all_epo_doc_numbers = []
    all_patent_office_doc_numbers = []
    all_other_doc_numbers = []
    
    for xml_str in xml_snippets:
        try:
            root = ET.fromstring(xml_str)
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML: {e}")
        
        # Find all document-id elements
        document_ids = root.findall('.//document-id')
        
        for doc_id in document_ids:
            format_attr = doc_id.get('format', '')
            doc_number_elem = doc_id.find('doc-number')
            
            # Skip if doc-number element doesn't exist or is empty
            if doc_number_elem is None or not doc_number_elem.text:
                continue
                
            doc_number = doc_number_elem.text.strip()
            
            # Categorize by format priority
            if format_attr == 'epo':
                all_epo_doc_numbers.append(doc_number)
            elif format_attr == 'patent-office':
                all_patent_office_doc_numbers.append(doc_number)
            else:
                # Handle other formats (lower priority)
                all_other_doc_numbers.append(doc_number)
    
    # Return in priority order: epo, patent-office, others
    return all_epo_doc_numbers + all_patent_office_doc_numbers + all_other_doc_numbers


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
