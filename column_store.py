"""
CE/CZ4123/SC4023 Big Data Management - Semester Group Project
column_store.py: Column-oriented data storage and query processing.

Responsibilities:
    - load_columns()     : Read CSV into separate per-column Python lists
    - build_town_index() : Pre-compute a boolean mask for town filtering
    - query()            : Scan columns to find the min-PSM record for (x, y)
"""

from config import MON_MAP, MAX_PRICE_PER_SQM


# ──────────────────────────────────────────────────────────────
# 1. LOAD CSV INTO COLUMN STORE
# ──────────────────────────────────────────────────────────────
def load_columns(csv_path: str) -> dict:
    """
    Read the CSV file and store each field in its own Python list (column store).

    Columns stored
    --------------
    year       : int
    month      : int
    town       : str  (upper-cased)
    block      : str
    floor_area : float
    flat_model : str
    lease_date : int
    price      : float
    psm        : float  (price / floor_area, pre-computed)

    Returns a dict mapping column name -> list.
    """
    col_year       = []
    col_month      = []
    col_town       = []
    col_block      = []
    col_floor_area = []
    col_flat_model = []
    col_lease_date = []
    col_price      = []
    col_psm        = []

    with open(csv_path, "r", encoding="utf-8") as fh:
        fh.readline()  # skip title row

        for line in fh:
            line = line.rstrip("\r\n")
            if not line:
                continue

            # Fields: month,town,flat_type,block,street_name,
            #         storey_range,floor_area_sqm,flat_model,
            #         lease_commence_date,resale_price
            parts = line.split(",")
            if len(parts) < 10:
                continue

            raw_month = parts[0].strip()   # e.g. "Jan-15"
            raw_town  = parts[1].strip().upper()
            raw_block = parts[3].strip()
            raw_area  = parts[6].strip()
            raw_model = parts[7].strip()
            raw_lease = parts[8].strip()
            raw_price = parts[9].strip()

            # Parse month string "Mon-YY" -> year (int), month (int)
            try:
                mon_str, yr_str = raw_month.split("-")
                yr_2digit = int(yr_str)
                year  = 2000 + yr_2digit
                month = MON_MAP[mon_str]
            except Exception:
                continue  # skip malformed rows

            try:
                area  = float(raw_area)
                price = float(raw_price)
                lease = int(raw_lease)
            except ValueError:
                continue

            psm = price / area  # pre-compute price per square meter

            col_year.append(year)
            col_month.append(month)
            col_town.append(raw_town)
            col_block.append(raw_block)
            col_floor_area.append(area)
            col_flat_model.append(raw_model)
            col_lease_date.append(lease)
            col_price.append(price)
            col_psm.append(psm)

    return {
        "year":       col_year,
        "month":      col_month,
        "town":       col_town,
        "block":      col_block,
        "floor_area": col_floor_area,
        "flat_model": col_flat_model,
        "lease_date": col_lease_date,
        "price":      col_price,
        "psm":        col_psm,
    }


# ──────────────────────────────────────────────────────────────
# 2. BUILD TOWN INDEX (pre-filter by town for reuse across x,y)
# ──────────────────────────────────────────────────────────────
def build_town_index(cols: dict, towns: list) -> list:
    """
    Return a boolean mask (list of bool) where True means the row's town
    is in the target towns list. Computed once, reused for every (x, y).
    """
    town_set = set(t.upper() for t in towns)
    return [t in town_set for t in cols["town"]]


# ──────────────────────────────────────────────────────────────
# 3. QUERY: find min-PSM record for a given (x, y)
# ──────────────────────────────────────────────────────────────
def query(cols: dict, town_mask: list,
          target_year: int, start_month: int,
          x: int, y: int) -> int:
    """
    Scan the column store and return the index of the record with the
    minimum price per square meter for the given (x, y) pair,
    or -1 if no record qualifies.

    Filtering conditions
    --------------------
    - Town in matched towns        (pre-filtered via town_mask)
    - Year == target_year
    - Month in [start_month, start_month + x - 1]
    - Floor_area >= y
    - PSM <= MAX_PRICE_PER_SQM (4725)
    """
    end_month = start_month + x - 1

    col_year       = cols["year"]
    col_month      = cols["month"]
    col_floor_area = cols["floor_area"]
    col_psm        = cols["psm"]

    best_psm   = None
    best_index = -1

    n = len(col_year)
    for i in range(n):
        if not town_mask[i]:
            continue
        if col_year[i] != target_year:
            continue
        m = col_month[i]
        if m < start_month or m > end_month:
            continue
        if col_floor_area[i] < y:
            continue
        psm = col_psm[i]
        if psm > MAX_PRICE_PER_SQM:
            continue
        if best_psm is None or psm < best_psm:
            best_psm   = psm
            best_index = i

    return best_index  # -1 means no result
