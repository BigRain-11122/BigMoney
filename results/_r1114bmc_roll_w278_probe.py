# -*- coding: utf-8 -*-
"""r1114 bm-c: W278 seat-probe builder ROLLER (E63 canon-clone, one-generation
machine shift of _r1112bmc_build_w277_probe.py; zero hand transcription r587).
Produces results/_r1114bmc_build_w278_probe.py which clones
results/_w277bmc_20261019_probe.py -> results/_w278bmc_20261019_probe.py.
Roll pipeline per needle/MUST string: single-pass token maps (W/w labels one
gen; band/ledger/K chain; owner counts; bare wave indices) THEN ordered
context patches, each global-count-asserted. Pre-flight validates every
needle's W277 text against the ACTUAL on-disk probe before rolling.
Same-window heals disclosed: (1) the r1112 Q3 mislabel (seat MSG named
w277-seat while citing the W276 seat commit 21b51a102) is healed at birth --
the W278 probe header cites the TRUE upstream W277 seat
MSG-20261019-080x-bmc-w277-seat origin c5f8b88f91; (2) W277 cycle chain
attributed to r1114-continuation (sixgate+finalize+fivekeys+sec78 landed this
window; closeout rides the same-window estate commit).
Receipt -> results/_r1114bmc_roll_w278_receipt.json."""
import ast, io, hashlib, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_BUILDER = os.path.join(REPO, "results", "_r1112bmc_build_w277_probe.py")
PROBE277 = os.path.join(REPO, "results", "_w277bmc_20261019_probe.py")
OUT_BUILDER = os.path.join(REPO, "results", "_r1114bmc_build_w278_probe.py")
OUT_RECEIPT = os.path.join(REPO, "results", "_r1114bmc_roll_w278_receipt.json")


def extract(path, name):
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("assign not found: %s" % name)


NEEDLES277 = extract(SRC_BUILDER, "NEEDLES")
MUSTC = extract(SRC_BUILDER, "MUST_CONTAIN")
MUSTN = extract(SRC_BUILDER, "MUST_NOT_CONTAIN")

raw = io.open(PROBE277, "rb").read()
crlf = b"\r\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\r\n", "\n")
for i, (old, new, expect) in enumerate(NEEDLES277, 1):
    n = body.count(new)
    assert n == expect, "preflight needle#%d: W277 text count=%d expect=%d head=%r" % (i, n, expect, new[:60])
print("preflight: %d needles all matched the on-disk W277 probe (crlf=%s)" % (len(NEEDLES277), crlf))

WMAP = {'W273': 'W274', 'W274': 'W275', 'W275': 'W276', 'W276': 'W277', 'W277': 'W278', 'W278': 'W279',
        'W279': 'W280'}
WLOW = {'w273': 'w274', 'w274': 'w275', 'w275': 'w276', 'w276': 'w277', 'w277': 'w278', 'w278': 'w279',
        'w279': 'w280'}
NUMU = {
    '615_901': '618_101', '618_101': '620_301', '617_900': '620_100', '617_901': '620_101',
    '618_100': '620_300', '620_100': '622_300', '620_101': '622_301', '620_300': '622_500',
    '620_301': '622_501', '620_500': '622_700', '622_100': '624_300', '622_300': '624_500',
    '622_301': '624_501', '622_500': '624_700', '622_501': '624_701', '622_700': '624_900',
    '624_300': '626_500', '624_500': '626_700', '624_501': '626_701', '624_700': '626_900',
    '624_701': '626_901', '624_900': '627_100', '626_500': '628_700', '626_700': '628_900',
    '626_701': '628_901', '626_900': '629_100',
    '1_024_935': '1_027_135', '1_027_135': '1_029_335', '1_029_335': '1_031_535', '1_031_535': '1_033_735',
    '598_520': '600_720', '600_720': '602_920', '602_920': '605_120', '605_120': '607_320'}
NUMC = {
    '1,024,935': '1,027,135', '1,027,135': '1,029,335', '1,029,335': '1,031,535', '1,031,535': '1,033,735',
    '598,520': '600,720', '600,720': '602,920', '602,920': '605,120', '605,120': '607,320'}
BARE = {'265': '266', '266': '267', '267': '268', '273': '274', '274': '275', '275': '276', '276': '277',
        '277': '278', '94': '95', '95': '96'}
ORDM = {'TWENTY-FIFTH': 'TWENTY-SIXTH', 'TWENTY-SIXTH': 'TWENTY-SEVENTH', 'TWENTY-SEVENTH': 'TWENTY-EIGHTH',
        'twenty-fifth': 'twenty-sixth', 'twenty-sixth': 'twenty-seventh', 'twenty-seventh': 'twenty-eighth'}


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
    ('P1', 'loop window r1112, 2026-10-19 ~08:0x', 'loop window r1114-continuation, 2026-10-19 ~10:2x', 1),
    ('P1b', 'loop window r1112', 'loop window r1114-continuation', 1),
    ('P2', 'loop r1112 window, 2026-10-19 ~08:0x', 'loop r1114-continuation window, 2026-10-19 ~10:2x', 1),
    ('P3', 'MSG-20261019-055x-bmc-w278-seat origin 21b51a102', 'MSG-20261019-080x-bmc-w277-seat origin c5f8b88f91', 1),
    ('P4', '5352c7cf343fc5e5 770a47fa1f r1110', '45ee1de94c7d36fd e0bc4a0ddd r1113', 1),
    ('P5', 'CLEAN-AT-BIRTH 9th gen 354a645155 r1111', 'CLEAN-AT-BIRTH 10th gen 9e53371814 r1114', 1),
    ('P6', 'clean-at-birth 9th generation, editor zero-heal (12 gate-clone builder authoring heals caught pre-write, r1111 disclosure)',
     'clean-at-birth 10th generation, 2 disclosed editor gate-region table-heals (faces absent from canon, zero canon anomalies; r1114 editor header disclosure)', 1),
    ('P7', 'appender-batched df7dedfd07+627c4e10f2+tail-shard-7', 'appender-batched 0df07c846b+644b4f8459', 1),
    ('P8', '39th consecutive r1111 + finalize one-pass', '40th consecutive r1114-continuation + finalize one-pass', 1),
    ('P9', 'n1_w277_results.json r1111 ledger', 'n1_w277_results.json r1114-continuation ledger', 1),
    ('P10', 'r1111 cycle estate + closeout e781164e41 (finalize product estate-carried)',
     'r1114-continuation cycle estate (sixgate+finalize+fivekeys+sec78 landed same-window; closeout rides the same-window estate commit)', 1),
    ('P11', 'r1111 splice face broken', 'r1114 splice face broken', 1),
    ('P12', 'r1111 clean-at-birth 9th-gen splice 354a645155 face', 'r1114 clean-at-birth 10th-gen splice 9e53371814 face', 1),
    ('P13', 'r1108 clean-at-birth 8th-gen splice 018782314d face', 'r1111 clean-at-birth 9th-gen splice 354a645155 face', 1),
    ('P14', 'r1105 clean-at-birth 7th-gen splice ec907d164 face', 'r1108 clean-at-birth 8th-gen splice 018782314d face', 1),
    ('P13x', 'registered+FINALIZED r1111 chain', 'registered+FINALIZED r1114-continuation chain', 1),
    ('P17', 'landed r1111 chain', 'landed r1114-continuation chain', 1),
    ('P18', 'own-wave complete r1111 chain', 'own-wave complete r1114-continuation chain', 2),
    ('P15', '267th', '268th', 2),
    ('P16', '96th own wave', '97th own wave', 1),
    ('P19', 'MSG-20261019-034x', 'MSG-20261019-055x', 1),
]

rolled = [tokens(new) for (old, new, expect) in NEEDLES277]
mustc278 = [tokens(m) for m in MUSTC]
mustn278 = [tokens(m) for m in MUSTN]

allstr = rolled + mustc278 + mustn278
patch_counts = {}
for pid, pat, rep, expect in PATCHES:
    tot = sum(s.count(pat) for s in allstr)
    assert tot == expect, "patch %s count=%d expect=%d :: %r" % (pid, tot, expect, pat[:70])
    for idx in range(len(allstr)):
        allstr[idx] = allstr[idx].replace(pat, rep)
    patch_counts[pid] = tot
    print("patch %s OK (%dx)" % (pid, tot))

rolled = allstr[:len(rolled)]
mustc278 = allstr[len(rolled):len(rolled) + len(mustc278)]
mustn278 = allstr[len(rolled) + len(mustc278):]

# old side = the W277 probe text (NEEDLES277's NEW), new side = rolled one generation
needles278 = [(new277, rolled_i, expect)
              for ((old276, new277, expect), rolled_i) in zip(NEEDLES277, rolled)]

# sanity: needle pairs must differ and new text must not equal old
for i, (old, new, expect) in enumerate(needles278, 1):
    assert old != new, "needle#%d rolled == old (no-op)" % i

HDR = '''# -*- coding: utf-8 -*-
"""r1114 builder: _w278bmc_20261019_probe.py canon-clone of
_w277bmc_20261019_probe.py per E63 age() machine-needle law (ordered exact
needles, each count-asserted, reverse-order wave rolls to avoid
duplicate-target collisions; live faces machine-verified pre-build this
window: W277 registry A 624701-626700 / B 626701-626900 bm-c, finalize
ledger 1,033,735 / merged 607,320 / klift +0.0000, owner 267 rows bmc 96 /
bma 130 / bmb 41, keytail [275, 276, 277], seat MSG-20261019-080x-bmc-w277-seat
origin c5f8b88f91). Triple-label heal canon rolls one generation per r1100
heal note (W275_W276_W277 labels kept rolling). Generated by machine roller
_r1114bmc_roll_w278_probe.py (token maps + count-asserted context patches,
zero hand transcription r587; heals: the r1112 Q3 seat-MSG mislabel corrected
to the true upstream W277 seat; W277 cycle chain attributed r1114-continuation)."""
import py_compile

SRC = "results/_w277bmc_20261019_probe.py"
DST = "results/_w278bmc_20261019_probe.py"

'''

lines = [HDR, "NEEDLES = ["]
for old, new, expect in needles278:
    lines.append("    (%r,\n     %r, %d),\n" % (old, new, expect))
lines.append("]\n\n")
lines.append("MUST_CONTAIN = %r\n\n" % (mustc278,))
lines.append("MUST_NOT_CONTAIN = %r\n\n" % (mustn278,))
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
    "roller": "r1114 bm-c W278 seat-probe builder roller (machine one-generation shift, E63 canon-clone lineage)",
    "src_builder": "results/_r1112bmc_build_w277_probe.py",
    "probe277_verified": True, "crlf": bool(crlf),
    "needles": len(needles278), "must_contain": len(mustc278), "must_not_contain": len(mustn278),
    "patch_counts": patch_counts,
    "out_builder": "results/_r1114bmc_build_w278_probe.py",
    "out_builder_bytes": len(data), "out_builder_sha16": sha16,
    "expected_bands": {"A": [626901, 628900], "B": [628901, 629100]},
    "heals": ["r1112-Q3 seat-MSG mislabel healed: W278 probe cites the true upstream W277 seat MSG-20261019-080x-bmc-w277-seat origin c5f8b88f91",
              "W277 cycle chain attribution = r1114-continuation (sixgate+finalize+fivekeys+sec78 this window; closeout rides same-window estate)"],
    "note": "expected bands per the W277 probe receipt leg4 projection + W277 freeze receipt downstream_seat face (staircase: A hops past registered W277 B tail 626_900 -> 626_901..628_900; B lands above own-A tail+1 -> 628_901..629_100); live walk governs r587.",
}
with io.open(OUT_RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("ROLL OK -> results/_r1114bmc_build_w278_probe.py bytes=%d sha16=%s" % (len(data), sha16))
