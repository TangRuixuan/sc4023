"""
CE/CZ4123/SC4023 Big Data Management - Semester Group Project
main.py: Entry point — argument parsing, matric number interpretation,
         query orchestration, and CSV output writing.

Usage:
    python main.py <MatricNumber> <CSVFilePath>

Example:
    python main.py U2320339E ResalePricesSingapore.csv
"""

import sys
from config import DIGIT_TO_TOWN, X_RANGE, Y_RANGE
from column_store import load_columns, build_town_index, query


# ──────────────────────────────────────────────────────────────
# DEFAULT PARAMETERS (overridden by CLI arguments if provided)
# ──────────────────────────────────────────────────────────────
DEFAULT_MATRIC   = "U2320339E"
DEFAULT_CSV_PATH = "ResalePricesSingapore.csv"


# ──────────────────────────────────────────────────────────────
# 1. PARSE MATRICULATION NUMBER
# ──────────────────────────────────────────────────────────────
def parse_matric(matric: str):
    """
    Extract target year, start month, and list of towns from a matric number.

    Parameters
    ----------
    matric : str
        e.g. "U2320339E"

    Returns
    -------
    target_year  : int   e.g. 2019
    start_month  : int   e.g. 3
    towns        : list[str]
    """
    digits_str = "".join(ch for ch in matric if ch.isdigit())
    if len(digits_str) < 7:
        raise ValueError(f"Matric number '{matric}' does not contain enough digits.")

    digits = [int(d) for d in digits_str]

    last_digit        = digits[-1]
    second_last_digit = digits[-2]

    for yr in range(2015, 2025):
        if yr % 10 == last_digit:
            target_year = yr
            break
    else:
        raise ValueError(f"No year in 2015-2024 ends with digit {last_digit}.")

    start_month = second_last_digit if second_last_digit != 0 else 10

    seen  = set()
    towns = []
    for d in digits:
        if d not in seen:
            seen.add(d)
            towns.append(DIGIT_TO_TOWN[d])

    return target_year, start_month, towns


# ──────────────────────────────────────────────────────────────
# 2. MAIN
# ──────────────────────────────────────────────────────────────
def main():
    # Allow CLI override: python main.py <MatricNum> [CSVPath]
    matric   = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_MATRIC
    csv_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_CSV_PATH

    print(f"Matric number : {matric}")
    print(f"CSV file      : {csv_path}")

    # --- Parse matric ---
    target_year, start_month, towns = parse_matric(matric)
    print(f"Target year   : {target_year}")
    print(f"Start month   : {start_month:02d}")
    print(f"Towns         : {towns}")
    print()

    # --- Load data into column store ---
    print("Loading data into column store...")
    cols = load_columns(csv_path)
    n_rows = len(cols["year"])
    print(f"Loaded {n_rows:,} records.\n")

    # --- Pre-build town mask (reused across all x, y) ---
    print("Building town index...")
    town_mask = build_town_index(cols, towns)

    # --- Run queries for all (x, y) pairs ---
    print("Running queries for all (x, y) pairs...\n")

    output_rows = []  # each element: (x, y, result_dict or None)

    for x in X_RANGE:      # 1..8
        for y in Y_RANGE:  # 80..150
            idx = query(cols, town_mask, target_year, start_month, x, y)
            if idx == -1:
                output_rows.append((x, y, None))
            else:
                rec = {
                    "year":       cols["year"][idx],
                    "month":      cols["month"][idx],
                    "town":       cols["town"][idx],
                    "block":      cols["block"][idx],
                    "floor_area": int(cols["floor_area"][idx]),
                    "flat_model": cols["flat_model"][idx],
                    "lease_date": cols["lease_date"][idx],
                    "psm":        round(cols["psm"][idx]),
                }
                output_rows.append((x, y, rec))

    # --- Write output CSV ---
    out_filename = f"ScanResult_{matric}.csv"
    with open(out_filename, "w", encoding="utf-8") as out:
        out.write("(x, y),Year,Month,Town,Block,Floor_Area,Flat_Model,"
                  "Lease_Commence_Date,Price_Per_Square_Meter\n")

        for x, y, rec in output_rows:
            xy_str = f"({x}, {y})"
            if rec is None:
                out.write(f"{xy_str},No result\n")
            else:
                out.write(
                    f"{xy_str},"
                    f"{rec['year']},"
                    f"{rec['month']:02d},"
                    f"{rec['town']},"
                    f"{rec['block']},"
                    f"{rec['floor_area']},"
                    f"{rec['flat_model']},"
                    f"{rec['lease_date']},"
                    f"{rec['psm']}\n"
                )

    print(f"Output written to: {out_filename}")
    valid_count = sum(1 for _, _, r in output_rows if r is not None)
    print(f"Valid (x, y) pairs: {valid_count} / {len(output_rows)}")


if __name__ == "__main__":
    main()
