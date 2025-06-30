"""
Core functionality for COBOL Copybook parsing and processing.
"""

import logging
from typing import Dict, List

from .models import PicInfo
from .patterns import CobolPatterns

# Configure logging
logger = logging.getLogger(__name__)


def parse_pic_string(pic_str: str) -> PicInfo:
    """
    Parse a PIC string and return information about the data type.
    
    Args:
        pic_str: The PIC clause string (e.g., 'X(10)', 'S9(5)V99')
        
    Returns:
        PicInfo object containing type, length, and precision information
        
    Examples:
        >>> parse_pic_string('X(10)')
        PicInfo(type='Char', length=10, precision=0)
        >>> parse_pic_string('S9(5)V99')
        PicInfo(type='Signed Float', length=7, precision=2)
    """
    # Expand repeating characters (e.g., X(10) -> XXXXXXXXXX)
    while True:
        match = CobolPatterns.PIC_PATTERN_REPEATS.search(pic_str)
        if not match:
            break
        
        char = match.group(1)
        count = int(match.group(2))
        expanded_str = char * count
        
        pic_str = CobolPatterns.PIC_PATTERN_REPEATS.sub(
            expanded_str, pic_str, 1
        )

    # Determine data type
    if CobolPatterns.PIC_PATTERN_FLOAT.match(pic_str):
        data_type = 'Float'
    elif CobolPatterns.PIC_PATTERN_INTEGER.match(pic_str):
        data_type = 'Integer'
    else:
        data_type = 'Char'

    # Handle signed numbers
    if pic_str.startswith('S'):
        data_type = f"Signed {data_type}"
        pic_str = pic_str[1:]

    # Calculate precision (decimal places)
    decimal_pos = 0
    if 'V' in pic_str:
        v_index = pic_str.index('V')
        decimal_pos = len(pic_str[v_index + 1:])
        pic_str = pic_str.replace('V', '')

    return PicInfo(
        type=data_type,
        length=len(pic_str),
        precision=decimal_pos
    )


def clean_cobol(lines: List[str]) -> List[str]:
    """
    Clean COBOL lines by converting multi-line statements to single lines.
    
    Args:
        lines: List of raw COBOL lines
        
    Returns:
        List of cleaned, single-line COBOL statements
        
    Examples:
        >>> lines = [
        ...     "      01  EXAMPLE-GROUP.",
        ...     "          05  FIELD-1 PIC X(10)."
        ... ]
        >>> clean_cobol(lines)
        ['01 EXAMPLE-GROUP.', '05 FIELD-1 PIC X(10).']
    """
    holder: List[str] = []
    output: List[str] = []

    for row in lines:
        # Extract content from columns 7-72 (standard COBOL format)
        row = row[6:72].rstrip()

        # Skip empty lines and comments
        if not row or row[0] in ('*', '/'):
            continue

        # Add to holder, stripping leading spaces for continuation lines
        if not holder:
            holder.append(row)
        else:
            holder.append(row.strip())

        # If line ends with period, it's a complete statement
        if row.endswith('.'):
            output.append(' '.join(holder))
            holder = []

    # Warn about incomplete statements
    if holder:
        logger.warning(
            "Found unfinished COBOL statement: %s", 
            ' '.join(holder)
        )

    return output


def parse_cobol(lines: List[str]) -> List[Dict]:
    """
    Parse COBOL lines into structured data.
    
    Args:
        lines: List of cleaned COBOL lines
        
    Returns:
        List of dictionaries containing parsed field information
        
    Examples:
        >>> lines = ['01 EXAMPLE-GROUP.', '05 FIELD-1 PIC X(10).']
        >>> parse_cobol(lines)
        [{'level': 1, 'name': 'EXAMPLE-GROUP', ...}, ...]
    """
    output: List[Dict] = []
    intify_fields = ["level", "occurs"]

    for row in lines:
        match = CobolPatterns.ROW_PATTERN.match(row.strip())
        
        if not match:
            logger.warning("Found unmatched row: %s", row.strip())
            continue

        field_data = match.groupdict()

        # Convert numeric fields
        for field in intify_fields:
            if field_data[field] is not None:
                field_data[field] = int(field_data[field])

        # Parse PIC information if present
        if field_data['pic'] is not None:
            field_data['pic_info'] = parse_pic_string(field_data['pic'])

        # Handle REDEFINES
        if field_data['redefines'] is not None:
            try:
                # Find the field being redefined
                redefined_item_index, redefined_item = next(
                    (index, item) for index, item in enumerate(output)
                    if item['name'] == field_data['redefines']
                )

                # Get the subgroup of the redefined item
                related_group = get_subgroup(
                    redefined_item['level'],
                    output[redefined_item_index + 1:]
                )

                # Remove the redefined item and its subgroup
                output = (
                    output[:redefined_item_index] + 
                    output[redefined_item_index + len(related_group) + 1:]
                )

                field_data['redefines'] = None
                
            except StopIteration:
                logger.warning(
                    "Could not find field to be redefined (%s) for row: %s",
                    field_data['redefines'], row.strip()
                )

        output.append(field_data)

    return output


def get_subgroup(parent_level: int, lines: List[Dict]) -> List[Dict]:
    """
    Get all lines that have a higher level than the parent level.
    
    Args:
        parent_level: The level number of the parent field
        lines: List of field dictionaries
        
    Returns:
        List of fields that belong to the subgroup
    """
    output: List[Dict] = []

    for row in lines:
        if row["level"] > parent_level:
            output.append(row)
        else:
            break

    return output


def denormalize_cobol(lines: List[Dict]) -> List[Dict]:
    """
    Denormalize COBOL by expanding OCCURS clauses.
    
    Args:
        lines: List of parsed COBOL field dictionaries
        
    Returns:
        List of denormalized field dictionaries
    """
    return handle_occurs(lines, 1)


def handle_occurs(
    lines: List[Dict], 
    occurs: int, 
    level_diff: int = 0, 
    name_postfix: str = ""
) -> List[Dict]:
    """
    Handle OCCURS clauses by expanding them into multiple fields.
    
    Args:
        lines: List of field dictionaries
        occurs: Number of occurrences
        level_diff: Level difference to apply
        name_postfix: Postfix to add to field names
        
    Returns:
        List of expanded field dictionaries
    """
    output: List[Dict] = []

    for i in range(1, occurs + 1):
        skip_till = 0
        new_name_postfix = (
            name_postfix if occurs == 1 
            else f"{name_postfix}-{i}"
        )

        for index, row in enumerate(lines):
            if index < skip_till:
                continue

            new_row = row.copy()
            new_row['level'] += level_diff
            new_row['indexed_by'] = None  # Not needed when flattened

            if row['occurs'] is None:
                # Simple field without OCCURS
                new_row['name'] = f"{row['name']}{new_name_postfix}"
                output.append(new_row)
            
            else:
                if row["pic"] is not None:
                    # Field with PIC and OCCURS - repeat the field
                    new_row['occurs'] = None

                    for j in range(1, row["occurs"] + 1):
                        row_to_add = new_row.copy()
                        row_to_add["name"] = (
                            f"{row['name']}{new_name_postfix}-{j}"
                        )
                        output.append(row_to_add)

                else:
                    # Group with OCCURS - get subgroup and recurse
                    occur_lines = get_subgroup(
                        row['level'], 
                        lines[index + 1:]
                    )

                    new_level_diff = (
                        level_diff + row['level'] - occur_lines[0]['level']
                    )

                    output.extend(
                        handle_occurs(
                            occur_lines, 
                            row['occurs'], 
                            new_level_diff, 
                            new_name_postfix
                        )
                    )

                    skip_till = index + len(occur_lines) + 1

    return output


def clean_names(
    lines: List[Dict],
    ensure_unique_names: bool = False,
    strip_prefix: bool = False,
    make_database_safe: bool = False
) -> List[Dict]:
    """
    Clean field names according to specified options.
    
    Args:
        lines: List of field dictionaries
        ensure_unique_names: Whether to ensure all names are unique
        strip_prefix: Whether to strip prefixes from names
        make_database_safe: Whether to make names database-safe
        
    Returns:
        List of field dictionaries with cleaned names
    """
    names: Dict[str, int] = {}

    for row in lines:
        if strip_prefix:
            # Remove prefix up to first dash
            dash_index = row['name'].find('-')
            if dash_index != -1:
                row['name'] = row['name'][dash_index + 1:]

            if row['indexed_by'] is not None:
                dash_index = row['indexed_by'].find('-')
                if dash_index != -1:
                    row['indexed_by'] = row['indexed_by'][dash_index + 1:]

        if ensure_unique_names:
            # Ensure unique names by adding suffix if needed
            base_name = row['name']
            i = 1
            while (base_name if i == 1 else f"{base_name}-{i}") in names:
                i += 1

            final_name = base_name if i == 1 else f"{base_name}-{i}"
            names[final_name] = 1

            if i > 1:
                row['name'] = final_name

        if make_database_safe:
            # Replace dashes with underscores for database compatibility
            row['name'] = row['name'].replace("-", "_")

    return lines


def process_cobol(lines: List[str]) -> List[Dict]:
    """
    Complete COBOL processing pipeline.
    
    Args:
        lines: List of raw COBOL lines
        
    Returns:
        List of processed field dictionaries
    """
    return clean_names(
        denormalize_cobol(parse_cobol(clean_cobol(lines))),
        ensure_unique_names=True,
        strip_prefix=True,
        make_database_safe=True
    )


def print_cobol(lines: List[Dict]) -> None:
    """
    Print COBOL fields in Copybook format.
    
    Args:
        lines: List of field dictionaries to print
    """
    output: List[str] = []
    default_padding = ' ' * 7
    levels: List[int] = [0]

    for row in lines:
        row_output: List[str] = []

        # Handle indentation based on level
        if row['level'] > levels[-1]:
            levels.append(row['level'])
        else:
            while row['level'] < levels[-1]:
                levels.pop()

        # Build field definition
        row_output.append((len(levels) - 1) * '  ')
        row_output.append(f"{row['level']:02d}  ")
        row_output.append(row['name'])

        if row['indexed_by'] is not None:
            row_output.append(f" INDEXED BY {row['indexed_by']}")

        if row['occurs'] is not None:
            row_output.append(f" OCCURS {row['occurs']:04d} TIMES")

        if row['pic'] is not None:
            row_output.append(f" PIC {row['pic']}")

        row_output.append(".")

        # Format output to 80-character lines
        max_data_length = 66
        outp = default_padding

        for data in row_output:
            if len(outp) + len(data) + 1 > max_data_length:
                # Complete current line
                outp += (80 - len(outp)) * ' '
                output.append(outp)

                # Start continuation line
                outp = (
                    default_padding + 
                    (len(levels) - 1) * '  ' + 
                    '    '
                )

            outp += data

        # Complete final line
        outp += (80 - len(outp)) * ' '
        output.append(outp)

    print("\n".join(output)) 