"""
PWIN Competitive Intelligence — Stakeholder utilities
======================================================
Pure functions: name normalisation, SCS band inference, column resolution.
No database or network dependencies.
"""

import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ── Name normalisation ───────────────────────────────────────────────────────

_HONORIFICS = {
    'mr', 'mrs', 'ms', 'miss', 'dr', 'prof', 'sir', 'dame',
    'reverend', 'rev', 'lord', 'lady',
}


def normalise_name(raw: str) -> str:
    """Convert organogram name variants to 'First Last'.

    Handles:
      'Gallagher, Daniel'              -> 'Daniel Gallagher'
      'Rouse, Deana (Deana), Miss'     -> 'Deana Rouse'
      'Berthon, Richard (Richard), Mr' -> 'Richard Berthon'
      'Isabelle Trowler'               -> 'Isabelle Trowler'
    """
    name = (raw or '').strip()
    if not name:
        return name

    if ',' in name:
        parts = name.split(',', 1)
        surname = parts[0].strip()
        rest = parts[1].strip()
        # strip parenthetical nicknames: "(Deana)", "(Richard)"
        rest = re.sub(r'\s*\([^)]*\)\s*', ' ', rest).strip()
        # strip trailing honorifics
        tokens = rest.split()
        while tokens and tokens[-1].lower().rstrip('.') in _HONORIFICS:
            tokens.pop()
        first = tokens[0] if tokens else ''
        return f'{first} {surname}'.strip() if first else surname

    return name


def slug(text: str) -> str:
    """Lowercase, spaces to hyphens, strip non-alphanumeric (except hyphens)."""
    s = text.lower().strip()
    s = re.sub(r'\s+', '-', s)
    s = re.sub(r'[^a-z0-9\-]', '', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def person_id(name_normalised: str, canonical_buyer_id: str) -> str:
    return f'{slug(name_normalised)}--{canonical_buyer_id}'


# ── SCS band inference ───────────────────────────────────────────────────────

# Checked in order — DeputyDirector before Director so 'Deputy Director' is
# not captured by the Director rule.
_BAND_PATTERNS = [
    ('PermanentSecretary', [
        'permanent secretary',
        'first permanent secretary',
        'second permanent secretary',
    ]),
    ('DirectorGeneral', ['director general', 'director-general']),
    ('DeputyDirector', ['deputy director']),
    ('Director', ['director']),
]


def infer_scs_band(job_title: str) -> str:
    """Infer SCS band from job title string."""
    t = (job_title or '').lower()
    for band, keywords in _BAND_PATTERNS:
        for kw in keywords:
            if kw in t:
                return band
    return 'Unknown'


# ── Column resolution ────────────────────────────────────────────────────────

# Maps logical field name -> ordered list of CSV header variants (current first,
# legacy 2011 spec variants after). resolve_col() tries each in order.
COLUMN_MAP = {
    'name':              ['Name'],
    'grade':             ['Grade (or equivalent)', 'Grade'],
    'job_title':         ['Job Title'],
    'parent_department': ['Parent Department'],
    'organisation':      ['Organisation'],
    'unit':              ['Unit'],
    'contact_email':     ['Contact E-mail', 'Contact Email'],
    'reports_to':        ['Reports to Senior Post', 'Reports To Senior Post'],
    'fte':               ['FTE'],
    'pay_floor':         ['Actual Pay Floor (£)', 'Actual Pay Floor'],
    'pay_ceiling':       ['Actual Pay Ceiling (£)', 'Actual Pay Ceiling'],
    'valid':             ['Valid?'],
    'post_ref':          ['Post Unique Reference'],
    'prof_group':        ['Professional/Occupational Group'],
    'notes':             ['Notes'],
}


def resolve_col(row: dict, field: str) -> str:
    """Return the value for a logical field, trying each header variant in order."""
    for header in COLUMN_MAP.get(field, []):
        if header in row:
            return (row[header] or '').strip()
    return ''
