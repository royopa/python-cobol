"""
Tests for core COBOL parsing functionality.
"""

import pytest
from unittest.mock import patch

from python_cobol.core import (
    parse_pic_string,
    clean_cobol,
    parse_cobol,
    get_subgroup,
    denormalize_cobol,
    clean_names,
    process_cobol,
    print_cobol,
)


class TestParsePicString:
    """Test PIC string parsing functionality."""
    
    def test_parse_char_pic(self):
        """Test parsing character PIC clauses."""
        result = parse_pic_string('X(10)')
        assert result.type == 'Char'
        assert result.length == 10
        assert result.precision == 0
        
    def test_parse_integer_pic(self):
        """Test parsing integer PIC clauses."""
        result = parse_pic_string('9(5)')
        assert result.type == 'Integer'
        assert result.length == 5
        assert result.precision == 0
        
    def test_parse_signed_integer_pic(self):
        """Test parsing signed integer PIC clauses."""
        result = parse_pic_string('S9(5)')
        assert result.type == 'Signed Integer'
        assert result.length == 5
        assert result.precision == 0
        
    def test_parse_float_pic(self):
        """Test parsing float PIC clauses."""
        result = parse_pic_string('9(5)V99')
        assert result.type == 'Float'
        assert result.length == 7
        assert result.precision == 2
        
    def test_parse_signed_float_pic(self):
        """Test parsing signed float PIC clauses."""
        result = parse_pic_string('S9(5)V99')
        assert result.type == 'Signed Float'
        assert result.length == 7
        assert result.precision == 2
        
    def test_parse_simple_char(self):
        """Test parsing simple character PIC."""
        result = parse_pic_string('X')
        assert result.type == 'Char'
        assert result.length == 1
        assert result.precision == 0


class TestCleanCobol:
    """Test COBOL line cleaning functionality."""
    
    def test_clean_simple_lines(self):
        """Test cleaning simple COBOL lines."""
        lines = [
            "      01  EXAMPLE-GROUP.",
            "          05  FIELD-1 PIC X(10)."
        ]
        result = clean_cobol(lines)
        expected = ['01 EXAMPLE-GROUP.', '05 FIELD-1 PIC X(10).']
        assert result == expected
        
    def test_clean_with_comments(self):
        """Test cleaning lines with comments."""
        lines = [
            "* This is a comment",
            "      01  EXAMPLE-GROUP.",
            "/ Another comment",
            "          05  FIELD-1 PIC X(10)."
        ]
        result = clean_cobol(lines)
        expected = ['01 EXAMPLE-GROUP.', '05 FIELD-1 PIC X(10).']
        assert result == expected
        
    def test_clean_continuation_lines(self):
        """Test cleaning continuation lines."""
        lines = [
            "      01  EXAMPLE-GROUP",
            "              PIC X(10)."
        ]
        result = clean_cobol(lines)
        expected = ['01 EXAMPLE-GROUP PIC X(10).']
        assert result == expected
        
    def test_clean_empty_lines(self):
        """Test cleaning lines with empty lines."""
        lines = [
            "",
            "      01  EXAMPLE-GROUP.",
            "  ",
            "          05  FIELD-1 PIC X(10)."
        ]
        result = clean_cobol(lines)
        expected = ['01 EXAMPLE-GROUP.', '05 FIELD-1 PIC X(10).']
        assert result == expected


class TestParseCobol:
    """Test COBOL parsing functionality."""
    
    def test_parse_simple_field(self):
        """Test parsing a simple field definition."""
        lines = ['01 EXAMPLE-GROUP.']
        result = parse_cobol(lines)
        assert len(result) == 1
        assert result[0]['level'] == 1
        assert result[0]['name'] == 'EXAMPLE-GROUP'
        assert result[0]['pic'] is None
        
    def test_parse_field_with_pic(self):
        """Test parsing a field with PIC clause."""
        lines = ['05 FIELD-1 PIC X(10).']
        result = parse_cobol(lines)
        assert len(result) == 1
        assert result[0]['level'] == 5
        assert result[0]['name'] == 'FIELD-1'
        assert result[0]['pic'] == 'X(10)'
        assert result[0]['pic_info'].type == 'Char'
        assert result[0]['pic_info'].length == 10
        
    def test_parse_field_with_occurs(self):
        """Test parsing a field with OCCURS clause."""
        lines = ['05 FIELD-1 OCCURS 3 TIMES PIC X(10).']
        result = parse_cobol(lines)
        assert len(result) == 1
        assert result[0]['level'] == 5
        assert result[0]['name'] == 'FIELD-1'
        assert result[0]['occurs'] == 3
        assert result[0]['pic'] == 'X(10)'
        
    def test_parse_field_with_redefines(self):
        """Test parsing a field with REDEFINES clause."""
        lines = [
            '05 FIELD-1 PIC X(10).',
            '05 FIELD-2 REDEFINES FIELD-1 PIC 9(10).'
        ]
        result = parse_cobol(lines)
        assert len(result) == 1  # FIELD-1 should be removed
        assert result[0]['name'] == 'FIELD-2'
        # Should be cleared after processing
        assert result[0]['redefines'] is None
        
    def test_parse_field_with_indexed_by(self):
        """Test parsing a field with INDEXED BY clause."""
        lines = [
            '05 FIELD-1 OCCURS 3 TIMES INDEXED BY IDX-1 PIC X(10).'
        ]
        result = parse_cobol(lines)
        assert len(result) == 1
        assert result[0]['level'] == 5
        assert result[0]['name'] == 'FIELD-1'
        assert result[0]['occurs'] == 3
        assert result[0]['indexed_by'] == 'IDX-1'
        assert result[0]['pic'] == 'X(10)'


class TestGetSubgroup:
    """Test subgroup extraction functionality."""
    
    def test_get_subgroup_simple(self):
        """Test getting a simple subgroup."""
        lines = [
            {'level': 1, 'name': 'GROUP-1'},
            {'level': 5, 'name': 'FIELD-1'},
            {'level': 5, 'name': 'FIELD-2'},
            {'level': 1, 'name': 'GROUP-2'}
        ]
        result = get_subgroup(1, lines[1:])
        assert len(result) == 2
        assert result[0]['name'] == 'FIELD-1'
        assert result[1]['name'] == 'FIELD-2'
        
    def test_get_subgroup_nested(self):
        """Test getting a nested subgroup."""
        lines = [
            {'level': 1, 'name': 'GROUP-1'},
            {'level': 5, 'name': 'FIELD-1'},
            {'level': 10, 'name': 'SUB-FIELD-1'},
            {'level': 10, 'name': 'SUB-FIELD-2'},
            {'level': 5, 'name': 'FIELD-2'},
            {'level': 1, 'name': 'GROUP-2'}
        ]
        result = get_subgroup(5, lines[2:4])
        assert len(result) == 2
        assert result[0]['name'] == 'SUB-FIELD-1'
        assert result[1]['name'] == 'SUB-FIELD-2'


class TestDenormalizeCobol:
    """Test COBOL denormalization functionality."""
    
    def test_denormalize_simple_occurs(self):
        """Test denormalizing simple OCCURS."""
        lines = [
            {'level': 1, 'name': 'GROUP-1', 'occurs': None},
            {'level': 5, 'name': 'FIELD-1', 'occurs': 3, 'pic': 'X(10)'}
        ]
        result = denormalize_cobol(lines)
        assert len(result) == 4  # 1 group + 3 fields
        assert result[1]['name'] == 'FIELD-1-1'
        assert result[2]['name'] == 'FIELD-1-2'
        assert result[3]['name'] == 'FIELD-1-3'
        
    def test_denormalize_group_occurs(self):
        """Test denormalizing group OCCURS."""
        lines = [
            {'level': 1, 'name': 'GROUP-1', 'occurs': 2},
            {'level': 5, 'name': 'FIELD-1', 'occurs': None, 'pic': 'X(10)'},
            {'level': 5, 'name': 'FIELD-2', 'occurs': None, 'pic': 'X(10)'}
        ]
        result = denormalize_cobol(lines)
        assert len(result) == 5  # 2 groups with 2 fields each + 1 group field
        assert result[1]['name'] == 'FIELD-1-1'
        assert result[2]['name'] == 'FIELD-2-1'
        assert result[3]['name'] == 'FIELD-1-2'
        assert result[4]['name'] == 'FIELD-2-2'


class TestCleanNames:
    """Test name cleaning functionality."""
    
    def test_clean_names_strip_prefix(self):
        """Test stripping prefixes from names."""
        lines = [
            {'name': 'PREFIX-FIELD-1', 'indexed_by': None},
            {'name': 'PREFIX-FIELD-2', 'indexed_by': 'PREFIX-IDX-1'}
        ]
        result = clean_names(lines, strip_prefix=True)
        assert result[0]['name'] == 'FIELD-1'
        assert result[1]['name'] == 'FIELD-2'
        assert result[1]['indexed_by'] == 'IDX-1'
        
    def test_clean_names_ensure_unique(self):
        """Test ensuring unique names."""
        lines = [
            {'name': 'FIELD-1', 'indexed_by': None},
            {'name': 'FIELD-1', 'indexed_by': None}
        ]
        result = clean_names(lines, ensure_unique_names=True)
        assert result[0]['name'] == 'FIELD-1'
        assert result[1]['name'] == 'FIELD-1-2'
        
    def test_clean_names_database_safe(self):
        """Test making names database safe."""
        lines = [
            {'name': 'FIELD-1', 'indexed_by': None},
            {'name': 'FIELD-WITH-DASHES', 'indexed_by': None}
        ]
        result = clean_names(lines, make_database_safe=True)
        assert result[0]['name'] == 'FIELD_1'
        assert result[1]['name'] == 'FIELD_WITH_DASHES'


class TestProcessCobol:
    """Test complete COBOL processing pipeline."""
    
    def test_process_cobol_complete(self):
        """Test complete processing pipeline."""
        lines = [
            "      01  PAULUS-EXAMPLE-GROUP.",
            "          05  PAULUS-ANOTHER-GROUP OCCURS 0002 TIMES.",
            "              10  PAULUS-FIELD-1 PIC X(3).",
            "              10  PAULUS-FIELD-2 PIC 9(3).",
            "          05  PAULUS-THIS-IS-ANOTHER-GROUP.",
            "              10  PAULUS-YES PIC X(5)."
        ]
        result = process_cobol(lines)
        
        # Should have denormalized OCCURS and cleaned names
        assert len(result) == 7  # 1 group + 2*2 fields + 1 group + 1 field
        assert result[0]['name'] == 'EXAMPLE_GROUP'
        assert result[1]['name'] == 'FIELD_1_1'
        assert result[2]['name'] == 'FIELD_2_1'
        assert result[3]['name'] == 'FIELD_1_2'
        assert result[4]['name'] == 'FIELD_2_2'
        assert result[5]['name'] == 'THIS_IS_ANOTHER_GROUP'
        assert result[6]['name'] == 'YES'


class TestPrintCobol:
    """Test COBOL printing functionality."""
    
    @patch('builtins.print')
    def test_print_cobol_simple(self, mock_print):
        """Test printing simple COBOL fields."""
        lines = [
            {
                'level': 1, 'name': 'EXAMPLE-GROUP', 
                'pic': None, 'occurs': None, 'indexed_by': None
            },
            {
                'level': 5, 'name': 'FIELD-1', 
                'pic': 'X(10)', 'occurs': None, 'indexed_by': None
            }
        ]
        print_cobol(lines)
        mock_print.assert_called()
        
    @patch('builtins.print')
    def test_print_cobol_with_occurs(self, mock_print):
        """Test printing COBOL fields with OCCURS."""
        lines = [
            {
                'level': 1, 'name': 'EXAMPLE-GROUP', 
                'pic': None, 'occurs': None, 'indexed_by': None
            },
            {
                'level': 5, 'name': 'FIELD-1', 
                'pic': 'X(10)', 'occurs': 3, 'indexed_by': None
            }
        ]
        print_cobol(lines)
        mock_print.assert_called()


if __name__ == '__main__':
    pytest.main([__file__]) 