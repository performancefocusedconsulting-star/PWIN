"""
Parse downloaded £25k spend transparency files into a common row format.

Each handler yields dicts with these keys (all strings, amount as str):
  raw_entity, raw_supplier_name, amount, payment_date, expense_type, expense_area

The caller (ingest_spend.py) is responsible for writing to spend_transactions.
"""
import csv
import io
import logging
import zipfile
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

log = logging.getLogger(__name__)

# ODS XML namespaces
_TABLE_NS = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
_TEXT_NS  = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


# ── ODS reader (stdlib only) ──────────────────────────────────────────────────

def _read_ods(path: Path):
    """Yield header-keyed dicts from the first sheet of an ODS file."""
    with zipfile.ZipFile(path) as z:
        with z.open("content.xml") as f:
            tree = ET.parse(f)
    root = tree.getroot()
    table = root.find(f".//{{{_TABLE_NS}}}table")
    if table is None:
        raise ValueError(f"No table element found in {path}")

    headers = None
    for row_el in table.findall(f"{{{_TABLE_NS}}}table-row"):
        cells = row_el.findall(f"{{{_TABLE_NS}}}table-cell")
        values = []
        for cell in cells:
            repeat = int(cell.get(f"{{{_TABLE_NS}}}number-columns-repeated", 1))
            text = cell.findtext(f"{{{_TEXT_NS}}}p", "")
            values.extend([text] * repeat)
        # Strip trailing empty cells introduced by column-repeat
        while values and values[-1] == "":
            values.pop()
        if headers is None:
            if any(values):
                headers = values
        elif any(values):
            row = dict(zip(headers, values))
            yield row


# ── CSV reader (BOM-tolerant) ────────────────────────────────────────────────

def _read_csv(path: Path):
    """Yield header-keyed dicts from a CSV file (UTF-8 with cp1252 fallback)."""
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(path, encoding=enc, newline="") as f:
                rows = list(csv.DictReader(f))
            yield from rows
            return
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path} as UTF-8 or cp1252")


# ── Column normaliser helpers ────────────────────────────────────────────────

def _find(row: dict, *candidates: str) -> str:
    """Return the value of the first matching key (case-insensitive), or ''."""
    lower = {k.lower().strip(): v for k, v in row.items()}
    for c in candidates:
        v = lower.get(c.lower())
        if v is not None:
            return str(v).strip()
    return ""


def _amount(s: str) -> str:
    """Strip currency symbols and thousands separators; keep minus signs."""
    return s.replace("£", "").replace(",", "").strip()


# Excel serial 1 = 1900-01-01 in Excel's (buggy) calendar; days are counted
# from 1899-12-30 in Python to compensate for Excel's mistaken leap-year-1900.
_EXCEL_EPOCH = date(1899, 12, 30)


def _normalise_date(s: str) -> str:
    """
    Return an ISO date string (YYYY-MM-DD) given any of the formats publishers
    use: DD/MM/YYYY (Home Office, DfE), DD-MMM-YY (MoD), or Excel serial number
    (MoJ family). Returns the original string unchanged if it can't be parsed.
    """
    if not s:
        return ""
    s = s.strip()
    # Excel serial number — pure digits, plausible range (~25,000 = 1968 to ~73,000 = 2099)
    if s.isdigit() and 20000 <= int(s) <= 80000:
        try:
            return (_EXCEL_EPOCH + timedelta(days=int(s))).isoformat()
        except (ValueError, OverflowError):
            pass
    # Try common formats
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%b-%y", "%d-%b-%Y",
                "%d/%m/%y", "%d %b %Y", "%d %B %Y",
                "%d.%m.%Y", "%d.%m.%y"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return s


# ── Format handlers ──────────────────────────────────────────────────────────

def _parse_home_office(path: Path):
    """
    Home Office monthly £25k CSV.
    Key columns: Expense Area, Supplier, Amount, Date, Expense Type
    The 'Expense Area' column carries the sub-org identity
    (Border Force, UKVI, Immigration Enforcement, DBS, etc.).
    """
    for row in _read_csv(path):
        raw_entity       = _find(row, "Expense Area", "ExpenseArea", "expense area")
        raw_supplier     = _find(row, "Supplier", "Supplier Name", "supplier name")
        amount           = _amount(_find(row, "Amount", "amount"))
        payment_date     = _normalise_date(_find(row, "Date", "Payment Date", "date"))
        expense_type     = _find(row, "Expense Type", "ExpenseType", "expense type")
        expense_area     = raw_entity

        if not raw_supplier or not amount:
            continue
        yield {
            "raw_entity":       raw_entity,
            "raw_supplier_name": raw_supplier,
            "amount":           amount,
            "payment_date":     payment_date,
            "expense_type":     expense_type,
            "expense_area":     expense_area,
        }


def _parse_moj(path: Path):
    """
    Ministry of Justice and its agencies (HMCTS, LAA, HMPPS, etc.).
    The entity identity comes from the catalogue entity_override — the caller
    sets raw_entity upstream.  Here we just yield the financial columns.
    Key columns: Vendor Name, Expenditure Type, Amount, Payment Date
    """
    for row in _read_csv(path):
        raw_supplier = _find(row, "Vendor Name", "Supplier", "Supplier Name",
                              "vendor name", "supplier")
        amount       = _amount(_find(row, "Amount", "Net Amount", "amount"))
        payment_date = _normalise_date(_find(row, "Payment Date", "Date", "payment date", "date"))
        expense_type = _find(row, "Expenditure Type", "Expense Type",
                              "expenditure type", "expense type", "Category",
                              "category")
        expense_area = _find(row, "Expense Area", "expense area", "Department",
                              "department", "Cost Centre", "cost centre")

        if not raw_supplier or not amount:
            continue
        yield {
            "raw_entity":       "",   # filled by caller from entity_override
            "raw_supplier_name": raw_supplier,
            "amount":           amount,
            "payment_date":     payment_date,
            "expense_type":     expense_type,
            "expense_area":     expense_area,
        }


def _parse_dfe(path: Path):
    """
    Department for Education monthly £25k CSV.
    Key columns: Beneficiary, Expenditure Type, Amount, Date, Expense Area
    """
    for row in _read_csv(path):
        raw_entity   = _find(row, "Expense Area", "expense area",
                              "Department Family", "department family")
        raw_supplier = _find(row, "Beneficiary", "Supplier", "supplier",
                              "beneficiary")
        amount       = _amount(_find(row, "Amount", "amount"))
        payment_date = _normalise_date(_find(row, "Date", "Payment Date", "date"))
        expense_type = _find(row, "Expenditure Type", "Expense Type",
                              "expenditure type", "expense type")
        expense_area = raw_entity

        if not raw_supplier or not amount:
            continue
        yield {
            "raw_entity":       raw_entity,
            "raw_supplier_name": raw_supplier,
            "amount":           amount,
            "payment_date":     payment_date,
            "expense_type":     expense_type,
            "expense_area":     expense_area,
        }


def _parse_mod(path: Path):
    """
    Ministry of Defence monthly £25k ODS file.
    Uses zipfile + xml.etree.ElementTree — no external dependencies.
    Key columns: Supplier Name, Amount, Expense Type, Expense Area,
                 Date (budget breakouts include DE&S, DIO, DNO, Strategic Command).
    """
    for row in _read_ods(path):
        raw_entity   = _find(row, "Expense Area", "expense area",
                              "TLB", "Top Level Budget", "tlb")
        raw_supplier = _find(row, "Supplier Name", "Supplier", "supplier name",
                              "supplier", "Vendor Name", "vendor name")
        amount       = _amount(_find(row, "Amount", "amount", "Net Amount", "Total", "total"))
        payment_date = _normalise_date(_find(row, "Date", "Payment Date", "date"))
        expense_type = _find(row, "Expense Type", "expenditure type",
                              "expense type", "Category", "category")
        expense_area = raw_entity

        if not raw_supplier or not amount:
            continue
        yield {
            "raw_entity":       raw_entity,
            "raw_supplier_name": raw_supplier,
            "amount":           amount,
            "payment_date":     payment_date,
            "expense_type":     expense_type,
            "expense_area":     expense_area,
        }


# ── Dispatcher ───────────────────────────────────────────────────────────────

_HANDLERS = {
    "home-office-v1":         _parse_home_office,
    "ministry-of-justice-v1": _parse_moj,
    "department-for-education-v1": _parse_dfe,
    "ministry-of-defence-v1": _parse_mod,
}


def parse_file(path: Path, format_id: str):
    """
    Yield normalised spend rows from *path* using the handler for *format_id*.
    Raises KeyError if format_id is unknown, ValueError if the file is unreadable.
    """
    handler = _HANDLERS[format_id]
    yield from handler(path)


if __name__ == "__main__":
    print("OK")
