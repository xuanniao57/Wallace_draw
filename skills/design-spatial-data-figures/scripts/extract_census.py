"""Extract the 50 resident-population rows from Census 2020 Table A."""
import argparse
import csv
from pathlib import Path

from openpyxl import load_workbook


def extract(workbook, output):
    sheet = load_workbook(workbook, read_only=True, data_only=True).active
    rows = iter(sheet.values)
    for row in rows:
        if str(row[2]).strip() == "2020 Census Resident Population":
            assert str(row[5]).strip() == "2010 Census Resident Population"
            break
    records = [(name, old, new) for name, _, new, _, old, *_ in rows
               if isinstance(old, int) and name not in {
                   "District of Columbia", "U.S. Total", "Puerto Rico", "U.S. Total and Puerto Rico"
               }]
    if len({r[0] for r in records}) != 50 or len(records) != 50:
        raise ValueError("Expected one record for each of the 50 states")
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["state", "resident_2010", "resident_2020"])
        writer.writerows(records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    extract(args.workbook, args.output)
