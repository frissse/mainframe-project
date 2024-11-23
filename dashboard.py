from rich.console import Console
from rich.table import Table

console = Console()

# Create a table
table = Table(title="System Dashboard")

# Add columns
table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
table.add_column("Value", justify="right", style="magenta")

# Add rows
table.add_row("CPU Usage", "25%")
table.add_row("Memory Usage", "60%")
table.add_row("Disk Space", "40 GB Free")

# Print the table
console.print(table)