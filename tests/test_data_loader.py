"""Tests for data_loader module."""

import csv
import tempfile
from pathlib import Path

import pytest

from coffee_report.data_loader import load_csv_file, load_multiple_files


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """Create a temporary CSV file with sample data."""
    filepath = tmp_path / "sample.csv"
    data = [
        ["student", "date", "coffee_spent", "sleep_hours", "study_hours", "mood", "exam"],
        ["Alice", "2024-06-01", "100", "7.0", "5", "good", "Math"],
        ["Alice", "2024-06-02", "150", "6.5", "6", "tired", "Math"],
        ["Bob", "2024-06-01", "200", "5.0", "8", "tired", "Math"],
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    return filepath


@pytest.fixture
def multiple_csv_files(tmp_path: Path) -> list[Path]:
    """Create multiple temporary CSV files with sample data."""
    file1 = tmp_path / "file1.csv"
    file2 = tmp_path / "file2.csv"
    
    data1 = [
        ["student", "date", "coffee_spent", "sleep_hours", "study_hours", "mood", "exam"],
        ["Alice", "2024-06-01", "100", "7.0", "5", "good", "Math"],
        ["Bob", "2024-06-01", "200", "5.0", "8", "tired", "Math"],
    ]
    data2 = [
        ["student", "date", "coffee_spent", "sleep_hours", "study_hours", "mood", "exam"],
        ["Alice", "2024-06-02", "150", "6.5", "6", "tired", "Math"],
        ["Charlie", "2024-06-01", "300", "4.0", "10", "zombie", "Math"],
    ]
    
    with open(file1, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data1)
    
    with open(file2, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data2)
    
    return [file1, file2]


class TestLoadCsvFile:
    """Tests for load_csv_file function."""
    
    def test_load_single_file(self, sample_csv_file: Path) -> None:
        """Test loading a single CSV file."""
        rows = list(load_csv_file(sample_csv_file))
        assert len(rows) == 3
        assert rows[0]["student"] == "Alice"
        assert rows[0]["coffee_spent"] == "100"
        assert rows[2]["student"] == "Bob"
    
    def test_load_empty_file(self, tmp_path: Path) -> None:
        """Test loading an empty CSV file (header only)."""
        filepath = tmp_path / "empty.csv"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("student,date,coffee_spent\n")
        
        rows = list(load_csv_file(filepath))
        assert len(rows) == 0
    
    def test_load_file_with_russian_names(self, tmp_path: Path) -> None:
        """Test loading a CSV file with Russian names."""
        filepath = tmp_path / "russian.csv"
        data = [
            ["student", "date", "coffee_spent"],
            ["Алексей Смирнов", "2024-06-01", "450"],
            ["Дарья Петрова", "2024-06-01", "200"],
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        rows = list(load_csv_file(filepath))
        assert len(rows) == 2
        assert rows[0]["student"] == "Алексей Смирнов"


class TestLoadMultipleFiles:
    """Tests for load_multiple_files function."""
    
    def test_load_multiple_files(self, multiple_csv_files: list[Path]) -> None:
        """Test loading multiple CSV files."""
        rows = load_multiple_files(multiple_csv_files)
        assert len(rows) == 4
        
        students = {row["student"] for row in rows}
        assert students == {"Alice", "Bob", "Charlie"}
    
    def test_load_no_files(self) -> None:
        """Test loading with empty file list."""
        rows = load_multiple_files([])
        assert len(rows) == 0
    
    def test_load_single_file_from_list(self, sample_csv_file: Path) -> None:
        """Test loading a single file from a list."""
        rows = load_multiple_files([sample_csv_file])
        assert len(rows) == 3

    def test_load_test_data_files(self) -> None:
        """Test loading the provided test data files."""
        data_dir = Path(__file__).parent / "data"
        files = [data_dir / "session1.csv", data_dir / "session2.csv"]
        rows = load_multiple_files(files)
        assert len(rows) == 24  # 18 from session1 + 6 from session2

        # Check Russian names are loaded correctly
        students = {row["student"] for row in rows}
        assert "Алексей Смирнов" in students
        assert "Дарья Петрова" in students
        assert "Ольга Морозова" in students
