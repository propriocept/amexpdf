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


def extract_dates_and_names(text):
    dates = []
    transaction_names = []

    for line in text.split("\n"):
        if re.match(r".*\d{2}\.\d{2}\.\d{2} \d{2}\.\d{2}\.\d{2}", line):
            date, _, name = line.split(" ", maxsplit=2)
            date = re.sub(r"[a-zA-Z]", "", date)
            dates.append(date)
            transaction_names.append(name)

    return dates, transaction_names


def extract_and_transform_amounts(text):
    transaction_amounts = []

    for line in text.split("\n"):
        if re.match(r"-?\d{1,3}(\.\d{3})*,\d{2}$", line):
            transaction_amounts.append(line)

    transaction_amounts = [
        amount.replace(".", "").replace(",", ".") for amount in transaction_amounts
    ]

    transaction_amounts = [
        f"-{amount}" if float(amount) > 0 else f"{abs(float(amount)):.2f}" for amount in transaction_amounts
    ]

    if len(transaction_amounts) > 2:
        transaction_amounts.pop(1)
        transaction_amounts.pop(-1)
        transaction_amounts.pop(-1)
        if transaction_amounts:
            min_amount = min(transaction_amounts, key=lambda x: float(x))
            transaction_amounts.remove(min_amount)

    return transaction_amounts


def validate_transactions(dates, transaction_names, transaction_amounts):
    assert len(dates) == len(transaction_names) == len(transaction_amounts), (
        f"{len(dates)=}, {len(transaction_names)=}, {len(transaction_amounts)=}"
    )


def parse_transactions(text):
    dates, transaction_names = extract_dates_and_names(text)
    transaction_amounts = extract_and_transform_amounts(text)
    validate_transactions(dates, transaction_names, transaction_amounts)

    return [(date, name, amount) for date, name, amount in zip(dates, transaction_names, transaction_amounts)]


@click.command()
@click.argument("pdf_path")
@click.argument("csv_output", default="amex_transactions.csv")
def main(pdf_path, csv_output):
    transactions = extract_transactions(pdf_path)

    with open(csv_output, "w", newline="") as csvfile:
        fieldnames = ["Date", "Name", "Amount"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=",")

        writer.writeheader()
        for date, name, amount in transactions:
            writer.writerow({"Date": date, "Name": name, "Amount": amount})


if __name__ == "__main__":
    main()
