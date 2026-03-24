"""Module for loading and parsing CSV data files."""

import csv
from pathlib import Path
from typing import Iterator


def load_csv_file(filepath: Path) -> Iterator[dict]:
    """Load a single CSV file and yield rows as dictionaries.
    
    Args:
        filepath: Path to the CSV file.
        
    Yields:
        Dictionary for each row with column names as keys.
    """
    with open(filepath, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def load_multiple_files(filepaths: list[Path]) -> list[dict]:
    """Load multiple CSV files and return all rows combined.
    
    Args:
        filepaths: List of paths to CSV files.
        
    Returns:
        List of all rows from all files.
    """
    all_rows = []
    for filepath in filepaths:
        all_rows.extend(load_csv_file(filepath))
    return all_rows
