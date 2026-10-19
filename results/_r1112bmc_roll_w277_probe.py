# -*- coding: utf-8 -*-
"""r1112 bm-c: W277 seat-probe builder ROLLER (E63 canon-clone, one-generation
machine shift of _r1109bmc_build_w276_probe.py; zero hand transcription r587).
Produces results/_r1112bmc_build_w277_probe.py which clones
results/_w276bmc_20261019_probe.py -> results/_w277bmc_20261019_probe.py.
Roll pipeline per needle/MUST string: single-pass token maps (W/w labels one
gen; band +2,200; ledger/K chain; owner counts; ordinal words; bare wave
indices) THEN ordered context patches Q1..Q19, each global-count-asserted.
Pre-flight validates every needle's W276 text against the ACTUAL on-disk
probe before rolling. Receipt -> results/_r1112bmc_roll_w277_receipt.json."""
import ast, io, hashlib, json, os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_BUILDER = os.path.join(REPO, "results", "_r1109bmc_build_w276_probe.py")
PROBE276 = os.path.join(REPO, "results", "_w276bmc_20261019_probe.py")
OUT_BUILDER = os.path.join(REPO, "results", "_r1112bmc_build_w277_probe.py")
OUT_RECEIPT = os.path.join(REPO, "results", "_r1112bmc_roll_w277_receipt.json")


def extract(path, name):
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise SystemExit("assign not found: %s" % name)


NEEDLES276 = extract(SRC_BUILDER, "NEEDLES")
MUSTC = extract(SRC_BUILDER, "MUST_CONTAIN")
MUSTN = extract(SRC_BUILDER, "MUST_NOT_CONTAIN")

raw = io.open(PROBE276, "rb").read()
crlf = b"\r\n" in raw
body = raw.decode("utf-8")
if crlf:
    body = body.replace("\r\n", "\n")
for i, (old, new, expect) in enumerate(NEEDLES276, 1):
    n = body.count(new)
    assert n == expect, "preflight needle#%d: W276 text count=%d expect=%d head=%r" % (i, n, expect, new[:60])
print("preflight: %d needles all matched the on-disk W276 probe (crlf=%s)" % (len(NEEDLES276), crlf))

WMAP = {'W272': 'W273', 'W273': 'W274', 'W274': 'W275', 'W275': 'W276', 'W276': 'W277', 'W277': 'W278',
        'W278': 'W279'}
WLOW = {'w272': 'w273', 'w273': 'w274', 'w274': 'w275', 'w275': 'w276', 'w276': 'w277', 'w277': 'w278', 'w278': 'w279'}
NUMU = {
    '613_701': '615_901', '615_901': '618_101', '617_900': '620_100', '617_901': '620_101',
    '618_100': '620_300', '618_101': '620_301', '620_100': '622_300', '620_101': '622_301',
    '620_300': '622_500', '620_301': '622_501', '620_500': '622_700', '622_100': '624_300',
    '622_300': '624_500', '622_301': '624_501', '622_500': '624_700', '622_501': '624_701',
    '622_700': '624_900', '624_300': '626_500', '624_500': '626_700', '624_501': '626_701',
    '624_700': '626_900',
    '1_022_735': '1_024_935', '1_024_935': '1_027_135', '1_027_135': '1_029_335', '1_029_335': '1_031_535',
    '596_320': '598_520', '598_520': '600_720', '600_720': '602_920', '602_920': '605_120'}
NUMC = {
    '1,022,735': '1,024,935', '1,024,935': '1,027,135', '1,027,135': '1,029,335', '1,029,335': '1,031,535',
    '596,320': '598,520', '598,520': '600,720', '600,720': '602,920', '602,920': '605,120'}
BARE = {'264': '265', '265': '266', '266': '267', '273': '274', '274': '275', '275': '276', '276': '277',
        '94': '95', '95': '96'}
ORDM = {'TWENTY-FOURTH': 'TWENTY-FIFTH', 'TWENTY-FIFTH': 'TWENTY-SIXTH', 'TWENTY-SIXTH': 'TWENTY-SEVENTH',
        'twenty-fourth': 'twenty-fifth', 'twenty-fifth': 'twenty-sixth'}


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
    ('Q1', 'loop window r1109, 2026-10-19 ~05:5x', 'loop window r1112, 2026-10-19 ~08:0x', 1),
    ('Q1b', 'loop window r1109', 'loop window r1112', 1),
    ('Q2', 'loop r1109 window, 2026-10-19 ~05:5x', 'loop r1112 window, 2026-10-19 ~08:0x', 1),
    ('Q3', 'MSG-20261019-034x-bmc-w276-seat origin bf4bbbde1', 'MSG-20261019-055x-bmc-w277-seat origin 21b51a102', 1),
    ('Q4', 'e4e1ce44f5afd03b 1fcc0bc30f r1107', '5352c7cf343fc5e5 770a47fa1f r1110', 1),
    ('Q5', 'CLEAN-AT-BIRTH 8th gen 018782314d r1108', 'CLEAN-AT-BIRTH 9th gen 354a645155 r1111', 1),
    ('Q6', 'clean-at-birth 8th generation, zero heals of any class',
     'clean-at-birth 9th generation, editor zero-heal (12 gate-clone builder authoring heals caught pre-write, r1111 disclosure)', 1),
    ('Q7', 'appender-batched 5089f02250+e639699d59', 'appender-batched df7dedfd07+627c4e10f2+tail-shard-7', 1),
    ('Q8', '38th consecutive r1108 + finalize one-pass', '39th consecutive r1111 + finalize one-pass', 1),
    ('Q9', 'n1_w276_results.json r1108 ledger', 'n1_w276_results.json r1111 ledger', 1),
    ('Q10', 'r1108 cycle estate fc01636095 + closeout c77ee358f5',
     'r1111 cycle estate + closeout e781164e41 (finalize product estate-carried)', 1),
    ('Q11', 'r1108 splice face broken', 'r1111 splice face broken', 1),
    ('Q12', 'r1108 clean-at-birth 8th-gen splice 018782314d face',
     'r1111 clean-at-birth 9th-gen splice 354a645155 face', 1),
    ('Q13', 'registered+FINALIZED r1108 chain', 'registered+FINALIZED r1111 chain', 1),
    ('Q13b', 'landed r1108 chain', 'landed r1111 chain', 1),
    ('Q14', 'own-wave complete r1108 chain', 'own-wave complete r1111 chain', 2),
    ('Q15', 'r1105 clean-at-birth 7th-gen splice ec907d164 face',
     'r1108 clean-at-birth 8th-gen splice 018782314d face', 1),
    ('Q16', 'r1102 clean-at-birth 6th-gen splice 04f2127db face',
     'r1105 clean-at-birth 7th-gen splice ec907d164 face', 1),
    ('Q17', '266th', '267th', 2),
    ('Q18', '95th own wave', '96th own wave', 1),
    ('Q19', 'MSG-20261019-012x', 'MSG-20261019-034x', 1),
]

rolled = [tokens(new) for (old, new, expect) in NEEDLES276]
mustc277 = [tokens(m) for m in MUSTC]
mustn277 = [tokens(m) for m in MUSTN]

allstr = rolled + mustc277 + mustn277
patch_counts = {}
for pid, pat, rep, expect in PATCHES:
    tot = sum(s.count(pat) for s in allstr)
    assert tot == expect, "patch %s count=%d expect=%d :: %r" % (pid, tot, expect, pat[:70])
    for idx in range(len(allstr)):
        allstr[idx] = allstr[idx].replace(pat, rep)
    patch_counts[pid] = tot
    print("patch %s OK (%dx)" % (pid, tot))

rolled = allstr[:len(rolled)]
mustc277 = allstr[len(rolled):len(rolled) + len(mustc277)]
mustn277 = allstr[len(rolled) + len(mustc277):]

# old side = the W276 probe text (NEEDLES276's NEW), new side = rolled one generation
needles277 = [(new276, rolled_i, expect)
              for ((old275, new276, expect), rolled_i) in zip(NEEDLES276, rolled)]

# sanity: needle pairs must differ and new text must not equal old
for i, (old, new, expect) in enumerate(needles277, 1):
    assert old != new, "needle#%d rolled == old (no-op)" % i

HDR = '''# -*- coding: utf-8 -*-
"""r1112 builder: _w277bmc_20261019_probe.py canon-clone of
_w276bmc_20261019_probe.py per E63 age() machine-needle law (ordered exact
needles, each count-asserted, reverse-order wave rolls to avoid
duplicate-target collisions; live faces machine-verified pre-build this
window: W276 registry A 622501-624500 / B 624501-624700 bm-c, finalize
ledger 1,031,535 / merged 605,120 / klift +0.0001, owner 266 rows bmc 95 /
bma 130 / bmb 41, keytail [274, 275, 276], seat MSG-20261019-055x-bmc-w276-seat
on origin). Triple-label heal canon rolls one generation per r1100 heal note
(W274_W275_W276 labels kept rolling). Generated by machine roller
_r1112bmc_roll_w277_probe.py (token maps + count-asserted context patches,
zero hand transcription r587)."""
import py_compile

SRC = "results/_w276bmc_20261019_probe.py"
DST = "results/_w277bmc_20261019_probe.py"

'''

lines = [HDR, "NEEDLES = ["]
for old, new, expect in needles277:
    lines.append("    (%r,\n     %r, %d),\n" % (old, new, expect))
lines.append("]\n\n")
lines.append("MUST_CONTAIN = %r\n\n" % (mustc277,))
lines.append("MUST_NOT_CONTAIN = %r\n\n" % (mustn277,))
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
    "roller": "r1112 bm-c W277 seat-probe builder roller (machine one-generation shift, E63 canon-clone lineage)",
    "src_builder": "results/_r1109bmc_build_w276_probe.py",
    "probe276_verified": True, "crlf": bool(crlf),
    "needles": len(needles277), "must_contain": len(mustc277), "must_not_contain": len(mustn277),
    "patch_counts": patch_counts,
    "out_builder": "results/_r1112bmc_build_w277_probe.py",
    "out_builder_bytes": len(data), "out_builder_sha16": sha16,
    "expected_bands": {"A": [624701, 626700], "B": [626701, 626900]},
    "note": "expected bands per W276 seat receipt leg4 projection (staircase: A hops past registered W276 B tail 624_700; B lands above own-A tail+1); live walk governs r587 -- the probe re-derives on the live registry.",
}
with io.open(OUT_RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("ROLL OK -> results/_r1112bmc_build_w277_probe.py bytes=%d sha16=%s" % (len(data), sha16))
