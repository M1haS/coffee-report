"""Tests for reports module."""

import pytest

from coffee_report.reports import (
    ReportRegistry,
    median_coffee_report,
    registry,
)


class TestMedianCoffeeReport:
    """Tests for median_coffee_report function."""
    
    def test_median_coffee_single_student(self) -> None:
        """Test median calculation for a single student."""
        rows = [
            {"student": "Alice", "coffee_spent": "100"},
            {"student": "Alice", "coffee_spent": "200"},
            {"student": "Alice", "coffee_spent": "300"},
        ]
        result = median_coffee_report(rows)
        assert "Alice" in result
        assert "200" in result

    def test_median_coffee_multiple_students(self) -> None:
        """Test median calculation for multiple students."""
        rows = [
            {"student": "Alice", "coffee_spent": "100"},
            {"student": "Alice", "coffee_spent": "150"},
            {"student": "Bob", "coffee_spent": "200"},
            {"student": "Bob", "coffee_spent": "250"},
        ]
        result = median_coffee_report(rows)

        # Alice median: 125, Bob median: 225
        # Bob should be first (higher spending)
        assert result.index("Bob") < result.index("Alice")
        assert "125" in result
        assert "225" in result
    
    def test_median_coffee_sorted_descending(self) -> None:
        """Test that results are sorted by median spending descending."""
        rows = [
            {"student": "Low", "coffee_spent": "10"},
            {"student": "Low", "coffee_spent": "20"},
            {"student": "High", "coffee_spent": "500"},
            {"student": "High", "coffee_spent": "600"},
            {"student": "Medium", "coffee_spent": "100"},
            {"student": "Medium", "coffee_spent": "150"},
        ]
        result = median_coffee_report(rows)
        
        # Check order: High, Medium, Low
        high_pos = result.index("High")
        medium_pos = result.index("Medium")
        low_pos = result.index("Low")
        
        assert high_pos < medium_pos < low_pos
    
    def test_median_coffee_odd_number_of_entries(self) -> None:
        """Test median with odd number of entries (middle value)."""
        rows = [
            {"student": "Alice", "coffee_spent": "100"},
            {"student": "Alice", "coffee_spent": "200"},
            {"student": "Alice", "coffee_spent": "300"},
        ]
        result = median_coffee_report(rows)
        assert "200" in result

    def test_median_coffee_even_number_of_entries(self) -> None:
        """Test median with even number of entries (average of two middle)."""
        rows = [
            {"student": "Alice", "coffee_spent": "100"},
            {"student": "Alice", "coffee_spent": "200"},
            {"student": "Alice", "coffee_spent": "300"},
            {"student": "Alice", "coffee_spent": "400"},
        ]
        result = median_coffee_report(rows)
        # Median of [100, 200, 300, 400] = (200 + 300) / 2 = 250
        assert "250" in result
    
    def test_median_coffee_empty_data(self) -> None:
        """Test with empty data."""
        result = median_coffee_report([])
        assert "Student" in result
        assert "Median Coffee Spent" in result
    
    def test_median_coffee_table_format(self) -> None:
        """Test that output is formatted as a table."""
        rows = [
            {"student": "Alice", "coffee_spent": "100"},
        ]
        result = median_coffee_report(rows)
        assert "+" in result or "|" in result  # Table borders


class TestReportRegistry:
    """Tests for ReportRegistry class."""
    
    def test_register_report(self) -> None:
        """Test registering a report."""
        registry = ReportRegistry()
        
        def dummy_report(rows: list) -> str:
            return "dummy"
        
        registry.register("dummy", dummy_report)
        assert registry.get("dummy") == dummy_report
    
    def test_get_unknown_report(self) -> None:
        """Test getting an unknown report."""
        registry = ReportRegistry()
        assert registry.get("unknown") is None
    
    def test_list_reports(self) -> None:
        """Test listing registered reports."""
        registry = ReportRegistry()
        registry.register("report1", lambda rows: "r1")
        registry.register("report2", lambda rows: "r2")
        
        reports = registry.list_reports()
        assert "report1" in reports
        assert "report2" in reports
        assert len(reports) == 2
    
    def test_global_registry_has_median_coffee(self) -> None:
        """Test that global registry has median-coffee report."""
        assert registry.get("median-coffee") is not None
        assert "median-coffee" in registry.list_reports()

    def test_median_coffee_with_test_data(self) -> None:
        """Test median calculation with the provided test data files."""
        from coffee_report.data_loader import load_multiple_files
        from pathlib import Path

        data_dir = Path(__file__).parent / "data"
        files = [data_dir / "session1.csv", data_dir / "session2.csv"]
        rows = load_multiple_files(files)

        result = median_coffee_report(rows)

        # Check all students are in the report
        assert "Алексей Смирнов" in result
        assert "Дарья Петрова" in result
        assert "Иван Кузнецов" in result
        assert "Мария Соколова" in result
        assert "Павел Новиков" in result
        assert "Елена Волкова" in result
        assert "Ольга Морозова" in result
        assert "Дмитрий Лебедев" in result

        # Check table headers
        assert "Student" in result
        assert "Median Coffee Spent" in result
