# -*- coding: utf-8 -*-
"""r922 bm-a W201 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG PENDING-archived verification face). Direct-author per the
r909/r912/r915/r916/r919/r921 physical chunk-roll machinery, rolled ONE
generation: extract current W200 fragments, roll W200->W201 with
count-asserted replacements, insert ADDITIVELY after the last
registered row; originals byte-identical zero-destroy. Old sides
DERIVED AT RUNTIME by the five-gen chain (zero transcription, r587):
r912 AST triples (W195_old, W196_new, cnt) -> r915 AST RULES_* ->
W197 text -> r916 AST RULES_W198_* -> W198 text -> r919 AST
RULES_W199_* -> W199 text -> r921 freeze S (AST) -> W200 text = this
build's old side; W201 fact substitutions derived at runtime from the
W200 new sides via the ordered S shift (projection-first, bands +2200
staircase, standalone numbers, ordinals, shas/rounds, bare wave
numbers LAST) -- every derived pair is count-asserted against the live
fragment by rep().

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r921bma_w201_probe_receipt.json (bands A 457_004..459_003 /
B 459_004..459_203, hops 1/1, SIXTY-FIRST staircase, leg0 rows 198
tail W200 owner_rows 190 bma_rows 115 ordinal 191 bma_ordinal 116
w200_ledger_head 854,345, leg2 conflicts 0, leg3 origin vacancy,
leg4 W202+ projection A 459_004..461_003 / B 459_204..459_403
hops 0/0 B-inside-A). Seat push 188ebe647
(MSG-2026-10-09-1812-bma-w201-seat + probe script + receipt, 3-item,
r921 seat push, ancestor-verified). W199=bm-a r919 five-face freeze
f312ec9d4, finalize LANDED r920 one-push c19c67450 (ledger 852,145
EXACT six-window streak, K=435,720 EXACT, four pred keys 4/4 PASS).
W200=bm-a r921 five-face freeze cd92a8d9c (dead-session estate
absorption, predecessor receipt 17:41 validated + committed bf6427c00)
+ engine self-burn 12/12 17:41..17:53, finalize LANDED r921 one-pass
push bdfe1efba (ledger 854,345 EXACT seven-window streak, K=437,920
EXACT, skill_line_v2 1.1882, se_mu 0.000370) -- W201 freeze-time
anchor = W200 finalize actuals per r590, zero roll-forward. Seat MSG
archive state = PENDING at freeze time (dead-session r921 seat round
never closed out -- the W201 seat MSG sits in fleet/inbox/, moves to
processed/ with THIS r922 freeze-window closeout per S7 law; honest
per frozen prereg sec.0).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment
PASS prints; r776 fragment-needle law (physical dumps
results/_r922bma_w201_face_*.txt, re-verified against the live files
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
RCPT = os.path.join(ROOT, "results", "_r921bma_w201_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r922bma_w201_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-1812-bma-w201-seat.md"
SEAT_PROCESSED = ("fleet/inbox/processed/"
                  "MSG-2026-10-09-1812-bma-w201-seat.md")
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W201_PREREG.md")
SEAT_SHA = "188ebe647"
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


# ---- five-gen extraction: r912 triples + r915/r916/r919 rules +
# r921 freeze S (AST) ----
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
    return t912, t915, t916, t919, t921


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


def apply_s_r921(text):
    for (a, b) in T921["S"]:
        text = text.replace(a, b)
    return text


# ---- S: ordered W200->W201 fact shift (projection-first; bands
# +2200 staircase; standalone numbers; ordinals; shas/rounds/MSG;
# bare wave numbers LAST; every entry verified collision-free) ----
S = [
    # B-phase: own-projection face (before bare shifts create W202)
    ("W201", "W202"),
    ("456_804..458_803", "459_004..461_003"),   # naive W202 A projection
    ("457_004..457_203", "459_204..459_403"),   # naive W202 B projection
    # C-phase: band staircase (+2200)
    ("456_804..457_003", "459_004..459_203"),   # B band
    ("454_804..455_003", "457_004..457_203"),   # arith-B (naive, in own-A)
    ("454_804..456_803", "457_004..459_003"),   # A band
    ("454_604..456_603", "456_804..458_803"),   # arith-A (naive, refused)
    ("454_604..454_803", "456_804..457_003"),   # prior-wave B band
    # D-phase: standalone band numbers
    ("set(range(454_804, 456_804))", "set(range(457_004, 459_004))"),
    ("set(range(456_804, 457_004))", "set(range(459_004, 459_204))"),
    ("(454_804, 456_803)", "(457_004, 459_003)"),   # pf row tuple A
    ("(456_804, 457_003)", "(459_004, 459_203)"),   # pf row tuple B
    ("== 454_804 == 454_803 + 1", "== 457_004 == 457_003 + 1"),
    ("== 456_804 == 456_803 + 1", "== 459_004 == 459_003 + 1"),
    ('"a_seed_base": 454_804,', '"a_seed_base": 457_004,'),
    ('"b_exit_seed_base": 456_804,', '"b_exit_seed_base": 459_004,'),
    ("jumps to 456_804", "jumps to 459_004"),
    ("# 456_804 and lands", "# 459_004 and lands"),
    ("454_803+1", "457_003+1"),
    ("456_803+1", "459_003+1"),
    # E-phase: ordinals/words
    ("one-hundred-fifteenth", "one-hundred-sixteenth"),
    ("rows 114 + candidate", "rows 115 + candidate"),
    ("TWO HUNDREDTH", "TWO HUNDRED AND FIRST"),
    ("engine_owner rows 189", "engine_owner rows 190"),
    ("SIXTIETH", "SIXTY-FIRST"),
    ("sixtieth", "sixty-first"),
    # F-phase: shas/rounds/MSG (r921->r922 BEFORE r919 freeze->r921;
    # r920->r921 BEFORE r918 probe->r920 probe)
    ("143fcfe1b", "188ebe647"),
    ("f312ec9d4", "cd92a8d9c"),
    ("r921", "r922"),
    ("r919 freeze", "r921 freeze"),
    ("r920", "r921"),
    ("r918 probe", "r920 probe"),
    ("MSG-2026-10-09-1645", "MSG-2026-10-09-1812"),
    ("MSG-1645", "MSG-1812"),
    ("852,145", "854,345"),
    ("435,720", "437,920"),
    # G-phase: bare wave numbers (LAST; 200->201 before 199->200)
    ("200", "201"),
    ("199", "200"),
]


def apply_s(text):
    for (a, b) in S:
        text = text.replace(a, b)
    return text


# ---- archive face: W201 seat MSG PENDING at freeze time (dead-session
# r921 seat round never closed out; the r922 freeze-window closeout
# moves it consumed->processed per S7 law -- W199-era PENDING pattern) ----
ARCH_MAT = (
    "    #     --no-verify; self-ack inbox->processed archive ALREADY LANDED\n"
    "    #     pre-freeze -- bm-a r920 seat-round closeout consumed->processed\n"
    "    #     (the W200 seat MSG sits in fleet/inbox/processed/ at\n"
    "    #     freeze time, honest archived per S7 law).",
    "    #     --no-verify; self-ack inbox->processed archive PENDING WITH\n"
    "    #     THIS freeze window -- bm-a r922 freeze-closeout archive move\n"
    "    #     (the W201 seat MSG sits in fleet/inbox/ at freeze time,\n"
    "    #     moves to processed/ with this window closeout, honest per\n"
    "    #     frozen prereg sec.0).")
ARCH_PF = (
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive ALREADY LANDED pre-freeze -- bm-a r920 seat-round\n"
    "    # closeout consumed->processed (the W200 seat MSG sits in\n"
    "    # fleet/inbox/processed/ at freeze time, honest archived\n"
    "    # per S7 law);",
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive PENDING WITH THIS freeze window -- bm-a r922 freeze\n"
    "    # closeout archive move (the W201 seat MSG sits in\n"
    "    # fleet/inbox/ at freeze time, moves to processed/ with this\n"
    "    # window closeout, honest per frozen prereg sec.0);")

# stale derivation: r921 STALE (W199-era tokens) rolled by the r921 S
# = W200-era tokens that must NOT survive in the W201 fragments;
# archive-state entries excluded (PENDING form is LEGIT W201 content)
# and ALREADY-form markers added as stale for W201.
ARCH_STALE_EXCLUDES = {
    "archive PENDING", "freeze-closeout archive move",
    "moves to processed/ with this window closeout"}
ARCH_STALE_ADDS = {
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


def derive_stale():
    src = open(R921F, encoding="utf-8").read()
    base = extract_stale_dict(R921F)
    assert base is not None, "r921 STALE dict not found"
    out = {}
    for frag, entries in base.items():
        rolled = []
        for e in entries:
            if e in ARCH_STALE_EXCLUDES:
                continue
            r = e
            for (a, b) in T921["S"]:
                r = r.replace(a, b)
            if r not in rolled:
                rolled.append(r)
        newfrag = frag.replace("200", "201")
        out[newfrag] = rolled + ARCH_STALE_ADDS.get(newfrag, [])
    return out


def roll_pairs(r912_list, r915_rules, r916_rules, r919_rules, w200_rules,
               w201_rules, drop_if, tag):
    """Five-gen chain: old side = r912 new side rolled by the r915 fact
    rules then r916 then r919 then the r921-freeze-S-derived W200 rules
    (= the live W200 text, zero transcription); new side = W201
    rule-rolled."""
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
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w200[:90]))
            continue
        pairs.append((w200, w201, cnt))
    return pairs


def main():
    global T921
    facts = {"round": 922, "machine": "bm-a", "wave": 201,
             "archive_state": "PENDING at freeze time (dead-session r921 "
                              "seat round never closed out) -- moves to "
                              "processed/ with THIS r922 freeze-window "
                              "closeout per S7 law"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '201: {"a": (457_004' in pf_probe:
        print("ALREADY APPLIED: W201 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "201: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 201 already on origin"
    assert '200: {"a": (454_804, 456_803)' in origin_pf, "origin W200 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W201 materializer face" not in origin_n1, "origin n1 W201 face present"
    assert '201: {"batch": "PERPETUAL-N1-W201"' not in origin_n1, \
        "origin n1 W201 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [457004, 459003] and B == [459004, 459203], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [456804, 458803] and \
        leg1["ARITH_B"] == [457004, 457203], "receipt arithmetic drift"
    assert r["bands"] == {"A": "457004_459003", "B": "459004_459203"}
    assert "SIXTY-FIRST" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 198 and leg0["tail"] == "W200"
    assert leg0["ordinal"] == 191 and leg0["bma_ordinal"] == 116
    assert leg0["owner_rows"] == 190 and leg0["bma_rows"] == 115
    assert leg0["w200_ledger_head"] == 854345
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W202p_A"] == "459004..461003" and \
        leg4["W202p_B"] == "459204..459403"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W202p_B_lands_inside_W202p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 200 and len(N1_BANDS) == 198, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 115 and owners.get("bm-c") == 35 \
        and owned == 190, "owner counts drift: %s" % owners
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
    assert os.path.exists(PREREG), "W201 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ (PENDING-state expectation violated)"
    assert not os.path.exists(os.path.join(ROOT, SEAT_PROCESSED)), \
        "seat MSG already in processed/ (PENDING-state expectation violated)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w200_results.json")), \
        "W200 finalize product missing (dep precondition)"
    for f in ("results/_r921bma_w201_probe.py",
              "results/_r921bma_w201_probe_receipt.json"):
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

    # ---- G4 extract W200 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat200 = chunk(n1n, "    # --- W200 materializer face",
                   "    _set_wave(2)", "mat200")
    assert mat200.rstrip("\n").endswith("_set_wave(2)"), "mat200 tail drift"
    cfg200 = chunk(n1n, '    200: {"batch": "PERPETUAL-N1-W200",',
                   '"engine_owner": "bm-a"},', "cfg200")
    pf200 = chunk(pfn, "    # W200 (bm-a r921 freeze, seat MSG-2026-10-09-1645-bma-w200-seat",
                 '"engine_owner": "bm-a"},', "pf200")
    claim200 = chunk(n1n, '          "+ W200 materializer face [same guard set',
                     '"r921 bm-a] "', "claim200")
    assert n1n.count(cfg200) == 1, "cfg200 not unique"
    assert n1n.count(claim200) == 1, "claim200 not unique"
    assert pfn.count(pf200) == 1, "pf200 not unique"
    for nm, frag in (("mat", mat200), ("cfg", cfg200),
                     ("pf", pf200), ("claim", claim200)):
        with open(os.path.join(ROOT, "results",
                               "_r922bma_w201_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                           (("mat", mat200), ("cfg", cfg200),
                            ("pf", pf200), ("claim", claim200))}

    # ---- G5-G7 derive rolled pairs (five-gen bloodline AST chain) ----
    t912, t915, t916, t919, t921 = load_bloodline()
    T921 = t921
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    rules_w200_mat = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_MAT"]]
    rules_w200_cfg = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CFG"]]
    rules_w200_pf = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_PF"]]
    rules_w200_claim = [(b, apply_s_r921(b)) for (a, b) in t919["RULES_W199_CLAIM"]]
    rules_w201_mat = [(b, apply_s(b)) for (a, b) in rules_w200_mat]
    rules_w201_cfg = [(b, apply_s(b)) for (a, b) in rules_w200_cfg]
    rules_w201_pf = [(b, apply_s(b)) for (a, b) in rules_w200_pf]
    rules_w201_claim = [(b, apply_s(b)) for (a, b) in rules_w200_claim]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"],
                           t916["RULES_W198_MAT"], t919["RULES_W199_MAT"],
                           rules_w200_mat, rules_w201_mat, drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"],
                           t916["RULES_W198_CFG"], t919["RULES_W199_CFG"],
                           rules_w200_cfg, rules_w201_cfg, drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"],
                          t916["RULES_W198_PF"], t919["RULES_W199_PF"],
                          rules_w200_pf, rules_w201_pf, drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"],
                             t916["RULES_W198_CLAIM"], t919["RULES_W199_CLAIM"],
                             rules_w200_claim, rules_w201_claim, drop_if, "claim")
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": 2}
    # archive pairs FIRST (ALREADY block replaced before fact shifts)
    m = rep(mat200, ARCH_MAT[0], ARCH_MAT[1], 1, "mat-arch")
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat201 = m
    c = cfg200
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg201 = c
    p = rep(pf200, ARCH_PF[0], ARCH_PF[1], 1, "pf-arch")
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf201 = p
    q = claim200
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim201 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W200 band citations (the registered W200 B band
    # 456_804..457_003 and the W201 arithmetic continuations
    # 456_804..458_803 / 457_004..457_203) are LEGITIMATE content of
    # the W201 fragments (prior-wave + own-arith faces) -- NOT stale.
    STALE = derive_stale()
    frags = {"mat201": mat201, "cfg201": cfg201, "pf201": pf201,
             "claim201": claim201}
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
    n1_b = n1n.replace(cfg200, cfg200 + "\n" + IND19 + cfg201, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w200_pos = n1_b.find("    # --- W200 materializer face")
    assert w200_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w200_pos)
    assert t141 > w200_pos, "T-141 marker not found after W200 face"
    n1_c = n1_b[:t141] + mat201 + "\n" + n1_b[t141:]
    claim_anchor = claim200 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim200 + "\n" + claim201 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf200, pf200 + "\n" + pf201, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '201: {"batch": "PERPETUAL-N1-W201",', 1),
        (n1_final, '200: {"batch": "PERPETUAL-N1-W200",', 1),
        (n1_final, '199: {"batch": "PERPETUAL-N1-W199",', 1),
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W201 materializer face", 1),
        (n1_final, "# --- W200 materializer face", 1),
        (n1_final, "# --- W199 materializer face", 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r922 bm-a] "', 1),
        (n1_final, '"r921 bm-a] "', 1),
        (n1_final, '"r919 bm-a] "', 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 457_004,', 1),
        (n1_final, '"b_exit_seed_base": 459_004,', 1),
        (n1_final, "n1_w201", 4),
        (n1_final, "PERPETUAL_N1_W201_PREREG.md", 2),
        (n1_final, "_set_wave(201)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 201)', 3),
        (n1_final, "range(17, 201):", 1),
        (n1_final, '"W202 A window; W202 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 459_004..461_003 ', 1),
        (n1_final, "bm-a r922 freeze-closeout archive move", 1),
        (n1_final, "(the W201 seat MSG sits in", 1),
        (n1_final, "(the W201 seat MSG sits in fleet/inbox/ at freeze time", 1),
        (pf_final, '201: {"a": (457_004, 459_003), "b_exit": (459_004, 459_203),', 1),
        (pf_final, '200: {"a": (454_804, 456_803), "b_exit": (456_804, 457_003),', 1),
        (pf_final, '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),', 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W201 (bm-a r922 freeze", 1),
        (pf_final, "# W200 (bm-a r921 freeze", 1),
        (pf_final, "# W199 (bm-a r919 freeze", 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W202+ projection (gate-derived r921)", 1),
        (pf_final, "archive PENDING WITH THIS freeze window -- bm-a r922 freeze", 1),
        (pf_final, "(the W201 seat MSG sits in", 1),
        (pf_final, "(the W201 seat MSG sits in\n    # fleet/inbox/ at freeze time", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W202+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 459_004..461_003 CLEAN hops=0 / B first-clean 459_204..459_403",
                   "W202 A window; W202 freezer MUST re-derive on the post-W201"):
        if needle not in pf_final:
            fails.append("pf W202+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[201]; "
         "print(json.dumps({'rows': len(B), 'w201': B.get(201), "
         "'w200': B.get(200), 'w199': B.get(199), 'w198': B.get(198), "
         "'w197': B.get(197), 'w196': B.get(196), 'w195': B.get(195), "
         "'w194': B.get(194), 'cfg201': [cfg['a_seed_base'], "
         "cfg['b_exit_seed_base'], cfg['shard_subdir'], cfg['out_name'], "
         "cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 199, "row count drift: %s" % post
    assert post["w201"] == {"a": [457004, 459003], "b_exit": [459004, 459203],
                           "engine_owner": "bm-a"}, "W201 row drift: %s" % post
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
    assert post["cfg201"] == [457004, 459004, "n1_w201",
                              "n1_w201_results.json", "bm-a"], \
        "W201 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[201] row: a=(457_004,459_003) "
          "b_exit=(459_004,459_203) engine_owner=bm-a (comment face rolled, "
          "W200 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[201] row: batch=PERPETUAL-N1-W201 "
          "a_seed_base=457_004 b_exit_seed_base=459_004 shard=n1_w201 "
          "out=n1_w201_results.json owner=bm-a")
    print("PASS 3/5 n1 W201 materializer face: %d+%d+%d+%d derived pairs + "
          "2 archive pairs (PENDING-archived face, dead-session r921 "
          "estate) all count-asserted; staircase SIXTY-FIRST; "
          "prior-wave parity->W200; deps range(17,201) all-landed clean; "
          "prereg presence assert->W201"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 198->199 rows + AST+py_compile + W200/W199/W198 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "PENDING-archived inbox/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W201 = 191st engine wave, bm-a 116th owned "
          "(rows 190+candidate per receipt leg0); A=457_004..459_003 "
          "hops=1 SIXTY-FIRST staircase; B=459_004..459_203 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W200 "
          "finalize landed r921, head 854,345 K 437,920); ADMIT "
          "receipt machine-read; receipt=results/_r922bma_w201_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
