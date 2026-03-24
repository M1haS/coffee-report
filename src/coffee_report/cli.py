"""Command-line interface for coffee report generation."""

import argparse
import sys
from pathlib import Path

from .data_loader import load_multiple_files
from .reports import registry


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments.
    
    Args:
        args: List of arguments (defaults to sys.argv[1:]).
        
    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Generate reports from student exam preparation CSV data."
    )
    parser.add_argument(
        "--files",
        nargs="+",
        type=str,
        required=True,
        help="Paths to CSV files with student data."
    )
    parser.add_argument(
        "--report",
        type=str,
        default="median-coffee",
        help="Report type to generate (default: median-coffee)."
    )
    return parser.parse_args(args)


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: List of command-line arguments.
        
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parsed_args = parse_args(args)
    
    # Validate file paths
    filepaths = []
    for file_path in parsed_args.files:
        path = Path(file_path)
        if not path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            return 1
        if not path.is_file():
            print(f"Error: Not a file: {file_path}", file=sys.stderr)
            return 1
        filepaths.append(path)
    
    # Validate report type
    report_func = registry.get(parsed_args.report)
    if report_func is None:
        available_reports = ", ".join(registry.list_reports())
        print(
            f"Error: Unknown report type '{parsed_args.report}'. "
            f"Available reports: {available_reports}",
            file=sys.stderr
        )
        return 1
    
    # Load data and generate report
    rows = load_multiple_files(filepaths)
    if not rows:
        print("Warning: No data found in the provided files.", file=sys.stderr)
        return 0
    
    report_output = report_func(rows)
    print(report_output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
