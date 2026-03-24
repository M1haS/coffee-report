"""Report generation module with extensible architecture."""

from statistics import median
from typing import Callable

from tabulate import tabulate


class ReportRegistry:
    """Registry for report types with extensible architecture."""
    
    def __init__(self):
        self._reports: dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable) -> None:
        """Register a report generator function.
        
        Args:
            name: Report name identifier.
            func: Function that generates the report.
        """
        self._reports[name] = func
    
    def get(self, name: str) -> Callable | None:
        """Get a report generator by name.
        
        Args:
            name: Report name identifier.
            
        Returns:
            Report generator function or None if not found.
        """
        return self._reports.get(name)
    
    def list_reports(self) -> list[str]:
        """List all registered report names."""
        return list(self._reports.keys())


def median_coffee_report(rows: list[dict]) -> str:
    """Generate median coffee spending report per student.
    
    Args:
        rows: List of data rows with student information.
        
    Returns:
        Formatted table string with students and their median coffee spending.
    """
    # Group coffee_spent by student
    student_spending: dict[str, list[float]] = {}
    for row in rows:
        student = row["student"]
        coffee_spent = float(row["coffee_spent"])
        if student not in student_spending:
            student_spending[student] = []
        student_spending[student].append(coffee_spent)
    
    # Calculate median for each student
    results = []
    for student, spending_list in student_spending.items():
        median_spending = median(spending_list)
        results.append((student, median_spending))
    
    # Sort by median spending descending
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Format as table
    table_data = [(student, f"{spending:.2f}") for student, spending in results]
    return tabulate(
        table_data,
        headers=["Student", "Median Coffee Spent"],
        tablefmt="grid"
    )


# Create global registry instance
registry = ReportRegistry()

# Register default reports
registry.register("median-coffee", median_coffee_report)
