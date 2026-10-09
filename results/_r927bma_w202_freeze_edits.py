# -*- coding: utf-8 -*-
"""r927 bm-a W202 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG ALREADY-archived verification face). Direct-author per the
r909/r912/r915/r916/r919/r921/r922 physical chunk-roll machinery, rolled
ONE generation: extract current W201 fragments, roll W201->W202 with
count-asserted replacements, insert ADDITIVELY after the last
registered row; originals byte-identical zero-destroy. Old sides
DERIVED AT RUNTIME by the six-gen chain (zero transcription, r587):
r912 AST triples (W195_old, W196_new, cnt) -> r915 AST RULES_* ->
W197 text -> r916 AST RULES_W198_* -> W198 text -> r919 AST
RULES_W199_* -> W199 text -> r921 freeze S (AST) -> W200 text ->
r922 freeze S (AST) -> W201 text = this build's old side; W202 fact
substitutions derived at runtime from the W201 new sides via the
ordered S shift (projection-first, bands +2200 staircase, standalone
numbers, ordinals, shas/rounds, bare wave numbers LAST; the fixed
W138 parity literal 94_201 sentinel-protected -- first generation
where the bare 201->202 shift would otherwise collide with it).

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r924bma_w202_probe_receipt.json (bands A 459_204..461_203 /
B 461_204..461_403, hops 1/1, SIXTY-SECOND staircase, leg0 rows 199
tail W201 owner_rows 191 bma_rows 116 ordinal 192 bma_ordinal 117
w201_ledger_head 856,545, leg2 conflicts 0, leg3 origin vacancy,
leg4 W203p A 461_204..463_203 / B 461_404..461_603 hops 0/0
B-inside-A). Seat push e2187e483
(MSG-2026-10-09-1935-bma-w202-seat + probe script + receipt, 3-item,
r924 seat push, ancestor-verified). W201=bm-a r923 five-face freeze
(dead-session estate absorption c1937ac47; r922 died pre-commit,
freeze receipt 18:41 validated) + engine self-burn 12/12; finalize
product generated 19:05:50, LANDED r924 estate-absorb push b71610ba4
(ledger 854,345+2,200=856,545 EXACT, K=440,120 EXACT, skill_line_v2
1.1885) -- W202 freeze-time anchor = W201 finalize actuals per r590,
zero roll-forward. Seat MSG archive state = ALREADY LANDED pre-freeze
(bm-a r925 seat-round closeout consumed->processed -- the W202 seat
MSG sits in fleet/inbox/processed/ at freeze time, honest archived
per S7 law).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment
PASS prints; r776 fragment-needle law (physical dumps
results/_r927bma_w202_face_*.txt, re-verified against the live files
at run time); r780/r781 verify-separation (all stale+presence asserts
in memory BEFORE any write); r666 safe write order (n1 first, then
pf). Dry-run by default; --write performs the live writes."""
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
RCPT = os.path.join(ROOT, "results", "_r924bma_w202_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r927bma_w202_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-1935-bma-w202-seat.md"
SEAT_PROCESSED = ("fleet/inbox/processed/"
                  "MSG-2026-10-09-1935-bma-w202-seat.md")
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W202_PREREG.md")
SEAT_SHA = "e2187e483"
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


# ---- six-gen extraction: r912 triples + r915/r916/r919 rules +
# r921/r922 freeze S (AST) ----
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
    return t912, t915, t916, t919, t921, t922


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


# ---- S: ordered W201->W202 fact shift (sentinel first; projection-
# first; bands +2200 staircase; standalone numbers; ordinals;
# shas/rounds/MSG; bare wave numbers LAST; every entry verified
# collision-free) ----
S = [
    # S0: sentinel-protect the fixed W138 parity literal 94_201 (first
    # generation where the bare current-wave shift 201->202 would
    # collide with it); restored as the final entry
    ("94_201", "\x00K94"),
    # B-phase: own-projection face (before bare shifts create W203)
    ("W202", "W203"),
    ("459_004..461_003", "461_204..463_203"),   # naive W203 A projection
    ("459_204..459_403", "461_404..461_603"),   # naive W203 B projection
    # C-phase: band staircase (+2200)
    ("459_004..459_203", "461_204..461_403"),   # B band
    ("457_004..459_003", "459_204..461_203"),   # A band
    ("457_004..457_203", "459_204..459_403"),   # arith-B (naive, in own-A)
    ("456_804..458_803", "459_004..461_003"),   # arith-A (naive, refused)
    ("456_804..457_003", "459_004..459_203"),   # prior-wave B band
    # D-phase: standalone band numbers
    ("set(range(457_004, 459_004))", "set(range(459_204, 461_204))"),
    ("set(range(459_004, 459_204))", "set(range(461_204, 461_404))"),
    ("(457_004, 459_003)", "(459_204, 461_203)"),   # pf row tuple A
    ("(459_004, 459_203)", "(461_204, 461_403)"),   # pf row tuple B
    ("== 457_004 == 457_003 + 1", "== 459_204 == 459_203 + 1"),
    ("== 459_004 == 459_003 + 1", "== 461_204 == 461_203 + 1"),
    ('"a_seed_base": 457_004,', '"a_seed_base": 459_204,'),
    ('"b_exit_seed_base": 459_004,', '"b_exit_seed_base": 461_204,'),
    ("jumps to 459_004", "jumps to 461_204"),
    ("# 459_004 and lands", "# 461_204 and lands"),
    ("457_003+1", "459_203+1"),
    ("459_003+1", "461_203+1"),
    # E-phase: ordinals/words
    ("one-hundred-sixteenth", "one-hundred-seventeenth"),
    ("rows 115 + candidate", "rows 116 + candidate"),
    ("TWO HUNDRED AND FIRST", "TWO HUNDRED AND SECOND"),
    ("engine_owner rows 190", "engine_owner rows 191"),
    ("SIXTY-FIRST", "SIXTY-SECOND"),
    ("sixty-first", "sixty-second"),
    # F-phase: shas/rounds/MSG/ledger (specific freeze-sha pair BEFORE
    # generic r921->r924; r921->r924 BEFORE r920->r921)
    ("r921 freeze", "r923 freeze"),
    ("cd92a8d9c", "c1937ac47"),
    ("188ebe647", "e2187e483"),
    ("r922", "r927"),
    ("r921", "r924"),
    ("r920", "r921"),
    ("MSG-2026-10-09-1812", "MSG-2026-10-09-1935"),
    ("MSG-1812", "MSG-1935"),
    ("854,345", "856,545"),
    ("437,920", "440,120"),
    # G-phase: bare wave numbers (LAST; 201->202 before 200->201)
    ("201", "202"),
    ("200", "201"),
    # S-final: restore the protected literal
    ("\x00K94", "94_201"),
]


def apply_s(text):
    for (a, b) in S:
        text = text.replace(a, b)
    return text


# ---- archive face: W202 seat MSG ALREADY LANDED pre-freeze (bm-a r925
# seat-round closeout consumed->processed per S7 law; the W202 seat MSG
# sits in fleet/inbox/processed/ at freeze time) -- the live W201
# fragments carry the PENDING form (dead-session r921 estate), replaced
# here with the ALREADY-LANDED W202 form (W200-era r921-script pattern) ----
ARCH_MAT = (
    "    #     --no-verify; self-ack inbox->processed archive PENDING WITH\n"
    "    #     THIS freeze window -- bm-a r922 freeze-closeout archive move\n"
    "    #     (the W201 seat MSG sits in fleet/inbox/ at freeze time,\n"
    "    #     moves to processed/ with this window closeout, honest per\n"
    "    #     frozen prereg sec.0).",
    "    #     --no-verify; self-ack inbox->processed archive ALREADY LANDED\n"
    "    #     pre-freeze -- bm-a r925 seat-round closeout consumed->processed\n"
    "    #     (the W202 seat MSG sits in fleet/inbox/processed/ at\n"
    "    #     freeze time, honest archived per S7 law).")
ARCH_PF = (
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive PENDING WITH THIS freeze window -- bm-a r922 freeze\n"
    "    # closeout archive move (the W201 seat MSG sits in\n"
    "    # fleet/inbox/ at freeze time, moves to processed/ with this\n"
    "    # window closeout, honest per frozen prereg sec.0);",
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive ALREADY LANDED pre-freeze -- bm-a r925 seat-round\n"
    "    # closeout consumed->processed (the W202 seat MSG sits in\n"
    "    # fleet/inbox/processed/ at freeze time, honest archived\n"
    "    # per S7 law);")

# r922 derive_stale reproduction constants (its own EXCLUDES/ADDS, read
# from the r922 source, zero transcription drift tolerated by assert)
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

# stale derivation: two-step -- (1) reproduce the r922 runtime STALE
# (W200-era tokens) from the r921 module dict per the r922 derive_stale
# semantics; (2) roll it one more generation by the r922 S (W200->W201)
# = W201-era tokens that must NOT survive in the W202 fragments; the
# W202-legit ALREADY-LANDED generic tokens excluded (they ARE the
# archive-state face of the W202 fragments); PENDING-form tokens added
# as stale for W202 (the W201 PENDING face must be fully replaced).
ARCH_STALE_EXCLUDES = {"archive ALREADY LANDED", "seat-round closeout",
                       "consumed->processed", "honest archived per S7 law",
                       "fleet/inbox/processed/ at"}
ARCH_STALE_ADDS = {
    "mat202": ["archive PENDING WITH", "freeze-closeout archive move",
               "moves to processed/ with this window closeout",
               "(the W201 seat MSG sits in", "fleet/inbox/ at freeze time"],
    "pf202": ["archive PENDING WITH", "freeze-closeout archive move",
              "moves to processed/ with this window closeout",
              "(the W201 seat MSG sits in", "fleet/inbox/ at freeze time"],
    "cfg202": [],
    "claim202": [],
}


def derive_stale():
    base = extract_stale_dict(R921F)
    assert base is not None, "r921 STALE dict not found"
    # step 1: r922 runtime STALE (W200-era) -- verbatim semantics of the
    # r922 derive_stale (its excludes + adds + the r921 S roll)
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
    # step 2: roll W200-era -> W201-era by the r922 S, frag keys 201->202
    out = {}
    for frag, entries in r922_stale.items():
        rolled = []
        for e in entries:
            if e in ARCH_STALE_EXCLUDES:
                continue
            r = e
            for (a, b) in T922["S"]:
                r = r.replace(a, b)
            if r not in rolled:
                rolled.append(r)
        newfrag = frag.replace("201", "202")
        out[newfrag] = rolled + ARCH_STALE_ADDS.get(newfrag, [])
    return out


def roll_pairs(r912_list, r915_rules, r916_rules, r919_rules, w200_rules,
               w201_rules, w202_rules, drop_if, tag):
    """Six-gen chain: old side = r912 new side rolled by the r915 fact
    rules then r916 then r919 then the r921-freeze-S-derived W200 rules
    then the r922-freeze-S-derived W201 rules (= the live W201 text,
    zero transcription); new side = W202 rule-rolled."""
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
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w201[:90]))
            continue
        pairs.append((w201, w202, cnt))
    return pairs


def main():
    global T921, T922
    facts = {"round": 927, "machine": "bm-a", "wave": 202,
             "archive_state": "ALREADY LANDED pre-freeze -- bm-a r925 "
                              "seat-round closeout consumed->processed "
                              "(the W202 seat MSG sits in "
                              "fleet/inbox/processed/ at freeze time, "
                              "honest archived per S7 law)"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '202: {"a": (459_204' in pf_probe:
        print("ALREADY APPLIED: W202 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "202: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 202 already on origin"
    assert '201: {"a": (457_004, 459_003)' in origin_pf, "origin W201 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W202 materializer face" not in origin_n1, "origin n1 W202 face present"
    assert '202: {"batch": "PERPETUAL-N1-W202"' not in origin_n1, \
        "origin n1 W202 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [459204, 461203] and B == [461204, 461403], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [459004, 461003] and \
        leg1["ARITH_B"] == [459204, 459403], "receipt arithmetic drift"
    assert r["bands"] == {"A": "459204_461203", "B": "461204_461403"}
    assert "SIXTY-SECOND" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 199 and leg0["tail"] == "W201"
    assert leg0["ordinal"] == 192 and leg0["bma_ordinal"] == 117
    assert leg0["owner_rows"] == 191 and leg0["bma_rows"] == 116
    assert leg0["w201_ledger_head"] == 856545
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W203p_A"] == "461204..463203" and \
        leg4["W203p_B"] == "461404..461603"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W203p_B_lands_inside_W203p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 201 and len(N1_BANDS) == 199, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 116 and owners.get("bm-c") == 35 \
        and owned == 191, "owner counts drift: %s" % owners
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
    assert os.path.exists(PREREG), "W202 per-wave prereg missing"
    assert not os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG still in fleet/inbox/ (ALREADY-archived expectation violated)"
    assert os.path.exists(os.path.join(ROOT, SEAT_PROCESSED)), \
        "seat MSG not in processed/ (ALREADY-archived expectation violated)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w201_results.json")), \
        "W201 finalize product missing (dep precondition)"
    for f in ("results/_r924bma_w202_probe.py",
              "results/_r924bma_w202_probe_receipt.json"):
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

    # ---- G4 extract W201 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat201 = chunk(n1n, "    # --- W201 materializer face",
                   "    _set_wave(2)", "mat201")
    assert mat201.rstrip("\n").endswith("_set_wave(2)"), "mat201 tail drift"
    cfg201 = chunk(n1n, '    201: {"batch": "PERPETUAL-N1-W201",',
                   '"engine_owner": "bm-a"},', "cfg201")
    pf201 = chunk(pfn, "    # W201 (bm-a r922 freeze, seat MSG-2026-10-09-1812-bma-w201-seat",
                 '"engine_owner": "bm-a"},', "pf201")
    claim201 = chunk(n1n, '          "+ W201 materializer face [same guard set',
                     '"r922 bm-a] "', "claim201")
    assert n1n.count(cfg201) == 1, "cfg201 not unique"
    assert n1n.count(claim201) == 1, "claim201 not unique"
    assert pfn.count(pf201) == 1, "pf201 not unique"
    for nm, frag in (("mat", mat201), ("cfg", cfg201),
                     ("pf", pf201), ("claim", claim201)):
        with open(os.path.join(ROOT, "results",
                               "_r927bma_w202_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                          (("mat", mat201), ("cfg", cfg201),
                           ("pf", pf201), ("claim", claim201))}

    # ---- G5-G7 derive rolled pairs (six-gen bloodline AST chain) ----
    t912, t915, t916, t919, t921, t922 = load_bloodline()
    T921 = t921
    T922 = t922
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    rules_w200_mat = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_MAT"]]
    rules_w200_cfg = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CFG"]]
    rules_w200_pf = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_PF"]]
    rules_w200_claim = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CLAIM"]]
    rules_w201_mat = [(b, apply_s_r922(b)) for (a, b) in rules_w200_mat]
    rules_w201_cfg = [(b, apply_s_r922(b)) for (a, b) in rules_w200_cfg]
    rules_w201_pf = [(b, apply_s_r922(b)) for (a, b) in rules_w200_pf]
    rules_w201_claim = [(b, apply_s_r922(b)) for (a, b) in rules_w200_claim]
    rules_w202_mat = [(b, apply_s(b)) for (a, b) in rules_w201_mat]
    rules_w202_cfg = [(b, apply_s(b)) for (a, b) in rules_w201_cfg]
    rules_w202_pf = [(b, apply_s(b)) for (a, b) in rules_w201_pf]
    rules_w202_claim = [(b, apply_s(b)) for (a, b) in rules_w201_claim]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"],
                           t916["RULES_W198_MAT"], t919["RULES_W199_MAT"],
                           rules_w200_mat, rules_w201_mat, rules_w202_mat,
                           drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"],
                           t916["RULES_W198_CFG"], t919["RULES_W199_CFG"],
                           rules_w200_cfg, rules_w201_cfg, rules_w202_cfg,
                           drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"],
                          t916["RULES_W198_PF"], t919["RULES_W199_PF"],
                          rules_w200_pf, rules_w201_pf, rules_w202_pf,
                          drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"],
                             t916["RULES_W198_CLAIM"], t919["RULES_W199_CLAIM"],
                             rules_w200_claim, rules_w201_claim,
                             rules_w202_claim, drop_if, "claim")
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": 2}
    # archive pairs FIRST (PENDING block replaced with the ALREADY-LANDED
    # W202 form before fact shifts)
    m = rep(mat201, ARCH_MAT[0], ARCH_MAT[1], 1, "mat-arch")
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat202 = m
    c = cfg201
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg202 = c
    p = rep(pf201, ARCH_PF[0], ARCH_PF[1], 1, "pf-arch")
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf202 = p
    q = claim201
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim202 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W201 band citations (the registered W201 B band
    # 459_004..459_203 and the W202 arithmetic continuations
    # 459_004..461_003 / 459_204..459_403) are LEGITIMATE content of
    # the W202 fragments (prior-wave + own-arith faces) -- NOT stale.
    STALE = derive_stale()
    frags = {"mat202": mat202, "cfg202": cfg202, "pf202": pf202,
             "claim202": claim202}
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
    n1_b = n1n.replace(cfg201, cfg201 + "\n" + IND19 + cfg202, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w201_pos = n1_b.find("    # --- W201 materializer face")
    assert w201_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w201_pos)
    assert t141 > w201_pos, "T-141 marker not found after W201 face"
    n1_c = n1_b[:t141] + mat202 + "\n" + n1_b[t141:]
    claim_anchor = claim201 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim201 + "\n" + claim202 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf201, pf201 + "\n" + pf202, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '202: {"batch": "PERPETUAL-N1-W202",', 1),
        (n1_final, '201: {"batch": "PERPETUAL-N1-W201",', 1),
        (n1_final, '200: {"batch": "PERPETUAL-N1-W200",', 1),
        (n1_final, '199: {"batch": "PERPETUAL-N1-W199",', 1),
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W202 materializer face", 1),
        (n1_final, "# --- W201 materializer face", 1),
        (n1_final, "# --- W200 materializer face", 1),
        (n1_final, "# --- W199 materializer face", 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r927 bm-a] "', 1),
        (n1_final, '"r922 bm-a] "', 1),
        (n1_final, '"r919 bm-a] "', 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 459_204,', 1),
        (n1_final, '"b_exit_seed_base": 461_204,', 1),
        (n1_final, "n1_w202", 4),
        (n1_final, "PERPETUAL_N1_W202_PREREG.md", 2),
        (n1_final, "_set_wave(202)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 202)', 3),
        (n1_final, "range(17, 202):", 1),
        (n1_final, '"W203 A window; W203 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 461_204..463_203 ', 1),
        (n1_final, "bm-a r925 seat-round closeout consumed->processed", 1),
        (n1_final, "(the W202 seat MSG sits in", 1),
        (n1_final, "(the W202 seat MSG sits in fleet/inbox/processed/ at", 1),
        (pf_final, '202: {"a": (459_204, 461_203), "b_exit": (461_204, 461_403),', 1),
        (pf_final, '201: {"a": (457_004, 459_003), "b_exit": (459_004, 459_203),', 1),
        (pf_final, '200: {"a": (454_804, 456_803), "b_exit": (456_804, 457_003),', 1),
        (pf_final, '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),', 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W202 (bm-a r927 freeze", 1),
        (pf_final, "# W201 (bm-a r922 freeze", 1),
        (pf_final, "# W200 (bm-a r921 freeze", 1),
        (pf_final, "# W199 (bm-a r919 freeze", 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W203+ projection (gate-derived r924)", 1),
        (pf_final, "archive ALREADY LANDED pre-freeze -- bm-a r925 seat", 1),
        (pf_final, "(the W202 seat MSG sits in", 1),
        (pf_final, "(the W202 seat MSG sits in\n    # fleet/inbox/processed/ at freeze time", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W203+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 461_204..463_203 CLEAN hops=0 / B first-clean 461_404..461_603",
                   "W203 A window; W203 freezer MUST re-derive on the post-W202"):
        if needle not in pf_final:
            fails.append("pf W203+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[202]; "
         "print(json.dumps({'rows': len(B), 'w202': B.get(202), "
         "'w201': B.get(201), 'w200': B.get(200), 'w199': B.get(199), "
         "'w198': B.get(198), 'w197': B.get(197), 'w196': B.get(196), "
         "'w195': B.get(195), 'w194': B.get(194), "
         "'cfg202': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 200, "row count drift: %s" % post
    assert post["w202"] == {"a": [459204, 461203], "b_exit": [461204, 461403],
                            "engine_owner": "bm-a"}, "W202 row drift: %s" % post
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
    assert post["cfg202"] == [459204, 461204, "n1_w202",
                              "n1_w202_results.json", "bm-a"], \
        "W202 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[202] row: a=(459_204,461_203) "
          "b_exit=(461_204,461_403) engine_owner=bm-a (comment face rolled, "
          "W201 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[202] row: batch=PERPETUAL-N1-W202 "
          "a_seed_base=459_204 b_exit_seed_base=461_204 shard=n1_w202 "
          "out=n1_w202_results.json owner=bm-a")
    print("PASS 3/5 n1 W202 materializer face: %d+%d+%d+%d derived pairs + "
          "2 archive pairs (ALREADY-LANDED face, r925 seat-round closeout "
          "pre-freeze) all count-asserted; staircase SIXTY-SECOND; "
          "prior-wave parity->W201; deps range(17,202) all-landed clean; "
          "prereg presence assert->W202"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 199->200 rows + AST+py_compile + W201/W200/W199 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "ALREADY-archived processed/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W202 = 192nd engine wave, bm-a 117th owned "
          "(rows 191+candidate per receipt leg0); A=459_204..461_203 "
          "hops=1 SIXTY-SECOND staircase; B=461_204..461_403 hops=1 "
          "own-A mutual exclusion (W141); ZERO in-flight upstream (W201 "
          "finalize landed r924, head 856,545 K 440,120); ADMIT "
          "receipt machine-read; receipt=results/_r927bma_w202_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
