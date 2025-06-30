#!/usr/bin/env python3
"""
Demonstration script for the Python COBOL Copybook Parser.

This script shows various ways to use the library to process COBOL files.
"""

import os
import sys

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from python_cobol import (
    process_cobol,
    parse_cobol,
    clean_cobol,
    clean_names,
)
from python_cobol.core import parse_pic_string


def demo_basic_processing():
    """Demonstrate basic COBOL processing."""
    print("=== Basic COBOL Processing ===")
    
    # Simple COBOL example
    cobol_lines = [
        "01  CUSTOMER-RECORD.",
        "    05  CUSTOMER-ID PIC 9(10).",
        "    05  CUSTOMER-NAME PIC X(50).",
        "    05  CUSTOMER-BALANCE PIC S9(10)V99."
    ]
    
    # Process with all features enabled
    fields = process_cobol(cobol_lines)
    
    print("Processed fields:")
    for field in fields:
        print(f"  {field['name']}: {field['pic']}")
        if field['pic_info']:
            print(f"    Type: {field['pic_info']['type']}")
            print(f"    Length: {field['pic_info']['length']}")
            print(f"    Precision: {field['pic_info']['precision']}")
        print()


def demo_pic_parsing():
    """Demonstrate PIC clause parsing."""
    print("=== PIC Clause Parsing ===")
    
    pic_examples = [
        'X(10)',      # Character field
        '9(5)',       # Integer field
        'S9(5)',      # Signed integer
        '9(5)V99',    # Decimal field
        'S9(5)V99',   # Signed decimal
        'X',          # Single character
        '9(3)',       # 3-digit number
    ]
    
    for pic in pic_examples:
        info = parse_pic_string(pic)
        print(
            f"PIC {pic:>10} -> Type: {info.type:>15}, "
            f"Length: {info.length:>2}, Precision: {info.precision}"
        )
    print()


def demo_occurs_processing():
    """Demonstrate OCCURS clause processing."""
    print("=== OCCURS Clause Processing ===")
    
    cobol_lines = [
        "01  ORDER-RECORD.",
        "    05  ORDER-ITEMS OCCURS 3 TIMES.",
        "        10  ITEM-CODE PIC X(10).",
        "        10  ITEM-QUANTITY PIC 9(3).",
        "        10  ITEM-PRICE PIC S9(7)V99."
    ]
    
    # Process with denormalization
    fields = process_cobol(cobol_lines)
    
    print("Denormalized fields:")
    for field in fields:
        print(f"  {field['name']}: {field['pic']}")
    print()


def demo_redefines_processing():
    """Demonstrate REDEFINES clause processing."""
    print("=== REDEFINES Clause Processing ===")
    
    cobol_lines = [
        "01  DATA-RECORD.",
        "    05  TEXT-FIELD PIC X(20).",
        "    05  NUMERIC-FIELD REDEFINES TEXT-FIELD PIC 9(20)."
    ]
    
    # Process with REDEFINES handling
    fields = process_cobol(cobol_lines)
    
    print("After REDEFINES processing:")
    for field in fields:
        print(f"  {field['name']}: {field['pic']}")
    print()


def demo_name_cleaning():
    """Demonstrate name cleaning options."""
    print("=== Name Cleaning Options ===")
    
    cobol_lines = [
        "01  PREFIX-CUSTOMER-RECORD.",
        "    05  PREFIX-CUSTOMER-ID PIC 9(10).",
        "    05  PREFIX-CUSTOMER-NAME PIC X(50)."
    ]
    
    # Parse without cleaning
    parsed = parse_cobol(clean_cobol(cobol_lines))
    
    print("Original names:")
    for field in parsed:
        print(f"  {field['name']}")
    
    # Clean names with different options
    cleaned = clean_names(parsed, strip_prefix=True, make_database_safe=True)
    
    print("\nCleaned names (strip prefix + database safe):")
    for field in cleaned:
        print(f"  {field['name']}")
    print()


def demo_file_processing():
    """Demonstrate processing a COBOL file."""
    print("=== File Processing ===")
    
    # Check if example file exists
    example_file = os.path.join(
        os.path.dirname(__file__), 'customer_record.cbl'
    )
    
    if os.path.exists(example_file):
        with open(example_file, 'r') as f:
            lines = f.readlines()
        
        # Process the file
        fields = process_cobol(lines)
        
        print(f"Processed {len(fields)} fields from {example_file}:")
        for field in fields:
            print(f"  {field['name']}: {field['pic']}")
    else:
        print(f"Example file not found: {example_file}")
    print()


def demo_step_by_step():
    """Demonstrate step-by-step processing."""
    print("=== Step-by-Step Processing ===")
    
    cobol_lines = [
        "      01  CUSTOMER-RECORD.",
        "          05  CUSTOMER-ID PIC 9(10).",
        "          05  CUSTOMER-NAME PIC X(50)."
    ]
    
    print("1. Original COBOL lines:")
    for line in cobol_lines:
        print(f"   {line}")
    
    print("\n2. After cleaning:")
    cleaned = clean_cobol(cobol_lines)
    for line in cleaned:
        print(f"   {line}")
    
    print("\n3. After parsing:")
    parsed = parse_cobol(cleaned)
    for field in parsed:
        print(f"   {field['name']}: {field['pic']}")
    
    print("\n4. After name cleaning:")
    final = clean_names(parsed, make_database_safe=True)
    for field in final:
        print(f"   {field['name']}: {field['pic']}")
    print()


def main():
    """Run all demonstrations."""
    print("Python COBOL Copybook Parser - Demonstration")
    print("=" * 50)
    
    try:
        demo_basic_processing()
        demo_pic_parsing()
        demo_occurs_processing()
        demo_redefines_processing()
        demo_name_cleaning()
        demo_file_processing()
        demo_step_by_step()
        
        print("All demonstrations completed successfully!")
        
    except Exception as e:
        print(f"Error during demonstration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 