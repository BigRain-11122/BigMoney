# -*- coding: utf-8 -*-
"""r1119 bm-c: W279 seat-probe builder ROLLER (E63 canon-clone, one-generation
machine shift of _r1114bmc_build_w278_probe.py; zero hand transcription r587).
Produces results/_r1119bmc_build_w279_probe.py which clones
results/_w278bmc_20261019_probe.py -> results/_w279bmc_20261019_probe.py.
Roll pipeline per needle/MUST string: single-pass token maps (W/w labels one
gen; band/ledger/K chain; owner counts; bare wave indices) THEN ordered
context patches, each global-count-asserted. Pre-flight validates every
needle's W278 text against the ACTUAL on-disk probe before rolling.
Same-window attribution disclosed: W278 cycle chain = r1118 (splice b6f486af35
+ engine burn 12/12 + sixgate 41st) + r1119 (finalize one-pass + fivekeys 6/6
+ sec78 backfill) same-session; W278 editor = CLEAN-AT-BIRTH 11th generation
with ZERO heals (needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured
law), replacing the prior-generation 2-disclosed-table-heals face.
Receipt -> results/_r1119bmc_roll_w279_receipt.json."""
import ast, io, hashlib, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_BUILDER = os.path.join(REPO, "results", "_r1114bmc_build_w278_probe.py")
PROBE278 = os.path.join(REPO, "results", "_w278bmc_20261019_probe.py")
OUT_BUILDER = os.path.join(REPO, "results", "_r1119bmc_build_w279_probe.py")
OUT_RECEIPT = os.path.join(REPO, "results", "_r1119bmc_roll_w279_receipt.json")


def extract(path, name):
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("assign not found: %s" % name)


NEEDLES278 = extract(SRC_BUILDER, "NEEDLES")
MUSTC = extract(SRC_BUILDER, "MUST_CONTAIN")
MUSTN = extract(SRC_BUILDER, "MUST_NOT_CONTAIN")

raw = io.open(PROBE278, "rb").read()
crlf = b"\r\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\r\n", "\n")
for i, (old, new, expect) in enumerate(NEEDLES278, 1):
    n = body.count(new)
    assert n == expect, "preflight needle#%d: W278 text count=%d expect=%d head=%r" % (i, n, expect, new[:60])
print("preflight: %d needles all matched the on-disk W278 probe (crlf=%s)" % (len(NEEDLES278), crlf))

WMAP = {'W273': 'W274', 'W274': 'W275', 'W275': 'W276', 'W276': 'W277', 'W277': 'W278', 'W278': 'W279',
        'W279': 'W280', 'W280': 'W281'}
WLOW = {'w273': 'w274', 'w274': 'w275', 'w275': 'w276', 'w276': 'w277', 'w277': 'w278', 'w278': 'w279',
        'w279': 'w280', 'w280': 'w281'}
NUMU = {
    '615_901': '618_101', '618_101': '620_301', '617_900': '620_100', '617_901': '620_101',
    '618_100': '620_300', '620_100': '622_300', '620_101': '622_301', '620_300': '622_500',
    '620_301': '622_501', '620_500': '622_700', '622_100': '624_300', '622_300': '624_500',
    '622_301': '624_501', '622_500': '624_700', '622_501': '624_701', '622_700': '624_900',
    '624_300': '626_500', '624_500': '626_700', '624_501': '626_701', '624_700': '626_900',
    '624_701': '626_901', '624_900': '627_100', '626_500': '628_700', '626_700': '628_900',
    '626_701': '628_901', '626_900': '629_100', '626_901': '629_101', '627_100': '629_300',
    '628_700': '630_900', '628_900': '631_100', '628_901': '631_101', '629_100': '631_300',
    '1_024_935': '1_027_135', '1_027_135': '1_029_335', '1_029_335': '1_031_535', '1_031_535': '1_033_735',
    '1_033_735': '1_035_935',
    '598_520': '600_720', '600_720': '602_920', '602_920': '605_120', '605_120': '607_320',
    '607_320': '609_520'}
NUMC = {
    '1,024,935': '1,027,135', '1,027,135': '1,029,335', '1,029,335': '1,031,535', '1,031,535': '1,033,735',
    '1,033,735': '1,035,935',
    '598,520': '600,720', '600,720': '602,920', '602,920': '605,120', '605,120': '607,320',
    '607,320': '609,520'}
BARE = {'265': '266', '266': '267', '267': '268', '268': '269', '273': '274', '274': '275', '275': '276',
        '276': '277', '277': '278', '278': '279', '94': '95', '95': '96', '96': '97'}
ORDM = {'TWENTY-FIFTH': 'TWENTY-SIXTH', 'TWENTY-SIXTH': 'TWENTY-SEVENTH', 'TWENTY-SEVENTH': 'TWENTY-EIGHTH',
        'TWENTY-EIGHTH': 'TWENTY-NINTH',
        'twenty-fifth': 'twenty-sixth', 'twenty-sixth': 'twenty-seventh', 'twenty-seventh': 'twenty-eighth',
        'twenty-eighth': 'twenty-ninth'}


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
    ('P1', 'loop window r1114-continuation, 2026-10-19 ~10:2x', 'loop window r1119, 2026-10-19 ~14:4x', 1),
    ('P1b', 'loop window r1114-continuation', 'loop window r1119', 1),
    ('P2', 'loop r1114-continuation window, 2026-10-19 ~10:2x', 'loop r1119 window, 2026-10-19 ~14:4x', 1),
    ('P3', 'MSG-20261019-080x-bmc-w278-seat origin c5f8b88f91', 'MSG-20261019-102x-bmc-w278-seat origin b187aa6214', 1),
    ('P4', '45ee1de94c7d36fd e0bc4a0ddd r1113', '99001d3d3f337942 df1aaba72a r1116', 1),
    ('P5', 'CLEAN-AT-BIRTH 10th gen 9e53371814 r1114', 'CLEAN-AT-BIRTH 11th gen b6f486af35 r1118', 1),
    ('P6', 'clean-at-birth 10th generation, 2 disclosed editor gate-region table-heals (faces absent from canon, zero canon anomalies; r1114 editor header disclosure)',
     'clean-at-birth 11th generation, zero heals (needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured law, zero table-heals; all count-asserted editor reps first-try; r1118 editor header disclosure)', 1),
    ('P7', 'appender-batched 0df07c846b+644b4f8459', 'appender-batched 60e630918f+b965e2ecf0', 1),
    ('P8', '40th consecutive r1114-continuation + finalize one-pass', '41st consecutive r1118 + finalize one-pass', 1),
    ('P9', 'n1_w278_results.json r1114-continuation ledger', 'n1_w278_results.json r1119 ledger', 1),
    ('P10', 'r1114-continuation cycle estate (sixgate+finalize+fivekeys+sec78 landed same-window; closeout rides the same-window estate commit)',
     'r1118+r1119 cycle estate (sixgate r1118 + finalize+fivekeys+sec78 r1119 same-session; closeout rides the r1119 estate commit)', 1),
    ('P11', 'r1114 splice face broken', 'r1118 splice face broken', 1),
    ('P12', 'r1114 clean-at-birth 10th-gen splice 9e53371814 face', 'r1118 clean-at-birth 11th-gen splice b6f486af35 face', 1),
    ('P13', 'r1111 clean-at-birth 9th-gen splice 354a645155 face', 'r1114 clean-at-birth 10th-gen splice 9e53371814 face', 1),
    ('P14', 'r1108 clean-at-birth 8th-gen splice 018782314d face', 'r1111 clean-at-birth 9th-gen splice 354a645155 face', 1),
    ('P13x', 'registered+FINALIZED r1114-continuation chain', 'registered+FINALIZED r1118+r1119 chain', 1),
    ('P17', 'landed r1114-continuation chain', 'landed r1118+r1119 chain', 1),
    ('P18', 'own-wave complete r1114-continuation chain', 'own-wave complete r1118+r1119 chain', 2),
    ('P15', '268th', '269th', 2),
    ('P16', '97th own wave', '98th own wave', 1),
    ('P19', 'MSG-20261019-055x', 'MSG-20261019-080x', 1),
]

rolled = [tokens(new) for (old, new, expect) in NEEDLES278]
mustc279 = [tokens(m) for m in MUSTC]
mustn279 = [tokens(m) for m in MUSTN]

allstr = rolled + mustc279 + mustn279
patch_counts = {}
for pid, pat, rep, expect in PATCHES:
    tot = sum(s.count(pat) for s in allstr)
    assert tot == expect, "patch %s count=%d expect=%d :: %r" % (pid, tot, expect, pat[:70])
    for idx in range(len(allstr)):
        allstr[idx] = allstr[idx].replace(pat, rep)
    patch_counts[pid] = tot
    print("patch %s OK (%dx)" % (pid, tot))

rolled = allstr[:len(rolled)]
mustc279 = allstr[len(rolled):len(rolled) + len(mustc279)]
mustn279 = allstr[len(rolled) + len(mustc279):]

# old side = the W278 probe text (NEEDLES278's NEW), new side = rolled one generation
needles279 = [(new278, rolled_i, expect)
              for ((old277, new278, expect), rolled_i) in zip(NEEDLES278, rolled)]

# sanity: needle pairs must differ and new text must not equal old
for i, (old, new, expect) in enumerate(needles279, 1):
    assert old != new, "needle#%d rolled == old (no-op)" % i

HDR = '''# -*- coding: utf-8 -*-
"""r1119 builder: _w279bmc_20261019_probe.py canon-clone of
_w278bmc_20261019_probe.py per E63 age() machine-needle law (ordered exact
needles, each count-asserted, reverse-order wave rolls to avoid
duplicate-target collisions; live faces machine-verified pre-build this
window: W278 registry A 626901-628900 / B 628901-629100 bm-c, finalize
ledger 1,035,935 / merged 609,520 / klift -0.0002, owner 268 rows bmc 97 /
bma 130 / bmb 41, keytail [276, 277, 278], seat MSG-20261019-102x-bmc-w278-seat
origin b187aa6214). Triple-label heal canon rolls one generation per r1100
heal note (W276_W277_W278 labels kept rolling). Generated by machine roller
_r1119bmc_roll_w279_probe.py (token maps + count-asserted context patches,
zero hand transcription r587; attribution: W278 cycle chain = r1118 sixgate +
r1119 finalize/fivekeys/sec78 same-session; W278 editor CLEAN-AT-BIRTH 11th
generation zero heals, needle preflight FIRST-RUN ZERO-MISMATCH r1077 law)."""
import py_compile

SRC = "results/_w278bmc_20261019_probe.py"
DST = "results/_w279bmc_20261019_probe.py"

'''

lines = [HDR, "NEEDLES = ["]
for old, new, expect in needles279:
    lines.append("    (%r,\n     %r, %d),\n" % (old, new, expect))
lines.append("]\n\n")
lines.append("MUST_CONTAIN = %r\n\n" % (mustc279,))
lines.append("MUST_NOT_CONTAIN = %r\n\n" % (mustn279,))
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
    "roller": "r1119 bm-c W279 seat-probe builder roller (machine one-generation shift, E63 canon-clone lineage)",
    "src_builder": "results/_r1114bmc_build_w278_probe.py",
    "probe278_verified": True, "crlf": bool(crlf),
    "needles": len(needles279), "must_contain": len(mustc279), "must_not_contain": len(mustn279),
    "patch_counts": patch_counts,
    "out_builder": "results/_r1119bmc_build_w279_probe.py",
    "out_builder_bytes": len(data), "out_builder_sha16": sha16,
    "expected_bands": {"A": [629101, 631100], "B": [631101, 631300]},
    "heals": ["W278 cycle chain attribution = r1118 (splice+burn+sixgate) + r1119 (finalize+fivekeys+sec78) same-session; closeout rides the r1119 estate commit",
              "W278 editor CLEAN-AT-BIRTH face rolled 10th->11th generation with ZERO heals (needle preflight FIRST-RUN ZERO-MISMATCH r1077 measured law), replacing the prior-generation 2-disclosed-table-heals face"],
    "note": "expected bands per the W278 probe receipt leg4 projection + W278 freeze receipt downstream_seat face (staircase: A hops past registered W278 B tail 629_100 -> 629_101..631_100; B lands above own-A tail+1 -> 631_101..631_300); live walk governs r587.",
}
with io.open(OUT_RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("ROLL OK -> results/_r1119bmc_build_w279_probe.py bytes=%d sha16=%s" % (len(data), sha16))
