#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple test for the COBOL parser based on the original example.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_cobol import process_cobol


def test_example():
    """Test the example COBOL file processing."""
    # Read the example file
    example_file = os.path.join(os.path.dirname(__file__), 'example.cbl')
    
    with open(example_file, 'r') as f:
        rows = process_cobol(f.readlines())
    
    # Verify the expected results
    assert rows[0]['name'] == 'EXAMPLE_GROUP'
    assert rows[1]['name'] == 'FIELD_2_1'
    assert rows[2]['name'] == 'FIELD_3_1_1'
    assert rows[3]['name'] == 'FIELD_3_1_2'
    assert rows[4]['name'] == 'FIELD_2_2'
    assert rows[5]['name'] == 'FIELD_3_2_1'
    assert rows[6]['name'] == 'FIELD_3_2_2'
    assert rows[7]['name'] == 'FIELD_2_3'
    assert rows[8]['name'] == 'FIELD_3_3_1'
    assert rows[9]['name'] == 'FIELD_3_3_2'
    assert rows[10]['name'] == 'THIS_IS_ANOTHER_GROUP'
    assert rows[11]['name'] == 'YES'
    
    print("All tests passed!")


if __name__ == '__main__':
    test_example() 