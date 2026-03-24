"""Tests for CLI module."""

import csv
import tempfile
from pathlib import Path

import pytest

from coffee_report.cli import main, parse_args


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


class TestParseArgs:
    """Tests for parse_args function."""
    
    def test_parse_files_required(self) -> None:
        """Test that --files is required."""
        with pytest.raises(SystemExit):
            parse_args([])
    
    def test_parse_default_report(self) -> None:
        """Test default report value."""
        args = parse_args(["--files", "data.csv"])
        assert args.report == "median-coffee"
    
    def test_parse_custom_report(self) -> None:
        """Test custom report value."""
        args = parse_args(["--files", "data.csv", "--report", "custom-report"])
        assert args.report == "custom-report"
    
    def test_parse_multiple_files(self) -> None:
        """Test parsing multiple files."""
        args = parse_args(["--files", "file1.csv", "file2.csv", "file3.csv"])
        assert args.files == ["file1.csv", "file2.csv", "file3.csv"]


class TestMain:
    """Tests for main function."""
    
    def test_main_success(self, sample_csv_file: Path, capsys: pytest.CaptureFixture) -> None:
        """Test successful execution."""
        exit_code = main(["--files", str(sample_csv_file)])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out
    
    def test_main_file_not_found(self, capsys: pytest.CaptureFixture) -> None:
        """Test error when file doesn't exist."""
        exit_code = main(["--files", "/nonexistent/file.csv"])
        assert exit_code == 1
        
        captured = capsys.readouterr()
        assert "Error" in captured.err
        assert "not found" in captured.err
    
    def test_main_unknown_report(self, sample_csv_file: Path, capsys: pytest.CaptureFixture) -> None:
        """Test error when report type is unknown."""
        exit_code = main(["--files", str(sample_csv_file), "--report", "unknown-report"])
        assert exit_code == 1
        
        captured = capsys.readouterr()
        assert "Error" in captured.err
        assert "unknown-report" in captured.err
    
    def test_main_median_coffee_report(self, sample_csv_file: Path, capsys: pytest.CaptureFixture) -> None:
        """Test median-coffee report generation."""
        exit_code = main(["--files", str(sample_csv_file), "--report", "median-coffee"])
        assert exit_code == 0

        captured = capsys.readouterr()
        # Alice: median of [100, 150] = 125
        # Bob: median of [200] = 200
        # Bob should be first (higher spending)
        assert "125" in captured.out
        assert "200" in captured.out
    
    def test_main_multiple_files(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test processing multiple files."""
        file1 = tmp_path / "file1.csv"
        file2 = tmp_path / "file2.csv"
        
        data1 = [
            ["student", "date", "coffee_spent"],
            ["Alice", "2024-06-01", "100"],
        ]
        data2 = [
            ["student", "date", "coffee_spent"],
            ["Bob", "2024-06-01", "200"],
        ]
        
        with open(file1, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data1)
        
        with open(file2, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(data2)
        
        exit_code = main(["--files", str(file1), str(file2)])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert "Alice" in captured.out
        assert "Bob" in captured.out
    
    def test_main_empty_files(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test processing files with no data rows."""
        filepath = tmp_path / "empty.csv"
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("student,date,coffee_spent\n")
        
        exit_code = main(["--files", str(filepath)])
        assert exit_code == 0
        
        captured = capsys.readouterr()
        assert "Warning" in captured.err
    
    def test_main_not_a_file(self, tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
        """Test error when path is not a file."""
        exit_code = main(["--files", str(tmp_path)])
        assert exit_code == 1

        captured = capsys.readouterr()
        assert "Error" in captured.err
        assert "Not a file" in captured.err

    def test_main_with_test_data_files(self, capsys: pytest.CaptureFixture) -> None:
        """Test with the provided test data files."""
        data_dir = Path(__file__).parent / "data"
        files = [str(data_dir / "session1.csv"), str(data_dir / "session2.csv")]
        exit_code = main(["--files"] + files)
        assert exit_code == 0

        captured = capsys.readouterr()
        # Check all students are in the output
        assert "Алексей Смирнов" in captured.out
        assert "Дарья Петрова" in captured.out
        assert "Иван Кузнецов" in captured.out
        assert "Мария Соколова" in captured.out
        assert "Павел Новиков" in captured.out
        assert "Елена Волкова" in captured.out
        assert "Ольга Морозова" in captured.out
        assert "Дмитрий Лебедев" in captured.out

        # Check table format
        assert "Student" in captured.out
        assert "Median Coffee Spent" in captured.out
