"""Tests: parse_spend.py — format handlers for all four departments."""
import csv
import io
import importlib.util
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import tempfile
import os

# Load parse_spend without importing (filename has no hyphens, but keep pattern consistent)
spec = importlib.util.spec_from_file_location(
    "parse_spend",
    Path(__file__).parent.parent / "agent" / "parse_spend.py",
)
ps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ps)


# ── Helpers to build synthetic files ────────────────────────────────────────

def _make_csv(rows: list[dict], tmp_dir: str, name: str = "test.csv") -> Path:
    path = Path(tmp_dir) / name
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def _make_ods(rows: list[dict], tmp_dir: str, name: str = "test.ods") -> Path:
    """Build a minimal valid ODS file from a list of dicts."""
    TABLE_NS  = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    TEXT_NS   = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
    OFFICE_NS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    def cell(value):
        c = ET.Element(f"{{{TABLE_NS}}}table-cell")
        p = ET.SubElement(c, f"{{{TEXT_NS}}}p")
        p.text = str(value)
        return c

    def make_row(values):
        row_el = ET.Element(f"{{{TABLE_NS}}}table-row")
        for v in values:
            row_el.append(cell(v))
        return row_el

    root = ET.Element(f"{{{OFFICE_NS}}}document-content")
    body = ET.SubElement(root, f"{{{OFFICE_NS}}}body")
    spreadsheet = ET.SubElement(body, f"{{{OFFICE_NS}}}spreadsheet")
    table = ET.SubElement(spreadsheet, f"{{{TABLE_NS}}}table")

    headers = list(rows[0].keys())
    table.append(make_row(headers))
    for row in rows:
        table.append(make_row([row[h] for h in headers]))

    content_xml = ET.tostring(root, encoding="unicode")

    path = Path(tmp_dir) / name
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("content.xml", content_xml)
    return path


# ── Home Office tests ────────────────────────────────────────────────────────

def test_home_office_basic():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_csv([
            {"Expense Area": "Border Force", "Supplier": "Acme Ltd",
             "Amount": "£50,000.00", "Date": "2025-01-15", "Expense Type": "IT Services"},
            {"Expense Area": "UKVI", "Supplier": "Beta Corp",
             "Amount": "£125,000.50", "Date": "2025-01-20", "Expense Type": "Consultancy"},
        ], tmp)
        rows = list(ps.parse_file(path, "home-office-v1"))
    assert len(rows) == 2
    assert rows[0]["raw_entity"] == "Border Force"
    assert rows[0]["raw_supplier_name"] == "Acme Ltd"
    assert rows[0]["amount"] == "50000.00"
    assert rows[1]["raw_entity"] == "UKVI"
    assert rows[1]["amount"] == "125000.50"


def test_home_office_skips_empty_supplier():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_csv([
            {"Expense Area": "Border Force", "Supplier": "",
             "Amount": "£50,000", "Date": "2025-01-15", "Expense Type": ""},
        ], tmp)
        rows = list(ps.parse_file(path, "home-office-v1"))
    assert rows == []


# ── MoJ tests ───────────────────────────────────────────────────────────────

def test_moj_basic():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_csv([
            {"Vendor Name": "Legal Systems Ltd", "Amount": "75000.00",
             "Payment Date": "2025-02-10", "Expenditure Type": "Professional Services"},
        ], tmp)
        rows = list(ps.parse_file(path, "ministry-of-justice-v1"))
    assert len(rows) == 1
    assert rows[0]["raw_supplier_name"] == "Legal Systems Ltd"
    assert rows[0]["amount"] == "75000.00"
    assert rows[0]["raw_entity"] == ""   # entity_override handled by caller


def test_moj_skips_no_amount():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_csv([
            {"Vendor Name": "Someone", "Amount": "",
             "Payment Date": "2025-02-10", "Expenditure Type": ""},
        ], tmp)
        rows = list(ps.parse_file(path, "ministry-of-justice-v1"))
    assert rows == []


# ── DfE tests ───────────────────────────────────────────────────────────────

def test_dfe_basic():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_csv([
            {"Beneficiary": "Capita Plc", "Amount": "£200,000",
             "Date": "2025-04-05", "Expenditure Type": "Managed Services",
             "Expense Area": "ESFA"},
        ], tmp)
        rows = list(ps.parse_file(path, "department-for-education-v1"))
    assert len(rows) == 1
    assert rows[0]["raw_supplier_name"] == "Capita Plc"
    assert rows[0]["amount"] == "200000"
    assert rows[0]["raw_entity"] == "ESFA"


# ── MoD ODS tests ────────────────────────────────────────────────────────────

def test_mod_ods_basic():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_ods([
            {"Supplier Name": "BAE Systems", "Amount": "500000",
             "Date": "2025-01-31", "Expense Type": "Equipment",
             "Expense Area": "DE&S"},
            {"Supplier Name": "Serco", "Amount": "£80,000",
             "Date": "2025-01-31", "Expense Type": "Facilities",
             "Expense Area": "Strategic Command"},
        ], tmp, "mod_jan.ods")
        rows = list(ps.parse_file(path, "ministry-of-defence-v1"))
    assert len(rows) == 2
    assert rows[0]["raw_supplier_name"] == "BAE Systems"
    assert rows[0]["raw_entity"] == "DE&S"
    assert rows[0]["amount"] == "500000"
    assert rows[1]["raw_entity"] == "Strategic Command"


def test_mod_skips_empty_rows():
    with tempfile.TemporaryDirectory() as tmp:
        path = _make_ods([
            {"Supplier Name": "Valid Co", "Amount": "30000",
             "Date": "2025-01-10", "Expense Type": "", "Expense Area": "DIO"},
            {"Supplier Name": "", "Amount": "10000",
             "Date": "2025-01-10", "Expense Type": "", "Expense Area": ""},
        ], tmp, "mod_test.ods")
        rows = list(ps.parse_file(path, "ministry-of-defence-v1"))
    assert len(rows) == 1
    assert rows[0]["raw_supplier_name"] == "Valid Co"


# ── Unknown format_id ────────────────────────────────────────────────────────

def test_unknown_format_raises():
    try:
        list(ps.parse_file(Path("dummy.csv"), "nonexistent-format-v1"))
        assert False, "expected KeyError"
    except KeyError:
        pass


if __name__ == "__main__":
    for fn_name in sorted(k for k in dir() if k.startswith("test_")):
        fn = globals()[fn_name]
        fn()
        print(f"  PASS  {fn_name}")
    print("OK")
