"""Initial exploration using pypdf."""

# %%
import re

from pypdf import PdfReader

# %%
# Load the PDF file from Users/anil/OneDrive/Documents/Money/Bank statements/Amex
pdf = PdfReader(
    "/Users/anil/OneDrive/Documents/Money/Bank statements/Amex/2024-10-02.pdf"
)

# %%
## The pdf contains transaction information in a table split across two columns in the page.
## Find the transaction information and print it.

# %%
dates = []
transaction_names = []
transaction_amounts = []

for page in pdf.pages[1:]:
    for line in page.extract_text().split("\n"):
        # If it is the transaction name, the line starts with two columns as dates in DD.MM.YY format
        # Collect the transaction date and name using regex.
        if re.match(r"\d{2}\.\d{2}\.\d{2}", line):
            date, _, name = line.split(" ", maxsplit=2)
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
# %%
# Remove the second, and last two transaction amounts as they are not transactions.
if len(transaction_amounts) > 2:
    transaction_amounts.pop(1)
    transaction_amounts.pop(-1)
    transaction_amounts.pop(-1)
if transaction_amounts:
    max_amount = max(
        transaction_amounts, key=lambda x: float(x.replace(".", "").replace(",", "."))
    )
    transaction_amounts.remove(max_amount)

# %%
print(f"{len(dates)=}, {len(transaction_names)=}, {len(transaction_amounts)=}")

# %%
assert len(dates) == len(transaction_names) == len(transaction_amounts)

# %%
for line in zip(dates, transaction_names, transaction_amounts):
    print(line)
