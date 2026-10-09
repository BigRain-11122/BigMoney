# -*- coding: utf-8 -*-
"""r905 bm-a W194 five-face freeze edits (five faces: pf N1_BANDS row +
n1 WAVE_CONFIGS row + n1 materializer face + n1 selftest claim + probe
selfcheck re-derive legs). Direct-author per the r787/r901 physical
chunk-roll machinery: extract current W193 fragments (physical face dumps
results/_r905bma_w194_face_*.txt per r776), roll W193->W194 with
count-asserted replacements, insert ADDITIVELY after the last registered
row; originals byte-identical zero-destroy.

Facts machine-read never transcribed (r587): ADMIT receipt
results/_r902bma_w194_probe_receipt.json (bands A 441604..443603 /
B 443604..443803, hops 1/1, FIFTY-FOURTH staircase, leg0 rows 191 tail
W193 owner_rows 183 bma_rows 108 ordinal 184 bma_ordinal 109 w191_ledger_head
833536, leg2 conflicts 0, leg3 origin vacancy, leg4 W195+ projection A
443604..445603 / B 443804..444003 hops 0/0 B-inside-A). Seat push
5cca13637 (MSG-2026-10-09-0627-bma-w194-seat + probe script + receipt,
3-item, r902). W192=bm-c five-face f8703842c registered, finalize LANDED;
W193=bm-a r901 five-face 5cf0d6175 registered, burn COMPLETE 12/12
(r902), finalize LANDED one-pass r904 (net chain head 838,945,
K=422,520 merged pool, product n1_w193_results.json on origin) -- ZERO
in-flight upstream seats, clean precondition freeze window.

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r560 insert-after-last-registered-row + anti-vanish + before/after
counts; r370 EOL-adaptive anchors; r580/r581/r445 AST + py_compile gate;
r581 multi-line assert messages paren-wrapped; r578 five-segment PASS
prints; r359 count prose from gate machine output; r776 fragment-needle
law (pairs built from the PHYSICAL probe dumps
results/_r905bma_w194_face_*.txt, re-verified against the live files at
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
RCPT = os.path.join(ROOT, "results", "_r902bma_w194_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r905bma_w194_freeze_receipt.json")
SEAT_INBOX = "fleet/inbox/MSG-2026-10-09-0627-bma-w194-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W194_PREREG.md")
SEAT_SHA = "5cca13637"
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
    facts = {"round": 905, "machine": "bm-a", "wave": 194}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    if '194: {"a": (441_604, 443_603)' in pf_probe:
        print("ALREADY APPLIED: W194 pf row present -- abort")
        return 3

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "194: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 194 already on origin"
    assert '193: {"a": (439_404, 441_403)' in origin_pf, "origin W193 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "W194 materializer face" not in origin_n1, "origin n1 W194 face present"
    assert '194: {"batch": "PERPETUAL-N1-W194"' not in origin_n1, \
        "origin n1 W194 cfg row present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    A = r["legs"]["leg1"]["A"]
    B = r["legs"]["leg1"]["B"]
    assert A == [441604, 443603] and B == [443604, 443803], \
        "receipt bands drift: %s %s" % (A, B)
    assert r["legs"]["leg1"]["hops_A"] == 1 and r["legs"]["leg1"]["hops_B"] == 1
    assert r["bands"] == {"A": "441604_443603", "B": "443604_443803"}
    leg0 = r["legs"]["leg0"]
    assert leg0["rows"] == 191 and leg0["tail"] == "W193"
    assert leg0["ordinal"] == 184 and leg0["bma_ordinal"] == 109
    assert leg0["owner_rows"] == 183 and leg0["bma_rows"] == 108
    assert leg0["w191_ledger_head"] == 833536
    assert r["legs"]["leg2"]["conflicts"] == 0
    assert r["legs"]["leg3"]["origin_vacancy"] is True
    leg4 = r["legs"]["leg4"]
    assert leg4["W195p_A"] == "443604..445603" and leg4["W195p_B"] == "443804..444003"
    assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0
    assert leg4["W195p_B_lands_inside_W195p_A"] is True
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 193 and len(N1_BANDS) == 191, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    owned = sum(v for k, v in owners.items() if k)
    assert owners.get("bm-a") == 108 and owners.get("bm-c") == 35 \
        and owned == 183, "owner counts drift: %s" % owners
    assert N1_BANDS[193] == {"a": (439404, 441403), "b_exit": (441404, 441603),
                            "engine_owner": "bm-a"}, "W193 row drift"
    assert N1_BANDS[192] == {"a": (437204, 439203), "b_exit": (439204, 439403),
                            "engine_owner": "bm-c"}, "W192 row drift"
    assert os.path.exists(PREREG), "W194 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT_INBOX)), \
        "seat MSG not in fleet/inbox/ at freeze time (archive-pending state)"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w193_results.json")), \
        "W193 finalize product missing (dep precondition)"
    facts["w192_results_on_disk"] = os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w192_results.json"))
    for f in ("results/_r902bma_w194_probe.py",
              "results/_r902bma_w194_probe_receipt.json"):
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

    # ---- G4 extract W193 chunks (LF face; r776 physical shapes) ----
    def chunk(text, start, end, stag):
        i = text.find(start)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j + len(end)]

    mat193 = chunk(n1n, "    # --- W193 materializer face",
                   "    _set_wave(2)", "mat193")
    assert mat193.rstrip("\n").endswith("_set_wave(2)"), "mat193 tail drift"
    cfg193 = chunk(n1n, '    193: {"batch": "PERPETUAL-N1-W193",',
                   '"engine_owner": "bm-a"},', "cfg193")
    pf193 = chunk(pfn, "    # W193 (bm-a r901 freeze, seat MSG-2026-10-09-0458-bma-w193-seat",
                 '"engine_owner": "bm-a"},', "pf193")
    claim193 = chunk(n1n, '          "+ W193 materializer face [same guard set',
                     '"r901 bm-a] "', "claim193")
    assert n1n.count(cfg193) == 1, "cfg193 not unique"
    assert n1n.count(claim193) == 1, "claim193 not unique"
    assert pfn.count(pf193) == 1, "pf193 not unique"

    # ---- G5 roll materializer block W193 -> W194 ----
    m = mat193
    R = [
        # header comment
        ("# --- W193 materializer face (r901 bm-a freeze, own-series law",
         "# --- W194 materializer face (r905 bm-a freeze, own-series law", 1),
        ("#     one-hundred-eighth owned per machine-derive (engine_owner==bm-a",
         "#     one-hundred-ninth owned per machine-derive (engine_owner==bm-a", 1),
        ("#     rows 107 + candidate); wave 192 = first free number after",
         "#     rows 108 + candidate); wave 193 = first free number after", 1),
        ("#     the REGISTERED W192 row (bm-c r787 freeze f8703842c) --",
         "#     the REGISTERED W193 row (bm-a r901 freeze 5cf0d6175) --", 1),
        ("#     SINGLE STATE zero seat gap (W2..W192 all registered). Seat",
         "#     SINGLE STATE zero seat gap (W2..W193 all registered). Seat", 1),
        ("#     published=reserved MSG-2026-10-09-0458-bma-w193-seat pushed",
         "#     published=reserved MSG-2026-10-09-0627-bma-w194-seat pushed", 1),
        ("#     to origin 9df3078c5 BEFORE this freeze, r565 law (payload",
         "#     to origin 5cca13637 BEFORE this freeze, r565 law (payload", 1),
        ("#     at fetch (r900 seat push), zero merge, zero",
         "#     at fetch (r902 seat push), zero merge, zero", 1),
        ("#     THIS freeze window -- bm-a r901 freeze-closeout archive move",
         "#     THIS freeze window -- bm-a r905 freeze-closeout archive move", 1),
        ("#     (the W193 seat MSG sits in fleet/inbox/ at freeze time,",
         "#     (the W194 seat MSG sits in fleet/inbox/ at freeze time,", 1),
        ("#     ONE HUNDRED-AND-NINETY-THIRD engine wave BY",
         "#     ONE HUNDRED-AND-NINETY-FOURTH engine wave BY", 1),
        ("#     MACHINE-DERIVE (engine_owner rows 182 + candidate; gate",
         "#     MACHINE-DERIVE (engine_owner rows 183 + candidate; gate", 1),
        ("#     W1..W191 finalize ALL LANDED (net chain head 833,536,\n"
         "    #     K=418,120 merged pool; W191 finalize one-pass bm-a r895)\n"
         "    #     + W192=bm-c five-face registered (f8703842c) finalize IN\n"
         "    #     FLIGHT upstream seat -- honest annotation per frozen\n"
         "    #     prereg sec.0; the finalize merge loop still derives the",
         "#     W1..W193 finalize ALL LANDED (net chain head 838,945,\n"
         "    #     K=422,520 merged pool; W193 finalize one-pass bm-a r904)\n"
         "    #     -- ZERO in-flight upstream seats, clean finalize chain\n"
         "    #     precondition; the finalize merge loop still derives the", 1),
        ("#     always on. ADMIT receipt results/_r900bma_w193_probe_receipt.json;",
         "#     always on. ADMIT receipt results/_r902bma_w194_probe_receipt.json;", 1),
        ("#     banned gate ADMIT 0; not a re-pick (R250: W193 bands were",
         "#     banned gate ADMIT 0; not a re-pick (R250: W194 bands were", 1),
        # code: wave pin + mirror cross-checks
        ("    _set_wave(193)", "    _set_wave(194)", 1),
        ('assert WAVE_CONFIGS[192]["a_seed_base"] == pf.N1_BANDS[192]["a"][0], \\',
         'assert WAVE_CONFIGS[193]["a_seed_base"] == pf.N1_BANDS[193]["a"][0], \\', 1),
        ('"W193 A band drift vs law mirror"',
         '"W194 A band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[192]["b_exit_seed_base"] == \\',
         'assert WAVE_CONFIGS[193]["b_exit_seed_base"] == \\', 1),
        ('pf.N1_BANDS[192]["b_exit"][0], "W193 B band drift vs law mirror"',
         'pf.N1_BANDS[193]["b_exit"][0], "W194 B band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[192].get("engine_owner") == \\',
         'assert WAVE_CONFIGS[193].get("engine_owner") == \\', 1),
        ('pf.N1_BANDS[192].get("engine_owner") == "bm-c", \\',
         'pf.N1_BANDS[193].get("engine_owner") == "bm-a", \\', 1),
        ('"W193 engine_owner drift (law mirror parity)"',
         '"W194 engine_owner drift (law mirror parity)"', 1),
        ("w192_a", "w193_a", 8),
        ("w192_b", "w193_b", 8),
        ('"W193 A/B band overlap"', '"W194 A/B band overlap"', 1),
        ('"W193 hits SEED_REGISTRY"', '"W194 hits SEED_REGISTRY"', 1),
        ('f"W193 {nm} hits v1"', 'f"W194 {nm} hits v1"', 1),
        ('f"W193 {nm} hits W1"', 'f"W194 {nm} hits W1"', 1),
        ('f"W193 {nm} hits probe seeds"', 'f"W194 {nm} hits probe seeds"', 1),
        # prior-wave disjointness + reserved bands
        ("# prior-wave disjointness W2..W192 (single state: all",
         "# prior-wave disjointness W2..W193 (single state: all", 1),
        ("WAVE_CONFIGS if w < 193):", "WAVE_CONFIGS if w < 194):", 2),
        ('f"W193 A hits W{wprev}"', 'f"W194 A hits W{wprev}"', 1),
        ('f"W193 B hits W{wprev}"', 'f"W194 B hits W{wprev}"', 1),
        ("n3r1_used192", "n3r1_used193", 3),
        ('"W193 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
         '"W194 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
        ('"W193 bands must clear the lfc actual draw range"',
         '"W194 bands must clear the lfc actual draw range"', 1),
        ('"W193 bands must clear the options_wave2 actual draw range"',
         '"W194 bands must clear the options_wave2 actual draw range"', 1),
        # band facts comment
        ("# band facts (law sec.4 W193 row, r795): A = FIRST-CLEAN past",
         "# band facts (law sec.4 W194 row, r795): A = FIRST-CLEAN past", 1),
        ("# the registered W192 B band (the arithmetic continuation",
         "# the registered W193 B band (the arithmetic continuation", 1),
        ("# 439_204..441_203 is REFUSED at its own start by the W192",
         "# 441_404..443_403 is REFUSED at its own start by the W193", 1),
        ("# B band 439_204..439_403, exactly as the W192 prereg sec5.5 +",
         "# B band 441_404..441_603, exactly as the W193 prereg sec5.5 +", 1),
        ("# bm-c r787 probe leg4 succession projection notes",
         "# bm-a r900 probe leg4 succession projection notes", 1),
        ("# 439_404..441_403; A base == prior-wave B tail+1 (439_403+1)",
         "# 441_604..443_603; A base == prior-wave B tail+1 (441_603+1)", 1),
        ("# machine-checkable -- A-hops-prior-B staircase FIFTY-THIRD",
         "# machine-checkable -- A-hops-prior-B staircase FIFTY-FOURTH", 1),
        ("# continuation 439_404..439_603 is CLEAN on the registered",
         "# continuation 441_604..441_803 is CLEAN on the registered", 1),
        ("# universe but lands INSIDE the W193 A band window --",
         "# universe but lands INSIDE the W194 A band window --", 1),
        ("# 441_404 and lands 441_404..441_603, hops=1, non-rotational",
         "# 443_604 and lands 443_604..443_803, hops=1, non-rotational", 1),
        ("# (441_403+1) machine-checkable; cross-window convergence",
         "# (443_603+1) machine-checkable; cross-window convergence", 1),
        ("# with the W192 prereg sec5.5 + bm-c r787 probe leg4",
         "# with the W193 prereg sec5.5 + bm-a r900 probe leg4", 1),
        ("# honored (post-W192 universe re-derive + own-wave A",
         "# honored (post-W193 universe re-derive + own-wave A", 1),
        ("# reservation when deriving B); seat MSG-0458 tail,",
         "# reservation when deriving B); seat MSG-0627 tail,", 1),
        # band facts asserts
        ('assert WAVE_CONFIGS[193]["a_seed_base"] == 439_404 == 439_403 + 1, (',
         'assert WAVE_CONFIGS[194]["a_seed_base"] == 441_604 == 441_603 + 1, (', 1),
        ('"W193 A must be the first-clean window past the registered "',
         '"W194 A must be the first-clean window past the registered "', 1),
        ('"W192 B band tail 439_403+1 (arithmetic continuation "',
         '"W193 B band tail 441_603+1 (arithmetic continuation "', 1),
        ('"439_204..441_203 REFUSED at its own start by the W192 B "',
         '"441_404..443_403 REFUSED at its own start by the W193 B "', 1),
        ('"band 439_204..439_403, exactly as the W192 prereg sec5.5 + "',
         '"band 441_404..441_603, exactly as the W193 prereg sec5.5 + "', 1),
        ('"bm-c r787 probe leg4 succession projection notes "',
         '"bm-a r900 probe leg4 succession projection notes "', 1),
        ('"staircase FIFTY-THIRD instance, E36 card)")',
         '"staircase FIFTY-FOURTH instance, E36 card)")', 1),
        ("arith_a192 = set(range(439_404, 441_404))",
         "arith_a193 = set(range(441_604, 443_604))", 1),
        ("assert not (arith_a192 & reg_ints), \\",
         "assert not (arith_a193 & reg_ints), \\", 1),
        ('"W193 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
         '"W194 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
        ('assert WAVE_CONFIGS[193]["b_exit_seed_base"] == 441_404 == 441_403 + 1, (',
         'assert WAVE_CONFIGS[194]["b_exit_seed_base"] == 443_604 == 443_603 + 1, (', 1),
        ('"W193 B must be the first-clean window past the own-wave A "',
         '"W194 B must be the first-clean window past the own-wave A "', 1),
        ('"band tail 441_403+1 (arithmetic continuation "',
         '"band tail 443_603+1 (arithmetic continuation "', 1),
        ('"439_404..439_603 CLEAN on the registered universe but "',
         '"441_604..441_803 CLEAN on the registered universe but "', 1),
        ('"lands INSIDE the W193 A band window; same-freeze mutual "',
         '"lands INSIDE the W194 A band window; same-freeze mutual "', 1),
        ('"own-wave A window reserved jumps to 441_404, first-clean "',
         '"own-wave A window reserved jumps to 443_604, first-clean "', 1),
        ("arith_b192 = set(range(441_404, 441_604))",
         "arith_b193 = set(range(443_604, 443_804))", 1),
        ("assert not (arith_b192 & reg_ints), \\",
         "assert not (arith_b193 & reg_ints), \\", 1),
        ('"W193 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
         '"W194 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
        ("assert not (arith_b192 & arith_a192), \\",
         "assert not (arith_b193 & arith_a193), \\", 1),
        ('"W193 A/B same-freeze mutual exclusion (B hops past own A)"',
         '"W194 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
        # entry identity + paths
        ('("PERPETUAL-N1-W193-SHARD-0",', '("PERPETUAL-N1-W194-SHARD-0",', 1),
        ('"n1w193-0of12"), "W193 entry identity"',
         '"n1w194-0of12"), "W194 entry identity"', 1),
        ('("PERPETUAL-N1-W193-SHARD-11",', '("PERPETUAL-N1-W194-SHARD-11",', 1),
        ('"n1w193-11of12")', '"n1w194-11of12")', 1),
        ('assert SHARD_DIR.endswith("n1_w193") and OUT.endswith(',
         'assert SHARD_DIR.endswith("n1_w194") and OUT.endswith(', 1),
        ('"n1_w193_results.json"), "W193 path drift"',
         '"n1_w194_results.json"), "W194 path drift"', 1),
        ('f"W193 shard dir collides with W{wprev}"',
         'f"W194 shard dir collides with W{wprev}"', 1),
        # finalize cumulative deps (all prior waves LANDED -- clean window)
        ("# W193 finalize cumulative deps: W17..W191 outputs ALL PRESENT",
         "# W194 finalize cumulative deps: W17..W193 outputs ALL PRESENT", 1),
        ("# (landed net chain head 833,536 = W191 bm-a r895 one-pass)\n"
         "        # + W192=bm-c five-face registered (f8703842c) finalize IN\n"
         "        # FLIGHT upstream seat -- honest annotation per frozen\n"
         "        # prereg sec.0; W193 finalize key-order precondition checks\n"
         "        # the W192 output at run time; the finalize merge loop\n"
         "        # derives the wave set from registry keys at run time and\n"
         "        # stays FAIL-CLOSED, r307 two-state law).",
         "# (landed net chain head 838,945 = W193 bm-a r904 one-pass)\n"
         "        # -- ZERO in-flight upstream seats, clean precondition\n"
         "        # freeze window; the finalize merge loop derives the wave\n"
         "        # set from registry keys at run time and stays\n"
         "        # FAIL-CLOSED, r307 two-state law).", 1),
        ("for _depw in range(17, 192):", "for _depw in range(17, 194):", 1),
        ('f"W193 finalize cumulative dep (W{_depw} output) missing"',
         'f"W194 finalize cumulative dep (W{_depw} output) missing"', 1),
        # prior-wave set derivation + prereg presence
        ("# registered wave below 193 composes; wave 15 excluded by",
         "# registered wave below 194 composes; wave 15 excluded by", 1),
        ("# design; SINGLE STATE (W2..W192 all registered -- no",
         "# design; SINGLE STATE (W2..W193 all registered -- no", 1),
        ("assert sorted(w for w in WAVE_CONFIGS if w < 193) == \\",
         "assert sorted(w for w in WAVE_CONFIGS if w < 194) == \\", 1),
        ("[w for w in range(16, 193)], \\", "[w for w in range(16, 194)], \\", 1),
        ('"W193 prior-wave set must derive from registry keys (no 15; " \\',
         '"W194 prior-wave set must derive from registry keys (no 15; " \\', 1),
        ('"W2..W192 registered single state)"',
         '"W2..W193 registered single state)"', 1),
        ('"research", "PERPETUAL_N1_W193_PREREG.md")), \\',
         '"research", "PERPETUAL_N1_W194_PREREG.md")), \\', 1),
        ('"W193 per-wave prereg missing (materializer requirement)"',
         '"W194 per-wave prereg missing (materializer requirement)"', 1),
    ]
    for k, (old, new, cnt) in enumerate(R):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat194 = m

    # ---- G6 roll WAVE_CONFIGS row ----
    c = cfg193
    RC = [
        ('193: {"batch": "PERPETUAL-N1-W193",',
         '194: {"batch": "PERPETUAL-N1-W194",', 1),
        ('"research/PERPETUAL_N1_W193_PREREG.md (wave-level frozen "',
         '"research/PERPETUAL_N1_W194_PREREG.md (wave-level frozen "', 1),
        ('new seed bands only; ONE HUNDRED-AND-NINETY-THIRD ENGINE-OWNED WAVE ',
         'new seed bands only; ONE HUNDRED-AND-NINETY-FOURTH ENGINE-OWNED WAVE ', 1),
        ('BY MACHINE-DERIVE (engine_owner rows 182 + candidate), ',
         'BY MACHINE-DERIVE (engine_owner rows 183 + candidate), ', 1),
        ('number law after the REGISTERED W192 row bm-c r787 freeze ',
         'number law after the REGISTERED W193 row bm-a r901 freeze ', 1),
        ('f8703842c, SINGLE STATE zero seat gap W2..W192 all ',
         '5cf0d6175, SINGLE STATE zero seat gap W2..W193 all ', 1),
        ('registered; W191 finalize landed prior-window r895, ledger ',
         'registered; W1..W193 finalize ALL LANDED (W193 bm-a r904 ', 1),
        ('head 833,536, merged pool K=418,120; W192=bm-c five-face ',
         'one-pass, ledger head 838,945, merged pool K=422,520) -- ', 1),
        ('registered (f8703842c) finalize IN FLIGHT -- honest in-flight ',
         'ZERO in-flight upstream seats, clean precondition; ', 1),
        ('upstream seat per frozen prereg sec.0; seat published=reserved ',
         'seat published=reserved ', 1),
        ('MSG-2026-10-09-0458-bma-w193-seat PUSHED to origin 9df3078c5 ',
         'MSG-2026-10-09-0627-bma-w194-seat PUSHED to origin 5cca13637 ', 1),
        ('at fetch (r900 seat push), zero merge, zero ',
         'at fetch (r902 seat push), zero merge, zero ', 1),
        ('engine_owner=bm-a, wave 192: ', 'engine_owner=bm-a, wave 193: ', 1),
        ('"A = FIRST-CLEAN past the registered W192 B band (the "',
         '"A = FIRST-CLEAN past the registered W193 B band (the "', 1),
        ('"arithmetic continuation 439_204..441_203 is REFUSED at its "',
         '"arithmetic continuation 441_404..443_403 is REFUSED at its "', 1),
        ('"own start by the W192 B band 439_204..439_403, exactly as "',
         '"own start by the W193 B band 441_404..441_603, exactly as "', 1),
        ('"the W192 prereg sec5.5 + bm-c r787 probe leg4 succession "',
         '"the W193 prereg sec5.5 + bm-a r900 probe leg4 succession "', 1),
        ('"439_404..441_403; A base == prior-wave B tail+1 "',
         '"441_604..443_603; A base == prior-wave B tail+1 "', 1),
        ('"machine-checkable = A-hops-prior-B staircase FIFTY-THIRD "',
         '"machine-checkable = A-hops-prior-B staircase FIFTY-FOURTH "', 1),
        ('"arithmetic continuation 439_404..439_603 is CLEAN on the "',
         '"arithmetic continuation 441_604..441_803 is CLEAN on the "', 1),
        ('"registered universe but lands INSIDE the W193 A band "',
         '"registered universe but lands INSIDE the W194 A band "', 1),
        ('"jumps to 441_404, first-clean 441_404..441_603 hops=1, "',
         '"jumps to 443_604, first-clean 443_604..443_803 hops=1, "', 1),
        ('"convergence with the W192 prereg sec5.5 + bm-c r787 probe leg4 + "',
         '"convergence with the W193 prereg sec5.5 + bm-a r900 probe leg4 + "', 1),
        ('"r900 probe succession projection notes re-derived -- all "',
         '"r902 probe succession projection notes re-derived -- all "', 1),
        ('"MANDATORY notes honored (post-W192 universe re-derive + "',
         '"MANDATORY notes honored (post-W193 universe re-derive + "', 1),
        ('"results/_r900bma_w193_probe_receipt.json; W194+ projection "',
         '"results/_r902bma_w194_probe_receipt.json; W195+ projection "', 1),
        ('"per this window gate: A first-clean 441_404..443_403 "',
         '"per this window gate: A first-clean 443_604..445_603 "', 1),
        ('"CLEAN / B first-clean 441_604..441_803 CLEAN -- naive "',
         '"CLEAN / B first-clean 443_804..444_003 CLEAN -- naive "', 1),
        ('"W193 B band 441_404..441_603 will refuse the naive "',
         '"W194 B band 443_604..443_803 will refuse the naive "', 1),
        ('"W194 A window; W194 freezer MUST re-derive on the "',
         '"W195 A window; W195 freezer MUST re-derive on the "', 1),
        ('"post-W193 universe AND reserve the own-wave A window "',
         '"post-W194 universe AND reserve the own-wave A window "', 1),
        ('"staircase card); W1..W191 finalize ALL LANDED (W191 "\n'
         '                                       "finalize one-pass bm-a r895, net chain head 833,536, "\n'
         '                                       "merged pool K=418,120) + W192=bm-c five-face registered "\n'
         '                                       "(f8703842c) finalize IN FLIGHT upstream seat -- honest "\n'
         '                                       "annotation per frozen prereg sec.0 -- finalize "',
         '"staircase card); W1..W193 finalize ALL LANDED (W193 "\n'
         '                                       "finalize one-pass bm-a r904, net chain head 838,945, "\n'
         '                                       "merged pool K=422,520) -- ZERO in-flight upstream "\n'
         '                                       "seats, clean finalize chain precondition -- finalize "', 1),
        ('"a_seed_base": 439_404,        # law sec.4 W193 A: 439_404..441_403 (FIRST-CLEAN past the registered W192 B band; arithmetic 439_204..441_203 REFUSED at own start by the W192 B band 439_204..439_403; hops=1; A-hops-prior-B staircase FIFTY-THIRD instance, E36 card; ordinal convergence per r587: W192 prereg sec5.5 prose anticipated fifty-third, r900 receipt machine-read FIFTY-THIRD)',
         '"a_seed_base": 441_604,        # law sec.4 W194 A: 441_604..443_603 (FIRST-CLEAN past the registered W193 B band; arithmetic 441_404..443_403 REFUSED at own start by the W193 B band 441_404..441_603; hops=1; A-hops-prior-B staircase FIFTY-FOURTH instance, E36 card; ordinal convergence per r587: W193 prereg sec5.5 prose anticipated fifty-fourth, r902 receipt machine-read FIFTY-FOURTH)', 1),
        ('"b_exit_seed_base": 441_404,   # law sec.4 W193 B: 441_404..441_603 (FIRST-CLEAN past the own-wave A window; arithmetic 439_404..439_603 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
         '"b_exit_seed_base": 443_604,   # law sec.4 W194 B: 443_604..443_803 (FIRST-CLEAN past the own-wave A window; arithmetic 441_604..441_803 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
        ('"shard_subdir": "n1_w193", "out_name": "n1_w193_results.json",',
         '"shard_subdir": "n1_w194", "out_name": "n1_w194_results.json",', 1),
    ]
    for k, (old, new, cnt) in enumerate(RC):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)
    cfg194 = c

    # ---- G7 roll pf N1_BANDS row ----
    p = pf193
    RP = [
        ("    # W193 (bm-a r901 freeze, seat MSG-2026-10-09-0458-bma-w193-seat",
         "    # W194 (bm-a r905 freeze, seat MSG-2026-10-09-0627-bma-w194-seat", 1),
        ("# pushed to origin 9df3078c5 pre-freeze r565 law (r900 seat",
         "# pushed to origin 5cca13637 pre-freeze r565 law (r902 seat", 1),
        ("# = direct fast-forward behind-0 at fetch (r900 seat push),",
         "# = direct fast-forward behind-0 at fetch (r902 seat push),", 1),
        ("# archive PENDING WITH THIS freeze window -- bm-a r901 freeze",
         "# archive PENDING WITH THIS freeze window -- bm-a r905 freeze", 1),
        ("# closeout archive move (the W193 seat MSG sits in",
         "# closeout archive move (the W194 seat MSG sits in", 1),
        ("# band gate ADMIT results/_r900bma_w193_probe_receipt.json: A = FIRST-CLEAN",
         "# band gate ADMIT results/_r902bma_w194_probe_receipt.json: A = FIRST-CLEAN", 1),
        ("# past the registered W192 B band (arithmetic continuation",
         "# past the registered W193 B band (arithmetic continuation", 1),
        ("# 439_204..441_203 REFUSED at its own start by the W192 B band",
         "# 441_404..443_403 REFUSED at its own start by the W193 B band", 1),
        ("# 439_204..439_403, exactly as the W192 prereg sec5.5 + bm-c r787 probe",
         "# 441_404..441_603, exactly as the W193 prereg sec5.5 + bm-a r900 probe", 1),
        ("# honest forward walk hops=1 -> 439_404..441_403, non-rotational",
         "# honest forward walk hops=1 -> 441_604..443_603, non-rotational", 1),
        ("# (439_403+1) machine-checkable -- A-hops-prior-B staircase",
         "# (441_603+1) machine-checkable -- A-hops-prior-B staircase", 1),
        ("# FIFTY-THIRD instance, E36 card);",
         "# FIFTY-FOURTH instance, E36 card);", 1),
        ("# continuation 439_404..439_603 CLEAN on the registered universe",
         "# continuation 441_604..441_803 CLEAN on the registered universe", 1),
        ("# but lands INSIDE the W193 A band window -- same-freeze mutual",
         "# but lands INSIDE the W194 A band window -- same-freeze mutual", 1),
        ("# own-wave A window reserved jumps to 441_404 -> 441_404..441_603,",
         "# own-wave A window reserved jumps to 443_604 -> 443_604..443_803,", 1),
        ("# own-wave A tail+1 (441_403+1) machine-checkable);",
         "# own-wave A tail+1 (443_603+1) machine-checkable);", 1),
        ("# W194+ projection (gate-derived r900): A first-clean",
         "# W195+ projection (gate-derived r902): A first-clean", 1),
        ("# 441_404..443_403 CLEAN hops=0 / B first-clean 441_604..441_803",
         "# 443_604..445_603 CLEAN hops=0 / B first-clean 443_804..444_003", 1),
        ("# registered W193 B band 441_404..441_603 will refuse the naive",
         "# registered W194 B band 443_604..443_803 will refuse the naive", 1),
        ("# W194 A window; W194 freezer MUST re-derive on the post-W193",
         "# W195 A window; W195 freezer MUST re-derive on the post-W194", 1),
        ("# NOT a re-pick (R250: W193 bands were never assigned).",
         "# NOT a re-pick (R250: W194 bands were never assigned).", 1),
        ('193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),',
         '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
    ]
    for k, (old, new, cnt) in enumerate(RP):
        p = rep(p, old, new, cnt, "pf-%02d" % k)
    pf194 = p

    # ---- G7b roll PASS-claim ----
    q = claim193
    RQ = [
        ('"+ W193 materializer face [same guard set, dep=W17..W191 "',
         '"+ W194 materializer face [same guard set, dep=W17..W193 "', 1),
        ('"outputs ALL PRESENT (landed net chain head 833,536 = "\n'
         '          "W191 bm-a r895 one-pass, K=418,120 merged pool) + W192 "\n'
         '          "IN-FLIGHT upstream seat (bm-c five-face registered "\n'
         '          "f8703842c, finalize pending on the bm-c lane, honest "\n'
         '          "annotation per frozen prereg sec.0), ONE HUNDRED-AND-NINETY-THIRD "',
         '"outputs ALL PRESENT (landed net chain head 838,945 = "\n'
         '          "W193 bm-a r904 one-pass, K=422,520 merged pool) -- ZERO "\n'
         '          "in-flight upstream seats, clean precondition, ONE HUNDRED-AND-NINETY-FOURTH "', 1),
        ('"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 182 "',
         '"ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows 183 "', 1),
        ("+ candidate) bm-a's one-hundred-eighth owned claim per ",
         "+ candidate) bm-a's one-hundred-ninth owned claim per ", 1),
        ('"machine-derive (engine_owner==bm-a rows 107 + candidate), "',
         '"machine-derive (engine_owner==bm-a rows 108 + candidate), "', 1),
        ('"A=FIRST-CLEAN past the registered W192 B band (staircase "',
         '"A=FIRST-CLEAN past the registered W193 B band (staircase "', 1),
        ('"FIFTY-THIRD instance, E36 card, hops=1) + B=FIRST-CLEAN past the "',
         '"FIFTY-FOURTH instance, E36 card, hops=1) + B=FIRST-CLEAN past the "', 1),
        ('"results/_r900bma_w193_probe_receipt.json, law sec.4 W193 row, "',
         '"results/_r902bma_w194_probe_receipt.json, law sec.4 W194 row, "', 1),
        ('"r901 bm-a] "', '"r905 bm-a] "', 1),
    ]
    for k, (old, new, cnt) in enumerate(RQ):
        q = rep(q, old, new, cnt, "claim-%02d" % k)
    claim194 = q

    # ---- G7c stale sweeps on the rolled fragments (r780/r781) ----
    # NOTE: W193 band citations (441_404..441_603 B band; the W194
    # arithmetic continuations 441_404..443_403 / 441_604..441_803) and
    # the seat-payload W191-product note are LEGITIMATE content of the
    # W194 fragments -- they are NOT in the stale lists.
    STALE = {
        "mat194": ["9df3078c5", "MSG-2026-10-09-0458", "r900 seat push",
                   "_r900bma", "FIFTY-THIRD", "439_204",
                   "439_404..441_403", "439_404..439_603",
                   "439_403+1", "441_403+1", '== "bm-c"',
                   "one-hundred-eighth", "rows 107 + candidate",
                   "ONE HUNDRED-AND-NINETY-THIRD", "W2..W192 all",
                   "arith_a192", "arith_b192", "w192_a", "w192_b",
                   "n3r1_used192", "W1..W191 finalize", "833,536",
                   "418,120", "r901 freeze-closeout", "bm-c r787",
                   "post-W192 universe", "MSG-0458 tail",
                   "range(17, 192)", "jumps to 441_404",
                   "n1w193", "n1_w193", "W193-SHARD", "W193 entry",
                   "W193 path drift", "W193 shard dir", "w < 193):",
                   "W2..W192 registered", "PERPETUAL_N1_W193_PREREG",
                   "W193 per-wave prereg", "W193 finalize cumulative dep",
                   "W193 prior-wave set", "disjointness W2..W192",
                   "W193 A/B band", "W193 hits", "W193 bands",
                   "W193 A window must", "W193 B window must",
                   "W193 A/B same-freeze", "W194+ projection",
                   "W193 A band drift", "W193 B band drift",
                   "W193 engine_owner drift"],
        "cfg194": ["9df3078c5", "MSG-2026-10-09-0458", "de1ad11f9",
                   "_r900bma", "FIFTY-THIRD", "439_204",
                   "439_404..441_403", "439_404..439_603",
                   "439_403+1", "441_403+1",
                   "W192 prereg sec5.5", "bm-c r787",
                   "W192=bm-c five-face", "f8703842c) finalize IN FLIGHT",
                   "833,536", "418,120", "ONE HUNDRED-AND-NINETY-THIRD",
                   "W2..W192 all", "W2..W192 registered",
                   "engine_owner rows 182", "r900 seat push",
                   "W194+ projection", "A first-clean 441_404..443_403",
                   "B first-clean 441_604..441_803",
                   "wave 192: ", "439_404,", "441_404,   #",
                   "n1_w193", "W193-SHARD", "r901 freeze-closeout",
                   "post-W192 universe", "W192 B band 439",
                   "W191 finalize landed prior-window"],
        "pf194": ["9df3078c5", "MSG-2026-10-09-0458", "_r900bma",
                  "FIFTY-THIRD", "439_204", "439_404..441_403",
                  "439_404..439_603", "439_403+1", "441_403+1",
                  "W194+ projection", "r900 seat", "gate-derived r900",
                  "bm-c r787", "W192 prereg sec5.5", "r901 freeze",
                  "the W193 seat MSG", "W192 B band",
                  "W193 A band window", "jumps to 441_404",
                  "W194 freezer", "post-W193 universe AND"],
        "claim194": ["_r900bma", "FIFTY-THIRD", "one-hundred-eighth",
                     "rows 107 + candidate", "rows 182 ",
                     "r901 bm-a] ", "W192 B band",
                     "ONE HUNDRED-AND-NINETY-THIRD",
                     "833,536", "418,120", "836,745",
                     "IN-FLIGHT upstream seat", "bm-c five-face",
                     "dep=W17..W191"],
    }
    frags = {"mat194": mat194, "cfg194": cfg194, "pf194": pf194,
             "claim194": claim194}
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
    n1_b = n1n.replace(cfg193, cfg193 + "\n" + IND19 + cfg194, 1)
    if n1_b == n1n:
        fails.append("cfg insertion no-op")
        print("RESULT: FAIL -- cfg insertion no-op")
        return 1
    w193_pos = n1_b.find("    # --- W193 materializer face")
    assert w193_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w193_pos)
    assert t141 > w193_pos, "T-141 marker not found after W193 face"
    n1_c = n1_b[:t141] + mat194 + "\n" + n1_b[t141:]
    claim_anchor = claim193 + '\n          "+ T-141 s2 "'
    assert n1_c.count(claim_anchor) == 1, "claim anchor not unique"
    n1_final = n1_c.replace(claim_anchor,
                            claim193 + "\n" + claim194 +
                            '\n          "+ T-141 s2 "', 1)
    pf_final = pfn.replace(pf193, pf193 + "\n" + pf194, 1)
    if pf_final == pfn:
        fails.append("pf insertion no-op")

    # ---- G9 presence + anti-vanish + malformed scans (r560/r819) ----
    checks = [
        (n1_final, '194: {"batch": "PERPETUAL-N1-W194",', 1),
        (n1_final, '193: {"batch": "PERPETUAL-N1-W193",', 1),
        (n1_final, '192: {"batch": "PERPETUAL-N1-W192",', 1),
        (n1_final, "# --- W194 materializer face", 1),
        (n1_final, "# --- W193 materializer face", 1),
        (n1_final, "# --- W192 materializer face", 1),
        (n1_final, '"r905 bm-a] "', 1),
        (n1_final, '"r901 bm-a] "', 1),
        (n1_final, '"r787 bm-c] "', 1),
        (n1_final, '"a_seed_base": 441_604,', 1),
        (n1_final, '"b_exit_seed_base": 443_604,', 1),
        (n1_final, "n1_w194", 4),
        (n1_final, "PERPETUAL_N1_W194_PREREG.md", 2),
        (n1_final, "_set_wave(194)", 1),
        (n1_final, 'sorted(w for w in WAVE_CONFIGS if w < 194)', 3),
        (n1_final, "range(17, 194):", 1),
        (n1_final, '"W195 A window; W195 freezer MUST re-derive on the "', 1),
        (n1_final, 'A first-clean 443_604..445_603 ', 1),
        (pf_final, '194: {"a": (441_604, 443_603), "b_exit": (443_604, 443_803),', 1),
        (pf_final, '193: {"a": (439_404, 441_403), "b_exit": (441_404, 441_603),', 1),
        (pf_final, "# W194 (bm-a r905 freeze", 1),
        (pf_final, "# W193 (bm-a r901 freeze", 1),
        (pf_final, "# W195+ projection (gate-derived r902)", 1),
    ]
    for src, needle, cnt in checks:
        got = src.count(needle)
        if got != cnt:
            fails.append("post-edit needle %r count %d != %d"
                         % (needle[:50], got, cnt))
    # W195+ projection prose present (probe leg4 verbatim, r587)
    for needle in ("# 443_604..445_603 CLEAN hops=0 / B first-clean 443_804..444_003",
                   "W195 A window; W195 freezer MUST re-derive on the post-W194"):
        if needle not in pf_final:
            fails.append("pf W195+ prose missing: %r" % needle[:60])
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
         "cfg = n1.WAVE_CONFIGS[194]; "
         "print(json.dumps({'rows': len(B), 'w194': B.get(194), "
         "'w193': B.get(193), 'w192': B.get(192), "
         "'cfg194': [cfg['a_seed_base'], cfg['b_exit_seed_base'], "
         "cfg['shard_subdir'], cfg['out_name'], cfg['engine_owner']]}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 192, "row count drift: %s" % post
    assert post["w194"] == {"a": [441604, 443603], "b_exit": [443604, 443803],
                           "engine_owner": "bm-a"}, "W194 row drift: %s" % post
    assert post["w193"] == {"a": [439404, 441403], "b_exit": [441404, 441603],
                           "engine_owner": "bm-a"}, "W193 row damaged: %s" % post
    assert post["w192"] == {"a": [437204, 439203], "b_exit": [439204, 439403],
                            "engine_owner": "bm-c"}, "W192 row damaged: %s" % post
    assert post["cfg194"] == [441604, 443604, "n1_w194",
                              "n1_w194_results.json", "bm-a"], \
        "W194 WAVE_CONFIGS drift: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[194] row: a=(441604,443603) "
          "b_exit=(443604,443803) engine_owner=bm-a (comment face rolled, "
          "W193 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[194] row: batch=PERPETUAL-N1-W194 "
          "a_seed_base=441_604 b_exit_seed_base=443_604 shard=n1_w194 "
          "out=n1_w194_results.json owner=bm-a")
    print("PASS 3/5 n1 W194 materializer face: %d+%d+%d+%d replacements all "
          "count-asserted; staircase FIFTY-FOURTH; prior-wave parity->W193; "
          "deps range(17,194) all-landed clean; prereg "
          "presence assert->W194" % (len(R), len(RC), len(RP), len(RQ)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha %s "
          "ancestor + registry 191->192 rows + AST+py_compile + W193/W192 "
          "byte-intact post-import + stale sweeps clean"
          % SEAT_SHA)
    print("PASS 5/5 summary: W194 = 184th engine wave, bm-a 109th owned "
          "(rows 183+candidate per receipt leg0); A=441_604..443_603 "
          "hops=1 FIFTY-FOURTH staircase; B=443_604..443_803 hops=1 "
          "own-A mutual exclusion; ZERO in-flight upstream (W193 "
          "finalize landed r904, head 838,945 K 422,520); ADMIT "
          "receipt machine-read; receipt=results/_r905bma_w194_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
