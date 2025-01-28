"""Extract the transaction information from an American Express PDF statement.

Usage:
    python -m amexpdf <pdf_path> [csv_output]

Arguments:
    pdf_path    Path to the PDF file to extract transactions from.
    csv_output  (Optional) Path to the output CSV file. Defaults to 'amex_transactions.csv'.
"""

from pypdf import PdfReader
import re
import csv
import click


def extract_transactions(pdf_path):
    transactions = []
    with open(pdf_path, "rb") as file:
        reader = PdfReader(pdf_path)
        for page in reader.pages[1:]:
            text = page.extract_text()
            transactions.extend(parse_transactions(text))
    return transactions


def parse_transactions(text):
    out: list[tuple[str, str, str]] = []
    dates: list[str] = []
    transaction_names: list[str] = []
    transaction_amounts: list[str] = []

    for line in text.split("\n"):
        # If it is the transaction name, the line starts with two columns as dates in DD.MM.YY format
        # Collect the transaction date and name using regex.
        if re.match(r".*\d{2}\.\d{2}\.\d{2} \d{2}\.\d{2}\.\d{2}", line):
            date, _, name = line.split(" ", maxsplit=2)
            # Remove all letters from the date string
            date = re.sub(r"[a-zA-Z]", "", date)
            dates.append(date)
            transaction_names.append(name)
        # Skip the line if it contains an interest rate. It is not a transaction.
        # An interest rate is a number with a comma as the decimal separator and a percentage sign.
        elif re.match(r".*\d+,\d+%", line):
            continue
        # The transaction amount line contains only a number, with a decimal point as a separator for thousands, and a comma as the decimal separator.
        # It can be negative or positive.
        elif re.match(r"-?\d{1,3}(\.\d{3})*,\d{2}$", line):
            transaction_amounts.append(line)

    # Let's just convert the numbers to proper floats, and then back again to strings with non-european decimal separators.
    transaction_amounts = [
        amount.replace(".", "").replace(",", ".") for amount in transaction_amounts
    ]
    transaction_amounts_float = [float(amount) for amount in transaction_amounts]
    # Include commas as thousands separators.
    transaction_amounts = [f"{amount:,.2f}" for amount in transaction_amounts_float]

    # Remove the second, and last two transaction amounts as they are not transactions.
    if len(transaction_amounts) > 2:
        transaction_amounts.pop(1)
        transaction_amounts.pop(-1)
        transaction_amounts.pop(-1)
        max_amount = max(transaction_amounts, key=lambda x: float(x))
        transaction_amounts.remove(max_amount)

    assert len(dates) == len(transaction_names) == len(transaction_amounts), (
        f"{len(dates)=}, {len(transaction_names)=}, {len(transaction_amounts)=}"
    )

    for date, name, amount in zip(dates, transaction_names, transaction_amounts):
        out.append((date, name, amount))

    return out


@click.command()
@click.argument("pdf_path")
@click.argument("csv_output", default="amex_transactions.csv")
def main(pdf_path, csv_output):
    transactions = extract_transactions(pdf_path)

    with open(csv_output, "w", newline="") as csvfile:
        fieldnames = ["Date", "Name", "Amount"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")

        writer.writeheader()
        for date, name, amount in transactions:
            writer.writerow({"Date": date, "Name": name, "Amount": amount})


if __name__ == "__main__":
    main()
