# -*- coding: utf-8 -*-
"""r909 bm-a W195 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + probe
selfcheck re-derive legs). Direct-author per the r787/r905 physical
chunk-roll machinery: extract current W194 fragments (physical face dumps
results/_r909bma_w195_face_*.txt per r776), roll W194->W195 with
count-asserted replacements, insert ADDITIVELY after the last registered
row; originals byte-identical zero-destroy.

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r907bma_w195_probe_receipt.json (bands A 443804..445803 /
B 445804..446003, hops 1/1, FIFTY-FIFTH staircase, leg0 rows 192 tail
W194 owner_rows 184 bma_rows 109 ordinal 185 bma_ordinal 110
w194_ledger_head 841145, leg2 conflicts 0, leg3 origin vacancy, leg4
W196+ projection A 445804..447803 / B 446004..446203 hops 0/0
B-inside-A). Seat push eb81c0878 (MSG-2026-10-09-0844-bma-w195-seat +
probe script + receipt, 3-item, r907). W194=bm-a r905 five-face
82670b0ba registered, burn COMPLETE 12/12, finalize LANDED r906
one-pass (ledger 841,145 EXACT, K=424,720, four pred keys PASS) --
ZERO in-flight upstream seats, clean precondition freeze window.

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581/r445 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment PASS
prints; r359 count prose from gate machine output; r776 fragment-needle
law (pairs built from the PHYSICAL probe dumps
results/_r909bma_w195_face_*.txt, re-verified against the live files at
run time); r780/r781 verify-separation (all stale+presence asserts in
memory BEFORE any write); r666 safe write order (n1 first, then pf)."""
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
RCPT = os.path.join(ROOT, "results", "_r907bma_w195_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r909bma_w195_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-0844-bma-w195-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W195_PREREG.md")
SEAT_SHA = "eb81c0878"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
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


def main():
    facts = {"round": 909, "machine": "bm-a", "wave": 195}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '195: {"a": (443_804, 445_803)' in pf_probe:
        print("ALREADY APPLIED: W195 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "195: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 195 already on origin"
    assert '194: {"a": (441_604, 443_603)' in origin_pf, "origin W194 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "W195 materializer face" not in origin_n1, "origin n1 W195 face present"
    assert '195: {"batch": "PERPETUAL-N1-W195"' not in origin_n1, \
        "origin n1 W195 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    A = r["legs"]["leg1"]["A"]
    B = r["legs"]["leg1"]["B"]
    assert A == [443804, 445803] and B == [445804, 446003], \
        "receipt bands drift: %s %s" % (A, B)
    assert r["legs"]["leg1"]["hops_A"] == 1 and r["legs"]["leg1"]["hops_B"] == 1
    assert r["bands"] == {"A": "443804_445803", "B": "445804_446003"}
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 192 and leg0["tail"] == "W194"
    assert leg0["ordinal"] == 185 and leg0["bma_ordinal"] == 110
    assert leg0["owner_rows"] == 184 and leg0["bma_rows"] == 109
    assert leg0["w194_ledger_head"] == 841145
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W196p_A"] == "445804..447803" and leg4["W196p_B"] == "446004..446203"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W196p_B_lands_inside_W196p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 194 and len(N1_BANDS) == 192, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 109 and owners.get("bm-c") == 35 \
        and owned == 184, "owner counts drift: %s" % owners
    assert N1_BANDS[194] == {"a": (441604, 443603), "b_exit": (443604, 443803),
                            "engine_owner": "bm-a"}, "W194 row drift"
    assert N1_BANDS[193] == {"a": (439404, 441403), "b_exit": (441404, 441603),
                            "engine_owner": "bm-a"}, "W193 row drift"
    assert os.path.exists(PREREG), "W195 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ at freeze time (archive-pending state)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w194_results.json")), \
        "W194 finalize product missing (dep precondition)"
    facts["w193_results_on_disk"] = os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w193_results.json"))
    for f in ("results/_r907bma_w195_probe.py",
              "results/_r907bma_w195_probe_receipt.json"):
        assert os.path.exists(os.path.join(ROOT, f)), \
            "seat-cited artifact missing: %s" % f
    facts["precheck"] = {"rows": len(N1_BANDS), "bma_rows": owners.get("bm-a"),
                         "bmc_rows": owners.get("bm-c"),
                         "owner_rows": owned,
                         "w193_results_on_disk": facts["w193_results_on_disk"]}

    # ---- G3 read live files, EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract W194 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat194 = chunk(n1n, "    # --- W194 materializer face",
                   "    _set_wave(2)", "mat194")
    assert mat194.rstrip("\n").endswith("_set_wave(2)"), "mat194 tail drift"
    cfg194 = chunk(n1n, '    194: {"batch": "PERPETUAL-N1-W194",',
                   '"engine_owner": "bm-a"},', "cfg194")
    pf194 = chunk(pfn, "    # W194 (bm-a r905 freeze, seat MSG-2026-10-09-0627-bma-w194-seat",
                 '"engine_owner": "bm-a"},', "pf194")
    claim194 = chunk(n1n, '          "+ W194 materializer face [same guard set',
                     '"r905 bm-a] "', "claim194")
    assert n1n.count(cfg194) == 1, "cfg194 not unique"
    assert n1n.count(claim194) == 1, "claim194 not unique"
    assert pfn.count(pf194) == 1, "pf194 not unique"

    # ---- G5 roll materializer block W194 -> W195 ----
    m = mat194
    R = [
        # header comment
        ("# --- W194 materializer face (r905 bm-a freeze, own-series law",
         "# --- W195 materializer face (r909 bm-a freeze, own-series law", 1),
        ("#     one-hundred-ninth owned per machine-derive (engine_owner==bm-a",
         "#     one-hundred-tenth owned per machine-derive (engine_owner==bm-a", 1),
        ("#     rows 108 + candidate); wave 193 = first free number after",
         "#     rows 109 + candidate); wave 194 = first free number after", 1),
        ("#     the REGISTERED W193 row (bm-a r901 freeze 5cf0d6175) --",
         "#     the REGISTERED W194 row (bm-a r905 freeze 82670b0ba) --", 1),
        ("#     SINGLE STATE zero seat gap (W2..W193 all registered). Seat",
         "#     SINGLE STATE zero seat gap (W2..W194 all registered). Seat", 1),
        ("#     published=reserved MSG-2026-10-09-0627-bma-w194-seat pushed",
         "#     published=reserved MSG-2026-10-09-0844-bma-w195-seat pushed", 1),
        ("#     to origin 5cca13637 BEFORE this freeze, r565 law (payload",
         "#     to origin eb81c0878 BEFORE this freeze, r565 law (payload", 1),
        ("#     the W191 finalize product already on origin since r895, not",
         "#     the W194 finalize product already on origin since r906, not", 1),
        ("#     at fetch (r902 seat push), zero merge, zero",
         "#     at fetch (r907 seat push), zero merge, zero", 1),
        ("#     THIS freeze window -- bm-a r905 freeze-closeout archive move",
         "#     THIS freeze window -- bm-a r909 freeze-closeout archive move", 1),
        ("#     (the W194 seat MSG sits in fleet/inbox/ at freeze time,",
         "#     (the W195 seat MSG sits in fleet/inbox/ at freeze time,", 1),
        ("#     ONE HUNDRED-AND-NINETY-FOURTH engine wave BY",
         "#     ONE HUNDRED-AND-NINETY-FIFTH engine wave BY", 1),
        ("#     MACHINE-DERIVE (engine_owner rows 183 + candidate; gate",
         "#     MACHINE-DERIVE (engine_owner rows 184 + candidate; gate", 1),
        ("#     W1..W193 finalize ALL LANDED (net chain head 838,945,",
         "#     W1..W194 finalize ALL LANDED (net chain head 841,145,", 1),
        ("#     K=422,520 merged pool; W193 finalize one-pass bm-a r904)",
         "#     K=424,720 merged pool; W194 finalize one-pass bm-a r906)", 1),
        ("always on. ADMIT receipt results/_r902bma_w194_probe_receipt.json;",
         "always on. ADMIT receipt results/_r907bma_w195_probe_receipt.json;", 1),
        ("#     banned gate ADMIT 0; not a re-pick (R250: W194 bands were",
         "#     banned gate ADMIT 0; not a re-pick (R250: W195 bands were", 1),
        # code: wave pin + mirror cross-checks
        ("    _set_wave(194)", "    _set_wave(195)", 1),
        ('assert WAVE_CONFIGS[193]["a_seed_base"] == pf.N1_BANDS[193]["a"][0], \\',
         'assert WAVE_CONFIGS[194]["a_seed_base"] == pf.N1_BANDS[194]["a"][0], \\', 1),
        ('"W194 A band drift vs law mirror"',
         '"W195 A band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[193]["b_exit_seed_base"] == \\',
         'assert WAVE_CONFIGS[194]["b_exit_seed_base"] == \\', 1),
        ('pf.N1_BANDS[193]["b_exit"][0], "W194 B band drift vs law mirror"',
         'pf.N1_BANDS[194]["b_exit"][0], "W195 B band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[193].get("engine_owner") == \\',
         'assert WAVE_CONFIGS[194].get("engine_owner") == \\', 1),
        ('pf.N1_BANDS[193].get("engine_owner") == "bm-a", \\',
         'pf.N1_BANDS[194].get("engine_owner") == "bm-a", \\', 1),
        ('"W194 engine_owner drift (law mirror parity)"',
         '"W195 engine_owner drift (law mirror parity)"', 1),
        ("w193_a", "w194_a", 8),
        ("w193_b", "w194_b", 8),
        ('"W194 A/B band overlap"', '"W195 A/B band overlap"', 1),
        ('"W194 hits SEED_REGISTRY"', '"W195 hits SEED_REGISTRY"', 1),
        ('f"W194 {nm} hits v1"', 'f"W195 {nm} hits v1"', 1),
        ('f"W194 {nm} hits W1"', 'f"W195 {nm} hits W1"', 1),
        ('f"W194 {nm} hits probe seeds"', 'f"W195 {nm} hits probe seeds"', 1),
        # prior-wave disjointness + reserved bands
        ("# prior-wave disjointness W2..W193 (single state: all",
         "# prior-wave disjointness W2..W194 (single state: all", 1),
        ("WAVE_CONFIGS if w < 194):", "WAVE_CONFIGS if w < 195):", 2),
        ('f"W194 A hits W{wprev}"', 'f"W195 A hits W{wprev}"', 1),
        ('f"W194 B hits W{wprev}"', 'f"W195 B hits W{wprev}"', 1),
        ("n3r1_used193", "n3r1_used194", 3),
        ('"W194 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
         '"W195 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
        ('"W194 bands must clear the lfc actual draw range"',
         '"W195 bands must clear the lfc actual draw range"', 1),
        ('"W194 bands must clear the options_wave2 actual draw range"',
         '"W195 bands must clear the options_wave2 actual draw range"', 1),
        # band facts comment
        ("# band facts (law sec.4 W194 row, r795): A = FIRST-CLEAN past",
         "# band facts (law sec.4 W195 row, r795): A = FIRST-CLEAN past", 1),
        ("# the registered W193 B band (the arithmetic continuation",
         "# the registered W194 B band (the arithmetic continuation", 1),
        ("# 441_404..443_403 is REFUSED at its own start by the W193",
         "# 443_604..445_603 is REFUSED at its own start by the W194", 1),
        ("# B band 441_404..441_603, exactly as the W193 prereg sec5.5 +",
         "# B band 443_604..443_803, exactly as the W194 prereg sec5.5 +", 1),
        ("# bm-a r900 probe leg4 succession projection notes",
         "# bm-a r902 probe leg4 succession projection notes", 1),
        ("# 441_604..443_603; A base == prior-wave B tail+1 (441_603+1)",
         "# 443_804..445_803; A base == prior-wave B tail+1 (443_803+1)", 1),
        ("# machine-checkable -- A-hops-prior-B staircase FIFTY-FOURTH",
         "# machine-checkable -- A-hops-prior-B staircase FIFTY-FIFTH", 1),
        ("# continuation 441_604..441_803 is CLEAN on the registered",
         "# continuation 443_804..444_003 is CLEAN on the registered", 1),
        ("# universe but lands INSIDE the W194 A band window --",
         "# universe but lands INSIDE the W195 A band window --", 1),
        ("# 443_604 and lands 443_604..443_803, hops=1, non-rotational",
         "# 445_804 and lands 445_804..446_003, hops=1, non-rotational", 1),
        ("# (443_603+1) machine-checkable; cross-window convergence",
         "# (445_803+1) machine-checkable; cross-window convergence", 1),
        ("# with the W193 prereg sec5.5 + bm-a r900 probe leg4",
         "# with the W194 prereg sec5.5 + bm-a r902 probe leg4", 1),
        ("# honored (post-W193 universe re-derive + own-wave A",
         "# honored (post-W194 universe re-derive + own-wave A", 1),
        ("# reservation when deriving B); seat MSG-0627 tail,",
         "# reservation when deriving B); seat MSG-0844 tail,", 1),
        # band facts asserts
        ('assert WAVE_CONFIGS[194]["a_seed_base"] == 441_604 == 441_603 + 1, (',
         'assert WAVE_CONFIGS[195]["a_seed_base"] == 443_804 == 443_803 + 1, (', 1),
        ('"W194 A must be the first-clean window past the registered "',
         '"W195 A must be the first-clean window past the registered "', 1),
        ('"W193 B band tail 441_603+1 (arithmetic continuation "',
         '"W194 B band tail 443_803+1 (arithmetic continuation "', 1),
        ('"441_404..443_403 REFUSED at its own start by the W193 B "',
         '"443_604..445_603 REFUSED at its own start by the W194 B "', 1),
        ('"band 441_404..441_603, exactly as the W193 prereg sec5.5 + "',
         '"band 443_604..443_803, exactly as the W194 prereg sec5.5 + "', 1),
        ('"bm-a r900 probe leg4 succession projection notes "',
         '"bm-a r902 probe leg4 succession projection notes "', 1),
        ('"staircase FIFTY-FOURTH instance, E36 card)")',
         '"staircase FIFTY-FIFTH instance, E36 card)")', 1),
        ("arith_a193 = set(range(441_604, 443_604))",
         "arith_a194 = set(range(443_804, 445_804))", 1),
        ("assert not (arith_a193 & reg_ints), \\",
         "assert not (arith_a194 & reg_ints), \\", 1),
        ('"W194 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
         '"W195 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
        ('assert WAVE_CONFIGS[194]["b_exit_seed_base"] == 443_604 == 443_603 + 1, (',
         'assert WAVE_CONFIGS[195]["b_exit_seed_base"] == 445_804 == 445_803 + 1, (', 1),
        ('"W194 B must be the first-clean window past the own-wave A "',
         '"W195 B must be the first-clean window past the own-wave A "', 1),
        ('"band tail 443_603+1 (arithmetic continuation "',
         '"band tail 445_803+1 (arithmetic continuation "', 1),
        ('"441_604..441_803 CLEAN on the registered universe but "',
         '"443_804..444_003 CLEAN on the registered universe but "', 1),
        ('"lands INSIDE the W194 A band window; same-freeze mutual "',
         '"lands INSIDE the W195 A band window; same-freeze mutual "', 1),
        ('"own-wave A window reserved jumps to 443_604, first-clean "',
         '"own-wave A window reserved jumps to 445_804, first-clean "', 1),
        ("arith_b193 = set(range(443_604, 443_804))",
         "arith_b194 = set(range(445_804, 446_004))", 1),
        ("assert not (arith_b193 & reg_ints), \\",
         "assert not (arith_b194 & reg_ints), \\", 1),
        ('"W194 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
         '"W195 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
        ("assert not (arith_b193 & arith_a193), \\",
         "assert not (arith_b194 & arith_a194), \\", 1),
        ('"W194 A/B same-freeze mutual exclusion (B hops past own A)"',
         '"W195 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
        # entry identity + paths
        ('assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W194-SHARD-0",',
         'assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W195-SHARD-0",', 1),
        ('"n1w194-0of12"), "W194 entry identity"',
         '"n1w195-0of12"), "W195 entry identity"', 1),
        ('assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W194-SHARD-11",',
         'assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W195-SHARD-11",', 1),
        ('"n1w194-11of12")', '"n1w195-11of12")', 1),
        ('assert SHARD_DIR.endswith("n1_w194") and OUT.endswith(',
         'assert SHARD_DIR.endswith("n1_w195") and OUT.endswith(', 1),
        ('"n1_w194_results.json"), "W194 path drift"',
         '"n1_w195_results.json"), "W195 path drift"', 1),
        ('f"W194 shard dir collides with W{wprev}"',
         'f"W195 shard dir collides with W{wprev}"', 1),
        # finalize cumulative deps (all prior waves LANDED -- clean window)
        ("# W194 finalize cumulative deps: W17..W193 outputs ALL PRESENT",
         "# W195 finalize cumulative deps: W17..W194 outputs ALL PRESENT", 1),
        ("# (landed net chain head 838,945 = W193 bm-a r904 one-pass)",
         "# (landed net chain head 841,145 = W194 bm-a r906 one-pass)", 1),
        ("for _depw in range(17, 194):", "for _depw in range(17, 195):", 1),
        ('f"W194 finalize cumulative dep (W{_depw} output) missing"',
         'f"W195 finalize cumulative dep (W{_depw} output) missing"', 1),
        # prior-wave set derivation + prereg presence
        ("# registered wave below 194 composes; wave 15 excluded by",
         "# registered wave below 195 composes; wave 15 excluded by", 1),
        ("# design; SINGLE STATE (W2..W193 all registered -- no",
         "# design; SINGLE STATE (W2..W194 all registered -- no", 1),
        ("assert sorted(w for w in WAVE_CONFIGS if w < 194) == \\",
         "assert sorted(w for w in WAVE_CONFIGS if w < 195) == \\", 1),
        ("[w for w in range(16, 194)], \\", "[w for w in range(16, 195)], \\", 1),
        ('"W194 prior-wave set must derive from registry keys (no 15; " \\',
         '"W195 prior-wave set must derive from registry keys (no 15; " \\', 1),
        ('"W2..W193 registered single state)"',
         '"W2..W194 registered single state)"', 1),
        ('"research", "PERPETUAL_N1_W194_PREREG.md")), \\',
         '"research", "PERPETUAL_N1_W195_PREREG.md")), \\', 1),
        ('"W194 per-wave prereg missing (materializer requirement)"',
         '"W195 per-wave prereg missing (materializer requirement)"', 1),
    ]
    for k, (old, new, cnt) in enumerate(R):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat195 = m

    # ---- G6 roll WAVE_CONFIGS row ----
    c = cfg194
    RC = [
        ('194: {"batch": "PERPETUAL-N1-W194",',
         '195: {"batch": "PERPETUAL-N1-W195",', 1),
        ('"research/PERPETUAL_N1_W194_PREREG.md (wave-level frozen "',
         '"research/PERPETUAL_N1_W195_PREREG.md (wave-level frozen "', 1),
        ('new seed bands only; ONE HUNDRED-AND-NINETY-FOURTH ENGINE-OWNED WAVE ',
         'new seed bands only; ONE HUNDRED-AND-NINETY-FIFTH ENGINE-OWNED WAVE ', 1),
        ('BY MACHINE-DERIVE (engine_owner rows 183 + candidate), ',
         'BY MACHINE-DERIVE (engine_owner rows 184 + candidate), ', 1),
        ('number law after the REGISTERED W193 row bm-a r901 freeze ',
         'number law after the REGISTERED W194 row bm-a r905 freeze ', 1),
        ('5cf0d6175, SINGLE STATE zero seat gap W2..W193 all ',
         '82670b0ba, SINGLE STATE zero seat gap W2..W194 all ', 1),
        ('registered; W1..W193 finalize ALL LANDED (W193 bm-a r904 ',
         'registered; W1..W194 finalize ALL LANDED (W194 bm-a r906 ', 1),
        ('one-pass, ledger head 838,945, merged pool K=422,520) -- ',
         'one-pass, ledger head 841,145, merged pool K=424,720) -- ', 1),
        ('MSG-2026-10-09-0627-bma-w194-seat PUSHED to origin 5cca13637 ',
         'MSG-2026-10-09-0844-bma-w195-seat PUSHED to origin eb81c0878 ', 1),
        ('(3-item; the W191 finalize product already on origin since r895, not re-shipped; W146 precedent); ',
         '(3-item; the W194 finalize product already on origin since r906, not re-shipped; W146 precedent); ', 1),
        ('at fetch (r902 seat push), zero merge, zero ',
         'at fetch (r907 seat push), zero merge, zero ', 1),
        ('engine_owner=bm-a, wave 193: ',
         'engine_owner=bm-a, wave 194: ', 1),
        ('"A = FIRST-CLEAN past the registered W193 B band (the "',
         '"A = FIRST-CLEAN past the registered W194 B band (the "', 1),
        ('"arithmetic continuation 441_404..443_403 is REFUSED at its "',
         '"arithmetic continuation 443_604..445_603 is REFUSED at its "', 1),
        ('"own start by the W193 B band 441_404..441_603, exactly as "',
         '"own start by the W194 B band 443_604..443_803, exactly as "', 1),
        ('"the W193 prereg sec5.5 + bm-a r900 probe leg4 succession "',
         '"the W194 prereg sec5.5 + bm-a r902 probe leg4 succession "', 1),
        ('"441_604..443_603; A base == prior-wave B tail+1 "',
         '"443_804..445_803; A base == prior-wave B tail+1 "', 1),
        ('"machine-checkable = A-hops-prior-B staircase FIFTY-FOURTH "',
         '"machine-checkable = A-hops-prior-B staircase FIFTY-FIFTH "', 1),
        ('"arithmetic continuation 441_604..441_803 is CLEAN on the "',
         '"arithmetic continuation 443_804..444_003 is CLEAN on the "', 1),
        ('"registered universe but lands INSIDE the W194 A band "',
         '"registered universe but lands INSIDE the W195 A band "', 1),
        ('"jumps to 443_604, first-clean 443_604..443_803 hops=1, "',
         '"jumps to 445_804, first-clean 445_804..446_003 hops=1, "', 1),
        ('"convergence with the W193 prereg sec5.5 + bm-a r900 probe leg4 + "',
         '"convergence with the W194 prereg sec5.5 + bm-a r902 probe leg4 + "', 1),
        ('"r902 probe succession projection notes re-derived -- all "',
         '"r907 probe succession projection notes re-derived -- all "', 1),
        ('"MANDATORY notes honored (post-W193 universe re-derive + "',
         '"MANDATORY notes honored (post-W194 universe re-derive + "', 1),
        ('"results/_r902bma_w194_probe_receipt.json; W195+ projection "',
         '"results/_r907bma_w195_probe_receipt.json; W196+ projection "', 1),
        ('"per this window gate: A first-clean 443_604..445_603 "',
         '"per this window gate: A first-clean 445_804..447_803 "', 1),
        ('"CLEAN / B first-clean 443_804..444_003 CLEAN -- naive "',
         '"CLEAN / B first-clean 446_004..446_203 CLEAN -- naive "', 1),
        ('"W194 B band 443_604..443_803 will refuse the naive "',
         '"W195 B band 445_804..446_003 will refuse the naive "', 1),
        ('"W195 A window; W195 freezer MUST re-derive on the "',
         '"W196 A window; W196 freezer MUST re-derive on the "', 1),
        ('"post-W194 universe AND reserve the own-wave A window "',
         '"post-W195 universe AND reserve the own-wave A window "', 1),
        ('staircase card); W1..W193 finalize ALL LANDED (W193 "\n'
         '                                       "finalize one-pass bm-a r904, net chain head 838,945, "',
         'staircase card); W1..W194 finalize ALL LANDED (W194 "\n'
         '                                       "finalize one-pass bm-a r906, net chain head 841,145, "', 1),
        ('"merged pool K=422,520) -- ZERO in-flight upstream "',
         '"merged pool K=424,720) -- ZERO in-flight upstream "', 1),
        ('"a_seed_base": 441_604,        # law sec.4 W194 A: 441_604..443_603 (FIRST-CLEAN past the registered W193 B band; arithmetic 441_404..443_403 REFUSED at own start by the W193 B band 441_404..441_603; hops=1; A-hops-prior-B staircase FIFTY-FOURTH instance, E36 card; ordinal convergence per r587: W193 prereg sec5.5 prose anticipated fifty-fourth, r902 receipt machine-read FIFTY-FOURTH)',
         '"a_seed_base": 443_804,        # law sec.4 W195 A: 443_804..445_803 (FIRST-CLEAN past the registered W194 B band; arithmetic 443_604..445_603 REFUSED at own start by the W194 B band 443_604..443_803; hops=1; A-hops-prior-B staircase FIFTY-FIFTH instance, E36 card; ordinal convergence per r587: W194 prereg sec5.5 prose anticipated fifty-fifth, r907 receipt machine-read FIFTY-FIFTH)', 1),
        ('"b_exit_seed_base": 443_604,   # law sec.4 W194 B: 443_604..443_803 (FIRST-CLEAN past the own-wave A window; arithmetic 441_604..441_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
         '"b_exit_seed_base": 445_804,   # law sec.4 W195 B: 445_804..446_003 (FIRST-CLEAN past the own-wave A window; arithmetic 443_804..444_003 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
        ('"shard_subdir": "n1_w194", "out_name": "n1_w194_results.json",',
         '"shard_subdir": "n1_w195", "out_name": "n1_w195_results.json",', 1),
    ]
    for k, (old, new, cnt) in enumerate(RC):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg195 = c

    # ---- G7 roll pf N1_BANDS row ----
    p = pf194
    RP = [
        ("    # W194 (bm-a r905 freeze, seat MSG-2026-10-09-0627-bma-w194-seat",
         "    # W195 (bm-a r909 freeze, seat MSG-2026-10-09-0844-bma-w195-seat", 1),
        ("# pushed to origin 5cca13637 pre-freeze r565 law (r902 seat",
         "# pushed to origin eb81c0878 pre-freeze r565 law (r907 seat", 1),
        ("# (3-item; the W191 finalize product already on origin since r895,",
         "# (3-item; the W194 finalize product already on origin since r906,", 1),
        ("# = direct fast-forward behind-0 at fetch (r902 seat push),",
         "# = direct fast-forward behind-0 at fetch (r907 seat push),", 1),
        ("# archive PENDING WITH THIS freeze window -- bm-a r905 freeze",
         "# archive PENDING WITH THIS freeze window -- bm-a r909 freeze", 1),
        ("# closeout archive move (the W194 seat MSG sits in",
         "# closeout archive move (the W195 seat MSG sits in", 1),
        ("# band gate ADMIT results/_r902bma_w194_probe_receipt.json: A = FIRST-CLEAN",
         "# band gate ADMIT results/_r907bma_w195_probe_receipt.json: A = FIRST-CLEAN", 1),
        ("# past the registered W193 B band (arithmetic continuation",
         "# past the registered W194 B band (arithmetic continuation", 1),
        ("# 441_404..443_403 REFUSED at its own start by the W193 B band",
         "# 443_604..445_603 REFUSED at its own start by the W194 B band", 1),
        ("# 441_404..441_603, exactly as the W193 prereg sec5.5 + bm-a r900 probe",
         "# 443_604..443_803, exactly as the W194 prereg sec5.5 + bm-a r902 probe", 1),
        ("# honest forward walk hops=1 -> 441_604..443_603, non-rotational",
         "# honest forward walk hops=1 -> 443_804..445_803, non-rotational", 1),
        ("# (441_603+1) machine-checkable -- A-hops-prior-B staircase",
         "# (443_803+1) machine-checkable -- A-hops-prior-B staircase", 1),
        ("# FIFTY-FOURTH instance, E36 card);",
         "# FIFTY-FIFTH instance, E36 card);", 1),
        ("# continuation 441_604..441_803 CLEAN on the registered universe",
         "# continuation 443_804..444_003 CLEAN on the registered universe", 1),
        ("# but lands INSIDE the W194 A band window -- same-freeze mutual",
         "# but lands INSIDE the W195 A band window -- same-freeze mutual", 1),
        ("# own-wave A window reserved jumps to 443_604 -> 443_604..443_803,",
         "# own-wave A window reserved jumps to 445_804 -> 445_804..446_003,", 1),
        ("# own-wave A tail+1 (443_603+1) machine-checkable);",
         "# own-wave A tail+1 (445_803+1) machine-checkable);", 1),
        ("# W195+ projection (gate-derived r902): A first-clean",
         "# W196+ projection (gate-derived r907): A first-clean", 1),
        ("# 443_604..445_603 CLEAN hops=0 / B first-clean 443_804..444_003",
         "# 445_804..447_803 CLEAN hops=0 / B first-clean 446_004..446_203", 1),
        ("# registered W194 B band 443_604..443_803 will refuse the naive",
         "# registered W195 B band 445_804..446_003 will refuse the naive", 1),
        ("# W195 A window; W195 freezer MUST re-derive on the post-W194",
         "# W196 A window; W196 freezer MUST re-derive on the post-W195", 1),
        ("# NOT a re-pick (R250: W194 bands were never assigned).",
         "# NOT a re-pick (R250: W195 bands were never assigned).", 1),
        ('194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),',
         '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
    ]
    for k, (old, new, cnt) in enumerate(RP):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf195 = p

    # ---- G7b roll PASS-claim ----
    q = claim194
    RQ = [
        ('"+ W194 materializer face [same guard set, dep=W17..W193 "',
         '"+ W195 materializer face [same guard set, dep=W17..W194 "', 1),
        ('"outputs ALL PRESENT (landed net chain head 838,945 = "',
         '"outputs ALL PRESENT (landed net chain head 841,145 = "', 1),
        ('"W193 bm-a r904 one-pass, K=422,520 merged pool) -- ZERO "',
         '"W194 bm-a r906 one-pass, K=424,720 merged pool) -- ZERO "', 1),
        ('"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-FOURTH "',
         '"in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-FIFTH "', 1),
        ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 183 "',
         '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 184 "', 1),
        ("+ candidate) bm-a's one-hundred-ninth owned claim per ",
         "+ candidate) bm-a's one-hundred-tenth owned claim per ", 1),
        ('"machine-derive (engine_owner==bm-a rows 108 + candidate), "',
         '"machine-derive (engine_owner==bm-a rows 109 + candidate), "', 1),
        ('"A=FIRST-CLEAN past the registered W193 B band (staircase "',
         '"A=FIRST-CLEAN past the registered W194 B band (staircase "', 1),
        ('"FIFTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
         '"FIFTY-FIFTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
        ('"results/_r902bma_w194_probe_receipt.json, law sec.4 W194 row, "',
         '"results/_r907bma_w195_probe_receipt.json, law sec.4 W195 row, "', 1),
        ('"r905 bm-a] "', '"r909 bm-a] "', 1),
    ]
    for k, (old, new, cnt) in enumerate(RQ):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim195 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W194 band citations (443_604..443_803 B band; the W195
    # arithmetic continuations 443_604..445_603 / 443_804..444_003) and
    # the seat-payload W194-product note are LEGITIMATE content of the
    # W195 fragments -- they are NOT in the stale lists.
    STALE = {
        "mat195": ["5cca13637", "MSG-2026-10-09-0627", "r902 seat push",
                   "_r902bma", "FIFTY-FOURTH", "441_404",
                   "441_604..443_603", "441_604..441_803",
                   "441_603+1", "443_603+1", '== "bm-c"',
                   "one-hundred-ninth", "rows 108 + candidate",
                   "ONE HUNDRED-AND-NINETY-FOURTH", "W2..W193 all",
                   "arith_a193", "arith_b193", "w193_a", "w193_b",
                   "n3r1_used193", "W1..W193 finalize", "838,945",
                   "422,520", "r905 freeze-closeout", "bm-a r904",
                   "bm-a r900 probe", "post-W193 universe",
                   "MSG-0627 tail", "range(17, 194)",
                   "jumps to 443_604", "n1w194", "n1_w194",
                   "W194-SHARD", "W194 entry", "W194 path drift",
                   "W194 shard dir", "w < 194):",
                   "W2..W193 registered", "PERPETUAL_N1_W194_PREREG",
                   "W194 per-wave prereg", "W194 finalize cumulative dep",
                   "W194 prior-wave set", "disjointness W2..W193",
                   "W194 A/B band", "W194 hits", "W194 bands",
                   "W194 A window must", "W194 B window must",
                   "W194 A/B same-freeze", "W195+ projection",
                   "W194 A band drift", "W194 B band drift",
                   "W194 engine_owner drift", "r901 freeze", "5cf0d6175",
                   "the W191 finalize product", "since r895"],
        "cfg195": ["5cca13637", "MSG-2026-10-09-0627", "_r902bma",
                   "FIFTY-FOURTH", "441_404",
                   "441_604..443_603", "441_604..441_803",
                   "441_603+1", "443_603+1",
                   "W193 prereg sec5.5", "bm-a r900",
                   "the W191 finalize product", "since r895",
                   "ONE HUNDRED-AND-NINETY-FOURTH",
                   "W2..W193 all", "W2..W193 registered",
                   "engine_owner rows 183", "r902 seat push",
                   "W195+ projection", "A first-clean 443_604..445_603",
                   "B first-clean 443_804..444_003",
                   "wave 193: ", "441_604,", "443_604,   #",
                   "n1_w194", "W194-SHARD", "r901 freeze",
                   "post-W193 universe", "W193 B band 441",
                   "bm-a r904", "5cf0d6175", "838,945", "422,520",
                   "W1..W193 finalize"],
        "pf195": ["5cca13637", "MSG-2026-10-09-0627", "_r902bma",
                  "FIFTY-FOURTH", "441_404", "441_604..443_603",
                  "441_604..441_803", "441_603+1", "443_603+1",
                  "W195+ projection", "r902 seat", "gate-derived r902",
                  "bm-a r900 probe", "W193 prereg sec5.5", "r905 freeze",
                  "the W194 seat MSG sits", "W193 B band",
                  "jumps to 443_604", "W195 freezer",
                  "post-W194 universe AND", "the W191 finalize product",
                  "since r895"],
        "claim195": ["_r902bma", "FIFTY-FOURTH", "one-hundred-ninth",
                     "rows 108 + candidate", "rows 183 ",
                     "r905 bm-a] ", "W193 B band",
                     "ONE HUNDRED-AND-NINETY-FOURTH",
                     "838,945", "422,520", "dep=W17..W193",
                     "bm-a r904"],
    }
    frags = {"mat195": mat195, "cfg195": cfg195, "pf195": pf195,
             "claim195": claim195}
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
    n1_b = n1n.replace(cfg194, cfg194 + "\n" + IND19 + cfg195, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w194_pos = n1_b.find("    # --- W194 materializer face")
    assert w194_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w194_pos)
    assert t141 > w194_pos, "T-141 marker not found after W194 face"
    n1_c = n1_b[:t141] + mat195 + "\n" + n1_b[t141:]
    claim_anchor = claim194 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim194 + "\n" + claim195 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf194, pf194 + "\n" + pf195, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '195: {"batch": "PERPETUAL-N1-W195",', 1),
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, "# --- W195 materializer face", 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, '"r909 bm-a] "', 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 443_804,', 1),
        (n1_final, '"b_exit_seed_base": 445_804,', 1),
        (n1_final, "n1_w195", 4),
        (n1_final, "PERPETUAL_N1_W195_PREREG.md", 2),
        (n1_final, "_set_wave(195)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 195)', 3),
        (n1_final, "range(17, 195):", 1),
        (n1_final, '"W196 A window; W196 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 445_804..447_803 ', 1),
        (pf_final, '195: {"a": (443_804, 445_803), "b_exit": (445_804, 446_003),', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W195 (bm-a r909 freeze", 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W196+ projection (gate-derived r907)", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W196+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 445_804..447_803 CLEAN hops=0 / B first-clean 446_004..446_203",
                   "W196 A window; W196 freezer MUST re-derive on the post-W195"):
        if needle not in pf_final:
            fails.append("pf W196+ prose missing: %r" % needle[:60])
    pat = re.compile(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})")
    for name, txt in (("pf", pf_final), ("n1", n1_final)):
        bad = [mm.group() for mm in pat.finditer(txt)
               if int(mm.group(3)) < int(mm.group(1))]
        if bad:
            fails.append("%s malformed windows: %s" % (name, bad[:5]))
    # CR/LF hygiene: the rolled fragments must carry no CR and no
    # triple-LF; the final outputs must introduce ZERO NEW anomalies
    # vs the originals (pre-existing blank-line shapes in untouched
    # regions are not this edit's responsibility -- delta check).
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
         "cfg = n1.WAVE_CONFIGS[195]; "
         "print(json.dumps({'rows': len(B), 'w195': B.get(195), "
         "'w194': B.get(194), 'w193': B.get(193), "
         "'cfg195': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 193, "row count drift: %s" % post
    assert post["w195"] == {"a": [443804, 445803], "b_exit": [445804, 446003],
                           "engine_owner": "bm-a"}, "W195 row drift: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                           "engine_owner": "bm-a"}, "W194 row damaged: %s" % post
    assert post["w193"] == {"a": [439404, 441403], "b_exit": [441404, 441603],
                            "engine_owner": "bm-a"}, "W193 row damaged: %s" % post
    assert post["cfg195"] == [443804, 445804, "n1_w195",
                              "n1_w195_results.json", "bm-a"], \
        "W195 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[195] row: a=(443804,445803) "
          "b_exit=(445804,446003) engine_owner=bm-a (comment face rolled, "
          "W194 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[195] row: batch=PERPETUAL-N1-W195 "
          "a_seed_base=443_804 b_exit_seed_base=445_804 shard=n1_w195 "
          "out=n1_w195_results.json owner=bm-a")
    print("PASS 3/5 n1 W195 materializer face: %d+%d+%d+%d replacements all "
          "count-asserted; staircase FIFTY-FIFTH; prior-wave parity->W194; "
          "deps range(17,195) all-landed clean; prereg "
          "presence assert->W195" % (len(R), len(RC), len(RP), len(RQ)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 192->193 rows + AST+py_compile + W194/W193 "
          "byte-intact post-import + stale sweeps clean"
          % SEAT_SHA)
    print("PASS 5/5 summary: W195 = 185th engine wave, bm-a 110th owned "
          "(rows 184+candidate per receipt leg0); A=443_804..445_803 "
          "hops=1 FIFTY-FIFTH staircase; B=445_804..446_003 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W194 "
          "finalize landed r906, head 841,145 K 424,720); ADMIT "
          "receipt machine-read; receipt=results/_r909bma_w195_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
