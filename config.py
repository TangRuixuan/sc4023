"""
CE/CZ4123/SC4023 Big Data Management - Semester Group Project
config.py: Central configuration and constants.
"""

# ── Town mapping (Table 1 from project spec) ──────────────────
DIGIT_TO_TOWN = {
    0: "BEDOK",
    1: "BUKIT PANJANG",
    2: "CLEMENTI",
    3: "CHOA CHU KANG",
    4: "HOUGANG",
    5: "JURONG WEST",
    6: "PASIR RIS",
    7: "TAMPINES",
    8: "WOODLANDS",
    9: "YISHUN",
}

# ── Query validity threshold ───────────────────────────────────
MAX_PRICE_PER_SQM = 4725

# ── Query parameter ranges (per spec) ─────────────────────────
X_RANGE = range(1, 9)    # x: 1 to 8 inclusive
Y_RANGE = range(80, 151) # y: 80 to 150 inclusive

# ── Month abbreviation -> integer (for "Mon-YY" CSV format) ───
MON_MAP = {
    "Jan": 1,  "Feb": 2,  "Mar": 3,  "Apr": 4,
    "May": 5,  "Jun": 6,  "Jul": 7,  "Aug": 8,
    "Sep": 9,  "Oct": 10, "Nov": 11, "Dec": 12,
}
