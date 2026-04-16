"""
Build qualify-content-v0.2.json from:
  - Winnability_Artifact_Judgment_Scorecard_v6.xlsx  (v6 questions, rubrics, archetypes)
  - qualify-content-v0.1.json                        (carry-forward: persona, incumbent triggers)

Run from repo root:
  python pwin-qualify/content/build_v02.py
"""
import zipfile, re, json, copy, os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
XLSX  = os.path.join(BASE, 'pwin-qualify', 'docs', 'Winnability_Artifact_Judgment_Scorecard_v6.xlsx')
V01   = os.path.join(BASE, 'pwin-qualify', 'content', 'qualify-content-v0.1.json')
OUT   = os.path.join(BASE, 'pwin-qualify', 'content', 'qualify-content-v0.2.json')

# ─────────────────────────────────────────
# 1. XLSX helpers
# ─────────────────────────────────────────
z = zipfile.ZipFile(XLSX)

ss_xml = z.read('xl/sharedStrings.xml').decode('utf-8')
strings_raw = re.findall(r'<si>(.*?)</si>', ss_xml, re.DOTALL)
_SS = []
for s in strings_raw:
    parts = re.findall(r'<t[^>]*>(.*?)</t>', s, re.DOTALL)
    val = ''.join(parts)
    for old, new in [
        ('&amp;','&'), ('&lt;','<'), ('&gt;','>'), ('&quot;','"'),
        ('&#10;','\n'), ('&#13;',''),
        ('\u2019',"'"), ('\u2018',"'"), ('\u201c','"'), ('\u201d','"'),
        ('\u2013','-'), ('\u2014','--'), ('\ufffd',"'"),
    ]:
        val = val.replace(old, new)
    _SS.append(val)

wb_xml = z.read('xl/workbook.xml').decode('utf-8')
_sheets = re.findall(r'<sheet[^>]+name="([^"]+)"[^>]+r:id="([^"]+)"', wb_xml)
rels_xml = z.read('xl/_rels/workbook.xml.rels').decode('utf-8')
_rel_map = dict(re.findall(r'Id="([^"]+)"[^>]+Target="([^"]+)"', rels_xml))
_name_to_file = {name: _rel_map.get(rid,'') for name, rid in _sheets}

def _read_sheet(name):
    target = _name_to_file.get(name, '')
    if not target: return {}
    if not target.startswith('xl/'): target = 'xl/' + target
    try:
        xml = z.read(target).decode('utf-8')
    except Exception:
        return {}
    cells = re.findall(r'<c r="([^"]+)"([^>]*)>(.*?)</c>', xml, re.DOTALL)
    data = {}
    for ref, attrs, content in cells:
        col_str = re.match(r'([A-Z]+)', ref).group(1)
        row_str = re.match(r'[A-Z]+(\d+)', ref).group(1)
        col = 0
        for ch in col_str:
            col = col * 26 + (ord(ch) - ord('A') + 1)
        row = int(row_str)
        t_match = re.search(r't="([^"]+)"', attrs)
        cell_type = t_match.group(1) if t_match else ''
        v_match = re.search(r'<v>(.*?)</v>', content)
        val = ''
        if v_match:
            val = v_match.group(1)
            if cell_type == 's':
                val = _SS[int(val)]
        data[(row, col)] = val
    return data

def _grid(data):
    if not data: return []
    max_row = max(r for r,c in data)
    max_col = max(c for r,c in data)
    return [[data.get((r,c),'') for c in range(1, max_col+1)] for r in range(1, max_row+1)]

def _g(row, idx):
    return (row[idx] if idx < len(row) else '').strip()

# ─────────────────────────────────────────
# 2. Load v0.1
# ─────────────────────────────────────────
with open(V01, encoding='utf-8') as f:
    v01 = json.load(f)

v01_qs = {q['id']: q for q in v01['questionPacks']['standard']['questions']}

def _v01q(n):
    return v01_qs.get('Q' + str(n), {})

# ─────────────────────────────────────────
# 3. Parse Excel sheets
# ─────────────────────────────────────────

# Core 25Q model
q_model_rows = _grid(_read_sheet('Core_25Q_Model'))
CAT_ID = {
    'Buyer Need & Decision Logic':              'bndl',
    'Stakeholder Position & Access':            'spa',
    'Competitive Position & Incumbent Dynamics':'cpid',
    'Procurement, Proposition & Solution Fit':  'ppsf',
    'Commercial, Delivery & Pursuit Readiness': 'cdpr',
}
q_model = {}
for row in q_model_rows[4:29]:
    qid = row[0]
    if not qid.startswith('Q'): continue
    q_model[qid] = {
        'id':               qid,
        'categoryId':       CAT_ID.get(_g(row,1), ''),
        'category':         _g(row,1),
        'critical':         _g(row,3).lower() == 'yes',
        'shortLabel':       _g(row,4),
        'text':             _g(row,5),
        'whyAsked':         _g(row,6),
        'requiredArtifacts':[a.strip() for a in _g(row,7).split(',') if a.strip()],
    }

# Core 25Q rubric
q_rubric_rows = _grid(_read_sheet('Core_25Q_Rubric'))
q_rubric = {}
for i, row in enumerate(q_rubric_rows[4:]):
    if i >= 25: break
    qid = 'Q%02d' % (i+1)
    q_rubric[qid] = {
        'executionEvidence': _g(row,7),
        'hurdles': {
            'Strongly Agree':    _g(row,8),  'Agree':           _g(row,9),
            'Disagree':          _g(row,10), 'Strongly Disagree':_g(row,11),
        },
        'benchmarkScenario': _g(row,12),
        'benchmarkExamples': {
            'Strongly Agree':    _g(row,13), 'Agree':           _g(row,14),
            'Disagree':          _g(row,15), 'Strongly Disagree':_g(row,16),
        },
        'challengeQuestionsByLevel': {
            'Strongly Agree':    _g(row,17), 'Agree':           _g(row,18),
            'Disagree':          _g(row,19), 'Strongly Disagree':_g(row,20),
        },
        'actionFocus': _g(row,21),
        'recommendedActionsByLevel': {
            'Strongly Agree':    _g(row,22), 'Agree':           _g(row,23),
            'Disagree':          _g(row,24), 'Strongly Disagree':_g(row,25),
        },
        'whatWouldMoveUp': _g(row,26),
        'scoreCap':        _g(row,27),
    }

# Archetype weights
arch_rows = _grid(_read_sheet('Archetype_Weights'))
ARCH_ID = {
    'Professional Consulting / Advisory':        'consulting_advisory',
    'Digital Transformation / SI / Delivery':    'digital_transformation_si',
    'Digital Product / SaaS / Platform':         'digital_product_saas',
    'BPO / Managed Service / Operational Outsourcing': 'bpo_managed_service',
    'Facilities / Field / Operational Service':  'facilities_operational',
    'Hybrid Transformation + Managed Service':   'hybrid_transformation_managed',
    'Framework / Panel Appointment':             'framework_panel',
    'Incumbent Renewal / Rebid':                 'incumbent_renewal',
}
arch_weights = {}
for row in arch_rows[1:]:
    name = row[0].strip() if row[0] else ''
    if not name: continue
    aid = ARCH_ID.get(name, name.lower().replace(' ','_').replace('/','_'))
    arch_weights[aid] = {
        'name':     name,
        'weights': {
            'bndl': float(row[1])/100 if row[1] else 0,
            'spa':  float(row[2])/100 if row[2] else 0,
            'cpid': float(row[3])/100 if row[3] else 0,
            'ppsf': float(row[4])/100 if row[4] else 0,
            'cdpr': float(row[5])/100 if row[5] else 0,
        },
        'rationale': _g(row, 6) if len(row) > 6 else '',
    }

def _parse_overlay(sheet_name, prefix, qw):
    rows = _grid(_read_sheet(sheet_name))
    result = {}
    for i, row in enumerate(rows[4:]):
        if i >= 8: break
        qid = '%s%02d' % (prefix, i+1)
        result[qid] = {
            'id':      qid,
            'critical': _g(row,1).lower() == 'yes',
            'text':     _g(row,2),
            'especiallyCriticalFor': _g(row,3),
            'whyAsked': _g(row,4),
            'requiredArtifacts': [a.strip() for a in _g(row,5).split(';') if a.strip()],
            'executionEvidence': _g(row,6),
            'hurdles': {
                'Strongly Agree':    _g(row,7),  'Agree':           _g(row,8),
                'Disagree':          _g(row,9),  'Strongly Disagree':_g(row,10),
            },
            'benchmarkExamples': {
                'Strongly Agree':    _g(row,12), 'Agree':           _g(row,13),
                'Disagree':          _g(row,14), 'Strongly Disagree':_g(row,15),
            },
            'challengeQuestionsByLevel': {
                'Strongly Agree':    _g(row,16), 'Agree':           _g(row,17),
                'Disagree':          _g(row,18), 'Strongly Disagree':_g(row,19),
            },
            'recommendedActionsByLevel': {
                'Strongly Agree':    _g(row,21), 'Agree':           _g(row,22),
                'Disagree':          _g(row,23), 'Strongly Disagree':_g(row,24),
            },
            'whatWouldMoveUp': _g(row,25),
            'scoreCap':        _g(row,26),
            'inflationSignals': [],
            'qw': qw,
        }
    return result

inc_qs   = _parse_overlay('Incumbent_Overlay_Rubric',   'I', 0.125)
chal_qs  = _parse_overlay('Challenger_Overlay_Rubric',  'C', 0.125)

# ─────────────────────────────────────────
# 4. Inflation signals
# ─────────────────────────────────────────
_NEW_SIGNALS = {
    'Q04': ['we expect them to retain the status quo', 'the incumbent is embedded',
            'they have no real reason to switch', 'we assume continuity bias',
            'there is no obvious reason they would change'],
    'Q21': ['we can make the numbers work', 'pricing will be competitive',
            'margins will be acceptable', 'we will find a way commercially',
            'the commercial model is still being worked through'],
    'Q22': ['our partners are aligned', 'we can resource this',
            'delivery is manageable', 'we have done similar work before',
            'our supply chain will support this'],
    'Q23': ['we are comfortable with the risk', 'risks are manageable',
            'TUPE is straightforward', 'transition risk is low',
            'there are no unusual contractual conditions'],
}

_INFLATION_MAP = {
    'Q01': [3,22], 'Q02': [3,21], 'Q03': [17], 'Q04': [],
    'Q05': [7],    'Q06': [8,13], 'Q07': [9,12], 'Q08': [14,15],
    'Q09': [11,20],'Q10': [21,23],'Q11': [2],   'Q12': [10],
    'Q13': [1,19], 'Q14': [4],    'Q15': [4],   'Q16': [6],
    'Q17': [5],    'Q18': [17,18],'Q19': [19],  'Q20': [19,20],
    'Q21': [],     'Q22': [],     'Q23': [],    'Q24': [7],
    'Q25': [24,22],
}

def _inflation(qid):
    ids = _INFLATION_MAP.get(qid, [])
    if ids:
        seen, result = set(), []
        for n in ids:
            for sig in _v01q(n).get('inflationSignals', []):
                if sig not in seen:
                    seen.add(sig); result.append(sig)
        return result
    return _NEW_SIGNALS.get(qid, [])

# ─────────────────────────────────────────
# 5. Rubric bands (derived from hurdles, v0.1 style)
# ─────────────────────────────────────────
def _rubric_from_hurdles(hurdles):
    def condense(text, max_len=200):
        text = text.strip()
        if not text: return ''
        sentences = re.split(r'(?<=[.!?])\s+', text)
        out = sentences[0]
        if len(out) > max_len:
            out = out[:max_len].rsplit(' ', 1)[0] + '.'
        return out
    return {level: condense(hurdles.get(level,'')) for level in
            ['Strongly Agree','Agree','Disagree','Strongly Disagree']}

# ─────────────────────────────────────────
# 6. v0.1 provenance
# ─────────────────────────────────────────
_PROV = {
    'Q01': ['Q3','Q22'], 'Q02': ['Q3','Q21'], 'Q03': ['Q17'], 'Q04': [],
    'Q05': ['Q7'],       'Q06': ['Q8','Q13'], 'Q07': ['Q9','Q12'], 'Q08': ['Q14','Q15'],
    'Q09': ['Q11','Q20'],'Q10': ['Q21','Q23'],'Q11': ['Q2'], 'Q12': ['Q10'],
    'Q13': ['Q1','Q19'], 'Q14': ['Q4'],       'Q15': ['Q4'], 'Q16': ['Q6'],
    'Q17': ['Q5'],       'Q18': ['Q17','Q18'],'Q19': ['Q19'],'Q20': ['Q19','Q20'],
    'Q21': [],           'Q22': [],           'Q23': [],     'Q24': ['Q7'],
    'Q25': ['Q24','Q22'],
}

# ─────────────────────────────────────────
# 7. Build question arrays
# ─────────────────────────────────────────
def _build_core_q(qid):
    m = q_model[qid]
    r = q_rubric.get(qid, {})
    hurdles = r.get('hurdles', {})
    return {
        'id':              qid,
        'cat':             m['categoryId'],
        'topic':           m['shortLabel'],
        'text':            m['text'],
        'critical':        m['critical'],
        'whyAsked':        m['whyAsked'],
        'requiredArtifacts': m['requiredArtifacts'],
        'rubric':          _rubric_from_hurdles(hurdles),
        'hurdles':         hurdles,
        'benchmarkScenario':        r.get('benchmarkScenario', ''),
        'benchmarkExamples':        r.get('benchmarkExamples', {}),
        'challengeQuestionsByLevel':r.get('challengeQuestionsByLevel', {}),
        'recommendedActionsByLevel':r.get('recommendedActionsByLevel', {}),
        'executionEvidence':        r.get('executionEvidence', ''),
        'actionFocus':              r.get('actionFocus', ''),
        'whatWouldMoveUp':          r.get('whatWouldMoveUp', ''),
        'scoreCap':                 r.get('scoreCap', ''),
        'inflationSignals':         _inflation(qid),
        'qw':              0.20,
        'v0_1_provenance': _PROV.get(qid, []),
    }

def _build_overlay_q(q_data):
    hurdles = q_data.get('hurdles', {})
    return {**q_data, 'rubric': _rubric_from_hurdles(hurdles)}

core_questions = [_build_core_q(qid) for qid in sorted(q_model.keys())]
inc_q_list     = [_build_overlay_q(inc_qs[qid])  for qid in sorted(inc_qs.keys())]
chal_q_list    = [_build_overlay_q(chal_qs[qid]) for qid in sorted(chal_qs.keys())]

# ─────────────────────────────────────────
# 8. Carry-forward from v0.1
# ─────────────────────────────────────────
persona = copy.deepcopy(v01['persona'])
persona['meta'] = {
    'version': '0.2.0', 'contentVersion': '0.2.0',
    'lastUpdated': '2026-04-16', 'schemaVersion': 'qualify-content-schema-v2',
}
# calibrationRules in v0.1 are plain strings; wrap them as dicts with a recast note
raw_rules = persona.get('workflowTriggers', {}).get('calibrationRules', [])
persona['workflowTriggers']['calibrationRules'] = [
    {'rule': r, 'note': 'RECAST-NEEDED: update question refs to v0.2 IDs'} if isinstance(r, str) else r
    for r in raw_rules
]

opp_calibration = copy.deepcopy(v01['opportunityTypeCalibration'])
opp_calibration['Facilities / Field / Operational Service'] = (
    "For facilities, field-based, and operational service contracts, the dominant challenge is delivery credibility "
    "at the required geographic and operational scale. Buyers scrutinise mobilisation timelines, staffing capacity, "
    "and the bidder's track record of operational continuity under TUPE. Alex should probe whether transition and "
    "staffing plans are documented and stress-tested, and whether the commercial model accounts for the full cost "
    "of mobilisation. Proposition and solution fit matter, but commercial and delivery realism typically determine "
    "whether a bid is credible. Challenge any scoring that assumes operational competence without documented evidence "
    "of comparable scale delivery."
)
opp_calibration['Hybrid Transformation + Managed Service'] = (
    "Hybrid transformation and managed service opportunities require the pursuit team to demonstrate competence "
    "across two distinct horizons: the transformation programme and the steady-state operational contract. Buyers "
    "typically weight both, but the evaluation often reveals which horizon carries more risk. Alex should probe "
    "whether the proposition is genuinely integrated or whether the team has merely added a managed service wrapper "
    "to a transformation bid. Solution fit and delivery credibility both carry significant weight. Challenge any "
    "scoring that presents the two horizons as independently strong without demonstrating coherent transition logic."
)
opp_calibration['Framework / Panel Appointment'] = (
    "Framework and panel appointments are evaluated on breadth of capability, compliance, and commercial construct "
    "rather than pursuit-specific relationship advantage. The competitive field is typically wide and the evaluation "
    "criteria are more formulaic. Alex should probe whether mandatory and suitability criteria are fully met, whether "
    "the proof story covers the full scope of the framework lot, and whether the commercial model is structured "
    "correctly for call-off. Stakeholder access carries less weight than in direct awards. Challenge any scoring "
    "that assumes framework approval translates into call-off success -- framework position and call-off win rate "
    "are different problems."
)

incumbent_v01 = v01['modifiers']['incumbent']

# ─────────────────────────────────────────
# 9. Assemble v0.2 JSON
# ─────────────────────────────────────────
content = {
    '$schema':     'qualify-content-schema-v2',
    'version':     '0.2.0',
    'lastUpdated': '2026-04-16',
    'changelog': [
        {
            'version': '0.1.0', 'date': '2026-04-09',
            'summary': 'Initial release. 24 questions, 6 categories, 4 archetype profiles, Alex Mercer persona, incumbent rebid modifier.',
        },
        {
            'version': '0.2.0', 'date': '2026-04-16',
            'summary': (
                'Pursuit Viability redesign. 25 v6 questions, 5 categories, 8 archetype profiles, '
                '4-stage model, 5-band RAG tier output, challenger overlay added, incumbent overlay '
                'restructured to 8 questions. PWIN number suppressed; viability tier is headline output.'
            ),
        },
    ],
    'stages': [
        {
            'id': 'identify', 'label': 'Identify', 'expectedMaturity': 'low',
            'description': (
                "The opportunity has been scanned and an initial view formed. Pre-market or earliest "
                "market-engagement signals have been picked up. No formal commitment to pursue has been made. "
                "Viability at this stage is mostly about strategic fit, preliminary contestability, and whether "
                "the opportunity is worth investing time to understand more deeply. Thin evidence bases are normal "
                "and expected. Strong assessments are rare by design -- a Strong at Identify requires genuine "
                "structural advantage that does not need further validation, not just early optimism."
            ),
        },
        {
            'id': 'capture', 'label': 'Capture', 'expectedMaturity': 'medium',
            'description': (
                "Active capture is underway. The team is engaging with the buyer ahead of any formal ITT or RFP. "
                "This is where relationship intelligence, buyer understanding, stakeholder access, and competitive "
                "position are built. Viability is mostly about whether the team is on the right trajectory -- gaps "
                "at Capture are recoverable if there is time to close them, but structural weaknesses (no champion, "
                "no insight, no differentiated position) become very difficult to fix once the ITT lands. "
                "Assessments should reflect what the team actually knows, not what they intend to find out."
            ),
        },
        {
            'id': 'pursue', 'label': 'Pursue', 'expectedMaturity': 'high',
            'description': (
                "The ITT or RFP is live. A formal pursuit is underway and the clock is running. Evidence depth, "
                "scoreability of the proposition, delivery confidence, and commercial viability all matter at this "
                "stage. The tolerance for gaps is much lower than at Capture -- what is not known or not built now "
                "will be absent from the submission. Assessments should be honest about what remains unresolved, "
                "because at Pursue, a gap is no longer a future action but a current risk."
            ),
        },
        {
            'id': 'submit', 'label': 'Submit', 'expectedMaturity': 'very-high',
            'description': (
                "The submission has been made or is imminent. The team may be at shortlist, BAFO, or preferred "
                "bidder stage. The question is about submission strength, competitive defensibility, and late-stage "
                "risk rather than evidence-building. Viability at Submit reflects the quality of what was built and "
                "written, not what is still intended. A Walk Away at Submit does not mean stop -- it means the "
                "expected value of continued investment is low and the team should be clear-eyed about why."
            ),
        },
    ],
    'ragTiers': [
        {'id': 'strong',        'label': 'Strong',        'ordinal': 5,
         'oneLineMeaning': 'Viability is high for the current stage. Position is earned and evidenced. Continue and consolidate.'},
        {'id': 'onTrack',       'label': 'On Track',      'ordinal': 4,
         'oneLineMeaning': 'Viability is appropriate for the current stage. Some gaps but nothing structural. Continue with focused improvements.'},
        {'id': 'conditional',   'label': 'Conditional',   'ordinal': 3,
         'oneLineMeaning': 'Viability is at the lower edge of acceptable for the current stage. Specific conditions must be met before further investment is justified.'},
        {'id': 'majorConcerns', 'label': 'Major Concerns','ordinal': 2,
         'oneLineMeaning': 'Viability is below what the stage requires. Material reshaping is required, or the pursuit should move to watch/shape rather than active pursuit.'},
        {'id': 'walkAway',      'label': 'Walk Away',     'ordinal': 1,
         'oneLineMeaning': 'Viability is structurally weak. Continued investment is not justified. Recommend qualifying out or returning to early-stage shaping only if the underlying conditions change.'},
    ],
    'ragCalibration': {
        'scoreBands': [
            {'id': 'top',         'minPct': 0.85},
            {'id': 'upperMiddle', 'minPct': 0.70},
            {'id': 'middle',      'minPct': 0.55},
            {'id': 'lowerMiddle', 'minPct': 0.35},
            {'id': 'bottom',      'minPct': 0.00},
        ],
        'matrix': {
            'identify': {'top': 'strong',  'upperMiddle': 'strong',  'middle': 'onTrack',      'lowerMiddle': 'conditional',   'bottom': 'majorConcerns'},
            'capture':  {'top': 'strong',  'upperMiddle': 'onTrack', 'middle': 'onTrack',      'lowerMiddle': 'conditional',   'bottom': 'majorConcerns'},
            'pursue':   {'top': 'strong',  'upperMiddle': 'onTrack', 'middle': 'conditional',  'lowerMiddle': 'majorConcerns', 'bottom': 'walkAway'},
            'submit':   {'top': 'strong',  'upperMiddle': 'onTrack', 'middle': 'conditional',  'lowerMiddle': 'majorConcerns', 'bottom': 'walkAway'},
        },
        'criticalQuestionCaps': {
            'identify': {'strongDisagreeOnCritical': 'conditional',   'multipleStrongDisagree': 'majorConcerns'},
            'capture':  {'strongDisagreeOnCritical': 'majorConcerns', 'multipleStrongDisagree': 'walkAway'},
            'pursue':   {'strongDisagreeOnCritical': 'majorConcerns', 'multipleStrongDisagree': 'walkAway'},
            'submit':   {'strongDisagreeOnCritical': 'walkAway',      'multipleStrongDisagree': 'walkAway'},
        },
    },
    'scoring': {
        'scorePts': {'Strongly Agree': 4, 'Agree': 3, 'Disagree': 2, 'Strongly Disagree': 1},
        'evidenceQualityMultipliers': {'high': 1.0, 'medium': 0.85, 'low': 0.65, 'veryLow': 0.40},
        'formula': {
            'perQuestion': '((response - 1) / 3) * evidenceQualityMultiplier',
            'perCategory': 'weighted_average(perQuestion * within_category_qw)',
            'perPursuit':  'sum(perCategory * archetype_weighted_category_weight)',
            'tierMapping': 'ragCalibration.matrix[stage][scoreBand], capped by criticalQuestionCaps[stage]',
        },
        'surfacedToUser': False,
    },
    'categories': [
        {'id': 'bndl', 'name': 'Buyer Need & Decision Logic',              'weight': 0.25,
         'description': "Tests the depth and currency of the team's understanding of why the buyer is going to market, what they most need, and what would make them choose change over continuity."},
        {'id': 'spa',  'name': 'Stakeholder Position & Access',            'weight': 0.20,
         'description': "Tests whether the team knows who really shapes the decision, has access to or reliable insight into key stakeholders, and understands what could work against them from a people and politics perspective."},
        {'id': 'cpid', 'name': 'Competitive Position & Incumbent Dynamics','weight': 0.20,
         'description': "Tests whether the team understands the competitive field well enough to win in it -- identifying the likely winner, understanding incumbent defensibility, and demonstrating an evidenced advantage where it matters most."},
        {'id': 'ppsf', 'name': 'Procurement, Proposition & Solution Fit',  'weight': 0.20,
         'description': "Tests whether the procurement design can reward the team's strengths, whether eligibility and suitability criteria are met, and whether the proposition and proof story are aligned to what the buyer actually values."},
        {'id': 'cdpr', 'name': 'Commercial, Delivery & Pursuit Readiness', 'weight': 0.15,
         'description': "Tests whether the deal is commercially viable, the delivery model is credible at the required scale, risks are understood and manageable, and the pursuit team has the capacity to execute to the required standard."},
    ],
    'weightProfiles': arch_weights,
    'archetypeProfile': {
        'consulting_advisory':           'consulting_advisory',
        'digital_transformation_si':     'digital_transformation_si',
        'digital_product_saas':          'digital_product_saas',
        'bpo_managed_service':           'bpo_managed_service',
        'facilities_operational':        'facilities_operational',
        'hybrid_transformation_managed': 'hybrid_transformation_managed',
        'framework_panel':               'framework_panel',
        'incumbent_renewal':             'incumbent_renewal',
        # v0.1 aliases for backward-compatibility
        'BPO':                   'bpo_managed_service',
        'IT Outsourcing':        'digital_transformation_si',
        'Managed Service':       'bpo_managed_service',
        'Digital Outcomes':      'digital_transformation_si',
        'Consulting / Advisory': 'consulting_advisory',
        'Infrastructure & Hardware': 'digital_product_saas',
        'Software / SaaS':       'digital_product_saas',
    },
    'questionPacks': {
        'core': {
            'id': 'core', 'name': 'Core 25 Questions',
            'description': (
                'The standard 25-question viability model. Applied to all pursuits. '
                'Archetype-adjusted category weights rebalance the score without changing the questions.'
            ),
            'questions': core_questions,
        }
    },
    'modifiers': {
        'incumbent': {
            'id': 'incumbent',
            'name': 'Incumbent Position Modifier',
            'description': incumbent_v01.get('description', ''),
            'trigger': {'field': 'context.role', 'matches': ['incumbent','Incumbent','We are the incumbent defending this contract']},
            'designPrinciples': incumbent_v01.get('designPrinciples', []),
            'architecture':     incumbent_v01.get('architecture', []),
            'addsQuestions':    inc_q_list,
            'addsPersonaTriggers': copy.deepcopy(incumbent_v01.get('addsPersonaTriggers', {})),
            'addsOutput':       copy.deepcopy(incumbent_v01.get('addsOutput', {})),
        },
        'challenger': {
            'id': 'challenger',
            'name': 'Challenger Position Modifier',
            'description': (
                "Activated when the team is challenging an incumbent. Adds 8 questions testing the strength "
                "of the displacement case, the buyer's switching motivation, and the team's readiness to counter "
                "incumbent defensibility."
            ),
            'trigger': {'field': 'context.role', 'matches': ['challenger','Challenger','We are challenging an incumbent']},
            'designPrinciples': [
                "The challenger question is not 'can we win?' -- it is 'why would the buyer switch, and do we have the evidence to make that case credible?'",
                "A competitive tender does not mean the buyer wants change. A challenger must earn the right to be taken seriously against an embedded incumbent.",
                "Switching motivation is a buyer property, not a bidder property. The team can describe switching drivers but cannot manufacture them.",
                "The strongest challengers understand the incumbent's position as well as the incumbent does. Displacement logic built on assumption is not displacement logic.",
                "Challenger inflation is systematic: teams in pursuit typically overstate switching appetite, understate incumbent continuity bias, and discount the weight of proven performance.",
            ],
            'architecture': [
                "Activated by context.role = challenger. Adds 8 C-questions to the core 25.",
                "C01-C04 test the displacement case: switching motivation, performance vulnerability, renewal-plus-improvement absence, and the strength of the challenger's entry point.",
                "C05-C08 test competitive readiness: understanding of the incumbent's counter-narrative, proof adjacency, commercial credibility, and the challenger's differentiated entry.",
                "The challengerPositionAssessment output captures the switching case strength, the incumbent's likely response posture, and the specific actions the challenger must take.",
                "One AI call with combined schema -- the core 25 and the 8 challenger questions are evaluated together, not sequentially.",
            ],
            'addsQuestions': chal_q_list,
            'addsPersonaTriggers': {
                'inflationTriggers': [
                    {'id': 'CI-1', 'trigger': "The team describes the buyer's dissatisfaction without naming a specific source or providing documented evidence of it.", 'alexResponse': "Flag: switching motivation described without evidence. Name the source or acknowledge this is inferred."},
                    {'id': 'CI-2', 'trigger': "The team claims the buyer wants a fresh supplier because a competitive tender was issued.", 'alexResponse': "Flag: the existence of a tender is not evidence of switching appetite. What does the buyer's engagement tell you?"},
                    {'id': 'CI-3', 'trigger': "The team asserts they have a stronger solution without explaining why the buyer would bear the switching cost to get it.", 'alexResponse': "Flag: superior capability does not override switching inertia. What is the buyer's specific reason to absorb the cost and risk of change?"},
                    {'id': 'CI-4', 'trigger': "The team describes competitor weaknesses without explaining why those weaknesses matter to this specific buyer at this stage.", 'alexResponse': "Flag: competitor weakness is only a displacement driver if the buyer is aware of it and weighs it. What is the evidence?"},
                ],
                'calibrationRules': [
                    {'id': 'CC-1', 'rule': 'If C01 is Disagree or Strongly Disagree, cap the overall assessment at Conditional regardless of core score. No switching case means no displacement logic.'},
                    {'id': 'CC-2', 'rule': 'If both C01 and C02 are Disagree or Strongly Disagree, cap at Major Concerns. Absent switching motivation combined with absent performance vulnerability is a structural problem.'},
                    {'id': 'CC-3', 'rule': "If C05 (incumbent counter-narrative) is Strongly Disagree, flag that the challenger is flying blind into the incumbent's strongest defence."},
                    {'id': 'CC-4', 'rule': "If the archetype is BPO / managed service and C01 is below Agree, auto-query: switching cost in this archetype is exceptionally high. The switching case must be especially robust."},
                ],
                'autoVerdictRules': [
                    {'id': 'CA-1', 'rule': 'If C01 is Strongly Disagree at Pursue or Submit stage, recommend Major Concerns or Walk Away. A challenger with no documented switching case at this stage is unlikely to overcome incumbent inertia.'},
                    {'id': 'CA-2', 'rule': 'If the archetype is bpo_managed_service or facilities_operational and the challenger has no documented proof adjacency (C06), flag that delivery credibility is the primary incumbent counter-argument and it is not addressed.'},
                    {'id': 'CA-3', 'rule': 'If challenger scores Strong on C01-C04 but Major Concerns on C05-C08, query the balance: strong displacement case but weak competitive readiness.'},
                ],
            },
            'addsOutput': {
                'challengerPositionAssessment': {
                    'id': 'challengerPositionAssessment',
                    'name': 'Challenger Position Assessment',
                    'description': "AI-generated assessment of the strength of the displacement case and the challenger's readiness to execute it.",
                    'schema': [
                        {'fieldName': 'displacementCaseStrength',           'description': 'Overall assessment of how strong the displacement case is. 1-5 where 5 = displacement case is strong, evidenced, and buyer-validated.'},
                        {'fieldName': 'switchingCaseRiskProfile',           'description': '4-quadrant RAG: switching motivation strength / switching risk neutralisation / proof adjacency / contestability. Each quadrant rated Red/Amber/Green.'},
                        {'fieldName': 'incumbentCounterReadiness',          'description': "How well-prepared the challenger is to handle the incumbent's likely counter-narrative."},
                        {'fieldName': 'buyerSwitchingMotivationAssessment', 'description': "Assessment of the strength and reliability of the buyer's switching motivation. Is it evidenced, inferred, or assumed?"},
                        {'fieldName': 'blindSpots',                         'description': 'What challengers in this archetype / sector typically do not know or underestimate about displacing an incumbent.'},
                        {'fieldName': 'challengerStrategyRecommendation',   'description': 'One of four postures: Press the advantage / Build the case / Address readiness gaps / Reassess viability.'},
                        {'fieldName': 'specificDisplacementActions',        'description': 'Named-role, time-bound actions the team should take to strengthen the displacement case or address readiness gaps.'},
                        {'fieldName': 'switchingRiskNeutralisationGaps',    'description': "Where the challenger has not adequately addressed the buyer's fear of switching risk."},
                        {'fieldName': 'proofAdjacencyAssessment',           'description': "Whether the challenger's proof story is close enough to the requirement to reduce perceived delivery risk."},
                    ],
                },
            },
        },
    },
    'persona': persona,
    'opportunityTypeCalibration': opp_calibration,
    'outputs': {
        'viabilityAssessment': {
            'id': 'viabilityAssessment',
            'name': 'Pursuit Viability Assessment',
            'description': "The headline output. A 5-band named RAG tier with a narrative explaining the tier, the key determinants, the strongest argument against the assigned tier, and stage-appropriate conditions or actions.",
            'schema': [
                {'fieldName': 'tier',                       'description': 'One of: strong | onTrack | conditional | majorConcerns | walkAway. This is the only output shown at a glance.'},
                {'fieldName': 'narrative',                  'description': "3-5 paragraphs from Alex explaining why this tier was assigned at this stage, written in Alex's direct coaching voice. Must reference the stage context explicitly."},
                {'fieldName': 'topThreeDeterminants',       'description': 'The three factors that most determined the tier. Each named, with a 1-2 sentence explanation of why it was decisive.'},
                {'fieldName': 'strongestArgumentAgainst',   'description': 'The single most credible argument that the tier is wrong in the team\'s favour -- forces honesty.'},
                {'fieldName': 'conditions',                 'description': 'If Conditional or Major Concerns: specific, named, time-bound conditions that would lift the tier. If Walk Away: what would have to change in the world. If On Track or Strong: omit.'},
                {'fieldName': 'actions',                    'description': '2-4 named-role, time-bound actions that would most improve the viability position. Prioritised by impact. Specific to this pursuit and stage.'},
                {'fieldName': 'stage',                      'description': 'The stage used for calibration. One of: identify | capture | pursue | submit.'},
                {'fieldName': 'criticalQuestionCapsApplied','description': 'Audit trail: which critical question caps were applied and what they changed. Empty if none. Format: [{questionId, level, capApplied, wouldHaveBeen}].'},
            ],
        },
        'perQuestionAssurance': {
            'id': 'perQuestionAssurance',
            'name': 'Per-Question Assurance Review',
            'description': 'Per-question Alex Mercer review. Verdict (Validated/Queried/Challenged), suggestedScore, narrative, challenge questions, capture actions, inflation detection. Mechanism unchanged from v0.1. Available as drill-down; not shown in headline.',
            'schemaLocation': 'inline in app -- see buildPersonaPrompt outputSchema parameter',
        },
        # addsOutput itself IS the rebidRiskAssessment object in v0.1
        'rebidRiskAssessment': copy.deepcopy(incumbent_v01.get('addsOutput', {})),
        'challengerPositionAssessment': {
            'id': 'challengerPositionAssessment',
            'name': 'Challenger Position Assessment',
            'description': 'Mirror of rebidRiskAssessment for challenger pursuits. Available when challenger modifier is active.',
            'schemaLocation': 'modifiers.challenger.addsOutput.challengerPositionAssessment.schema',
        },
    },
    'sources': [
        {'id': 'v6-spec',      'name': 'Winnability Artifact Judgment Scorecard v6',
         'file': 'pwin-qualify/docs/Winnability_Artifact_Judgment_Scorecard_v6.xlsx',
         'note': 'Source for 25 core questions, 8 incumbent overlay questions, 8 challenger overlay questions, archetype weights, rubric hurdles, benchmark examples, challenge prompts, and actions.'},
        {'id': 'v02-brief',    'name': 'Pursuit Viability v0.2 Positioning Brief',
         'file': 'pwin-qualify/docs/PWIN_Qualify_v02_PositioningBrief.md'},
        {'id': 'v02-delta',    'name': 'Pursuit Viability v0.2 Content Delta Plan',
         'file': 'pwin-qualify/docs/PWIN_Qualify_v02_ContentDeltaPlan.md'},
        {'id': 'v02-preserve', 'name': 'Pursuit Viability v0.2 Preservation Inventory',
         'file': 'pwin-qualify/docs/PWIN_Qualify_v02_PreservationInventory.md'},
        {'id': 'rebid-review', 'name': 'PWIN Rebid Module Review',
         'file': 'pwin-qualify/docs/PWIN_Rebid_Module_Review.xlsx',
         'note': 'Source for incumbent overlay design principles, addsPersonaTriggers, and rebidRiskAssessment output -- all carried verbatim from v0.1.'},
    ],
}

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(content, f, indent=2, ensure_ascii=False)

print('Written:', OUT)
print('Core questions:       ', len(content['questionPacks']['core']['questions']))
print('Incumbent overlay Qs: ', len(content['modifiers']['incumbent']['addsQuestions']))
print('Challenger overlay Qs:', len(content['modifiers']['challenger']['addsQuestions']))
print('Archetype profiles:   ', len(content['weightProfiles']))
print('Categories:           ', len(content['categories']))
kb = len(json.dumps(content, ensure_ascii=False)) // 1024
print('JSON size:             %d KB' % kb)
