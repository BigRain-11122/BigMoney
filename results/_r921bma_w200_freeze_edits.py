# -*- coding: utf-8 -*-
"""r921 bm-a W200 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + seat
MSG ALREADY-archived verification face). Direct-author per the
r909/r912/r915/r916/r919 physical chunk-roll machinery, rolled ONE
generation: extract current W199 fragments, roll W199->W200 with
count-asserted replacements, insert ADDITIVELY after the last
registered row; originals byte-identical zero-destroy. Old sides
DERIVED AT RUNTIME by the four-gen chain (zero transcription, r587):
r912 AST triples (W195_old, W196_new, cnt) -> r915 AST RULES_* ->
W197 text -> r916 AST RULES_W198_* -> W198 text -> r919 AST
RULES_W199_* -> W199 text = this build's old side; W200 fact
substitutions derived at runtime from the r919 new sides via the
ordered S shift (projection-first, bands +2200 staircase, standalone
numbers, ordinals, shas/rounds, bare wave numbers LAST) -- every
derived pair is count-asserted against the live fragment by rep().

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r920bma_w200_probe_receipt.json (bands A 454_804..456_803 /
B 456_804..457_003, hops 1/1, SIXTIETH staircase, leg0 rows 197
tail W199 owner_rows 189 bma_rows 114 ordinal 190 bma_ordinal 115
w199_ledger_head 852,145, leg2 conflicts 0, leg3 origin vacancy,
leg4 W201+ projection A 456_804..458_803 / B 457_004..457_203
hops 0/0 B-inside-A). Seat push 143fcfe1b
(MSG-2026-10-09-1645-bma-w200-seat + probe script + receipt, 3-item,
r920 seat push, ancestor-verified). W198=bm-a r916 five-face freeze
82b881a4f, finalize LANDED r917 one-pass origin d4ea4b348 (ledger
849,945 EXACT five-window streak, K=433,520 EXACT, four pred keys
4/4 PASS). W199=bm-a r919 five-face freeze f312ec9d4 (dead-session
estate takeover absorb) + engine self-burn 12/12 15:38..15:50,
finalize LANDED r920 one-push c19c67450 (ledger 852,145 EXACT
six-window streak, K=435,720 EXACT, skill_line_v2 1.1881) -- W200
freeze-time anchor = W199 finalize actuals per r590, zero
roll-forward. Seat MSG archive state = ALREADY PROCESSED at the
seat round r920 closeout (commit 980db1d3e consumed->processed per
S7 law -- the W173 W195-era ALREADY-archived pattern; archive-pending
N/A this window).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment
PASS prints; r776 fragment-needle law (physical dumps
results/_r921bma_w200_face_*.txt, re-verified against the live files
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
RCPT = os.path.join(ROOT, "results", "_r920bma_w200_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r921bma_w200_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-1645-bma-w200-seat.md"
SEAT_PROCESSED = ("fleet/inbox/processed/"
                  "MSG-2026-10-09-1645-bma-w200-seat.md")
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W200_PREREG.md")
SEAT_SHA = "143fcfe1b"
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


# ---- four-gen extraction: r912 triples + r915/r916/r919 rules ----
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
    return t912, t915, t916, t919


def apply_rules(text, rules, tag):
    for (a, b) in rules:
        if a in text:
            text = text.replace(a, b)
    return text


# ---- S: ordered W199->W200 fact shift (projection-first; bands
# +2200 staircase; standalone numbers; ordinals; shas/rounds/MSG;
# bare wave numbers LAST; every entry verified collision-free) ----
S = [
    # B-phase: own-projection face (before bare shifts create W200)
    ("W200", "W201"),
    ("454_604..456_603", "456_804..458_803"),   # naive W201 A projection
    ("454_804..455_003", "457_004..457_203"),   # naive W201 B projection
    # C-phase: band staircase (+2200)
    ("454_604..454_803", "456_804..457_003"),   # B band
    ("452_604..452_803", "454_804..455_003"),   # arith-B (naive, in own-A)
    ("452_604..454_603", "454_804..456_803"),   # A band
    ("452_404..454_403", "454_604..456_603"),   # arith-A (naive, refused)
    ("452_404..452_603", "454_604..454_803"),   # prior-wave B band
    # D-phase: standalone band numbers
    ("set(range(452_604, 454_604))", "set(range(454_804, 456_804))"),
    ("set(range(454_604, 454_804))", "set(range(456_804, 457_004))"),
    ("(452_604, 454_603)", "(454_804, 456_803)"),   # pf row tuple A
    ("(454_604, 454_803)", "(456_804, 457_003)"),   # pf row tuple B
    ("== 452_604 == 452_603 + 1", "== 454_804 == 454_803 + 1"),
    ("== 454_604 == 454_603 + 1", "== 456_804 == 456_803 + 1"),
    ('"a_seed_base": 452_604,', '"a_seed_base": 454_804,'),
    ('"b_exit_seed_base": 454_604,', '"b_exit_seed_base": 456_804,'),
    ("jumps to 454_604", "jumps to 456_804"),
    ("# 454_604 and lands", "# 456_804 and lands"),
    ("452_603+1", "454_803+1"),
    ("454_603+1", "456_803+1"),
    # E-phase: ordinals/words
    ("one-hundred-fourteenth", "one-hundred-fifteenth"),
    ("rows 113 + candidate", "rows 114 + candidate"),
    ("ONE HUNDRED-AND-NINETY-NINTH", "TWO HUNDREDTH"),
    ("engine_owner rows 188", "engine_owner rows 189"),
    ("FIFTY-NINTH", "SIXTIETH"),
    ("fifty-ninth", "sixtieth"),
    # F-phase: shas/rounds/MSG (r919->r921 BEFORE r916 freeze->r919;
    # r918->r920 BEFORE r915 probe->r918 probe)
    ("3a875bf43", "143fcfe1b"),
    ("82b881a4f", "f312ec9d4"),
    ("r919", "r921"),
    ("r916 freeze", "r919 freeze"),
    ("r917", "r920"),
    ("r918", "r920"),
    ("r915 probe", "r918 probe"),
    ("MSG-2026-10-09-1507", "MSG-2026-10-09-1645"),
    ("MSG-1507", "MSG-1645"),
    ("849,945", "852,145"),
    ("433,520", "435,720"),
    # G-phase: bare wave numbers (LAST; 199->200 before 198->199)
    ("199", "200"),
    ("198", "199"),
]


def apply_s(text):
    for (a, b) in S:
        text = text.replace(a, b)
    return text


# ---- archive face: W200 seat MSG ALREADY PROCESSED at the seat-round
# closeout (r920 980db1d3e consumed->processed; the W173-era
# ALREADY-archived pattern; pending-block replaced explicitly) ----
ARCH_MAT = (
    "    #     --no-verify; self-ack inbox->processed archive PENDING WITH\n"
    "    #     THIS freeze window -- bm-a r919 freeze-closeout archive move\n"
    "    #     (the W199 seat MSG sits in fleet/inbox/ at freeze time,\n"
    "    #     moves to processed/ with this window closeout, honest per\n"
    "    #     frozen prereg sec.0).",
    "    #     --no-verify; self-ack inbox->processed archive ALREADY LANDED\n"
    "    #     pre-freeze -- bm-a r920 seat-round closeout consumed->processed\n"
    "    #     (the W200 seat MSG sits in fleet/inbox/processed/ at\n"
    "    #     freeze time, honest archived per S7 law).")
ARCH_PF = (
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive PENDING WITH THIS freeze window -- bm-a r919 freeze\n"
    "    # closeout archive move (the W199 seat MSG sits in\n"
    "    # fleet/inbox/ at freeze time, moves to processed/ with this\n"
    "    # window closeout, honest per frozen prereg sec.0);",
    "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
    "    # archive ALREADY LANDED pre-freeze -- bm-a r920 seat-round\n"
    "    # closeout consumed->processed (the W200 seat MSG sits in\n"
    "    # fleet/inbox/processed/ at freeze time, honest archived\n"
    "    # per S7 law);")

STALE = {
    "mat200": ["3a875bf43", "MSG-2026-10-09-1507", "r918 seat push",
               "_r918bma", "FIFTY-NINTH", "fifty-ninth", "452_604",
               "452_604..454_603", "452_604..452_803",
               "452_404..454_403", "452_404..452_603", "452_603+1",
               "454_603+1", '== "bm-c"',
               "one-hundred-fourteenth", "rows 113 + candidate",
               "ONE HUNDRED-AND-NINETY-NINTH", "W2..W198 all",
               "arith_a198", "arith_b198", "w198_a", "w198_b",
               "n3r1_used198", "W1..W198 finalize", "849,945",
               "433,520", "r919 freeze-closeout", "one-pass bm-a r917",
               "W198 bm-a r917 one-pass", "bm-a r915 probe",
               "post-W198 universe", "MSG-1507 tail",
               "range(17, 199)", "jumps to 454_604", "n1w199", "n1_w199",
               "W199-SHARD", "W199 entry", "W199 path drift",
               "W199 shard dir", "w < 199):", "W2..W198 registered",
               "PERPETUAL_N1_W199_PREREG", "W199 per-wave prereg",
               "W199 finalize cumulative dep", "W199 prior-wave set",
               "disjointness W2..W198", "W199 A/B band", "W199 hits",
               "W199 bands", "W199 A window must", "W199 B window must",
               "W199 A/B same-freeze", "W200+ projection",
               "W199 A band drift", "W199 B band drift",
               "W199 engine_owner drift", "r909 freeze", "b9b962672",
               "the W198 finalize product", "since r917",
               "02cf6b44d", "522a0aef5", "82b881a4f",
               "engine_owner rows 188", "archive PENDING",
               "freeze-closeout archive move",
               "moves to processed/ with this window closeout"],
    "cfg200": ["3a875bf43", "MSG-2026-10-09-1507", "_r918bma",
               "FIFTY-NINTH", "fifty-ninth", "452_604",
               "452_604..454_603", "452_604..452_803",
               "452_404..454_403", "452_404..452_603", "452_603+1",
               "454_603+1", "W198 prereg sec5.5", "bm-a r915 probe",
               "the W198 finalize product", "since r917",
               "ONE HUNDRED-AND-NINETY-NINTH", "W2..W198 all",
               "W2..W198 registered", "engine_owner rows 188",
               "r918 seat push", "W200+ projection",
               "A first-clean 454_604..456_603",
               "B first-clean 454_804..455_003", "wave 198: ",
               '"a_seed_base": 452_604,', '"b_exit_seed_base": 454_604,',
               "n1_w199", "W199-SHARD", "r916 freeze", "post-W198 universe",
               "one-pass bm-a r917", "W198 bm-a r917", "849,945",
               "433,520", "82b881a4f", "W1..W198 finalize",
               "W198 B band 452_404..452_603"],
    "pf200": ["3a875bf43", "MSG-2026-10-09-1507", "_r918bma",
              "FIFTY-NINTH", "fifty-ninth", "452_604",
              "452_404..454_403", "452_604..454_603",
              "452_604..452_803", "452_404..452_603", "452_603+1",
              "454_603+1", "W200+ projection", "r918 seat push",
              "gate-derived r918", "bm-a r915 probe",
              "W198 prereg sec5.5", "r916 freeze",
              "W198 B band", "jumps to 454_604", "W200 freezer",
              "post-W198 universe AND", "the W198 finalize product",
              "since r917", "archive PENDING",
              "freeze-closeout archive move",
              "moves to processed/ with this window closeout",
              "W199 bands were", "ONE HUNDRED-AND-NINETY-NINTH",
              "one-hundred-fourteenth", "rows 113 + candidate",
              "engine_owner rows 188", "849,945", "433,520",
              "82b881a4f", "W1..W198 finalize", "n1w199", "n1_w199"],
    "claim200": ["_r918bma", "FIFTY-NINTH", "one-hundred-fourteenth",
                 "rows 113 + candidate", "rows 188 ",
                 "r919 bm-a] ", "W198 B band",
                 "ONE HUNDRED-AND-NINETY-NINTH",
                 "849,945", "433,520", "dep=W17..W198",
                 "W198 bm-a r917 one-pass", "law sec.4 W199 row"],
}


def roll_pairs(r912_list, r915_rules, r916_rules, r919_rules, w200_rules,
                drop_if, tag):
    """Four-gen chain: old side = r912 new side rolled by the r915 fact
    rules then the r916 fact rules then the r919 fact rules (= the live
    W199 text, zero transcription); new side = W200 rule-rolled."""
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
            fails.append("UNCHANGED PAIR [%s]: %r" % (tag, w199[:90]))
            continue
        pairs.append((w199, w200, cnt))
    return pairs


def main():
    facts = {"round": 921, "machine": "bm-a", "wave": 200,
             "archive_state": "ALREADY processed at the seat round r920 "
                              "closeout (commit 980db1d3e consumed->processed "
                              "per S7 law) -- archive-pending N/A"}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '200: {"a": (454_804, 456_803)' in pf_probe:
        print("ALREADY APPLIED: W200 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "200: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 200 already on origin"
    assert '199: {"a": (452_604, 454_603)' in origin_pf, "origin W199 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "# --- W200 materializer face" not in origin_n1, "origin n1 W200 face present"
    assert '200: {"batch": "PERPETUAL-N1-W200"' not in origin_n1, \
        "origin n1 W200 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    leg1 = r["legs"]["leg1"]
    A, B = leg1["A"], leg1["B"]
    assert A == [454804, 456803] and B == [456804, 457003], \
        "receipt bands drift: %s %s" % (A, B)
    assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1
    assert leg1["ARITH_A"] == [454604, 456603] and \
        leg1["ARITH_B"] == [454804, 455003], "receipt arithmetic drift"
    assert r["bands"] == {"A": "454804_456803", "B": "456804_457003"}
    assert "SIXTIETH" in leg1["A_semantics"], \
        "receipt A_semantics ordinal face missing"
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 197 and leg0["tail"] == "W199"
    assert leg0["ordinal"] == 190 and leg0["bma_ordinal"] == 115
    assert leg0["owner_rows"] == 189 and leg0["bma_rows"] == 114
    assert leg0["w199_ledger_head"] == 852145
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W201p_A"] == "456804..458803" and \
        leg4["W201p_B"] == "457004..457203"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W201p_B_lands_inside_W201p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 199 and len(N1_BANDS) == 197, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 114 and owners.get("bm-c") == 35 \
        and owned == 189, "owner counts drift: %s" % owners
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
    assert os.path.exists(PREREG), "W200 per-wave prereg missing"
    assert not os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG back in fleet/inbox/ (ALREADY-archived state violated)"
    assert os.path.exists(os.path.join(ROOT, SEAT_PROCESSED)), \
        "seat MSG not in fleet/inbox/processed/ (ALREADY-archived state)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w199_results.json")), \
        "W199 finalize product missing (dep precondition)"
    for f in ("results/_r920bma_w200_probe.py",
              "results/_r920bma_w200_probe_receipt.json"):
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

    # ---- G4 extract W199 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat199 = chunk(n1n, "    # --- W199 materializer face",
                   "    _set_wave(2)", "mat199")
    assert mat199.rstrip("\n").endswith("_set_wave(2)"), "mat199 tail drift"
    cfg199 = chunk(n1n, '    199: {"batch": "PERPETUAL-N1-W199",',
                   '"engine_owner": "bm-a"},', "cfg199")
    pf199 = chunk(pfn, "    # W199 (bm-a r919 freeze, seat MSG-2026-10-09-1507-bma-w199-seat",
                 '"engine_owner": "bm-a"},', "pf199")
    claim199 = chunk(n1n, '          "+ W199 materializer face [same guard set',
                     '"r919 bm-a] "', "claim199")
    assert n1n.count(cfg199) == 1, "cfg199 not unique"
    assert n1n.count(claim199) == 1, "claim199 not unique"
    assert pfn.count(pf199) == 1, "pf199 not unique"
    for nm, frag in (("mat", mat199), ("cfg", cfg199),
                     ("pf", pf199), ("claim", claim199)):
        with open(os.path.join(ROOT, "results",
                               "_r921bma_w200_face_%s.txt" % nm),
                  "w", encoding="utf-8", newline="") as fh:
            fh.write(frag)
    facts["dump_sizes"] = {nm: len(frag) for nm, frag in
                           (("mat", mat199), ("cfg", cfg199),
                            ("pf", pf199), ("claim", claim199))}

    # ---- G5-G7 derive rolled pairs (four-gen bloodline AST chain) ----
    t912, t915, t916, t919 = load_bloodline()
    drop_if = [x[0] if isinstance(x, tuple) else x for x in t915["DROP_IF"]]
    rules_w200_mat = [(b, apply_s(b)) for (a, b) in t919["RULES_W199_MAT"]]
    rules_w200_cfg = [(b, apply_s(b)) for (a, b) in t919["RULES_W199_CFG"]]
    rules_w200_pf = [(b, apply_s(b)) for (a, b) in t919["RULES_W199_PF"]]
    rules_w200_claim = [(b, apply_s(b)) for (a, b) in t919["RULES_W199_CLAIM"]]
    pairs_mat = roll_pairs(t912["R"], t915["RULES_MAT"],
                           t916["RULES_W198_MAT"], t919["RULES_W199_MAT"],
                           rules_w200_mat, drop_if, "mat")
    pairs_cfg = roll_pairs(t912["RC"], t915["RULES_CFG"],
                           t916["RULES_W198_CFG"], t919["RULES_W199_CFG"],
                           rules_w200_cfg, drop_if, "cfg")
    pairs_pf = roll_pairs(t912["RP"], t915["RULES_PF"],
                          t916["RULES_W198_PF"], t919["RULES_W199_PF"],
                          rules_w200_pf, drop_if, "pf")
    pairs_claim = roll_pairs(t912["RQ"], t915["RULES_CLAIM"],
                            t916["RULES_W198_CLAIM"], t919["RULES_W199_CLAIM"],
                            rules_w200_claim, drop_if, "claim")
    facts["pair_counts"] = {"mat": len(pairs_mat), "cfg": len(pairs_cfg),
                            "pf": len(pairs_pf), "claim": len(pairs_claim),
                            "dropped_archive": (len(t912["R"]) - len(pairs_mat))
                            + (len(t912["RP"]) - len(pairs_pf)),
                            "archive_pairs": 2}
    # archive pairs FIRST (pending block replaced before fact shifts)
    m = rep(mat199, ARCH_MAT[0], ARCH_MAT[1], 1, "mat-arch")
    for k, (old, new, cnt) in enumerate(pairs_mat):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat200 = m
    c = cfg199
    for k, (old, new, cnt) in enumerate(pairs_cfg):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg200 = c
    p = rep(pf199, ARCH_PF[0], ARCH_PF[1], 1, "pf-arch")
    for k, (old, new, cnt) in enumerate(pairs_pf):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf200 = p
    q = claim199
    for k, (old, new, cnt) in enumerate(pairs_claim):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim200 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W199 band citations (the registered W199 B band
    # 454_604..454_803 and the W200 arithmetic continuations
    # 454_604..456_603 / 454_804..455_003) are LEGITIMATE content of
    # the W200 fragments (prior-wave + own-arith faces) -- NOT stale.
    frags = {"mat200": mat200, "cfg200": cfg200, "pf200": pf200,
             "claim200": claim200}
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
    n1_b = n1n.replace(cfg199, cfg199 + "\n" + IND19 + cfg200, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w199_pos = n1_b.find("    # --- W199 materializer face")
    assert w199_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w199_pos)
    assert t141 > w199_pos, "T-141 marker not found after W199 face"
    n1_c = n1_b[:t141] + mat200 + "\n" + n1_b[t141:]
    claim_anchor = claim199 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim199 + "\n" + claim200 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf199, pf199 + "\n" + pf200, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '200: {"batch": "PERPETUAL-N1-W200",', 1),
        (n1_final, '199: {"batch": "PERPETUAL-N1-W199",', 1),
        (n1_final, '198: {"batch": "PERPETUAL-N1-W198",', 1),
        (n1_final, '197: {"batch": "PERPETUAL-N1-W197",', 1),
        (n1_final, '196: {"batch": "PERPETUAL-N1-W196",', 1),
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W200 materializer face", 1),
        (n1_final, "# --- W199 materializer face", 1),
        (n1_final, "# --- W198 materializer face", 1),
        (n1_final, "# --- W197 materializer face", 1),
        (n1_final, "# --- W196 materializer face", 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r921 bm-a] "', 1),
        (n1_final, '"r919 bm-a] "', 1),
        (n1_final, '"r916 bm-a] "', 1),
        (n1_final, '"r915 bm-a] "', 1),
        (n1_final, '"r912 bm-a] "', 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 454_804,', 1),
        (n1_final, '"b_exit_seed_base": 456_804,', 1),
        (n1_final, "n1_w200", 4),
        (n1_final, "PERPETUAL_N1_W200_PREREG.md", 2),
        (n1_final, "_set_wave(200)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 200)', 3),
        (n1_final, "range(17, 200):", 1),
        (n1_final, '"W201 A window; W201 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 456_804..458_803 ', 1),
        (n1_final, "bm-a r920 seat-round closeout consumed->processed", 1),
        (n1_final, "(the W200 seat MSG sits in", 1),
        (n1_final, "(the W200 seat MSG sits in fleet/inbox/processed/ at", 1),
        (pf_final, '200: {"a": (454_804, 456_803), "b_exit": (456_804, 457_003),', 1),
        (pf_final, '199: {"a": (452_604, 454_603), "b_exit": (454_604, 454_803),', 1),
        (pf_final, '198: {"a": (450_404, 452_403), "b_exit": (452_404, 452_603),', 1),
        (pf_final, '197: {"a": (448_204, 450_203), "b_exit": (450_204, 450_403),', 1),
        (pf_final, '196: {"a": (446_004, 448_003), "b_exit": (448_004, 448_203),', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W200 (bm-a r921 freeze", 1),
        (pf_final, "# W199 (bm-a r919 freeze", 1),
        (pf_final, "# W198 (bm-a r916 freeze", 1),
        (pf_final, "# W197 (bm-a r915 freeze", 1),
        (pf_final, "# W196 (bm-a r912 freeze", 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W201+ projection (gate-derived r920)", 1),
        (pf_final, "archive ALREADY LANDED pre-freeze -- bm-a r920 seat-round", 1),
        (pf_final, "(the W200 seat MSG sits in", 1),
        (pf_final, "(the W200 seat MSG sits in\n    # fleet/inbox/processed/ at freeze time", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W201+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 456_804..458_803 CLEAN hops=0 / B first-clean 457_004..457_203",
                   "W201 A window; W201 freezer MUST re-derive on the post-W200"):
        if needle not in pf_final:
            fails.append("pf W201+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[200]; "
         "print(json.dumps({'rows': len(B), 'w200': B.get(200), "
         "'w199': B.get(199), 'w198': B.get(198), 'w197': B.get(197), "
         "'w196': B.get(196), 'w195': B.get(195), 'w194': B.get(194), "
         "'cfg200': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 198, "row count drift: %s" % post
    assert post["w200"] == {"a": [454804, 456803], "b_exit": [456804, 457003],
                           "engine_owner": "bm-a"}, "W200 row drift: %s" % post
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
    assert post["cfg200"] == [454804, 456804, "n1_w200",
                              "n1_w200_results.json", "bm-a"], \
        "W200 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[200] row: a=(454_804,456_803) "
          "b_exit=(456_804,457_003) engine_owner=bm-a (comment face rolled, "
          "W199 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[200] row: batch=PERPETUAL-N1-W200 "
          "a_seed_base=454_804 b_exit_seed_base=456_804 shard=n1_w200 "
          "out=n1_w200_results.json owner=bm-a")
    print("PASS 3/5 n1 W200 materializer face: %d+%d+%d+%d derived pairs + "
          "2 archive pairs (ALREADY-archived face) all count-asserted; "
          "staircase SIXTIETH; prior-wave parity->W199; deps range(17,200) "
          "all-landed clean; prereg presence assert->W200"
          % (len(pairs_mat), len(pairs_cfg), len(pairs_pf),
             len(pairs_claim)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 197->198 rows + AST+py_compile + W199/W198/W197 "
          "byte-intact post-import + stale sweeps clean + seat MSG "
          "ALREADY-archived processed/ verified"
          % SEAT_SHA)
    print("PASS 5/5 summary: W200 = 190th engine wave, bm-a 115th owned "
          "(rows 189+candidate per receipt leg0); A=454_804..456_803 "
          "hops=1 SIXTIETH staircase; B=456_804..457_003 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W199 "
          "finalize landed r920, head 852,145 K 435,720); ADMIT "
          "receipt machine-read; receipt=results/_r921bma_w200_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
