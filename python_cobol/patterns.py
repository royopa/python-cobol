"""
Regular expression patterns for COBOL Copybook parsing.
"""

import re
from typing import ClassVar


class CobolPatterns:
    """Regular expression patterns for parsing COBOL Copybook statements."""
    
    # Base pattern for COBOL field definitions
    ROW_PATTERN_BASE: ClassVar[str] = r'^(?P<level>\d{2})\s+(?P<name>\S+)'
    
    # Optional patterns for different COBOL clauses
    ROW_PATTERN_OCCURS: ClassVar[str] = r'\s+OCCURS (?P<occurs>\d+) TIMES'
    ROW_PATTERN_INDEXED_BY: ClassVar[str] = (
        r"\s+INDEXED BY\s(?P<indexed_by>\S+)"
    )
    ROW_PATTERN_REDEFINES: ClassVar[str] = r"\s+REDEFINES\s(?P<redefines>\S+)"
    ROW_PATTERN_PIC: ClassVar[str] = r'\s+PIC\s+(?P<pic>\S+)'
    ROW_PATTERN_END: ClassVar[str] = r'\.$'
    
    # Optional pattern format
    OPT_PATTERN_FORMAT: ClassVar[str] = "({})?"
    
    # Compiled regex pattern for complete COBOL field definition
    ROW_PATTERN: ClassVar[re.Pattern] = re.compile(
        ROW_PATTERN_BASE + 
        OPT_PATTERN_FORMAT.format(ROW_PATTERN_REDEFINES) + 
        OPT_PATTERN_FORMAT.format(ROW_PATTERN_OCCURS) + 
        OPT_PATTERN_FORMAT.format(ROW_PATTERN_INDEXED_BY) + 
        OPT_PATTERN_FORMAT.format(ROW_PATTERN_PIC) + 
        ROW_PATTERN_END
    )
    
    # PIC clause patterns
    PIC_PATTERN_REPEATS: ClassVar[re.Pattern] = re.compile(r'(.)\((\d+)\)')
    PIC_PATTERN_FLOAT: ClassVar[re.Pattern] = re.compile(r'S?[9Z]*[.V][9Z]+')
    PIC_PATTERN_INTEGER: ClassVar[re.Pattern] = re.compile(r'S?[9Z]+') 