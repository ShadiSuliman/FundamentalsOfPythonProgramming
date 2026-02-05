from __future__ import annotations

import csv
from datetime import datetime, date
from collections import defaultdict
from typing import Dict, List, Tuple


FINNISH_WEEKDAYS: Dict[int, str] = {
    0: "maanantai",
    1: "tiistai",
    2: "keskiviikko",
    3: "torstai",
    4: "perjantai",
    5: "lauantai",
    6: "sunnuntai",
}


def to_finnish_number(value: float) -> str:
    """
    Format a float with two decimals and a comma as the decimal separator
    (Finnish style), e.g. 12.30 -> "12,30".
    """
    return f"{value:.2f}".replace(".", ",")


def parse_timestamp(ts: str) -> datetime:
    """
    Parse a timestamp string into a datetime object.
    Supports common formats like:
      - "2025-10-13 00:00:00"
      - "2025-10-13T00:00:00"
      - "2025-10-13 00:00"
      - "2025-10-13T00:00"
    Raises ValueError if parsing fails.
    """
    text = ts.strip().replace("T", " ")
    # Try most common formats first
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    # Last attempt: datetime.fromisoformat
    return datetime.fromisoformat(ts.strip())


def read_data(filename: str) -> List[List[str]]:
    """
    Reads the CSV file and returns rows as a list of lists (strings).
    Automatically detects delimiter (comma/semicolon) when possible.
    Skips empty lines.
    """
    with open(filename, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)

        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=";,")
        except csv.Error:
            dialect = csv.excel  # default comma

        reader = csv.reader(f, dialect)
        rows: List[List[str]] = []
        for row in reader:
            if not row or all(not cell.strip() for cell in row):
                continue
            rows.append([cell.strip() for cell in row])
        return rows


def is_header_row(row: List[str]) -> bool:
    """
    Heuristic to detect a header row.
    If the first column is not parseable as a timestamp, treat it as header.
    """
    try:
        parse_timestamp(row[0])
        return False
    except Exception:
        return True


def compute_daily_totals(rows: List[List[str]]) -> Dict[date, Tuple[float, float, float, float, float, float]]:
    """
    Compute daily totals for consumption (v1-v3) and production (v1-v3).

    Assumed column order per row:
      0: timestamp
      1-3: consumption phase v1-v3 (Wh)
      4-6: production phase v1-v3 (Wh)

    Returns:
      dict[date] -> (cons_v1_kwh, cons_v2_kwh, cons_v3_kwh, prod_v1_kwh, prod_v2_kwh, prod_v3_kwh)
    """
    totals_wh: Dict[date, List[float]] = defaultdict(lambda: [0.0] * 6)

    for row in rows:
        # Expect at least 7 columns
        if len(row) < 7:
            continue

        dt = parse_timestamp(row[0])
        day = dt.date()

        # Convert Wh strings to floats (Wh), accumulate
        # Handle possible decimal commas in file by replacing ',' -> '.'
        def to_float(s: str) -> float:
            return float(s.replace(",", "."))

        c1 = to_float(row[1])
        c2 = to_float(row[2])
        c3 = to_float(row[3])
        p1 = to_float(row[4])
        p2 = to_float(row[5])
        p3 = to_float(row[6])

        totals_wh[day][0] += c1
        totals_wh[day][1] += c2
        totals_wh[day][2] += c3
        totals_wh[day][3] += p1
        totals_wh[day][4] += p2
        totals_wh[day][5] += p3

    # Convert Wh -> kWh
    totals_kwh: Dict[date, Tuple[float, float, float, float, float, float]] = {}
    for d, vals in totals_wh.items():
        totals_kwh[d] = (
            vals[0] / 1000.0,
            vals[1] / 1000.0,
            vals[2] / 1000.0,
            vals[3] / 1000.0,
            vals[4] / 1000.0,
            vals[5] / 1000.0,
        )
    return totals_kwh


def print_report(daily: Dict[date, Tuple[float, float, float, float, float, float]]) -> None:
    """
    Print a user-friendly table for week 42 electricity consumption and production.
    Uses Finnish weekday names, dd.mm.yyyy date format, and comma decimals.
    """
    print("Week 42 electricity consumption and production (kWh, by phase)\n")
    print("Day          Date        Consumption [kWh]               Production [kWh]")
    print("            (dd.mm.yyyy)  v1      v2      v3             v1     v2     v3")
    print("---------------------------------------------------------------------------")

    # Print in date order (Mon..Sun)
    for d in sorted(daily.keys()):
        weekday_name = FINNISH_WEEKDAYS[d.weekday()]
        date_str = d.strftime("%d.%m.%Y")

        c1, c2, c3, p1, p2, p3 = daily[d]

        c1s = to_finnish_number(c1)
        c2s = to_finnish_number(c2)
        c3s = to_finnish_number(c3)
        p1s = to_finnish_number(p1)
        p2s = to_finnish_number(p2)
        p3s = to_finnish_number(p3)

        # Align columns (simple fixed-width formatting)
        print(
            f"{weekday_name:<12} {date_str:<10}   "
            f"{c1s:>6}  {c2s:>6}  {c3s:>6}         "
            f"{p1s:>6} {p2s:>6} {p3s:>6}"
        )


def main() -> None:
    """
    Main function: reads data, computes daily totals, and prints the report.
    """
    rows = read_data("week42.csv")

    # Remove header if present
    if rows and is_header_row(rows[0]):
        rows = rows[1:]

    daily_totals = compute_daily_totals(rows)
    print_report(daily_totals)


if __name__ == "__main__":
    main()
