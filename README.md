# Test Remote MCP Server - Expense Tracker

A FastMCP-based remote server for managing expenses with category support and detailed tracking.

## Overview

This project provides a Model Context Protocol (MCP) implementation for an Expense Tracker service. It uses FastMCP to expose expense management tools that can be integrated with Claude Desktop or other MCP-compatible clients.

## Features

- **Add Expenses**: Log new expense entries with date, amount, category, and notes
- **Category Support**: Organize expenses by category and subcategory
- **Database Persistence**: SQLite database for reliable data storage
- **Async Operations**: Built with async/await for efficient concurrent operations
- **Proxy Server**: Includes a proxy server configuration for remote access

## Project Structure

```
test-remote-mcp-server/
├── main.py              # Main FastMCP server with expense tracking tools
├── proxy.py             # Proxy configuration for remote server access
├── categories.json      # Category definitions for expenses
├── pyproject.toml       # Project configuration and dependencies
└── README.md            # This file
```

## Installation

### Prerequisites
- Python 3.11 or higher
- pip or Poetry package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/deepakbishnoi717/test-remote-mcp-server.git
cd test-remote-mcp-server
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

Or using Poetry:
```bash
poetry install
```

## Usage

### Running the Local Server

Start the local FastMCP server:
```bash
python main.py
```

### Using the Proxy Server

To run the proxy server that connects to a remote FastMCP Cloud instance:
```bash
python proxy.py
```

## Available Tools

### add_expense
Add a new expense entry to the database.

**Parameters:**
- `date` (string): Date of the expense (e.g., "2024-01-15")
- `amount` (float): Amount spent
- `category` (string): Main expense category
- `subcategory` (string, optional): Subcategory for the expense
- `note` (string, optional): Additional notes about the expense

**Example:**
```python
await add_expense("2024-01-15", 25.50, "Food", "Groceries", "Weekly shopping")
```

## Database

The project uses SQLite for data persistence. The database is automatically initialized on first run and includes:
- Automatic table creation
- WAL (Write-Ahead Logging) for better concurrency
- Categories table mapping for expense organization

Database file location: System temporary directory (`expenses.db`)

## Technology Stack

- **FastMCP**: Model Context Protocol framework
- **aiosqlite**: Asynchronous SQLite driver
- **Python 3.11+**: Modern Python with async support

## Configuration

### Categories
Expense categories are defined in `categories.json`. Customize this file to add or modify expense categories for your use case.

## Integration with Claude Desktop

To use this server with Claude Desktop:

1. Set up the server following the installation steps above
2. Configure Claude Desktop to connect to this MCP server
3. Use natural language queries to manage your expenses

## License

This project is open source and available under the appropriate license.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## Support

For issues or questions, please open an issue on GitHub at:
https://github.com/deepakbishnoi717/test-remote-mcp-server/issues
