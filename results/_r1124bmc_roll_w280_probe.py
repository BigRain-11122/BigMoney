# -*- coding: utf-8 -*-
"""r1124 bm-c: W280 seat-probe builder ROLLER (E63 canon-clone, one-generation
machine shift of _r1119bmc_build_w279_probe.py; zero hand transcription r587).
Produces results/_r1124bmc_build_w280_probe.py which clones
results/_w279bmc_20261019_probe.py -> results/_w280bmc_20261019_probe.py.
Roll pipeline per needle/MUST string: single-pass token maps (W/w labels one
gen; band/ledger/K chain arithmetic +2,200; owner counts; bare wave indices)
THEN ordered context patches, each global-count-asserted. Pre-flight validates
every needle's W279 text against the ACTUAL on-disk probe before rolling.
Same-window attribution disclosed: W279 cycle chain = r1123 (splice 3810f4a7ac
+ engine burn 12/12 batches 498d178d0b+332e8e8656) + r1124 (sixgate 42nd +
finalize one-pass 1,038,135/611,720 EXACT + fivekeys 6/6 + sec78 backfill
placeholders=0) same-session; W279 editor = CLEAN-AT-BIRTH 12th generation
with ZERO editor heals (needle preflight FIRST-RUN one disclosed table-heal =
push-race- x2 delivery prose forms, expectation-table face only, r1077
measured law measured-governs).
Receipt -> results/_r1124bmc_roll_w280_receipt.json."""
import ast, io, hashlib, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_BUILDER = os.path.join(REPO, "results", "_r1119bmc_build_w279_probe.py")
PROBE279 = os.path.join(REPO, "results", "_w279bmc_20261019_probe.py")
OUT_BUILDER = os.path.join(REPO, "results", "_r1124bmc_build_w280_probe.py")
OUT_RECEIPT = os.path.join(REPO, "results", "_r1124bmc_roll_w280_receipt.json")


def extract(path, name):
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("assign not found: %s" % name)


NEEDLES279 = extract(SRC_BUILDER, "NEEDLES")
MUSTC = extract(SRC_BUILDER, "MUST_CONTAIN")
MUSTN = extract(SRC_BUILDER, "MUST_NOT_CONTAIN")

raw = io.open(PROBE279, "rb").read()
crlf = b"\r\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\r\n", "\n")
for i, (old, new, expect) in enumerate(NEEDLES279, 1):
    n = body.count(new)
    assert n == expect, "preflight needle#%d: W279 text count=%d expect=%d head=%r" % (i, n, expect, new[:60])
print("preflight: %d needles all matched the on-disk W279 probe (crlf=%s)" % (len(NEEDLES279), crlf))

WMAP = {'W273': 'W274', 'W274': 'W275', 'W275': 'W276', 'W276': 'W277', 'W277': 'W278', 'W278': 'W279',
        'W279': 'W280', 'W280': 'W281', 'W281': 'W282', 'W282': 'W283'}
WLOW = {'w273': 'w274', 'w274': 'w275', 'w275': 'w276', 'w276': 'w277', 'w277': 'w278', 'w278': 'w279',
        'w279': 'w280', 'w280': 'w281', 'w281': 'w282', 'w282': 'w283'}
NUMU = {
    '615_901': '618_101', '618_101': '620_301', '617_900': '620_100', '617_901': '620_101',
    '618_100': '620_300', '620_100': '622_300', '620_101': '622_301', '620_300': '622_500',
    '620_301': '622_501', '620_500': '622_700', '622_100': '624_300', '622_300': '624_500',
    '622_301': '624_501', '622_500': '624_700', '622_501': '624_701', '622_700': '624_900',
    '624_300': '626_500', '624_500': '626_700', '624_501': '626_701', '624_700': '626_900',
    '624_701': '626_901', '624_900': '627_100', '626_500': '628_700', '626_700': '628_900',
    '626_701': '628_901', '626_900': '629_100', '626_901': '629_101', '627_100': '629_300',
    '628_700': '630_900', '628_900': '631_100', '628_901': '631_101', '629_100': '631_300',
    '629_101': '631_301', '629_300': '631_500', '630_900': '633_100', '631_100': '633_300',
    '631_101': '633_301', '631_300': '633_500', '631_301': '633_501', '631_500': '633_700',
    '633_100': '635_300',
    '1_024_935': '1_027_135', '1_027_135': '1_029_335', '1_029_335': '1_031_535', '1_031_535': '1_033_735',
    '1_033_735': '1_035_935', '1_035_935': '1_038_135',
    '598_520': '600_720', '600_720': '602_920', '602_920': '605_120', '605_120': '607_320',
    '607_320': '609_520', '609_520': '611_720'}
NUMC = {
    '1,024,935': '1,027,135', '1,027,135': '1,029,335', '1,029,335': '1,031,535', '1,031,535': '1,033,735',
    '1,033,735': '1,035,935', '1,035,935': '1,038,135',
    '598,520': '600,720', '600,720': '602,920', '602,920': '605,120', '605,120': '607,320',
    '607,320': '609,520', '609,520': '611,720'}
BARE = {'265': '266', '266': '267', '267': '268', '268': '269', '269': '270', '273': '274', '274': '275',
        '275': '276', '276': '277', '277': '278', '278': '279', '279': '280', '280': '281',
        '94': '95', '95': '96', '96': '97', '97': '98'}
ORDM = {'TWENTY-FIFTH': 'TWENTY-SIXTH', 'TWENTY-SIXTH': 'TWENTY-SEVENTH', 'TWENTY-SEVENTH': 'TWENTY-EIGHTH',
        'TWENTY-EIGHTH': 'TWENTY-NINTH', 'TWENTY-NINTH': 'THIRTIETH',
        'twenty-fifth': 'twenty-sixth', 'twenty-sixth': 'twenty-seventh', 'twenty-seventh': 'twenty-eighth',
        'twenty-eighth': 'twenty-ninth', 'twenty-ninth': 'thirtieth'}


def sub1(pat, mapping, s):
    return re.sub(pat, lambda m: mapping.get(m.group(0), m.group(0)), s)


def tokens(s):
    s = sub1(r'W\d{3}', WMAP, s)
    s = sub1(r'w\d{3}', WLOW, s)
    s = sub1(r'\d_\d{3}_\d{3}|\d{3}_\d{3}', NUMU, s)
    s = sub1(r'\d,\d{3},\d{3}|\d{3},\d{3}', NUMC, s)
    s = sub1(r'\b\d{2,3}\b', BARE, s)
    s = sub1(r'TWENTY-[A-Z]+|twenty-[a-z]+', ORDM, s)
    return s


# ordered context patches (post-token-roll patterns), each global-count-asserted.
PATCHES = [
    ('P1', 'loop window r1119, 2026-10-19 ~14:4x', 'loop window r1124, 2026-10-19 ~20:0x', 1),
    ('P1b', 'loop window r1119', 'loop window r1124', 1),
    ('P2', 'loop r1119 window, 2026-10-19 ~14:4x', 'loop r1124 window, 2026-10-19 ~20:0x', 1),
    ('P3', 'MSG-20261019-102x-bmc-w279-seat origin b187aa6214', 'MSG-20261019-145x-bmc-w279-seat origin 900c23fe7d', 1),
    ('P4', '99001d3d3f337942 df1aaba72a r1116', 'c2fc7c34d0e41a68 ba5c725b42 r1122', 1),
    ('P5', 'CLEAN-AT-BIRTH 11th gen b6f486af35 r1118', 'CLEAN-AT-BIRTH 12th gen 3810f4a7ac r1123', 1),
    ('P6', 'clean-at-birth 11th generation, zero heals (needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured law, zero table-heals; all count-asserted editor reps first-try; r1118 editor header disclosure)',
     'clean-at-birth 12th generation, zero editor heals (E63 23rd-gen editor CLEAN-AT-BIRTH; needle preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose forms, expectation-table face only, zero canon anomalies; r1123 editor header disclosure)', 1),
    ('P7', 'appender-batched 60e630918f+b965e2ecf0', 'appender-batched 498d178d0b+332e8e8656', 1),
    ('P8', '41st consecutive r1118 + finalize one-pass', '42nd consecutive r1124 + finalize one-pass', 1),
    ('P9', 'n1_w279_results.json r1119 ledger', 'n1_w279_results.json r1124 ledger', 1),
    ('P10', 'r1118+r1119 cycle estate (sixgate r1118 + finalize+fivekeys+sec78 r1119 same-session; closeout rides the r1119 estate commit)',
     'r1123+r1124 cycle estate (splice+burn r1123 + sixgate+finalize+fivekeys+sec78 r1124 same-session; closeout rides the r1124 estate commit)', 1),
    ('P11', 'r1118 splice face broken', 'r1123 splice face broken', 1),
    ('P12', 'r1118 clean-at-birth 11th-gen splice b6f486af35 face', 'r1123 clean-at-birth 12th-gen splice 3810f4a7ac face', 1),
    ('P13', 'r1114 clean-at-birth 10th-gen splice 9e53371814 face', 'r1118 clean-at-birth 11th-gen splice b6f486af35 face', 1),
    ('P14', 'r1111 clean-at-birth 9th-gen splice 354a645155 face', 'r1114 clean-at-birth 10th-gen splice 9e53371814 face', 1),
    ('P13x', 'registered+FINALIZED r1118+r1119 chain', 'registered+FINALIZED r1123+r1124 chain', 1),
    ('P17', 'landed r1118+r1119 chain', 'landed r1123+r1124 chain', 1),
    ('P18', 'own-wave complete r1118+r1119 chain', 'own-wave complete r1123+r1124 chain', 2),
    ('P15', '269th', '270th', 2),
    ('P16', '98th own wave', '99th own wave', 1),
    ('P19', 'MSG-20261019-080x', 'MSG-20261019-102x', 1),
]

rolled = [tokens(new) for (old, new, expect) in NEEDLES279]
mustc280 = [tokens(m) for m in MUSTC]
mustn280 = [tokens(m) for m in MUSTN]

allstr = rolled + mustc280 + mustn280
patch_counts = {}
for pid, pat, rep, expect in PATCHES:
    tot = sum(s.count(pat) for s in allstr)
    assert tot == expect, "patch %s count=%d expect=%d :: %r" % (pid, tot, expect, pat[:70])
    for idx in range(len(allstr)):
        allstr[idx] = allstr[idx].replace(pat, rep)
    patch_counts[pid] = tot
    print("patch %s OK (%dx)" % (pid, tot))

rolled = allstr[:len(rolled)]
mustc280 = allstr[len(rolled):len(rolled) + len(mustc280)]
mustn280 = allstr[len(rolled) + len(mustc280):]

# old side = the W279 probe text (NEEDLES279's NEW), new side = rolled one generation
needles280 = [(new279, rolled_i, expect)
              for ((old278, new279, expect), rolled_i) in zip(NEEDLES279, rolled)]

# sanity: needle pairs must differ and new text must not equal old
for i, (old, new, expect) in enumerate(needles280, 1):
    assert old != new, "needle#%d rolled == old (no-op)" % i

HDR = '''# -*- coding: utf-8 -*-
"""r1124 builder: _w280bmc_20261019_probe.py canon-clone of
_w279bmc_20261019_probe.py per E63 age() machine-needle law (ordered exact
needles, each count-asserted, reverse-order wave rolls to avoid
duplicate-target collisions; live faces machine-verified pre-build this
window: W279 registry A 629101-631100 / B 631101-631300 bm-c, finalize
ledger 1,038,135 / merged 611,720 / klift +0.0000, owner 269 rows bmc 98 /
bma 130 / bmb 41, keytail [277, 278, 279], seat MSG-20261019-145x-bmc-w279-seat
origin 900c23fe7d). Triple-label heal canon rolls one generation per r1100
heal note (W277_W278_W279 labels kept rolling). Generated by machine roller
_r1124bmc_roll_w280_probe.py (token maps + count-asserted context patches,
zero hand transcription r587; attribution: W279 cycle chain = r1123 splice+burn +
r1124 sixgate+finalize+fivekeys+sec78 same-session; W279 editor CLEAN-AT-BIRTH 12th
generation zero editor heals, needle preflight FIRST-RUN one disclosed table-heal
push-race- x2 delivery prose forms r1077 measured law)."""
import py_compile

SRC = "results/_w279bmc_20261019_probe.py"
DST = "results/_w280bmc_20261019_probe.py"

'''

lines = [HDR, "NEEDLES = ["]
for old, new, expect in needles280:
    lines.append("    (%r,\n     %r, %d),\n" % (old, new, expect))
lines.append("]\n\n")
lines.append("MUST_CONTAIN = %r\n\n" % (mustc280,))
lines.append("MUST_NOT_CONTAIN = %r\n\n" % (mustn280,))
BUILD_LOGIC = '''
raw = open(SRC, "rb").read()
crlf = b"\\r\\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\\r\\n", "\\n")

for i, (old, new, expect) in enumerate(NEEDLES, 1):
    n = body.count(old)
    assert n == expect, f"needle#{i} count={n} expect={expect} :: head={old[:80]!r}"
    body = body.replace(old, new)
    print(f"needle#{i:02d} OK ({expect}x) {old[:48]!r}")

for m in MUST_CONTAIN:
    assert m in body, f"MUST_CONTAIN missing: {m!r}"
for m in MUST_NOT_CONTAIN:
    assert m not in body, f"MUST_NOT_CONTAIN leaked: {m!r}"

if crlf:
    body = body.replace("\\n", "\\r\\n")
with open(DST, "wb") as f:
    f.write(body.encode("utf-8"))
py_compile.compile(DST, doraise=True)
print("BUILD OK ->", DST, "| EOL=crlf" if crlf else "| EOL=lf",
      "| bytes", len(body.encode('utf-8')), "| needles", len(NEEDLES))
'''
src_out = "".join(lines) + BUILD_LOGIC
data = src_out.encode("utf-8")
with io.open(OUT_BUILDER, "wb") as f:
    f.write(data)
import py_compile
py_compile.compile(OUT_BUILDER, doraise=True)
sha16 = hashlib.sha256(data).hexdigest()[:16]
receipt = {
    "roller": "r1124 bm-c W280 seat-probe builder roller (machine one-generation shift, E63 canon-clone lineage)",
    "src_builder": "results/_r1119bmc_build_w279_probe.py",
    "probe279_verified": True, "crlf": bool(crlf),
    "needles": len(needles280), "must_contain": len(mustc280), "must_not_contain": len(mustn280),
    "patch_counts": patch_counts,
    "out_builder": "results/_r1124bmc_build_w280_probe.py",
    "out_builder_bytes": len(data), "out_builder_sha16": sha16,
    "expected_bands": {"A": [631301, 633300], "B": [633301, 633500]},
    "heals": ["W279 cycle chain attribution = r1123 (splice 3810f4a7ac+burn 12/12) + r1124 (sixgate 42nd+finalize 1,038,135/611,720 EXACT+fivekeys 6/6+sec78 placeholders=0) same-session; closeout rides the r1124 estate commit",
              "W279 editor CLEAN-AT-BIRTH face rolled 11th->12th generation with ZERO editor heals (needle preflight FIRST-RUN one disclosed table-heal = push-race- x2 delivery prose forms, expectation-table face only, r1077 measured law)"],
    "note": "expected bands per the W279 freeze receipt downstream_seat face (staircase inherited: W280 naive A start 631_101 lands INSIDE registered W279 B 631_101..631_300 -> A hops past W279 B tail 631_300 -> 631_301..633_300 TWENTY-NINTH consecutive A-hop expected; B own-A reservation cascade lands above own-A tail 633_300+1 -> 633_301..633_500 THIRTIETH consecutive above-own-A expected); live walk governs r587.",
}
with io.open(OUT_RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("ROLL OK -> results/_r1124bmc_build_w280_probe.py bytes=%d sha16=%s" % (len(data), sha16))
