# -*- coding: utf-8 -*-
"""r901 bm-a W193 five-face freeze edits (takeover closeout of the dead
r901 session: prereg freeze landed+pushed 9c0c089b8 pre-death; this
window lands the remaining five faces). Direct-author per the r787 bm-c
precedent (interactive-window direct-author, extraction-from-emission
N/A honest -- the W193 prereg itself WAS buildgen-emitted r830/r833/r877
lineage 9c0c089b8; the five-face freeze edits follow the r787 physical
chunk-roll machinery: extract current W192 fragments, roll W192->W193
with count-asserted replacements, insert ADDITIVELY after the last
registered row; originals byte-identical zero-destroy).

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r900bma_w193_probe_receipt.json (bands A 439404..441403 /
B 441404..441603, hops 1/1, FIFTY-THIRD staircase, leg0 rows 190 tail
W192 owner_rows 182 bma_rows 107 ordinal 183 bma_ordinal 108, leg2
conflicts 0, leg3 origin vacancy, leg4 W194+ projection A 441404..443403
/ B 441604..441803 hops 0/0 B-inside-A). Seat push 9df3078c5
(MSG-2026-10-09-0458-bma-w193-seat + probe script + receipt, 3-item).
W192=bm-c five-face registered f8703842c, finalize IN FLIGHT on the
bm-c lane -> honest in-flight upstream annotation per frozen prereg
sec.0 (the zero-in-flight-upstream assertion not applicable);
W193 finalize key-order precondition checks the W192 output at run
time (FAIL-CLOSED r307 two-state law in the finalize merge loop).

Inherited-defect fix disclosed: the r787-lineage W192 face's
arith_a190/arith_b190 CLEAN asserts referenced the PRIOR face's
variables (stale-copy face); the W193 face rolls them to its OWN
arith_a192/arith_b192 (the W191-face original correct pattern).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581/r445 AST + py_compile
gate; r581 multi-line assert messages paren-wrapped; r578 five-segment
PASS prints; r359 count prose from gate machine output; r776
fragment-needle law (pairs built from the PHYSICAL probe dumps
results/_r901bma_w193_face_*.txt, re-verified against the live files
at run time); r780/r781 verify-separation (all stale+presence
asserts in memory BEFORE any write); r666 safe write order (n1 first,
then pf -- a pf row without a WAVE_CONFIGS entry would be a dead face
for one tick, the reverse never ignites)."""
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
RCPT = os.path.join(ROOT, "results", "_r900bma_w193_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r901bma_w193_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-0458-bma-w193-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W193_PREREG.md")
SEAT_SHA = "9df3078c5"
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
    facts = {"round": 901, "machine": "bm-a", "wave": 193}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '193: {"a": (439_404, 441_403)' in pf_probe:
        print("ALREADY APPLIED: W193 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "193: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 193 already on origin"
    assert '192: {"a": (437_204, 439_203)' in origin_pf, "origin W192 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "W193 materializer face" not in origin_n1, "origin n1 W193 face present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    A = r["legs"]["leg1"]["A"]
    B = r["legs"]["leg1"]["B"]
    assert A == [439404, 441403] and B == [441404, 441603], \
        "receipt bands drift: %s %s" % (A, B)
    assert r["legs"]["leg1"]["hops_A"] == 1 and r["legs"]["leg1"]["hops_B"] == 1
    assert r["bands"] == {"A": "439404_441403", "B": "441404_441603"}
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 190 and leg0["tail"] == "W192"
    assert leg0["ordinal"] == 183 and leg0["bma_ordinal"] == 108
    assert leg0["owner_rows"] == 182 and leg0["bma_rows"] == 107
    assert leg0["w191_ledger_head"] == 833536
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W194p_A"] == "441404..443403" and leg4["W194p_B"] == "441604..441803"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W194p_B_lands_inside_W194p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 192 and len(N1_BANDS) == 190, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 107 and owners.get("bm-c") == 35 \
        and owned == 182, "owner counts drift: %s" % owners
    assert N1_BANDS[192] == {"a": (437204, 439203), "b_exit": (439204, 439403),
                            "engine_owner": "bm-c"}, "W192 row drift"
    assert N1_BANDS[191] == {"a": (435004, 437003), "b_exit": (437004, 437203),
                            "engine_owner": "bm-a"}, "W191 row drift"
    assert os.path.exists(PREREG), "W193 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ at freeze time (archive-pending state)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w191_results.json")), \
        "W191 finalize product missing (dep precondition)"
    facts["w192_results_on_disk"] = os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w192_results.json"))
    for f in ("results/_r900bma_w193_probe.py",
              "results/_r900bma_w193_probe_receipt.json"):
        assert os.path.exists(os.path.join(ROOT, f)), \
            "seat-cited artifact missing: %s" % f
    facts["precheck"] = {"rows": len(N1_BANDS), "bma_rows": owners.get("bm-a"),
                         "bmc_rows": owners.get("bm-c"),
                         "owner_rows": owned,
                         "w192_results_on_disk": facts["w192_results_on_disk"]}

    # ---- G3 read live files, EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract W192 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat192 = chunk(n1n, "    # --- W192 materializer face",
                   "    _set_wave(2)", "mat192")
    assert mat192.rstrip("\n").endswith("_set_wave(2)"), "mat192 tail drift"
    cfg192 = chunk(n1n, '    192: {"batch": "PERPETUAL-N1-W192",',
                  '"engine_owner": "bm-c"},', "cfg192")
    pf192 = chunk(pfn, "    # W192 (bm-c r787 freeze, seat MSG-20261008-2351-bmc-w192-seat",
                 '"engine_owner": "bm-c"},', "pf192")
    claim192 = chunk(n1n, '          "+ W192 materializer face [same guard set',
                     '"r787 bm-c] "', "claim192")
    assert n1n.count(cfg192) == 1, "cfg192 not unique"
    assert n1n.count(claim192) == 1, "claim192 not unique"
    assert pfn.count(pf192) == 1, "pf192 not unique"

    # ---- G5 roll materializer block W192 -> W193 ----
    m = mat192
    R = [
        # header comment
        ("# --- W192 materializer face (r787 bm-c freeze, own-series law",
         "# --- W193 materializer face (r901 bm-a freeze, own-series law", 1),
        ("#     under CEO de-throttle order O-20261001-2355 sec.2): bm-c's",
         "#     under CEO de-throttle order O-20261001-2355 sec.2): bm-a's", 1),
        ("#     thirty-fifth owned per machine-derive (engine_owner==bm-c",
         "#     one-hundred-eighth owned per machine-derive (engine_owner==bm-a", 1),
        ("#     rows 34 + candidate); wave 191 = first free number after",
         "#     rows 107 + candidate); wave 192 = first free number after", 1),
        ("#     the REGISTERED W191 row (bm-a r894 freeze e5e4af81b) --",
         "#     the REGISTERED W192 row (bm-c r787 freeze f8703842c) --", 1),
        ("#     SINGLE STATE zero seat gap (W2..W191 all registered). Seat",
         "#     SINGLE STATE zero seat gap (W2..W192 all registered). Seat", 1),
        ("#     published=reserved MSG-20261008-2351-bmc-w192-seat pushed",
         "#     published=reserved MSG-2026-10-09-0458-bma-w193-seat pushed", 1),
        ("#     to origin 1abe1a57f BEFORE this freeze, r565 law (payload",
         "#     to origin 9df3078c5 BEFORE this freeze, r565 law (payload", 1),
        ("#     = seat MSG only (Git Data API direct-build push, zero\n"
         "    #     local commit -- sec.6.1.4 channel; the pre-seat probe\n"
         "    #     script + receipt landed with the W192 prereg freeze\n"
         "    #     commit de1ad11f9 next, interactive-window payload note;\n"
         "    #     the W191 finalize product already on origin since r895, not",
         "#     = seat MSG + pre-seat probe script + probe receipt (3-item;\n"
         "    #     the W191 finalize product already on origin since r895, not", 1),
        ("#     deletion-set EMPTY; delivery window = direct fast-forward behind-0\n"
         "    #     at fetch (r787 S0 pull), zero merge, zero",
         "#     deletion-set EMPTY; delivery window = direct fast-forward behind-0\n"
         "    #     at fetch (r900 seat push), zero merge, zero", 1),
        ("#     --no-verify; self-ack inbox->processed archive ALREADY LANDED\n"
         "    #     pre-freeze -- bm-c interactive-window self-ack archive move (the W192 seat\n"
         "    #     MSG sits in fleet/inbox/processed/ at freeze time, honest\n"
         "    #     archived).",
         "#     --no-verify; self-ack inbox->processed archive PENDING WITH\n"
         "    #     THIS freeze window -- bm-a r901 freeze-closeout archive move\n"
         "    #     (the W193 seat MSG sits in fleet/inbox/ at freeze time,\n"
         "    #     moves to processed/ with this window closeout, honest per\n"
         "    #     frozen prereg sec.0).", 1),
        ("#     ONE HUNDRED-AND-NINETY-SECOND engine wave BY",
         "#     ONE HUNDRED-AND-NINETY-THIRD engine wave BY", 1),
        ("#     MACHINE-DERIVE (engine_owner rows 181 + candidate; gate",
         "#     MACHINE-DERIVE (engine_owner rows 182 + candidate; gate", 1),
        ("#     W1..W191 finalize ALL LANDED (net chain head 833,536,\n"
         "    #     K=418,120 merged pool; W191 finalize one-pass bm-a r895)\n"
         "    #     -- ZERO in-flight upstream seats, clean finalize chain\n"
         "    #     precondition; the finalize merge loop still derives the",
         "#     W1..W191 finalize ALL LANDED (net chain head 833,536,\n"
         "    #     K=418,120 merged pool; W191 finalize one-pass bm-a r895)\n"
         "    #     + W192=bm-c five-face registered (f8703842c) finalize IN\n"
         "    #     FLIGHT upstream seat -- honest annotation per frozen\n"
         "    #     prereg sec.0; the finalize merge loop still derives the", 1),
        ("#     always on. ADMIT receipt results/_r787bmc_w192_probe_receipt.json;",
         "#     always on. ADMIT receipt results/_r900bma_w193_probe_receipt.json;", 1),
        ("#     banned gate ADMIT 0; not a re-pick (R250: W192 bands were",
         "#     banned gate ADMIT 0; not a re-pick (R250: W193 bands were", 1),
        # code: wave pin + mirror cross-checks
        ("    _set_wave(192)", "    _set_wave(193)", 1),
        ('assert WAVE_CONFIGS[191]["a_seed_base"] == pf.N1_BANDS[191]["a"][0], \\',
         'assert WAVE_CONFIGS[192]["a_seed_base"] == pf.N1_BANDS[192]["a"][0], \\', 1),
        ('"W192 A band drift vs law mirror"',
         '"W193 A band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[191]["b_exit_seed_base"] == \\',
         'assert WAVE_CONFIGS[192]["b_exit_seed_base"] == \\', 1),
        ('pf.N1_BANDS[191]["b_exit"][0], "W192 B band drift vs law mirror"',
         'pf.N1_BANDS[192]["b_exit"][0], "W193 B band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[191].get("engine_owner") == \\',
         'assert WAVE_CONFIGS[192].get("engine_owner") == \\', 1),
        ('pf.N1_BANDS[191].get("engine_owner") == "bm-a", \\',
         'pf.N1_BANDS[192].get("engine_owner") == "bm-c", \\', 1),
        ('"W192 engine_owner drift (law mirror parity)"',
         '"W193 engine_owner drift (law mirror parity)"', 1),
        ("w191_a", "w192_a", 8),
        ("w191_b", "w192_b", 8),
        ('"W192 A/B band overlap"', '"W193 A/B band overlap"', 1),
        ('"W192 hits SEED_REGISTRY"', '"W193 hits SEED_REGISTRY"', 1),
        ('f"W192 {nm} hits v1"', 'f"W193 {nm} hits v1"', 1),
        ('f"W192 {nm} hits W1"', 'f"W193 {nm} hits W1"', 1),
        ('f"W192 {nm} hits probe seeds"', 'f"W193 {nm} hits probe seeds"', 1),
        # prior-wave disjointness + reserved bands
        ("# prior-wave disjointness W2..W191 (single state: all",
         "# prior-wave disjointness W2..W192 (single state: all", 1),
        ("WAVE_CONFIGS if w < 192):", "WAVE_CONFIGS if w < 193):", 2),
        ('f"W192 A hits W{wprev}"', 'f"W193 A hits W{wprev}"', 1),
        ('f"W192 B hits W{wprev}"', 'f"W193 B hits W{wprev}"', 1),
        ("n3r1_used191", "n3r1_used192", 3),
        ('"W192 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
         '"W193 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
        ('"W192 bands must clear the lfc actual draw range"',
         '"W193 bands must clear the lfc actual draw range"', 1),
        ('"W192 bands must clear the options_wave2 actual draw range"',
         '"W193 bands must clear the options_wave2 actual draw range"', 1),
        # band facts comment
        ("# band facts (law sec.4 W192 row, r795): A = FIRST-CLEAN past",
         "# band facts (law sec.4 W193 row, r795): A = FIRST-CLEAN past", 1),
        ("# the registered W191 B band (the arithmetic continuation",
         "# the registered W192 B band (the arithmetic continuation", 1),
        ("# 437_004..439_003 is REFUSED at its own start by the W191",
         "# 439_204..441_203 is REFUSED at its own start by the W192", 1),
        ("# B band 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection +\n"
         "        # r892 probe leg4 + r787 probe leg1 succession projection notes",
         "# B band 439_204..439_403, exactly as the W192 prereg sec5.5 +\n"
         "        # bm-c r787 probe leg4 succession projection notes", 1),
        ("# 437_204..439_203; A base == prior-wave B tail+1 (437_203+1)",
         "# 439_404..441_403; A base == prior-wave B tail+1 (439_403+1)", 1),
        ("# machine-checkable -- A-hops-prior-B staircase FIFTY-SECOND",
         "# machine-checkable -- A-hops-prior-B staircase FIFTY-THIRD", 1),
        ("# continuation 437_204..437_403 is CLEAN on the registered",
         "# continuation 439_404..439_603 is CLEAN on the registered", 1),
        ("# universe but lands INSIDE the W192 A band window --",
         "# universe but lands INSIDE the W193 A band window --", 1),
        ("# 439_204 and lands 439_204..439_403, hops=1, non-rotational",
         "# 441_404 and lands 441_404..441_603, hops=1, non-rotational", 1),
        ("# (439_203+1) machine-checkable; cross-window convergence",
         "# (441_403+1) machine-checkable; cross-window convergence", 1),
        ("# with the W191 seat W192+ projection + r892 probe leg4 + r787",
         "# with the W192 prereg sec5.5 + bm-c r787 probe leg4", 1),
        ("# honored (post-W191 universe re-derive + own-wave A",
         "# honored (post-W192 universe re-derive + own-wave A", 1),
        ("# reservation when deriving B); seat MSG-2351 tail,",
         "# reservation when deriving B); seat MSG-0458 tail,", 1),
        # band facts asserts
        ('assert WAVE_CONFIGS[192]["a_seed_base"] == 437_204 == 437_203 + 1, (',
         'assert WAVE_CONFIGS[193]["a_seed_base"] == 439_404 == 439_403 + 1, (', 1),
        ('"W192 A must be the first-clean window past the registered "',
         '"W193 A must be the first-clean window past the registered "', 1),
        ('"W191 B band tail 437_203+1 (arithmetic continuation "',
         '"W192 B band tail 439_403+1 (arithmetic continuation "', 1),
        ('"437_004..439_003 REFUSED at its own start by the W191 B "',
         '"439_204..441_203 REFUSED at its own start by the W192 B "', 1),
        ('"band 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection + "',
         '"band 439_204..439_403, exactly as the W192 prereg sec5.5 + "', 1),
        ('"r892 probe leg4 + r787 probe leg1 succession projection notes "',
         '"bm-c r787 probe leg4 succession projection notes "', 1),
        ('"staircase FIFTY-SECOND instance, E36 card)")',
         '"staircase FIFTY-THIRD instance, E36 card)")', 1),
        ("arith_a191 = set(range(437_204, 439_204))",
         "arith_a192 = set(range(439_404, 441_404))", 1),
        ("assert not (arith_a190 & reg_ints), \\",
         "assert not (arith_a192 & reg_ints), \\", 1),
        ('"W192 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
         '"W193 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
        ('assert WAVE_CONFIGS[192]["b_exit_seed_base"] == 439_204 == 439_203 + 1, (',
         'assert WAVE_CONFIGS[193]["b_exit_seed_base"] == 441_404 == 441_403 + 1, (', 1),
        ('"W192 B must be the first-clean window past the own-wave A "',
         '"W193 B must be the first-clean window past the own-wave A "', 1),
        ('"band tail 439_203+1 (arithmetic continuation "',
         '"band tail 441_403+1 (arithmetic continuation "', 1),
        ('"437_204..437_403 CLEAN on the registered universe but "',
         '"439_404..439_603 CLEAN on the registered universe but "', 1),
        ('"lands INSIDE the W192 A band window; same-freeze mutual "',
         '"lands INSIDE the W193 A band window; same-freeze mutual "', 1),
        ('"own-wave A window reserved jumps to 439_204, first-clean "',
         '"own-wave A window reserved jumps to 441_404, first-clean "', 1),
        ("arith_b191 = set(range(439_204, 439_404))",
         "arith_b192 = set(range(441_404, 441_604))", 1),
        ("assert not (arith_b190 & reg_ints), \\",
         "assert not (arith_b192 & reg_ints), \\", 1),
        ('"W192 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
         '"W193 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
        ("assert not (arith_b190 & arith_a190), \\",
         "assert not (arith_b192 & arith_a192), \\", 1),
        ('"W192 A/B same-freeze mutual exclusion (B hops past own A)"',
         '"W193 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
        # entry identity + paths
        ('("PERPETUAL-N1-W192-SHARD-0",', '("PERPETUAL-N1-W193-SHARD-0",', 1),
        ('"n1w192-0of12"), "W192 entry identity"',
         '"n1w193-0of12"), "W193 entry identity"', 1),
        ('("PERPETUAL-N1-W192-SHARD-11",', '("PERPETUAL-N1-W193-SHARD-11",', 1),
        ('"n1w192-11of12")', '"n1w193-11of12")', 1),
        ('assert SHARD_DIR.endswith("n1_w192") and OUT.endswith(',
         'assert SHARD_DIR.endswith("n1_w193") and OUT.endswith(', 1),
        ('"n1_w192_results.json"), "W192 path drift"',
         '"n1_w193_results.json"), "W193 path drift"', 1),
        ('f"W192 shard dir collides with W{wprev}"',
         'f"W193 shard dir collides with W{wprev}"', 1),
        # finalize cumulative deps (range UNCHANGED: W192 output in-flight)
        ("# W192 finalize cumulative deps: W17..W191 outputs ALL PRESENT",
         "# W193 finalize cumulative deps: W17..W191 outputs ALL PRESENT", 1),
        ("# (landed net chain head 833,536 = W191 bm-a r895 one-pass --\n"
         "        # ZERO in-flight upstream seats, clean precondition freeze\n"
         "        # window; the finalize merge loop derives the wave set from\n"
         "        # registry keys at run time and stays FAIL-CLOSED, r307\n"
         "        # two-state law).",
         "# (landed net chain head 833,536 = W191 bm-a r895 one-pass)\n"
         "        # + W192=bm-c five-face registered (f8703842c) finalize IN\n"
         "        # FLIGHT upstream seat -- honest annotation per frozen\n"
         "        # prereg sec.0; W193 finalize key-order precondition checks\n"
         "        # the W192 output at run time; the finalize merge loop\n"
         "        # derives the wave set from registry keys at run time and\n"
         "        # stays FAIL-CLOSED, r307 two-state law).", 1),
        ('f"W192 finalize cumulative dep (W{_depw} output) missing"',
         'f"W193 finalize cumulative dep (W{_depw} output) missing"', 1),
        # prior-wave set derivation + prereg presence
        ("# registered wave below 192 composes; wave 15 excluded by",
         "# registered wave below 193 composes; wave 15 excluded by", 1),
        ("# design; SINGLE STATE (W2..W191 all registered -- no",
         "# design; SINGLE STATE (W2..W192 all registered -- no", 1),
        ("assert sorted(w for w in WAVE_CONFIGS if w < 192) == \\",
         "assert sorted(w for w in WAVE_CONFIGS if w < 193) == \\", 1),
        ("[w for w in range(16, 192)], \\", "[w for w in range(16, 193)], \\", 1),
        ('"W192 prior-wave set must derive from registry keys (no 15; " \\',
         '"W193 prior-wave set must derive from registry keys (no 15; " \\', 1),
        ('"W2..W191 registered single state)"',
         '"W2..W192 registered single state)"', 1),
        ('"research", "PERPETUAL_N1_W192_PREREG.md")), \\',
         '"research", "PERPETUAL_N1_W193_PREREG.md")), \\', 1),
        ('"W192 per-wave prereg missing (materializer requirement)"',
         '"W193 per-wave prereg missing (materializer requirement)"', 1),
    ]
    for k, (old, new, cnt) in enumerate(R):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat193 = m

    # ---- G6 roll WAVE_CONFIGS row ----
    c = cfg192
    RC = [
        ('192: {"batch": "PERPETUAL-N1-W192",',
         '193: {"batch": "PERPETUAL-N1-W193",', 1),
        ('"research/PERPETUAL_N1_W192_PREREG.md (wave-level frozen "',
         '"research/PERPETUAL_N1_W193_PREREG.md (wave-level frozen "', 1),
        ('new seed bands only; ONE HUNDRED-AND-NINETY-SECOND ENGINE-OWNED WAVE ',
         'new seed bands only; ONE HUNDRED-AND-NINETY-THIRD ENGINE-OWNED WAVE ', 1),
        ('BY MACHINE-DERIVE (engine_owner rows 181 + candidate), ',
         'BY MACHINE-DERIVE (engine_owner rows 182 + candidate), ', 1),
        ('number law after the REGISTERED W191 row bm-a r894 freeze ',
         'number law after the REGISTERED W192 row bm-c r787 freeze ', 1),
        ('e5e4af81b, SINGLE STATE zero seat gap W2..W191 all ',
         'f8703842c, SINGLE STATE zero seat gap W2..W192 all ', 1),
        ('"head 833,536, merged pool K=418,120; seat published=reserved "',
         '"head 833,536, merged pool K=418,120; W192=bm-c five-face "\n'
         '                                       "registered (f8703842c) finalize IN FLIGHT -- honest in-flight "\n'
         '                                       "upstream seat per frozen prereg sec.0; seat published=reserved "', 1),
        ('MSG-20261008-2351-bmc-w192-seat PUSHED to origin 1abe1a57f ',
         'MSG-2026-10-09-0458-bma-w193-seat PUSHED to origin 9df3078c5 ', 1),
        ('seat MSG only, Git Data API direct-build push zero local commit -- sec.6.1.4 channel; the pre-seat probe script + receipt landed with the W192 prereg freeze commit de1ad11f9 next, interactive-window payload note; the W191 finalize product already on origin since r895, not re-shipped; W146 precedent); ',
         'seat MSG + pre-seat probe script + probe receipt (3-item; the W191 finalize product already on origin since r895, not re-shipped; W146 precedent); ', 1),
        ('at fetch (r787 S0 pull), zero merge, zero ',
         'at fetch (r900 seat push), zero merge, zero ', 1),
        ('engine_owner=bm-c, wave 191: ', 'engine_owner=bm-a, wave 192: ', 1),
        ('A = FIRST-CLEAN past the registered W191 B band (the ',
         'A = FIRST-CLEAN past the registered W192 B band (the ', 1),
        ('arithmetic continuation 437_004..439_003 is REFUSED at its ',
         'arithmetic continuation 439_204..441_203 is REFUSED at its ', 1),
        ('own start by the W191 B band 437_004..437_203, exactly as ',
         'own start by the W192 B band 439_204..439_403, exactly as ', 1),
        ('the W191 prereg sec5.5 + W191 seat W192+ projection + r892 probe leg4 + r787 probe leg1 succession ',
         'the W192 prereg sec5.5 + bm-c r787 probe leg4 succession ', 1),
        ('437_204..439_203; A base == prior-wave B tail+1 ',
         '439_404..441_403; A base == prior-wave B tail+1 ', 1),
        ('machine-checkable = A-hops-prior-B staircase FIFTY-SECOND ',
         'machine-checkable = A-hops-prior-B staircase FIFTY-THIRD ', 1),
        ('arithmetic continuation 437_204..437_403 is CLEAN on the ',
         'arithmetic continuation 439_404..439_603 is CLEAN on the ', 1),
        ('registered universe but lands INSIDE the W192 A band ',
         'registered universe but lands INSIDE the W193 A band ', 1),
        ('jumps to 439_204, first-clean 439_204..439_403 hops=1, ',
         'jumps to 441_404, first-clean 441_404..441_603 hops=1, ', 1),
        ('convergence with the W191 seat W192+ projection + r892 probe leg4 + ',
         'convergence with the W192 prereg sec5.5 + bm-c r787 probe leg4 + ', 1),
        ('r787 probe succession projection notes re-derived -- all ',
         'r900 probe succession projection notes re-derived -- all ', 1),
        ('MANDATORY notes honored (post-W191 universe re-derive + ',
         'MANDATORY notes honored (post-W192 universe re-derive + ', 1),
        ('results/_r787bmc_w192_probe_receipt.json; W193+ projection ',
         'results/_r900bma_w193_probe_receipt.json; W194+ projection ', 1),
        ('per this window gate: A first-clean 439_204..441_203 ',
         'per this window gate: A first-clean 441_404..443_403 ', 1),
        ('CLEAN / B first-clean 439_404..439_603 CLEAN -- naive ',
         'CLEAN / B first-clean 441_604..441_803 CLEAN -- naive ', 1),
        ('W192 B band 439_204..439_403 will refuse the naive ',
         'W193 B band 441_404..441_603 will refuse the naive ', 1),
        ('W193 A window; W193 freezer MUST re-derive on the ',
         'W194 A window; W194 freezer MUST re-derive on the ', 1),
        ('post-W192 universe AND reserve the own-wave A window ',
         'post-W193 universe AND reserve the own-wave A window ', 1),
        ('"merged pool K=418,120) -- ZERO in-flight upstream "\n'
         '                                       "seats, clean finalize chain precondition -- finalize "',
         '"merged pool K=418,120) + W192=bm-c five-face registered "\n'
         '                                       "(f8703842c) finalize IN FLIGHT upstream seat -- honest "\n'
         '                                       "annotation per frozen prereg sec.0 -- finalize "', 1),
        ('"a_seed_base": 437_204,        # law sec.4 W192 A: 437_204..439_203 (FIRST-CLEAN past the registered W191 B band; arithmetic 437_004..439_003 REFUSED at own start by the W191 B band; hops=1; A-hops-prior-B staircase FIFTY-SECOND instance, E36 card; ordinal convergence per r587: W191 prereg sec5.5 prose anticipated fifty-second, r787 receipt machine-read FIFTY-SECOND)',
         '"a_seed_base": 439_404,        # law sec.4 W193 A: 439_404..441_403 (FIRST-CLEAN past the registered W192 B band; arithmetic 439_204..441_203 REFUSED at own start by the W192 B band 439_204..439_403; hops=1; A-hops-prior-B staircase FIFTY-THIRD instance, E36 card; ordinal convergence per r587: W192 prereg sec5.5 prose anticipated fifty-third, r900 receipt machine-read FIFTY-THIRD)', 1),
        ('"b_exit_seed_base": 439_204,   # law sec.4 W192 B: 439_204..439_403 (FIRST-CLEAN past the own-wave A window; arithmetic 437_204..437_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
         '"b_exit_seed_base": 441_404,   # law sec.4 W193 B: 441_404..441_603 (FIRST-CLEAN past the own-wave A window; arithmetic 439_404..439_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
        ('"shard_subdir": "n1_w192", "out_name": "n1_w192_results.json",',
         '"shard_subdir": "n1_w193", "out_name": "n1_w193_results.json",', 1),
        ('"engine_owner": "bm-c"},', '"engine_owner": "bm-a"},', 1),
    ]
    for k, (old, new, cnt) in enumerate(RC):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg193 = c

    # ---- G7 roll pf N1_BANDS row ----
    p = pf192
    RP = [
        ("    # W192 (bm-c r787 freeze, seat MSG-20261008-2351-bmc-w192-seat",
         "    # W193 (bm-a r901 freeze, seat MSG-2026-10-09-0458-bma-w193-seat", 1),
        ("# pushed to origin 1abe1a57f pre-freeze r565 law (r787 pre-freeze",
         "# pushed to origin 9df3078c5 pre-freeze r565 law (r900 seat", 1),
        ("# window; payload = seat MSG only, Git Data API direct-build push",
         "# push; payload = seat MSG + pre-seat probe script + probe receipt", 1),
        ("# zero local commit -- sec.6.1.4 channel; the pre-seat probe\n"
         "    # script + receipt landed with the W192 prereg freeze commit\n"
         "    # de1ad11f9 next, interactive-window payload note; the W191\n"
         "    # finalize product already on origin since r895, not re-shipped,\n"
         "    # W146 same-push precedent);",
         "# (3-item; the W191 finalize product already on origin since r895,\n"
         "    # not re-shipped, W146 same-push precedent);", 1),
        ("# deletion-set EMPTY; delivery window\n"
         "    # = direct fast-forward behind-0 at fetch (r892 pre-seat\n"
         "    # push), zero merge, zero --no-verify; self-ack archive ALREADY\n"
         "    # LANDED pre-freeze -- bm-a r892-closeout-window archive move (the W191\n"
         "    # seat MSG sits in fleet/inbox/processed/ at freeze time, honest\n"
         "    # archived);",
         "# deletion-set EMPTY; delivery window\n"
         "    # = direct fast-forward behind-0 at fetch (r900 seat push),\n"
         "    # zero merge, zero --no-verify; self-ack inbox->processed\n"
         "    # archive PENDING WITH THIS freeze window -- bm-a r901 freeze\n"
         "    # closeout archive move (the W193 seat MSG sits in\n"
         "    # fleet/inbox/ at freeze time, moves to processed/ with this\n"
         "    # window closeout, honest per frozen prereg sec.0);", 1),
        ("# band gate ADMIT results/_r787bmc_w192_probe_receipt.json: A = FIRST-CLEAN",
         "# band gate ADMIT results/_r900bma_w193_probe_receipt.json: A = FIRST-CLEAN", 1),
        ("# past the registered W191 B band (arithmetic continuation",
         "# past the registered W192 B band (arithmetic continuation", 1),
        ("# 437_004..439_003 REFUSED at its own start by the W191 B band",
         "# 439_204..441_203 REFUSED at its own start by the W192 B band", 1),
        ("# 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection + r892 probe",
         "# 439_204..439_403, exactly as the W192 prereg sec5.5 + bm-c r787 probe", 1),
        ("# leg4 + r787 probe leg1 succession projection notes all anticipated;",
         "# leg4 succession projection notes all anticipated;", 1),
        ("# honest forward walk hops=1 -> 437_204..439_203, non-rotational",
         "# honest forward walk hops=1 -> 439_404..441_403, non-rotational", 1),
        ("# (437_203+1) machine-checkable -- A-hops-prior-B staircase",
         "# (439_403+1) machine-checkable -- A-hops-prior-B staircase", 1),
        ("# FIFTY-SECOND instance, E36 card);",
         "# FIFTY-THIRD instance, E36 card);", 1),
        ("# continuation 437_204..437_403 CLEAN on the registered universe",
         "# continuation 439_404..439_603 CLEAN on the registered universe", 1),
        ("# but lands INSIDE the W192 A band window -- same-freeze mutual",
         "# but lands INSIDE the W193 A band window -- same-freeze mutual", 1),
        ("# own-wave A window reserved jumps to 439_204 -> 439_204..439_403,",
         "# own-wave A window reserved jumps to 441_404 -> 441_404..441_603,", 1),
        ("# own-wave A tail+1 (439_203+1) machine-checkable);",
         "# own-wave A tail+1 (441_403+1) machine-checkable);", 1),
        ("# W193+ projection (gate-derived r787): A first-clean",
         "# W194+ projection (gate-derived r900): A first-clean", 1),
        ("# 439_204..441_203 CLEAN hops=0 / B first-clean 439_404..439_603",
         "# 441_404..443_403 CLEAN hops=0 / B first-clean 441_604..441_803", 1),
        ("# registered W192 B band 439_204..439_403 will refuse the naive",
         "# registered W193 B band 441_404..441_603 will refuse the naive", 1),
        ("# W193 A window; W193 freezer MUST re-derive on the post-W192",
         "# W194 A window; W194 freezer MUST re-derive on the post-W193", 1),
        ("# NOT a re-pick (R250: W192 bands were never assigned).",
         "# NOT a re-pick (R250: W193 bands were never assigned).", 1),
        ('192: {"a": (437_204, 439_203), "b_exit": (439_204, 439_403),',
         '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        ('         "engine_owner": "bm-c"},',
         '         "engine_owner": "bm-a"},', 1),
    ]
    for k, (old, new, cnt) in enumerate(RP):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf193 = p

    # ---- G7b roll PASS-claim ----
    q = claim192
    RQ = [
        ('"+ W192 materializer face [same guard set, dep=W17..W191 "',
         '"+ W193 materializer face [same guard set, dep=W17..W191 "', 1),
        ('"W191 bm-a r895 one-pass, K=418,120 merged pool; ZERO "\n'
         '          "in-flight upstream seats), ONE HUNDRED-AND-NINETY-SECOND "',
         '"W191 bm-a r895 one-pass, K=418,120 merged pool) + W192 "\n'
         '          "IN-FLIGHT upstream seat (bm-c five-face registered "\n'
         '          "f8703842c, finalize pending on the bm-c lane, honest "\n'
         '          "annotation per frozen prereg sec.0), ONE HUNDRED-AND-NINETY-THIRD "', 1),
        ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 181 "',
         '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 182 "', 1),
        ("+ candidate) bm-c's thirty-fifth owned claim per ",
         "+ candidate) bm-a's one-hundred-eighth owned claim per ", 1),
        ('"machine-derive (engine_owner==bm-c rows 34 + candidate), "',
         '"machine-derive (engine_owner==bm-a rows 107 + candidate), "', 1),
        ('"A=FIRST-CLEAN past the registered W191 B band (staircase "',
         '"A=FIRST-CLEAN past the registered W192 B band (staircase "', 1),
        ('"FIFTY-SECOND instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
         '"FIFTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
        ('"results/_r787bmc_w192_probe_receipt.json, law sec.4 W192 row, "',
         '"results/_r900bma_w193_probe_receipt.json, law sec.4 W193 row, "', 1),
        ('"r787 bm-c] "', '"r901 bm-a] "', 1),
    ]
    for k, (old, new, cnt) in enumerate(RQ):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim193 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W192 B band citations (439_204..439_403) and the W193
    # arithmetic continuations (439_204..441_203 / 439_404..439_603) are
    # LEGITIMATE content of the W193 fragments -- they are NOT in the
    # stale lists.
    STALE = {
        "mat193": ["1abe1a57f", "MSG-20261008-2351", "r787 S0 pull",
                   "de1ad11f9", "_r787bmc", "FIFTY-SECOND", "437_004",
                   "437_204..439_203", "437_204..437_403",
                   "439_204 == ", "engine_owner==bm-c",
                   "thirty-fifth", "rows 34 + candidate",
                   "ONE HUNDRED-AND-NINETY-SECOND", "W191 seat",
                   "W2..W191 all", "arith_a190", "arith_b190",
                   "w191_a", "w191_b", "n3r1_used191", "bm-c's",
                   "ZERO in-flight upstream"],
        "cfg193": ["1abe1a57f", "MSG-20261008-2351", "de1ad11f9",
                   "_r787bmc", "FIFTY-SECOND", "437_004",
                   "437_204..439_203", "437_204..437_403",
                   "W191 seat", "W2..W191 all",
                   "W193+ projection", "r787 S0 pull",
                   "ZERO in-flight upstream"],
        "pf193": ["1abe1a57f", "MSG-20261008-2351", "de1ad11f9",
                  "_r787bmc", "FIFTY-SECOND", "437_004",
                  "437_204..437_403", "W191 seat",
                  "W193+ projection", "r787 pre-freeze",
                  "gate-derived r787"],
        "claim193": ["_r787bmc", "FIFTY-SECOND", "bm-c's", "thirty-fifth",
                     "rows 34 + candidate", "rows 181 ",
                     "r787 bm-c] ", "W191 B band",
                     "ONE HUNDRED-AND-NINETY-SECOND", "ZERO \"",
                     "merged pool; ZERO"],
    }
    frags = {"mat193": mat193, "cfg193": cfg193, "pf193": pf193,
             "claim193": claim193}
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
    n1_b = n1n.replace(cfg192, cfg192 + "\n" + IND19 + cfg193, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w192_pos = n1_b.find("    # --- W192 materializer face")
    assert w192_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w192_pos)
    assert t141 > w192_pos, "T-141 marker not found after W192 face"
    n1_c = n1_b[:t141] + mat193 + "\n" + n1_b[t141:]
    claim_anchor = claim192 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim192 + "\n" + claim193 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf192, pf192 + "\n" + pf193, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, '192: {"batch": "PERPETUAL-N1-W192",', 1),
        (n1_final, '191: {"batch": "PERPETUAL-N1-W191",', 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, "# --- W192 materializer face", 1),
        (n1_final, "# --- W191 materializer face", 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"r894 bm-a] "', 1),
        (n1_final, '"a_seed_base": 439_404,', 1),
        (n1_final, '"b_exit_seed_base": 441_404,', 1),
        (n1_final, "n1_w193", 4),
        (n1_final, "PERPETUAL_N1_W193_PREREG.md", 2),
        (n1_final, "_set_wave(193)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 193)', 3),
        (n1_final, "range(17, 192):", 2),
        (n1_final, '"W194 A window; W194 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 441_404..443_403 ', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, '192: {"a": (437_204, 439_203), "b_exit": (439_204, 439_403),', 1),
        (pf_final, "# W193 (bm-a r901 freeze", 1),
        (pf_final, "# W192 (bm-c r787 freeze", 1),
        (pf_final, "# W194+ projection (gate-derived r900)", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W194+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 441_404..443_403 CLEAN hops=0 / B first-clean 441_604..441_803",
                   "W194 A window; W194 freezer MUST re-derive on the post-W193"):
        if needle not in pf_final:
            fails.append("pf W194+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[193]; "
         "print(json.dumps({'rows': len(B), 'w193': B.get(193), "
         "'w192': B.get(192), 'w191': B.get(191), "
         "'cfg193': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 191, "row count drift: %s" % post
    assert post["w193"] == {"a": [439404, 441403], "b_exit": [441404, 441603],
                           "engine_owner": "bm-a"}, "W193 row drift: %s" % post
    assert post["w192"] == {"a": [437204, 439203], "b_exit": [439204, 439403],
                           "engine_owner": "bm-c"}, "W192 row damaged: %s" % post
    assert post["w191"] == {"a": [435004, 437003], "b_exit": [437004, 437203],
                            "engine_owner": "bm-a"}, "W191 row damaged: %s" % post
    assert post["cfg193"] == [439404, 441404, "n1_w193",
                              "n1_w193_results.json", "bm-a"], \
        "W193 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[193] row: a=(439404,441403) "
          "b_exit=(441404,441603) engine_owner=bm-a (comment face rolled, "
          "W192 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[193] row: batch=PERPETUAL-N1-W193 "
          "a_seed_base=439_404 b_exit_seed_base=441_404 shard=n1_w193 "
          "out=n1_w193_results.json owner=bm-a")
    print("PASS 3/5 n1 W193 materializer face: %d+%d+%d+%d replacements all "
          "count-asserted; staircase FIFTY-THIRD; prior-wave parity->W192; "
          "deps range(17,192) with W192-in-flight honest note; prereg "
          "presence assert->W193" % (len(R), len(RC), len(RP), len(RQ)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 190->191 rows + AST+py_compile + W192/W191 "
          "byte-intact post-import + stale sweeps clean"
          % SEAT_SHA)
    print("PASS 5/5 summary: W193 = 183rd engine wave, bm-a 108th owned "
          "(rows 182+candidate per receipt leg0); A=439_404..441_403 "
          "hops=1 FIFTY-THIRD staircase; B=441_404..441_603 hops=1 "
          "own-A mutual exclusion; W192 in-flight upstream honest; ADMIT "
          "receipt machine-read; receipt=results/_r901bma_w193_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
