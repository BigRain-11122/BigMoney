# -*- coding: utf-8 -*-
"""r936 bm-a W203 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG ALREADY-archived verification face). Direct-author per the
r909/r912/r915/r916/r919/r921/r922/r927 physical chunk-roll machinery,
rolled ONE generation: extract current W202 fragments, roll W202->W203
with count-asserted replacements, insert ADDITIVELY after the last
registered row; originals byte-identical zero-destroy. Old sides
DERIVED AT RUNTIME by the seven-gen chain (zero transcription, r587):
r912 AST triples (W195_old, W196_new, cnt) -> r915 AST RULES_* ->
W197 text -> r916 AST RULES_W198_* -> W198 text -> r919 AST
RULES_W199_* -> W199 text -> r921 freeze S (AST) -> W200 text ->
r922 freeze S (AST) -> W201 text -> r927 freeze S (AST) -> W202 text
= this build's old side (verified byte-identical against the r935
physical probe dumps results/_r935bma_probe_frag_*202.txt, r776 law).
W203 fact substitutions derived at runtime from the W202 new sides
via the ordered S shift (projection-first, bands staircase,
standalone numbers, ordinals, shas/rounds, bare wave numbers LAST;
the fixed W138 parity literal 94_201 sentinel-protected AND the
2026 date face sentinel-protected -- first generation where the bare
202->203 shift would otherwise collide with MSG dates and the
O-20261001-2355 order number).

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r930bma_w203_probe_receipt.json (bands A 461_404..463_403 /
B 463_404..463_603, hops 1/1, SIXTY-THIRD staircase, leg0 rows 200
tail W202 owner_rows 192 bma_rows 117 ordinal 193 bma_ordinal 118
w202_ledger_head 858,745, leg2 conflicts 0, leg3 origin vacancy,
leg4 W204p A 463_404..465_403 / B 463_604..463_803 hops 0/0
B-inside-A). Seat push dc00bfa54 (MSG-2026-10-09-2329-bma-w203-seat
+ probe script + probe receipt, 3-item, r930 seat push,
ancestor-verified). W201=bm-a r923 five-face freeze c1937ac47
(dead-session estate absorption) + engine self-burn 12/12; finalize
LANDED r924 estate-absorb push b71610ba4 (ledger 854,345+2,200=
856,545 EXACT, K=440,120 EXACT, skill_line_v2 1.1885). W202=bm-a
five-face freeze c76a84dc2 (r927 authored, died pre-commit; r928
estate-absorb landed; freeze sha machine-pinned via git log -S by
the r934 buildgen, superseding the r930 probe d372c9xx lineage
misnote) + engine self-burn 12/12; finalize LANDED r928 one-pass
push c76a84dc2 (ledger 856,545+2,200=858,745 EXACT, K=442,320
EXACT, skill_line_v2 1.1887) -- W203 freeze-time anchor = W202
finalize actuals per r590, zero roll-forward. Seat MSG archive
state = ALREADY LANDED pre-freeze (bm-a r930 seat-round closeout
consumed->processed same round per S7 law; the W203 seat MSG sits in
fleet/inbox/processed/ at freeze time).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment
PASS prints; r776 fragment-needle law (physical dumps re-verified
against the live files AND the r935 probe dumps at run time);
r780/r781 verify-separation (all stale+presence asserts in memory
BEFORE any write); r666 safe write order (n1 first, then pf).
Dry-run by default; --write performs the live writes."""
import ast
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")
R912 = os.path.join(ROOT, "results", "_r912bma_w196_freeze_edits.py")
R915 = os.path.join(ROOT, "results", "_r915bma_w197_freeze_edits.py")
R916 = os.path.join(ROOT, "results", "_r916bma_w198_freeze_edits.py")
R919 = os.path.join(ROOT, "results", "_r919bma_w199_freeze_edits.py")
R921F = os.path.join(ROOT, "results", "_r921bma_w200_freeze_edits.py")
R922F = os.path.join(ROOT, "results", "_r922bma_w201_freeze_edits.py")
R927F = os.path.join(ROOT, "results", "_r927bma_w202_freeze_edits.py")
RCPT = os.path.join(ROOT, "results", "_r930bma_w203_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r936bma_w203_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-2329-bma-w203-seat.md"
SEAT_PROCESSED = ("fleet/inbox/processed/"
                  "MSG-2026-10-09-2329-bma-w203-seat.md")
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W203_PREREG.md")
SEAT_SHA = "dc00bfa54"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
WRITE = "--write" in sys.argv
fails = []


def git_out(args):
    p = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "-C", ROOT]
                       + args, capture_output=True, creationflags=CNW)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def rep(text, old, new, expect, tag):
    n = text.count(old)
    if n != expect:
        fails.append("REPLACEMENT COUNT MISMATCH [%s]: got %d expect %d"
                      " literal=%r" % (tag, n, expect, old[:100]))
        return text
    return text.replace(old, new)


def extract_lists(path, names):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in names
                and isinstance(node.value, ast.List)):
            out[node.targets[0].id] = [ast.literal_eval(e)
                                       for e in node.value.elts]
    return out


def extract_stale_dict(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "STALE"
                and isinstance(node.value, ast.Dict)):
            out = {}
            for k, v in zip(node.value.keys, node.value.values):
                key = ast.literal_eval(k)
                assert isinstance(v, ast.List), "STALE value not a list"
                out[key] = [ast.literal_eval(e) for e in v.elts]
            return out
    return None


# ---- seven-gen extraction: r912 triples + r915/r916/r919 rules +
# r921/r922/r927 freeze S (AST) ----
def load_bloodline():
    t912 = extract_lists(R912, ("R", "RC", "RP", "RQ"))
    assert set(t912) == {"R", "RC", "RP", "RQ"}, \
        "r912 lists missing: %s" % sorted(t912)
    t915 = extract_lists(R915, ("RULES_MAT", "RULES_CFG", "RULES_PF",
                                "RULES_CLAIM", "MAT_ARCHIVE", "PF_ARCHIVE",
                                "DROP_IF"))
    assert set(t915) == {"RULES_MAT", "RULES_CFG", "RULES_PF",
                         "RULES_CLAIM", "MAT_ARCHIVE", "PF_ARCHIVE",
                         "DROP_IF"}, "r915 lists missing: %s" % sorted(t915)
    t916 = extract_lists(R916, ("RULES_W198_MAT", "RULES_W198_CFG",
                                "RULES_W198_PF", "RULES_W198_CLAIM"))
    assert set(t916) == {"RULES_W198_MAT", "RULES_W198_CFG",
                         "RULES_W198_PF", "RULES_W198_CLAIM"}, \
        "r916 lists missing: %s" % sorted(t916)
    t919 = extract_lists(R919, ("RULES_W199_MAT", "RULES_W199_CFG",
                                "RULES_W199_PF", "RULES_W199_CLAIM"))
    assert set(t919) == {"RULES_W199_MAT", "RULES_W199_CFG",
                         "RULES_W199_PF", "RULES_W199_CLAIM"}, \
        "r919 lists missing: %s" % sorted(t919)
    t921 = extract_lists(R921F, ("S",))
    assert set(t921) == {"S"}, "r921 freeze S list missing"
    t922 = extract_lists(R922F, ("S",))
    assert set(t922) == {"S"}, "r922 freeze S list missing"
    t927 = extract_lists(R927F, ("S",))
    assert set(t927) == {"S"}, "r927 freeze S list missing"
    return t912, t915, t916, t919, t921, t922, t927


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


def apply_s_r921(text):
    for (a, b) in T921["S"]:
        text = text.replace(a, b)
    return text


def apply_s_r922(text):
    for (a, b) in T922["S"]:
        text = text.replace(a, b)
    return text


def apply_s_r927(text):
    for (a, b) in T927["S"]:
        text = text.replace(a, b)
    return text


# ---- S: ordered W202->W203 fact shift (sentinels first; projection-
# first; bands staircase; standalone numbers; ordinals;
# shas/rounds/MSG; bare wave numbers LAST; every entry verified
# collision-free) ----
S = [
    # S0: sentinel-protect the fixed W138 parity literal 94_201 (the
    # bare 201->202 shift below would corrupt it); restored at the end
    ("94_201", "\x00K94"),
    # S0b: date sentinel -- MSG dates and the O-20261001-2355 order
    # number contain "2026" which the bare 202->203 shift would
    # corrupt (NEW this generation: W202-S did not need it); restored
    # at the end
    ("MSG-2026-10-09-1935", "MSG-2026-10-09-2329"),
    ("MSG-1935", "MSG-2329"),
    ("2026", "\x00Y26"),
    # B-phase: own-projection face (before bare shifts create W204)
    ("W203", "W204"),
    ("461_204..463_203", "463_404..465_403"),   # naive W204 A projection
    ("461_404..461_603", "463_604..463_803"),   # naive W204 B projection
    # C-phase: band staircase (each band face rolls one wave)
    ("461_204..461_403", "463_404..463_603"),   # B band
    ("459_204..461_203", "461_404..463_403"),   # A band
    ("459_204..459_403", "461_404..461_603"),   # arith-B (naive, in own-A)
    ("459_004..461_003", "461_204..463_203"),   # arith-A (naive, refused)
    ("459_004..459_203", "461_204..461_403"),   # prior-wave B band
    # D-phase: standalone band numbers
    ("set(range(459_204, 461_204))", "set(range(461_404, 463_404))"),
    ("set(range(461_204, 461_404))", "set(range(463_404, 463_604))"),
    ("(459_204, 461_203)", "(461_404, 463_403)"),   # pf row tuple A
    ("(461_204, 461_403)", "(463_404, 463_603)"),   # pf row tuple B
    ("== 459_204 == 459_203 + 1", "== 461_404 == 461_403 + 1"),
    ("== 461_204 == 461_203 + 1", "== 463_404 == 463_403 + 1"),
    ('"a_seed_base": 459_204,', '"a_seed_base": 461_404,'),
    ('"b_exit_seed_base": 461_204,', '"b_exit_seed_base": 463_404,'),
    ("jumps to 461_204", "jumps to 463_404"),
    ("# 461_204 and lands", "# 463_404 and lands"),
    ("459_203+1", "461_403+1"),
    ("461_203+1", "463_403+1"),
    # E-phase: ordinals/words
    ("one-hundred-seventeenth", "one-hundred-eighteenth"),
    ("rows 116 + candidate", "rows 117 + candidate"),
    ("TWO HUNDRED AND SECOND", "TWO HUNDRED AND THIRD"),
    ("engine_owner rows 191", "engine_owner rows 192"),
    ("SIXTY-SECOND", "SIXTY-THIRD"),
    ("sixty-second", "sixty-third"),
    # F-phase: ledger heads
    ("856,545", "858,745"),
    ("440,120", "442,320"),
    # F-phase: rounds/shas (finalize cites BEFORE the generic r924->r930
    # roll; the W201-probe cites r921->r924 AFTER it so they survive)
    ("bm-a r924", "bm-a r928"),
    ("since r924", "since r928"),
    ("r923 freeze", "r928 freeze"),
    ("c1937ac47", "c76a84dc2"),
    ("e2187e483", "dc00bfa54"),
    ("r927", "r936"),
    ("r924", "r930"),
    ("r921", "r924"),
    # G-phase: bare wave numbers (LAST; 202->203 before 201->202)
    ("202", "203"),
    ("201", "202"),
    # S-final: restore the protected literals
    ("\x00Y26", "2026"),
    ("\x00K94", "94_201"),
]


def apply_s(text):
    for (a, b) in S:
        text = text.replace(a, b)
    return text


# r922 derive_stale reproduction constants (verbatim semantics of the
# r927 script's step-1, read from the r927 source, zero transcription
# drift tolerated by assert)
R922_EXCLUDES = {"archive PENDING", "freeze-closeout archive move",
                 "moves to processed/ with this window closeout"}
R922_ADDS = {
    "mat201": ["archive ALREADY LANDED", "seat-round closeout",
               "consumed->processed", "honest archived per S7 law",
               "fleet/inbox/processed/ at",
               "(the W200 seat MSG sits in"],
    "pf201": ["archive ALREADY LANDED", "seat-round closeout",
              "consumed->processed", "honest archived per S7 law",
              "fleet/inbox/processed/ at",
              "(the W200 seat MSG sits in"],
    "cfg201": [],
    "claim201": [],
}

# r927 runtime STALE reproduction constants (its step-2 excludes/adds,
# read from the r927 source)
R927_EXCLUDES = {"archive ALREADY LANDED", "seat-round closeout",
                 "consumed->processed", "honest archived per S7 law",
                 "fleet/inbox/processed/ at"}
R927_ADDS = {
    "mat202": ["archive PENDING WITH", "freeze-closeout archive move",
               "moves to processed/ with this window closeout",
               "(the W201 seat MSG sits in", "fleet/inbox/ at freeze time"],
    "pf202": ["archive PENDING WITH", "freeze-closeout archive move",
              "moves to processed/ with this window closeout",
              "(the W201 seat MSG sits in", "fleet/inbox/ at freeze time"],
    "cfg202": [],
    "claim202": [],
}

# this generation's step-3 excludes: the generic ALREADY-LANDED tokens
# legitimately survive in the W203 fragments (the W203 archive face
# is ALREADY-LANDED via the r930 seat-round closeout); adds: none --
# the W202 fragments carry no PENDING face and the W202-specific
# ALREADY forms are produced by the T927 roll itself
W203_STALE_EXCLUDES = {"archive ALREADY LANDED", "seat-round closeout",
                       "consumed->processed", "honest archived per S7 law",
                       "fleet/inbox/processed/ at"}
W203_STALE_ADDS = {}


def derive_stale():
    base = extract_stale_dict(R921F)
    assert base is not None, "r921 STALE dict not found"
    # step 1: r922 runtime STALE (W200-era) -- verbatim semantics of
    # the r927 script's step 1
    r922_stale = {}
    for frag, entries in base.items():
        rolled = []
        for e in entries:
            if e in R922_EXCLUDES:
                continue
            r = e
            for (a, b) in T921["S"]:
                r = r.replace(a, b)
            if r not in rolled:
                rolled.append(r)
        newfrag = frag.replace("200", "201")
        r922_stale[newfrag] = rolled + R922_ADDS.get(newfrag, [])
    # step 2: r927 runtime STALE (W201-era) -- verbatim semantics of
    # the r927 script's step 2
    r927_stale = {}
    for frag, entries in r922_stale.items():
        rolled = []
        for e in entries:
            if e in R927_EXCLUDES:
                continue
            r = e
            for (a, b) in T922["S"]:
                r = r.replace(a, b)
            if r not in rolled:
                rolled.append(r)
        newfrag = frag.replace("201", "202")
        r927_stale[newfrag] = rolled + R927_ADDS.get(newfrag, [])
    # step 3: roll W201-era -> W202-era by the r927 S (the stale set
    # for the W203 fragments), frag keys 202->203
    out = {}
    for frag, entries in r927_stale.items():
        rolled = []
        for e in entries:
            if e in W203_STALE_EXCLUDES:
                continue
            r = e
            for (a, b) in T927["S"]:
                r = r.replace(a, b)
            if r not in rolled:
                rolled.append(r)
        newfrag = frag.replace("202", "203")
        out[newfrag] = rolled + W203_STALE_ADDS.get(newfrag, [])
    return out


def roll_pairs(r912_list, r915_rules, r916_rules, r919_rules, w200_rules,
               w201_rules, w202_rules, w203_rules, drop_if, tag):
    """Seven-gen chain: old side = r912 new side rolled by the r915
    fact rules then r916 then r919 then the r921-freeze-S-derived W200
    rules then the r922-freeze-S-derived W201 rules then the
    r927-freeze-S-derived W202 rules (= the live W202 text, zero
    transcription); new side = W203 rule-rolled."""
    pairs = []
    for (w195_old, w196_new, cnt) in r912_list:
        if any(d in w196_new for d in drop_if):
            continue  # archive-state lines handled by explicit arch pairs
        w197 = apply_rules(w196_new, r915_rules, tag)
        if w197 == w196_new:
            fails.append("R915-ROLL UNCHANGED [%s]: %r" % (tag, w196_new[:90]))
            continue
        w198 = apply_rules(w197, r916_rules, tag)
        if w198 == w197:
            fails.append("R916-ROLL UNCHANGED [%s]: %r" % (tag, w197[:90]))
            continue
        w199 = apply_rules(w198, r919_rules, tag)
        if w199 == w198:
            fails.append("R919-ROLL UNCHANGED [%s]: %r" % (tag, w198[:90]))
            continue
        w200 = apply_rules(w199, w200_rules, tag)
        if w200 == w199:
            fails.append("W200-ROLL UNCHANGED [%s]: %r" % (tag, w199[:90]))
            continue
        w201 = apply_rules(w200, w201_rules, tag)
        if w201 == w200:
            fails.append("W201-ROLL UNCHANGED [%s]: %r" % (tag, w200[:90]))
            continue
        w202 = apply_rules(w201, w202_rules, tag)
        if w202 == w201:
            fails.append("W202-ROLL UNCHANGED [%s]: %r" % (tag, w201[:90]))
            continue
        w203 = apply_rules(w202, w203_rules, tag)
        if w203 == w202:
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w202[:90]))
            continue
        pairs.append((w202, w203, cnt))
    return pairs


def build_arch(frag, start_tok, end_tok, shifts, stag):
    """Runtime-extracted archive pair (zero transcription, r909
    spirit): locate the ALREADY-LANDED block in the live fragment,
    build the next-generation form via count-asserted shifts."""
    i = frag.find(start_tok)
    assert i >= 0, "archive start not found [%s]" % stag
    ls = frag.rfind("\n", 0, i) + 1
    j = frag.find(end_tok, i)
    assert j > i, "archive end not found [%s]" % stag
    block = frag[ls:j + len(end_tok)]
    assert frag.count(block) == 1, "archive block not unique [%s]" % stag
    new = block
    for (a, b) in shifts:
        assert new.count(a) == 1, ("archive shift count != 1 [%s]: %r"
                                   % (stag, a))
        new = new.replace(a, b)
    return block, new


ARCH_SHIFTS = [("bm-a r925 seat-round", "bm-a r930 seat-round"),
               ("(the W202 seat MSG", "(the W203 seat MSG")]


def main():
    global T921, T922, T927
    facts = {"round": 936, "machine": "bm-a", "wave": 203,
             "archive_state": "ALREADY LANDED pre-freeze -- bm-a r930 "
                              "seat-round closeout consumed->processed "
                              "same round (the W203 seat MSG sits in "
                              "fleet/inbox/processed/ at freeze time, "
                              "honest archived per S7 law)"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '203: {"a": (461_404' in pf_probe:
        print("ALREADY APPLIED: W203 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "203: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 203 already on origin"
    assert '202: {"a": (459_204, 461_203)' in origin_pf, "origin W202 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W203 materializer face" not in origin_n1, "origin n1 W203 face present"
    assert '203: {"batch": "PERPETUAL-N1-W203"' not in origin_n1, \
        "origin n1 W203 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [461404, 463403] and B == [463404, 463603], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [461204, 463203] and \
        leg1["ARITH_B"] == [461404, 461603], "receipt arithmetic drift"
    assert r["bands"] == {"A": "461404_463403", "B": "463404_463603"}
    assert "SIXTY-THIRD" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 200 and leg0["tail"] == "W202"
    assert leg0["ordinal"] == 193 and leg0["bma_ordinal"] == 118
    assert leg0["owner_rows"] == 192 and leg0["bma_rows"] == 117
    assert leg0["w202_ledger_head"] == 858745
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W204p_A"] == "463404..465403" and \
        leg4["W204p_B"] == "463604..463803"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W204p_B_lands_inside_W204p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 202 and len(N1_BANDS) == 200, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 117 and owners.get("bm-c") == 35 \
        and owned == 192, "owner counts drift: %s" % owners
    assert N1_BANDS[202] == {"a": (459204, 461203), "b_exit": (461204, 461403),
                            "engine_owner": "bm-a"}, "W202 row drift"
    assert N1_BANDS[201] == {"a": (457004, 459003), "b_exit": (459004, 459203),
                            "engine_owner": "bm-a"}, "W201 row drift"
    assert N1_BANDS[200] == {"a": (454804, 456803), "b_exit": (456804, 457003),
                            "engine_owner": "bm-a"}, "W200 row drift"
    assert N1_BANDS[199] == {"a": (452604, 454603), "b_exit": (454604, 454803),
                            "engine_owner": "bm-a"}, "W199 row drift"
    assert N1_BANDS[198] == {"a": (450404, 452403), "b_exit": (452404, 452603),
                            "engine_owner": "bm-a"}, "W198 row drift"
    assert N1_BANDS[197] == {"a": (448204, 450203), "b_exit": (450204, 450403),
                            "engine_owner": "bm-a"}, "W197 row drift"
    assert N1_BANDS[196] == {"a": (446004, 448003), "b_exit": (448004, 448203),
                            "engine_owner": "bm-a"}, "W196 row drift"
    assert N1_BANDS[195] == {"a": (443804, 445803), "b_exit": (445804, 446003),
                            "engine_owner": "bm-a"}, "W195 row drift"
    assert N1_BANDS[194] == {"a": (441604, 443603), "b_exit": (443604, 443803),
                            "engine_owner": "bm-a"}, "W194 row drift"
    assert os.path.exists(PREREG), "W203 per-wave prereg missing"
    assert not os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG still in fleet/inbox/ (ALREADY-archived expectation violated)"
    assert os.path.exists(os.path.join(ROOT, SEAT_PROCESSED)), \
        "seat MSG not in processed/ (ALREADY-archived expectation violated)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w202_results.json")), \
        "W202 finalize product missing (dep precondition)"
    for f in ("results/_r930bma_w203_probe.py",
              "results/_r930bma_w203_probe_receipt.json"):
        assert os.path.exists(os.path.join(ROOT, f)), \
            "seat-cited artifact missing: %s" % f
    facts["precheck"] = {"rows": len(N1_BANDS), "bma_rows": owners.get("bm-a"),
                         "bmc_rows": owners.get("bm-c"),
                         "bmb_rows": owners.get("bm-b"),
                         "owner_rows": owned}

    # ---- G3 read live files, EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract W202 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat202 = chunk(n1n, "    # --- W202 materializer face",
                   "    _set_wave(2)", "mat202")
    assert mat202.rstrip("\n").endswith("_set_wave(2)"), "mat202 tail drift"
    cfg202 = chunk(n1n, '    202: {"batch": "PERPETUAL-N1-W202",',
                   '"engine_owner": "bm-a"},', "cfg202")
    pf202 = chunk(pfn, "    # W202 (bm-a r927 freeze, seat MSG-2026-10-09-1935-bma-w202-seat",
                 '"engine_owner": "bm-a"},', "pf202")
    claim202 = chunk(n1n, '          "+ W202 materializer face [same guard set',
                     '"r927 bm-a] "', "claim202")
    assert n1n.count(cfg202) == 1, "cfg202 not unique"
    assert n1n.count(claim202) == 1, "claim202 not unique"
    assert pfn.count(pf202) == 1, "pf202 not unique"
    # r776 double-verification: byte-identical against the r935
    # physical probe dumps (dead-session estate absorbed as old sides;
    # the probe files carry CRLF, our LF-normalized chunks compare via
    # EOL-normalized equality -- content parity, r814 family note)
    for nm, frag in (("cfg202", cfg202), ("pf202", pf202),
                     ("mat202", mat202), ("claim202", claim202)):
        probe_path = os.path.join(ROOT, "results",
                                 "_r935bma_probe_frag_%s.txt" % nm)
        probe = open(probe_path, encoding="utf-8", newline="").read()
        assert frag == probe.replace("\r\n", "\n"), \
            "r935 probe dump DRIFT [%s]" % nm
    for nm, frag in (("mat", mat202), ("cfg", cfg202),
                     ("pf", pf202), ("claim", claim202)):
        with open(os.path.join(ROOT, "results",
                               "_r936bma_w203_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                          (("mat", mat202), ("cfg", cfg202),
                           ("pf", pf202), ("claim", claim202))}

    # ---- G5-G7 derive rolled pairs (seven-gen bloodline AST chain) ----
    t912, t915, t916, t919, t921, t922, t927 = load_bloodline()
    T921 = t921
    T922 = t922
    T927 = t927
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    rules_w200_mat = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_MAT"]]
    rules_w200_cfg = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CFG"]]
    rules_w200_pf = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_PF"]]
    rules_w200_claim = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CLAIM"]]
    rules_w201_mat = [(b, apply_s_r922(b)) for (a, b) in rules_w200_mat]
    rules_w201_cfg = [(b, apply_s_r922(b)) for (a, b) in rules_w200_cfg]
    rules_w201_pf = [(b, apply_s_r922(b)) for (a, b) in rules_w200_pf]
    rules_w201_claim = [(b, apply_s_r922(b)) for (a, b) in rules_w200_claim]
    rules_w202_mat = [(b, apply_s_r927(b)) for (a, b) in rules_w201_mat]
    rules_w202_cfg = [(b, apply_s_r927(b)) for (a, b) in rules_w201_cfg]
    rules_w202_pf = [(b, apply_s_r927(b)) for (a, b) in rules_w201_pf]
    rules_w202_claim = [(b, apply_s_r927(b)) for (a, b) in rules_w201_claim]
    rules_w203_mat = [(b, apply_s(b)) for (a, b) in rules_w202_mat]
    rules_w203_cfg = [(b, apply_s(b)) for (a, b) in rules_w202_cfg]
    rules_w203_pf = [(b, apply_s(b)) for (a, b) in rules_w202_pf]
    rules_w203_claim = [(b, apply_s(b)) for (a, b) in rules_w202_claim]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"],
                           t916["RULES_W198_MAT"], t919["RULES_W199_MAT"],
                           rules_w200_mat, rules_w201_mat, rules_w202_mat,
                           rules_w203_mat, drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"],
                           t916["RULES_W198_CFG"], t919["RULES_W199_CFG"],
                           rules_w200_cfg, rules_w201_cfg, rules_w202_cfg,
                           rules_w203_cfg, drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"],
                          t916["RULES_W198_PF"], t919["RULES_W199_PF"],
                          rules_w200_pf, rules_w201_pf, rules_w202_pf,
                          rules_w203_pf, drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"],
                             t916["RULES_W198_CLAIM"], t919["RULES_W199_CLAIM"],
                             rules_w200_claim, rules_w201_claim,
                             rules_w202_claim, rules_w203_claim,
                             drop_if, "claim")
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": 2}
    # archive pairs FIRST (runtime-extracted ALREADY-LANDED W202 block
    # replaced with the ALREADY-LANDED W203 form before fact shifts)
    arch_mat_left, arch_mat_right = build_arch(
        mat202, "--no-verify; self-ack inbox->processed archive ALREADY LANDED",
        "honest archived per S7 law).", ARCH_SHIFTS, "mat-arch-build")
    arch_pf_left, arch_pf_right = build_arch(
        pf202, "archive ALREADY LANDED pre-freeze -- bm-a r925 seat-round",
        "per S7 law);", ARCH_SHIFTS, "pf-arch-build")
    m = rep(mat202, arch_mat_left, arch_mat_right, 1, "mat-arch")
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat203 = m
    c = cfg202
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg203 = c
    p = rep(pf202, arch_pf_left, arch_pf_right, 1, "pf-arch")
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf203 = p
    q = claim202
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim203 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W202 band citations (the registered W202 B band
    # 461_204..461_403 and the W203 arithmetic continuations
    # 461_204..463_203 / 461_404..461_603) are LEGITIMATE content of
    # the W203 fragments (prior-wave + own-arith faces) -- NOT stale.
    STALE = derive_stale()
    frags = {"mat203": mat203, "cfg203": cfg203, "pf203": pf203,
             "claim203": claim203}
    for frag, stale_list in STALE.items():
        txt = frags[frag]
        for s in stale_list:
            if s in txt:
                fails.append("%s stale token remains: %r" % (frag, s[:60]))

    if fails:
        print("RESULT: FAIL (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    # ---- G8 insertions (r560 additive, after last registered row) ----
    IND19 = " " * 19
    n1_b = n1n.replace(cfg202, cfg202 + "\n" + IND19 + cfg203, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w202_pos = n1_b.find("    # --- W202 materializer face")
    assert w202_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w202_pos)
    assert t141 > w202_pos, "T-141 marker not found after W202 face"
    n1_c = n1_b[:t141] + mat203 + "\n" + n1_b[t141:]
    claim_anchor = claim202 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim202 + "\n" + claim203 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf202, pf202 + "\n" + pf203, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '203: {"batch": "PERPETUAL-N1-W203",', 1),
        (n1_final, '202: {"batch": "PERPETUAL-N1-W202",', 1),
        (n1_final, '201: {"batch": "PERPETUAL-N1-W201",', 1),
        (n1_final, '200: {"batch": "PERPETUAL-N1-W200",', 1),
        (n1_final, '199: {"batch": "PERPETUAL-N1-W199",', 1),
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, "# --- W203 materializer face", 1),
        (n1_final, "# --- W202 materializer face", 1),
        (n1_final, "# --- W201 materializer face", 1),
        (n1_final, "# --- W200 materializer face", 1),
        (n1_final, "# --- W199 materializer face", 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, '"r936 bm-a] "', 1),
        (n1_final, '"r927 bm-a] "', 1),
        (n1_final, '"r922 bm-a] "', 1),
        (n1_final, '"r919 bm-a] "', 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"a_seed_base": 461_404,', 1),
        (n1_final, '"b_exit_seed_base": 463_404,', 1),
        (n1_final, "n1_w203", 4),
        (n1_final, "PERPETUAL_N1_W203_PREREG.md", 2),
        (n1_final, "_set_wave(203)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 203)', 3),
        (n1_final, "range(17, 203):", 1),
        (n1_final, '"W204 A window; W204 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 463_404..465_403 ', 1),
        (n1_final, "bm-a r930 seat-round closeout consumed->processed", 1),
        (n1_final, "(the W203 seat MSG sits in", 1),
        (n1_final, "(the W203 seat MSG sits in fleet/inbox/processed/ at", 1),
        (pf_final, '203: {"a": (461_404, 463_403), "b_exit": (463_404, 463_603),', 1),
        (pf_final, '202: {"a": (459_204, 461_203), "b_exit": (461_204, 461_403),', 1),
        (pf_final, '201: {"a": (457_004, 459_003), "b_exit": (459_004, 459_203),', 1),
        (pf_final, '200: {"a": (454_804, 456_803), "b_exit": (456_804, 457_003),', 1),
        (pf_final, '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),', 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, "# W203 (bm-a r936 freeze", 1),
        (pf_final, "# W202 (bm-a r927 freeze", 1),
        (pf_final, "# W201 (bm-a r922 freeze", 1),
        (pf_final, "# W200 (bm-a r921 freeze", 1),
        (pf_final, "# W199 (bm-a r919 freeze", 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W204+ projection (gate-derived r930)", 1),
        (pf_final, "archive ALREADY LANDED pre-freeze -- bm-a r930 seat", 1),
        (pf_final, "(the W203 seat MSG sits in", 1),
        (pf_final, "(the W203 seat MSG sits in\n    # fleet/inbox/processed/ at freeze time", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W204+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 463_404..465_403 CLEAN hops=0 / B first-clean 463_604..463_803",
                   "W204 A window; W204 freezer MUST re-derive on the post-W203"):
        if needle not in pf_final:
            fails.append("pf W204+ prose missing: %r" % needle[:60])
    pat = re.compile(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})")
    for name, txt in (("pf", pf_final), ("n1", n1_final)):
        bad = [mm.group() for mm in pat.finditer(txt)
               if int(mm.group(3)) < int(mm.group(1))]
        if bad:
            fails.append("%s malformed windows: %s" % (name, bad[:5]))
    # CR/LF hygiene: rolled fragments carry no CR and no triple-LF;
    # final outputs introduce ZERO NEW anomalies vs the originals.
    for frag, txt in frags.items():
        if "\r" in txt:
            fails.append("%s fragment carries a bare CR" % frag)
        if "\n\n\n" in txt:
            fails.append("%s fragment carries triple-LF" % frag)
    n1_out_probe = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out_probe = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    for name, out_txt, raw in (("n1", n1_out_probe, n1_raw),
                               ("pf", pf_out_probe, pf_raw)):
        for tok in ("\r\r", "\n\n\n"):
            if out_txt.count(tok) != raw.count(tok):
                fails.append("%s anomaly count DRIFT for %r: %d -> %d"
                             % (name, tok, raw.count(tok), out_txt.count(tok)))

    # ---- G9b AST gate (r580/r581) ----
    ast.parse(n1_final)
    ast.parse(pf_final)
    print("AST gate: both files parse OK")

    if fails:
        print("RESULT: FAIL at gates (%d) -- zero writes" % len(fails))
        for f in fails:
            print("  -", f)
        return 1

    if not WRITE:
        print("DRY-RUN PASS: all gates green, zero writes "
              "(rerun with --write to land)")
        with open(OUT_RCPT.replace(".json", "_dryrun.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(facts, fh, indent=1, ensure_ascii=False)
        return 0

    # ---- G10 live writes (r666 safe order: n1 FIRST then pf) ----
    n1_out = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    with open(N1P, "w", encoding="utf-8", newline="") as fh:
        fh.write(n1_out)
    with open(PFP, "w", encoding="utf-8", newline="") as fh:
        fh.write(pf_out)
    print("LIVE WRITES DONE: pf %d->%d B, n1 %d->%d B"
          % (len(pfn), len(pf_final), len(n1n), len(n1_final)))

    # ---- G11 py_compile + post-import guard ----
    for f in (N1P, PFP):
        prc = subprocess.run([sys.executable, "-m", "py_compile", f],
                             capture_output=True, creationflags=CNW)
        assert prc.returncode == 0, "py_compile failed: %s" % f
    chk = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, 'scripts'); "
         "sys.path.insert(0, '.'); "
         "from perpetual_faces import N1_BANDS as B; "
         "import perpetual_faces_n1 as n1; "
         "cfg = n1.WAVE_CONFIGS[203]; "
         "print(json.dumps({'rows': len(B), 'w203': B.get(203), "
         "'w202': B.get(202), 'w201': B.get(201), 'w200': B.get(200), "
         "'w199': B.get(199), 'w198': B.get(198), 'w197': B.get(197), "
         "'w196': B.get(196), 'w195': B.get(195), 'w194': B.get(194), "
         "'cfg203': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 201, "row count drift: %s" % post
    assert post["w203"] == {"a": [461404, 463403], "b_exit": [463404, 463603],
                            "engine_owner": "bm-a"}, "W203 row drift: %s" % post
    assert post["w202"] == {"a": [459204, 461203], "b_exit": [461204, 461403],
                            "engine_owner": "bm-a"}, "W202 row damaged: %s" % post
    assert post["w201"] == {"a": [457004, 459003], "b_exit": [459004, 459203],
                            "engine_owner": "bm-a"}, "W201 row damaged: %s" % post
    assert post["w200"] == {"a": [454804, 456803], "b_exit": [456804, 457003],
                            "engine_owner": "bm-a"}, "W200 row damaged: %s" % post
    assert post["w199"] == {"a": [452604, 454603], "b_exit": [454604, 454803],
                            "engine_owner": "bm-a"}, "W199 row damaged: %s" % post
    assert post["w198"] == {"a": [450404, 452403], "b_exit": [452404, 452603],
                            "engine_owner": "bm-a"}, "W198 row damaged: %s" % post
    assert post["w197"] == {"a": [448204, 450203], "b_exit": [450204, 450403],
                            "engine_owner": "bm-a"}, "W197 row damaged: %s" % post
    assert post["w196"] == {"a": [446004, 448003], "b_exit": [448004, 448203],
                            "engine_owner": "bm-a"}, "W196 row damaged: %s" % post
    assert post["w195"] == {"a": [443804, 445803], "b_exit": [445804, 446003],
                            "engine_owner": "bm-a"}, "W195 row damaged: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                            "engine_owner": "bm-a"}, "W194 row damaged: %s" % post
    assert post["cfg203"] == [461404, 463404, "n1_w203",
                              "n1_w203_results.json", "bm-a"], \
        "W203 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[203] row: a=(461_404,463_403) "
          "b_exit=(463_404,463_603) engine_owner=bm-a (comment face rolled, "
          "W202 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[203] row: batch=PERPETUAL-N1-W203 "
          "a_seed_base=461_404 b_exit_seed_base=463_404 shard=n1_w203 "
          "out=n1_w203_results.json owner=bm-a")
    print("PASS 3/5 n1 W203 materializer face: %d+%d+%d+%d derived pairs + "
          "2 archive pairs (ALREADY-LANDED face, r930 seat-round closeout "
          "pre-freeze) all count-asserted; staircase SIXTY-THIRD; "
          "prior-wave parity->W202; deps range(17,203) all-landed clean; "
          "prereg presence assert->W203"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 200->201 rows + AST+py_compile + W202/W201/W200 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "ALREADY-archived processed/ verified + r935 probe dump parity"
          % SEAT_SHA)
    print("PASS 5/5 summary: W203 = 193rd engine wave, bm-a 118th owned "
          "(rows 192+candidate per receipt leg0); A=461_404..463_403 "
          "hops=1 SIXTY-THIRD staircase; B=463_404..463_603 hops=1 "
          "own-A mutual exclusion (W141); ZERO in-flight upstream (W202 "
          "finalize landed r928, head 858,745 K 442,320); ADMIT "
          "receipt machine-read; receipt=results/_r936bma_w203_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
