"""
Unit tests for the extractor module.

Tests cover all extraction logic including:
- Priority ordering (epo > patent-office > others)
- Error handling (malformed XML, missing elements)
- Edge cases (empty values, multiple documents)
- XML embedded in text documents
"""

import pytest
from pathlib import Path
import tempfile
from extractor import extract_doc_numbers, read_xml_file, extract_doc_numbers_from_file, extract_xml_from_text


class TestExtractDocNumbers:
    """Tests for extract_doc_numbers function."""
    
    def test_extract_with_priority_order(self):
        """Test that doc-numbers are extracted in correct priority order."""
        xml = """<?xml version="1.0"?>
        <root>
            <application-reference>
                <document-id format="epo">
                    <doc-number>111111</doc-number>
                </document-id>
                <document-id format="patent-office">
                    <doc-number>222222</doc-number>
                </document-id>
            </application-reference>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111", "222222"]
    
    def test_extract_reverse_order_in_xml(self):
        """Test priority is enforced even when XML has patent-office before epo."""
        xml = """<?xml version="1.0"?>
        <root>
            <application-reference>
                <document-id format="patent-office">
                    <doc-number>222222</doc-number>
                </document-id>
                <document-id format="epo">
                    <doc-number>111111</doc-number>
                </document-id>
            </application-reference>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111", "222222"]
    
    def test_extract_multiple_epo_documents(self):
        """Test extraction of multiple documents with same format."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
            <document-id format="epo">
                <doc-number>333333</doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111", "333333", "222222"]
    
    def test_extract_with_other_format(self):
        """Test that unknown formats are included after known ones."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="unknown">
                <doc-number>999999</doc-number>
            </document-id>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111", "999999"]
    
    def test_extract_no_format_attribute(self):
        """Test handling of document-id without format attribute."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id>
                <doc-number>999999</doc-number>
            </document-id>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111", "999999"]
    
    def test_extract_empty_doc_number(self):
        """Test that empty doc-number elements are skipped."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number></doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["222222"]
    
    def test_extract_whitespace_only_doc_number(self):
        """Test that whitespace-only doc-number elements are skipped."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number>   </doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["222222"]
    
    def test_extract_missing_doc_number_element(self):
        """Test that document-id without doc-number child is skipped."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <country>US</country>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["222222"]
    
    def test_extract_with_leading_trailing_whitespace(self):
        """Test that doc-number values are trimmed."""
        xml = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number>  111111  </doc-number>
            </document-id>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111"]
    
    def test_extract_no_matching_elements(self):
        """Test extraction returns empty list when no doc-numbers found."""
        xml = """<?xml version="1.0"?>
        <root>
            <some-other-element>
                <data>value</data>
            </some-other-element>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == []
    
    def test_extract_nested_document_ids(self):
        """Test extraction from deeply nested structure."""
        xml = """<?xml version="1.0"?>
        <root>
            <level1>
                <level2>
                    <application-reference>
                        <document-id format="epo">
                            <doc-number>111111</doc-number>
                        </document-id>
                    </application-reference>
                </level2>
            </level1>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["111111"]
    
    def test_malformed_xml(self):
        """Test that malformed XML raises ValueError."""
        xml = """<root><unclosed>"""
        
        with pytest.raises(ValueError, match="Failed to parse XML"):
            extract_doc_numbers(xml)
    
    def test_empty_xml(self):
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError):
            extract_doc_numbers("")
    
    def test_sample_from_challenge(self):
        """Test with the exact sample from the challenge description."""
        xml = """<?xml version="1.0"?>
        <root>
            <application-reference ucid="US-XXXXXXXX-A" is-representative="NO" us-art-unit="9999" us-series-code="99">
                <document-id mxw-id="ABCD99999999" load-source="docdb" format="epo">
                    <country>US</country>
                    <doc-number>999000888</doc-number>
                    <kind>A</kind>
                    <date>20051213</date>
                    <lang>EN</lang>
                </document-id>
                <document-id mxw-id="ABCD88888888" load-source="patent-office" format="patent-office">
                    <country>US</country>
                    <doc-number>66667777</doc-number>
                    <lang>EN</lang>
                </document-id>
            </application-reference>
        </root>"""
        
        result = extract_doc_numbers(xml)
        assert result == ["999000888", "66667777"]


class TestExtractXmlFromText:
    """Tests for extract_xml_from_text function."""
    
    def test_extract_xml_from_middle_of_document(self):
        """Test extracting XML embedded in a text document."""
        content = """
        This is some text before the XML.
        Here comes the patent data:
        
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        
        And some text after the XML.
        """
        
        xmls = extract_xml_from_text(content)
        assert len(xmls) == 1
        assert '<root>' in xmls[0]
        assert '<doc-number>111111</doc-number>' in xmls[0]
        assert 'some text before' not in xmls[0]
    
    def test_extract_multiple_xml_snippets(self):
        """Test extracting multiple XML snippets from one document."""
        content = """
        First patent:
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        
        Second patent:
        <root>
            <document-id format="epo">
                <doc-number>222222</doc-number>
            </document-id>
        </root>
        
        End of document.
        """
        
        xmls = extract_xml_from_text(content)
        assert len(xmls) == 2
        assert '<doc-number>111111</doc-number>' in xmls[0]
        assert '<doc-number>222222</doc-number>' in xmls[1]
    
    def test_extract_xml_with_xml_declaration(self):
        """Test that pure XML with declaration is returned as-is."""
        content = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>"""
        
        xmls = extract_xml_from_text(content)
        assert len(xmls) == 1
        assert xmls[0].strip() == content.strip()
    
    def test_extract_xml_pure_root_element(self):
        """Test that pure XML starting with <root> is returned as-is."""
        content = """<root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>"""
        
        xmls = extract_xml_from_text(content)
        assert len(xmls) == 1
        assert xmls[0].strip() == content.strip()
    
    def test_extract_xml_with_attributes_in_root(self):
        """Test extracting XML where root has attributes."""
        content = """
        Some preamble text
        <root id="test" version="1.0">
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        Some epilogue text
        """
        
        xmls = extract_xml_from_text(content)
        assert len(xmls) == 1
        assert '<root id="test" version="1.0">' in xmls[0]
        assert 'preamble' not in xmls[0]
        assert 'epilogue' not in xmls[0]


class TestExtractDocNumbersFromEmbeddedXml:
    """Tests for extracting doc-numbers from XML embedded in text."""
    
    def test_extract_from_text_with_embedded_xml(self):
        """Test complete extraction from document with embedded XML."""
        content = """
        Patent Document Analysis Report
        ================================
        
        The following XML contains patent information:
        
        <root>
            <application-reference>
                <document-id format="epo">
                    <doc-number>999000888</doc-number>
                </document-id>
                <document-id format="patent-office">
                    <doc-number>66667777</doc-number>
                </document-id>
            </application-reference>
        </root>
        
        End of patent data.
        """
        
        result = extract_doc_numbers(content)
        assert result == ["999000888", "66667777"]
    
    def test_extract_with_priority_from_embedded_xml(self):
        """Test priority ordering works with embedded XML."""
        content = """
        Random text here
        <root>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        More random text
        """
        
        result = extract_doc_numbers(content)
        assert result == ["111111", "222222"]


class TestExtractDocNumbersFromMultipleSnippets:
    """Tests for extracting doc-numbers from multiple XML snippets."""
    
    def test_extract_from_multiple_snippets(self):
        """Test extraction from document with multiple XML snippets."""
        content = """
        Patent Batch Report
        ===================
        
        Patent 1:
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        
        Patent 2:
        <root>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>
        
        End of report.
        """
        
        result = extract_doc_numbers(content)
        assert result == ["111111", "222222"]
    
    def test_extract_with_priority_across_multiple_snippets(self):
        """Test that priority is maintained across multiple XML snippets."""
        content = """
        Snippet 1:
        <root>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>
        
        Snippet 2:
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
        </root>
        
        Snippet 3:
        <root>
            <document-id format="patent-office">
                <doc-number>333333</doc-number>
            </document-id>
        </root>
        """
        
        result = extract_doc_numbers(content)
        # All epo first, then all patent-office
        assert result == ["111111", "222222", "333333"]
    
    def test_extract_multiple_docs_per_snippet(self):
        """Test extraction with multiple doc-numbers in each snippet."""
        content = """
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>
        
        <root>
            <document-id format="epo">
                <doc-number>333333</doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>444444</doc-number>
            </document-id>
        </root>
        """
        
        result = extract_doc_numbers(content)
        # All epo first (from both snippets), then all patent-office (from both snippets)
        assert result == ["111111", "333333", "222222", "444444"]


class TestReadXmlFile:
    """Tests for read_xml_file function."""
    
    def test_read_utf8_file(self):
        """Test reading a UTF-8 encoded XML file."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.xml') as f:
            f.write('<?xml version="1.0"?><root><test>data</test></root>')
            temp_path = Path(f.name)
        
        try:
            content = read_xml_file(temp_path)
            assert '<root>' in content
            assert '<test>data</test>' in content
        finally:
            temp_path.unlink()
    
    def test_read_nonexistent_file(self):
        """Test that reading nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            read_xml_file(Path("/nonexistent/file.xml"))
    
    def test_read_latin1_file(self):
        """Test reading a Latin-1 encoded file (fallback)."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='latin-1', delete=False, suffix='.xml') as f:
            # Write some latin-1 specific character
            f.write('<?xml version="1.0"?><root><test>café</test></root>')
            temp_path = Path(f.name)
        
        try:
            content = read_xml_file(temp_path)
            assert '<root>' in content
        finally:
            temp_path.unlink()


class TestExtractDocNumbersFromFile:
    """Tests for extract_doc_numbers_from_file function."""
    
    def test_extract_from_valid_file(self):
        """Test extraction from a valid XML file."""
        xml_content = """<?xml version="1.0"?>
        <root>
            <document-id format="epo">
                <doc-number>111111</doc-number>
            </document-id>
            <document-id format="patent-office">
                <doc-number>222222</doc-number>
            </document-id>
        </root>"""
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.xml') as f:
            f.write(xml_content)
            temp_path = Path(f.name)
        
        try:
            result = extract_doc_numbers_from_file(temp_path)
            assert result == ["111111", "222222"]
        finally:
            temp_path.unlink()
    
    def test_extract_from_malformed_file(self):
        """Test that malformed XML in file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.xml') as f:
            f.write('<root><unclosed>')
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Failed to parse XML"):
                extract_doc_numbers_from_file(temp_path)
        finally:
            temp_path.unlink()
    
    def test_extract_from_nonexistent_file(self):
        """Test that nonexistent file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            extract_doc_numbers_from_file(Path("/nonexistent/file.xml"))
    
    def test_extract_from_empty_file(self):
        """Test that empty file raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False, suffix='.xml') as f:
            f.write('')
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError):
                extract_doc_numbers_from_file(temp_path)
        finally:
            temp_path.unlink()
