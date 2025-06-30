"""
Command-line interface for the COBOL Copybook parser.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from .core import (
    parse_cobol, clean_cobol, denormalize_cobol, clean_names, print_cobol
)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )


def read_cobol_file(file_path: Path) -> List[str]:
    """
    Read COBOL file and return lines.
    
    Args:
        file_path: Path to the COBOL file
        
    Returns:
        List of lines from the file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find file: {file_path}")
    
    if not file_path.is_file():
        raise IOError(f"Path is not a file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.readlines()


def process_cobol_file(
    file_path: Path,
    skip_all_processing: bool = False,
    skip_unique_names: bool = False,
    skip_denormalize: bool = False,
    skip_strip_prefix: bool = False,
    verbose: bool = False
) -> None:
    """
    Process a COBOL file according to the specified options.
    
    Args:
        file_path: Path to the COBOL file
        skip_all_processing: Skip all processing steps
        skip_unique_names: Skip making names unique
        skip_denormalize: Skip denormalization
        skip_strip_prefix: Skip stripping prefixes
        verbose: Enable verbose logging
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Read the file
        lines = read_cobol_file(file_path)
        logger.info(f"Read {len(lines)} lines from {file_path}")
        
        # Parse the COBOL
        parsed_lines = parse_cobol(clean_cobol(lines))
        logger.info(f"Parsed {len(parsed_lines)} fields")
        
        if not skip_all_processing:
            # Apply processing steps based on flags
            if not skip_denormalize:
                parsed_lines = denormalize_cobol(parsed_lines)
                logger.info("Applied denormalization")
            
            if not skip_strip_prefix or not skip_unique_names:
                parsed_lines = clean_names(
                    parsed_lines,
                    ensure_unique_names=not skip_unique_names,
                    strip_prefix=not skip_strip_prefix,
                    make_database_safe=True
                )
                logger.info("Applied name cleaning")
        
        # Print the result
        print_cobol(parsed_lines)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Parse and process COBOL Copybook files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s example.cbl                    # Process with all options enabled
  %(prog)s example.cbl --skip-denormalize # Skip denormalization
  %(prog)s example.cbl --verbose          # Enable verbose logging
        """
    )
    
    parser.add_argument(
        "filename",
        type=Path,
        help="Path to the COBOL Copybook file"
    )
    
    parser.add_argument(
        "--skip-all-processing",
        action="store_true",
        help="Skip all processing steps (only parse and clean)"
    )
    
    parser.add_argument(
        "--skip-unique-names",
        action="store_true",
        help="Skip making all field names unique"
    )
    
    parser.add_argument(
        "--skip-denormalize",
        action="store_true",
        help="Skip denormalizing OCCURS clauses"
    )
    
    parser.add_argument(
        "--skip-strip-prefix",
        action="store_true",
        help="Skip stripping prefixes from field names"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    return parser


def main() -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        process_cobol_file(
            file_path=args.filename,
            skip_all_processing=args.skip_all_processing,
            skip_unique_names=args.skip_unique_names,
            skip_denormalize=args.skip_denormalize,
            skip_strip_prefix=args.skip_strip_prefix,
            verbose=args.verbose
        )
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 