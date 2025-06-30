#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python COBOL Copybook Parser

A Python library to parse and denormalize COBOL Copybooks.
Supports REDEFINES, INDEXED BY, OCCURS statements and more.
"""

from .core import (
    clean_cobol,
    parse_cobol,
    denormalize_cobol,
    clean_names,
    process_cobol,
    print_cobol,
)
from .models import CobolField, PicInfo
from .patterns import CobolPatterns

__version__ = "1.0.0"
__author__ = "Paulus Schoutsen, Rodrigo"
__email__ = "paulus@paulusschoutsen.nl, rodrigo@example.com"

__all__ = [
    # Core functions
    "clean_cobol",
    "parse_cobol", 
    "denormalize_cobol",
    "clean_names",
    "process_cobol",
    "print_cobol",
    # Models
    "CobolField",
    "PicInfo",
    # Patterns
    "CobolPatterns",
]
