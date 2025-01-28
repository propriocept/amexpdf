# AmexPDF

AmexPDF is a Python tool to extract transaction information from American Express PDF statements and save it to a CSV file.

## Installation

To install, run:
```bash
uv build
uv tool install .
```

## Usage

To extract transactions from a PDF statement and save them to a CSV file, run:
```bash
uv run python -m amexpdf <pdf_path> [csv_output]
```

- `pdf_path`: Path to the PDF file to extract transactions from.
- `csv_output` (Optional): Path to the output CSV file. Defaults to `amex_transactions.csv`.

## Example

```bash
uv run python -m amexpdf /path/to/statement.pdf transactions.csv
```

This will extract the transactions from `statement.pdf` and save them to `transactions.csv`.

## Development

### Install editable version
```bash
uv build
uv pip install -e .
```

### Running Tests

To run the tests afer installing, use:
```bash
uv run pytest
```
