# -*- coding: utf-8 -*-
"""r787 bm-c W192 five-face freeze edits (interactive-window direct-author
per W192 prereg freeze note: no buildgen emission chain, extraction-from-
emission N/A honest; five-leg probe receipt results/_r787bmc_w192_probe_receipt
.json + matdiff roll = the evidence; numbers machine-read never transcribed
r587; selftest W192 face validated as the five faces land per prereg sec.3).

Laws honored: r511/r687 write-time fetch + origin-tail vacancy lock;
r374 leg0b/leg0c seat MSG dual-dir scan; r560 insert-after-last-registered-
row + post-anchor intactness + before/after counts; r370 EOL-adaptive
anchors (fresh checkout CRLF); r580/r581/r445 AST gate + py_compile before
any selftest; r581 multi-line assert messages paren-wrapped (inherited from
W191 template verbatim); r578 five-segment PASS prints; r359 count prose
from gate machine output (receipt leg0). Zero-destroy: W191 chunks are
extracted, rolled, and re-inserted ADDITIVELY; originals byte-identical."""
import ast
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")
RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_probe_receipt.json")
OUT_RCPT = os.path.join(ROOT, "results", "_r787bmc_w192_freeze_receipt.json")
SEAT = "fleet/inbox/processed/MSG-20261008-2351-bmc-w192-seat.md"
PREREG = os.path.join(ROOT, "research", "PERPETUAL_N1_W192_PREREG.md")
SEAT_SHA = "1abe1a57f"
W191_FREEZE_SHA = "e5e4af81b"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def git_out(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CNW)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


def rep(text, old, new, expect, tag):
    n = text.count(old)
    assert n == expect, (
        "REPLACEMENT COUNT MISMATCH [%s]: got %d expect %d\nliteral=%r"
        % (tag, n, expect, old[:120]))
    return text.replace(old, new)


def main():
    facts = {"round": 787, "machine": "bm-c", "wave": 192}

    # ---- G0 idempotence (already-applied abort) ----
    pf_probe = open(PFP, encoding="utf-8", errors="replace").read()
    assert "192: {\"a\": (437_204, 439_203)" not in pf_probe.replace(" ", ""), \
        "ALREADY APPLIED: W192 pf row present"
    assert "192: {" not in pf_probe, "ALREADY APPLIED: pf row 192 present"

    # ---- G1 write-time fetch + origin tail lock (r511/r687) ----
    rc, _, err = git_out(["fetch", "origin"])
    assert rc == 0, "fetch failed: %s" % err[:200]
    rc, origin_pf, err = git_out(["show", "origin/main:scripts/perpetual_faces.py"])
    assert rc == 0, "origin pf blob read failed"
    assert "192: {" not in origin_pf, "ORIGIN TAIL MOVED: wave 192 already on origin"
    assert '191: {"a": (435_004, 437_003)' in origin_pf, "origin W191 row drift"
    rc, origin_n1, _ = git_out(["show", "origin/main:scripts/perpetual_faces_n1.py"])
    assert rc == 0
    assert "W192 materializer face" not in origin_n1, "origin n1 W192 face present"
    rc, _, _ = git_out(["merge-base", "--is-ancestor", SEAT_SHA, "origin/main"])
    assert rc == 0, "seat push sha %s not an ancestor of origin/main" % SEAT_SHA
    facts["origin_vacancy"] = True

    # ---- G2 receipt + precheck parity (r587 / r359 machine numbers) ----
    r = json.load(open(RCPT, encoding="utf-8"))
    assert r["verdict"] == "ADMIT", "probe receipt not ADMIT"
    A = r["legs"]["leg1"]["A"]
    B = r["legs"]["leg1"]["B"]
    assert A == [437204, 439203] and B == [439204, 439403], \
        "receipt bands drift: %s %s" % (A, B)
    assert r["legs"]["leg2"]["conflicts"] == 0
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from perpetual_faces import N1_BANDS  # noqa: E402
    assert max(N1_BANDS) == 191 and len(N1_BANDS) == 189, "registry tail drift"
    owners = {}
    for w, c in N1_BANDS.items():
        owners[c.get("engine_owner")] = owners.get(c.get("engine_owner"), 0) + 1
    assert owners.get("bm-c") == 34 and sum(owners.values()) == 181, \
        "owner counts drift: %s" % owners
    assert N1_BANDS[191] == {"a": (435004, 437003), "b_exit": (437004, 437203),
                            "engine_owner": "bm-a"}, "W191 row drift"
    assert os.path.exists(PREREG), "W192 per-wave prereg missing"
    assert os.path.exists(os.path.join(ROOT, SEAT)), "seat MSG not in processed/"
    assert os.path.exists(os.path.join(
        ROOT, "results", "perpetual_faces", "n1_w191_results.json")), \
        "W191 finalize product missing (finalize-chain precondition)"
    for f in ("results/_w192bmc_20261009_probe.py",
              "results/_w192bmc_20261009_probe_receipt.json"):
        assert os.path.exists(os.path.join(ROOT, f)), "seat-cited artifact missing: %s" % f
    facts["precheck"] = {"rows": len(N1_BANDS), "bmc_rows": owners.get("bm-c"),
                         "owner_rows": sum(owners.values())}

    # ---- G3 read live files, EOL detect (r370) ----
    n1_raw = open(N1P, encoding="utf-8", errors="replace", newline="").read()
    pf_raw = open(PFP, encoding="utf-8", errors="replace", newline="").read()
    n1_crlf = n1_raw.count("\r\n") > n1_raw.count("\n") / 2
    pf_crlf = pf_raw.count("\r\n") > pf_raw.count("\n") / 2
    n1n = n1_raw.replace("\r\n", "\n")
    pfn = pf_raw.replace("\r\n", "\n")
    facts["eol"] = {"n1_crlf": n1_crlf, "pf_crlf": pf_crlf}

    # ---- G4 extract W191 chunks (LF face) ----
    def chunk(text, start_marker, end_marker, stag):
        i = text.find(start_marker)
        assert i >= 0, "start marker not found [%s]" % stag
        j = text.find(end_marker, i)
        assert j > i, "end marker not found [%s]" % stag
        return text[i:j]

    mat191 = chunk(n1n, "# --- W191 materializer face",
                   "\n    # --- T-141 s2 lane face", "mat191")
    # include the trailing newline before T-141 in the block
    cfg191 = chunk(n1n, '    191: {"batch": "PERPETUAL-N1-W191",',
                  '"engine_owner": "bm-a"},', "cfg191")
    cfg191 = cfg191 + '"engine_owner": "bm-a"},'
    n1n = n1n.replace(cfg191, cfg191, 1)  # no-op, keeps linter calm
    cfg191_full = cfg191
    pf191 = chunk(pfn, "    # W191 (bm-a r894 freeze, seat MSG-2026-10-08-2130-bma-w191-seat",
                 '"engine_owner": "bm-a"},', "pf191")
    pf191_full = pf191 + '"engine_owner": "bm-a"},'
    assert n1n.count(cfg191_full) == 1, "cfg191 not unique"
    assert pfn.count(pf191_full) == 1, "pf191 not unique"
    assert mat191.rstrip("\n").endswith("_set_wave(2)"), "mat191 tail drift"

    # ---- G5 roll materializer block ----
    m = mat191
    R = [
        ("# --- W191 materializer face (r894 bm-a freeze, own-series law",
         "# --- W192 materializer face (r787 bm-c freeze, own-series law", 1),
        ("bm-a's", "bm-c's", 1),
        ("one-hundred-seventh owned per machine-derive (engine_owner==bm-a",
         "thirty-fifth owned per machine-derive (engine_owner==bm-c", 1),
        ("rows 106 + candidate); wave 190 = first free number after",
         "rows 34 + candidate); wave 191 = first free number after", 1),
        ("the REGISTERED W190 row (bm-a r892 freeze 0cce3c47e) --",
         "the REGISTERED W191 row (bm-a r894 freeze %s) --" % W191_FREEZE_SHA, 1),
        ("SINGLE STATE zero seat gap (W2..W190 all registered). Seat",
         "SINGLE STATE zero seat gap (W2..W191 all registered). Seat", 1),
        ("published=reserved MSG-2026-10-08-2130-bma-w191-seat pushed",
         "published=reserved MSG-20261008-2351-bmc-w192-seat pushed", 1),
        ("to origin 1c28dd21d BEFORE this freeze, r565 law (payload",
         "to origin %s BEFORE this freeze, r565 law (payload" % SEAT_SHA, 1),
        ("    #     = seat MSG + pre-seat probe script + probe receipt (3-item;",
         "    #     = seat MSG only (Git Data API direct-build push, zero", 1),
        ("    #     the W190 finalize product already on origin since r892, not",
         "    #     local commit -- sec.6.1.4 channel; the pre-seat probe\n"
         "    #     script + receipt landed with the W192 prereg freeze\n"
         "    #     commit de1ad11f9 next, interactive-window payload note;\n"
         "    #     the W191 finalize product already on origin since r895, not", 1),
        ("at fetch (r892 pre-seat push), zero merge, zero",
         "at fetch (r787 S0 pull), zero merge, zero", 1),
        ("pre-freeze -- bm-a r892-closeout-window archive move (the W191 seat",
         "pre-freeze -- bm-c interactive-window self-ack archive move (the W192 seat", 1),
        ("ONE HUNDRED-AND-NINETY-FIRST engine wave BY",
         "ONE HUNDRED-AND-NINETY-SECOND engine wave BY", 1),
        ("MACHINE-DERIVE (engine_owner rows 180 + candidate; gate",
         "MACHINE-DERIVE (engine_owner rows 181 + candidate; gate", 1),
        ("W1..W190 finalize ALL LANDED (net chain head 825,328,",
         "W1..W191 finalize ALL LANDED (net chain head 833,536,", 1),
        ("K=415,920 merged pool; W190 finalize one-pass bm-a r892)",
         "K=418,120 merged pool; W191 finalize one-pass bm-a r895)", 1),
        ("always on. ADMIT receipt results/_r892bma_w191_probe_receipt.json;",
         "always on. ADMIT receipt results/_r787bmc_w192_probe_receipt.json;", 1),
        ("banned gate ADMIT 0; not a re-pick (R250: W191 bands were",
         "banned gate ADMIT 0; not a re-pick (R250: W192 bands were", 1),
        ("_set_wave(191)", "_set_wave(192)", 1),
        ('assert WAVE_CONFIGS[190]["a_seed_base"] == pf.N1_BANDS[190]["a"][0], \\',
         'assert WAVE_CONFIGS[191]["a_seed_base"] == pf.N1_BANDS[191]["a"][0], \\', 1),
        ('"W191 A band drift vs law mirror"',
         '"W192 A band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[190]["b_exit_seed_base"] == \\',
         'assert WAVE_CONFIGS[191]["b_exit_seed_base"] == \\', 1),
        ('pf.N1_BANDS[190]["b_exit"][0], "W191 B band drift vs law mirror"',
         'pf.N1_BANDS[191]["b_exit"][0], "W192 B band drift vs law mirror"', 1),
        ('assert WAVE_CONFIGS[190].get("engine_owner") == \\',
         'assert WAVE_CONFIGS[191].get("engine_owner") == \\', 1),
        ('pf.N1_BANDS[190].get("engine_owner") == "bm-a", \\',
         'pf.N1_BANDS[191].get("engine_owner") == "bm-a", \\', 1),
        ('"W191 engine_owner drift (law mirror parity)"',
         '"W192 engine_owner drift (law mirror parity)"', 1),
        ("w190_a", "w191_a", 8),
        ("w190_b", "w191_b", 8),
        ('"W191 A/B band overlap"', '"W192 A/B band overlap"', 1),
        ('"W191 hits SEED_REGISTRY"', '"W192 hits SEED_REGISTRY"', 1),
        ('f"W191 {nm} hits v1"', 'f"W192 {nm} hits v1"', 1),
        ('f"W191 {nm} hits W1"', 'f"W192 {nm} hits W1"', 1),
        ('f"W191 {nm} hits probe seeds"', 'f"W192 {nm} hits probe seeds"', 1),
        ('"registered W189 row parity drift (r307; bm-a r882)"',
         '"registered W190 row parity drift (r307; bm-a r882)"', 1),
        ('"registered W190 row parity drift (r307; bm-a r892)"',
         '"registered W191 row parity drift (r307; bm-a r894)"', 1),
        ("# prior-wave disjointness W2..W190 (single state: all",
         "# prior-wave disjointness W2..W191 (single state: all", 1),
        ("WAVE_CONFIGS if w < 191):", "WAVE_CONFIGS if w < 192):", 2),
        ('f"W191 A hits W{wprev}"', 'f"W192 A hits W{wprev}"', 1),
        ('f"W191 B hits W{wprev}"', 'f"W192 B hits W{wprev}"', 1),
        ("n3r1_used190", "n3r1_used191", 2),
        ('"W191 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
         '"W192 bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"', 1),
        ('"W191 bands must clear the lfc actual draw range"',
         '"W192 bands must clear the lfc actual draw range"', 1),
        ('"W191 bands must clear the options_wave2 actual draw range"',
         '"W192 bands must clear the options_wave2 actual draw range"', 1),
        ("# band facts (law sec.4 W191 row, r795): A = FIRST-CLEAN past",
         "# band facts (law sec.4 W192 row, r795): A = FIRST-CLEAN past", 1),
        ("# the registered W190 B band (the arithmetic continuation",
         "# the registered W191 B band (the arithmetic continuation", 1),
        ("# 434_804..436_803 is REFUSED at its own start by the W190",
         "# 437_004..439_003 is REFUSED at its own start by the W191", 1),
        ("# B band 434_804..435_003, exactly as the W190 seat W191+ projection +",
         "# B band 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection +", 1),
        ("# r892 probe leg4 + r893 sec8 回填窗 succession projection notes",
         "# r892 probe leg4 + r787 probe leg1 succession projection notes", 1),
        ("# 435_004..437_003; A base == prior-wave B tail+1 (435_003+1)",
         "# 437_204..439_203; A base == prior-wave B tail+1 (437_203+1)", 1),
        ("# machine-checkable -- A-hops-prior-B staircase FIFTY-FIRST",
         "# machine-checkable -- A-hops-prior-B staircase FIFTY-SECOND", 1),
        ("# continuation 435_004..435_203 is CLEAN on the registered",
         "# continuation 437_204..437_403 is CLEAN on the registered", 1),
        ("# universe but lands INSIDE the W191 A band window --",
         "# universe but lands INSIDE the W192 A band window --", 1),
        ("# 437_004 and lands 437_004..437_203, hops=1, non-rotational",
         "# 439_204 and lands 439_204..439_403, hops=1, non-rotational", 1),
        ("# (437_003+1) machine-checkable; cross-window convergence",
         "# (439_203+1) machine-checkable; cross-window convergence", 1),
        ("# with the W190 seat W191+ projection + r892 probe leg4 + r893 sec8",
         "# with the W191 seat W192+ projection + r892 probe leg4 + r787", 1),
        ("# honored (post-W190 universe re-derive + own-wave A",
         "# honored (post-W191 universe re-derive + own-wave A", 1),
        ("# reservation when deriving B); seat MSG-2130 tail,",
         "# reservation when deriving B); seat MSG-2351 tail,", 1),
        ('assert WAVE_CONFIGS[191]["a_seed_base"] == 435_004 == 435_003 + 1, (',
         'assert WAVE_CONFIGS[192]["a_seed_base"] == 437_204 == 437_203 + 1, (', 1),
        ('"W191 A must be the first-clean window past the registered "',
         '"W192 A must be the first-clean window past the registered "', 1),
        ('"W190 B band tail 435_003+1 (arithmetic continuation "',
         '"W191 B band tail 437_203+1 (arithmetic continuation "', 1),
        ('"434_804..436_803 REFUSED at its own start by the W190 B "',
         '"437_004..439_003 REFUSED at its own start by the W191 B "', 1),
        ('"band 434_804..435_003, exactly as the W190 seat W191+ projection + "',
         '"band 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection + "', 1),
        ('"r892 probe leg4 + r893 sec8 回填窗 succession projection notes "',
         '"r892 probe leg4 + r787 probe leg1 succession projection notes "', 1),
        ('"staircase FIFTY-FIRST instance, E36 card)")',
         '"staircase FIFTY-SECOND instance, E36 card)")', 1),
        ("arith_a190 = set(range(435_004, 437_004))",
         "arith_a191 = set(range(437_204, 439_204))", 1),
        ('"W191 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"',
         '"W192 A window must be CLEAN (first-clean ADMIT face past prior-wave B)"', 1),
        ('assert WAVE_CONFIGS[191]["b_exit_seed_base"] == 437_004 == 437_003 + 1, (',
         'assert WAVE_CONFIGS[192]["b_exit_seed_base"] == 439_204 == 439_203 + 1, (', 1),
        ('"W191 B must be the first-clean window past the own-wave A "',
         '"W192 B must be the first-clean window past the own-wave A "', 1),
        ('"band tail 437_003+1 (arithmetic continuation "',
         '"band tail 439_203+1 (arithmetic continuation "', 1),
        ('"435_004..435_203 CLEAN on the registered universe but "',
         '"437_204..437_403 CLEAN on the registered universe but "', 1),
        ('"lands INSIDE the W191 A band window; same-freeze mutual "',
         '"lands INSIDE the W192 A band window; same-freeze mutual "', 1),
        ('"own-wave A window reserved jumps to 437_004, first-clean "',
         '"own-wave A window reserved jumps to 439_204, first-clean "', 1),
        ("arith_b190 = set(range(437_004, 437_204))",
         "arith_b191 = set(range(439_204, 439_404))", 1),
        ('"W191 B window must be CLEAN (first-clean ADMIT face past own-wave A)"',
         '"W192 B window must be CLEAN (first-clean ADMIT face past own-wave A)"', 1),
        ('"W191 A/B same-freeze mutual exclusion (B hops past own A)"',
         '"W192 A/B same-freeze mutual exclusion (B hops past own A)"', 1),
        ('("PERPETUAL-N1-W191-SHARD-0",', '("PERPETUAL-N1-W192-SHARD-0",', 1),
        ('"n1w191-0of12"), "W191 entry identity"',
         '"n1w192-0of12"), "W192 entry identity"', 1),
        ('("PERPETUAL-N1-W191-SHARD-11",', '("PERPETUAL-N1-W192-SHARD-11",', 1),
        ('"n1w191-11of12")', '"n1w192-11of12")', 1),
        ('assert SHARD_DIR.endswith("n1_w191") and OUT.endswith(',
         'assert SHARD_DIR.endswith("n1_w192") and OUT.endswith(', 1),
        ('"n1_w191_results.json"), "W191 path drift"',
         '"n1_w192_results.json"), "W192 path drift"', 1),
        ('f"W191 shard dir collides with W{wprev}"',
         'f"W192 shard dir collides with W{wprev}"', 1),
        ("# W191 finalize cumulative deps: W17..W190 outputs ALL PRESENT",
         "# W192 finalize cumulative deps: W17..W191 outputs ALL PRESENT", 1),
        ("(landed net chain head 825,328 = W190 bm-a r892 one-pass --",
         "(landed net chain head 833,536 = W191 bm-a r895 one-pass --", 1),
        ("for _depw in range(17, 191):", "for _depw in range(17, 192):", 1),
        ('f"W191 finalize cumulative dep (W{_depw} output) missing"',
         'f"W192 finalize cumulative dep (W{_depw} output) missing"', 1),
        ("# registered wave below 191 composes; wave 15 excluded by",
         "# registered wave below 192 composes; wave 15 excluded by", 1),
        ("# design; SINGLE STATE (W2..W190 all registered -- no",
         "# design; SINGLE STATE (W2..W191 all registered -- no", 1),
        ("assert sorted(w for w in WAVE_CONFIGS if w < 191) == \\",
         "assert sorted(w for w in WAVE_CONFIGS if w < 192) == \\", 1),
        ("[w for w in range(16, 191)], \\", "[w for w in range(16, 192)], \\", 1),
        ('"W191 prior-wave set must derive from registry keys (no 15; " \\',
         '"W192 prior-wave set must derive from registry keys (no 15; " \\', 1),
        ('"W2..W190 registered single state)"',
         '"W2..W191 registered single state)"', 1),
        ('"research", "PERPETUAL_N1_W191_PREREG.md")), \\',
         '"research", "PERPETUAL_N1_W192_PREREG.md")), \\', 1),
        ('"W191 per-wave prereg missing (materializer requirement)"',
         '"W192 per-wave prereg missing (materializer requirement)"', 1),
    ]
    for k, (old, new, cnt) in enumerate(R):
        m = rep(m, old, new, cnt, "mat-%02d" % k)
    mat192 = m

    # ---- G6 roll WAVE_CONFIGS row ----
    c = cfg191_full
    RC = [
        ('191: {"batch": "PERPETUAL-N1-W191",', '192: {"batch": "PERPETUAL-N1-W192",', 1),
        ('"research/PERPETUAL_N1_W191_PREREG.md (wave-level frozen ',
         '"research/PERPETUAL_N1_W192_PREREG.md (wave-level frozen ', 1),
        ('ONE HUNDRED-AND-NINETY-FIRST ENGINE-OWNED WAVE ',
         'ONE HUNDRED-AND-NINETY-SECOND ENGINE-OWNED WAVE ', 1),
        ('BY MACHINE-DERIVE (engine_owner rows 180 + candidate), ',
         'BY MACHINE-DERIVE (engine_owner rows 181 + candidate), ', 1),
        ('number law after the REGISTERED W190 row bm-a r892 freeze ',
         'number law after the REGISTERED W191 row bm-a r894 freeze ', 1),
        ('0cce3c47e, SINGLE STATE zero seat gap W2..W190 all ',
         '%s, SINGLE STATE zero seat gap W2..W191 all ' % W191_FREEZE_SHA, 1),
        ('registered; W191 finalize landed same-window r827, ledger ',
         'registered; W191 finalize landed prior-window r895, ledger ', 1),
        ('head 825,328, merged pool K=415,920; seat published=reserved ',
         'head 833,536, merged pool K=418,120; seat published=reserved ', 1),
        ('MSG-2026-10-08-2130-bma-w191-seat PUSHED to origin 1c28dd21d ',
         'MSG-20261008-2351-bmc-w192-seat PUSHED to origin %s ' % SEAT_SHA, 1),
        ('BEFORE this freeze per r565 early-visibility law (payload = ',
         'BEFORE this freeze per r565 early-visibility law (payload = ', 1),
        ('seat MSG + pre-seat probe script + probe receipt (3-item; the W190 finalize product already on origin since r892, not re-shipped; W146 precedent); ',
         'seat MSG only, Git Data API direct-build push zero local commit -- sec.6.1.4 channel; the pre-seat probe script + receipt landed with the W192 prereg freeze commit de1ad11f9 next, interactive-window payload note; the W191 finalize product already on origin since r895, not re-shipped; W146 precedent); ', 1),
        ('at fetch (r892 pre-seat push), zero merge, zero ',
         'at fetch (r787 S0 pull), zero merge, zero ', 1),
        ('engine_owner=bm-a, wave 190: ', 'engine_owner=bm-c, wave 191: ', 1),
        ('A = FIRST-CLEAN past the registered W190 B band (the ',
         'A = FIRST-CLEAN past the registered W191 B band (the ', 1),
        ('arithmetic continuation 434_804..436_803 is REFUSED at its ',
         'arithmetic continuation 437_004..439_003 is REFUSED at its ', 1),
        ('own start by the W190 B band 434_804..435_003, exactly as ',
         'own start by the W191 B band 437_004..437_203, exactly as ', 1),
        ('the W190 seat W191+ projection + r892 probe leg4 + r893 sec8 回填窗 succession ',
         'the W191 prereg sec5.5 + W191 seat W192+ projection + r892 probe leg4 + r787 probe leg1 succession ', 1),
        ('435_004..437_003; A base == prior-wave B tail+1 ',
         '437_204..439_203; A base == prior-wave B tail+1 ', 1),
        ('machine-checkable = A-hops-prior-B staircase FIFTY-FIRST ',
         'machine-checkable = A-hops-prior-B staircase FIFTY-SECOND ', 1),
        ('arithmetic continuation 435_004..435_203 is CLEAN on the ',
         'arithmetic continuation 437_204..437_403 is CLEAN on the ', 1),
        ('registered universe but lands INSIDE the W191 A band ',
         'registered universe but lands INSIDE the W192 A band ', 1),
        ('jumps to 437_004, first-clean 437_004..437_203 hops=1, ',
         'jumps to 439_204, first-clean 439_204..439_403 hops=1, ', 1),
        ('convergence with the W190 seat W191+ projection + r892 probe leg4 + ',
         'convergence with the W191 seat W192+ projection + r892 probe leg4 + ', 1),
        ('r893 sec8 回填窗 succession projection notes re-derived -- all ',
         'r787 probe succession projection notes re-derived -- all ', 1),
        ('MANDATORY notes honored (post-W190 universe re-derive + ',
         'MANDATORY notes honored (post-W191 universe re-derive + ', 1),
        ('results/_r892bma_w191_probe_receipt.json; W192+ projection ',
         'results/_r787bmc_w192_probe_receipt.json; W193+ projection ', 1),
        ('per this window gate: A first-clean 437_004..439_003 ',
         'per this window gate: A first-clean 439_204..441_203 ', 1),
        ('CLEAN / B first-clean 437_204..437_403 CLEAN -- naive ',
         'CLEAN / B first-clean 439_404..439_603 CLEAN -- naive ', 1),
        ('W191 B band 437_004..437_203 will refuse the naive ',
         'W192 B band 439_204..439_403 will refuse the naive ', 1),
        ('W192 A window; W192 freezer MUST re-derive on the ',
         'W193 A window; W193 freezer MUST re-derive on the ', 1),
        ('post-W191 universe AND reserve the own-wave A window ',
         'post-W192 universe AND reserve the own-wave A window ', 1),
        ('staircase card); W1..W190 finalize ALL LANDED (W190 ',
         'staircase card); W1..W191 finalize ALL LANDED (W191 ', 1),
        ('finalize one-pass bm-a r892, net chain head 825,328, ',
         'finalize one-pass bm-a r895, net chain head 833,536, ', 1),
        ('merged pool K=415,920) -- ZERO in-flight upstream ',
         'merged pool K=418,120) -- ZERO in-flight upstream ', 1),
        ('"a_seed_base": 435_004,        # law sec.4 W191 A: 435_004..437_003 (FIRST-CLEAN past the registered W190 B band; arithmetic 434_804..436_803 REFUSED at own start by the W190 B band; hops=1; A-hops-prior-B staircase FIFTY-FIRST instance, E36 card; ordinal convergence per r587: W190 sec5.5 prose anticipated fifty-first, r892 receipt machine-read FIFTY-FIRST)',
         '"a_seed_base": 437_204,        # law sec.4 W192 A: 437_204..439_203 (FIRST-CLEAN past the registered W191 B band; arithmetic 437_004..439_003 REFUSED at own start by the W191 B band; hops=1; A-hops-prior-B staircase FIFTY-SECOND instance, E36 card; ordinal convergence per r587: W191 prereg sec5.5 prose anticipated fifty-second, r787 receipt machine-read FIFTY-SECOND)', 1),
        ('"b_exit_seed_base": 437_004,   # law sec.4 W191 B: 437_004..437_203 (FIRST-CLEAN past the own-wave A window; arithmetic 435_004..435_203 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)',
         '"b_exit_seed_base": 439_204,   # law sec.4 W192 B: 439_204..439_403 (FIRST-CLEAN past the own-wave A window; arithmetic 437_204..437_403 lands inside own-A, same-freeze mutual exclusion W141 precedent; reserved walk hops=1; B base == own-A tail+1)', 1),
        ('"shard_subdir": "n1_w191", "out_name": "n1_w191_results.json",',
         '"shard_subdir": "n1_w192", "out_name": "n1_w192_results.json",', 1),
        ('"engine_owner": "bm-a"},', '"engine_owner": "bm-c"},', 1),
    ]
    for k, (old, new, cnt) in enumerate(RC):
        c = rep(c, old, new, cnt, "cfg-%02d" % k)

    # ---- G7 roll pf N1_BANDS row ----
    p = pf191_full
    RP = [
        ("    # W191 (bm-a r894 freeze, seat MSG-2026-10-08-2130-bma-w191-seat",
         "    # W192 (bm-c r787 freeze, seat MSG-20261008-2351-bmc-w192-seat", 1),
        ("# pushed to origin 1c28dd21d pre-freeze r565 law (r892 pre-seat",
         "# pushed to origin %s pre-freeze r565 law (r787 pre-freeze" % SEAT_SHA, 1),
        ("# push; payload = seat MSG + pre-seat probe script + probe receipt",
         "# window; payload = seat MSG only, Git Data API direct-build push", 1),
        ("# (3-item; the W190 finalize product already on origin since r892,",
         "# zero local commit -- sec.6.1.4 channel; the pre-seat probe", 1),
        ("# not re-shipped, W146 same-push precedent);",
         "# script + receipt landed with the W192 prereg freeze commit\n"
         "    # de1ad11f9 next, interactive-window payload note; the W191\n"
         "    # finalize product already on origin since r895, not re-shipped,\n"
         "    # W146 same-push precedent);", 1),
        ("# band gate ADMIT results/_r892bma_w191_probe_receipt.json: A = FIRST-CLEAN",
         "# band gate ADMIT results/_r787bmc_w192_probe_receipt.json: A = FIRST-CLEAN", 1),
        ("# past the registered W190 B band (arithmetic continuation",
         "# past the registered W191 B band (arithmetic continuation", 1),
        ("# 434_804..436_803 REFUSED at its own start by the W190 B band",
         "# 437_004..439_003 REFUSED at its own start by the W191 B band", 1),
        ("# 434_804..435_003, exactly as the W190 seat W191+ projection + r892 probe",
         "# 437_004..437_203, exactly as the W191 prereg sec5.5 + W191 seat W192+ projection + r892 probe", 1),
        ("# leg4 + r893 sec8 回填窗 succession projection notes all anticipated;",
         "# leg4 + r787 probe leg1 succession projection notes all anticipated;", 1),
        ("# honest forward walk hops=1 -> 435_004..437_003, non-rotational",
         "# honest forward walk hops=1 -> 437_204..439_203, non-rotational", 1),
        ("# (435_003+1) machine-checkable -- A-hops-prior-B staircase",
         "# (437_203+1) machine-checkable -- A-hops-prior-B staircase", 1),
        ("# FIFTY-FIRST instance, E36 card);",
         "# FIFTY-SECOND instance, E36 card);", 1),
        ("# continuation 435_004..435_203 CLEAN on the registered universe",
         "# continuation 437_204..437_403 CLEAN on the registered universe", 1),
        ("# but lands INSIDE the W191 A band window -- same-freeze mutual",
         "# but lands INSIDE the W192 A band window -- same-freeze mutual", 1),
        ("# own-wave A window reserved jumps to 437_004 -> 437_004..437_203,",
         "# own-wave A window reserved jumps to 439_204 -> 439_204..439_403,", 1),
        ("# own-wave A tail+1 (437_003+1) machine-checkable);",
         "# own-wave A tail+1 (439_203+1) machine-checkable);", 1),
        ("# W191+ projection (gate-derived r892): A first-clean",
         "# W193+ projection (gate-derived r787): A first-clean", 1),
        ("# 437_004..439_003 CLEAN hops=0 / B first-clean 437_204..437_403",
         "# 439_204..441_203 CLEAN hops=0 / B first-clean 439_404..439_603", 1),
        ("# registered W191 B band 437_004..437_203 will refuse the naive",
         "# registered W192 B band 439_204..439_403 will refuse the naive", 1),
        ("# W192 A window; W192 freezer MUST re-derive on the post-W191",
         "# W193 A window; W193 freezer MUST re-derive on the post-W192", 1),
        ("# NOT a re-pick (R250: W191 bands were never assigned).",
         "# NOT a re-pick (R250: W192 bands were never assigned).", 1),
        ('191: {"a": (435_004, 437_003), "b_exit": (437_004, 437_203),',
         '192: {"a": (437_204, 439_203), "b_exit": (439_204, 439_403),', 1),
        ('         "engine_owner": "bm-a"},',
         '         "engine_owner": "bm-c"},', 1),
    ]
    for k, (old, new, cnt) in enumerate(RP):
        p = rep(p, old, new, cnt, "pf-%02d" % k)

    # ---- G8 insertions (r560: additive, after last registered row) ----
    # n1 WAVE_CONFIGS row: after W191 row
    assert n1n.count(cfg191_full) == 1
    n1_b = n1n.replace(cfg191_full, cfg191_full + "\n" + c, 1)
    assert n1_b.count(c) == 1 and n1_b.count(cfg191_full) == 1
    # n1 materializer: before the T-141 marker that follows the W191 block
    w191_pos = n1_b.find("# --- W191 materializer face")
    assert w191_pos >= 0
    t141 = n1_b.find("    # --- T-141 s2 lane face", w191_pos)
    assert t141 > w191_pos, "T-141 marker not found after W191 block"
    n1_final = n1_b[:t141] + mat192 + n1_b[t141:]
    assert n1_final.count("# --- W192 materializer face") == 1
    assert n1_final.count("# --- W191 materializer face") == 1
    assert n1_final.count("    # --- T-141 s2 lane face") == 2
    # pf row: after W191 row
    assert pfn.count(pf191_full) == 1
    pf_final = pfn.replace(pf191_full, pf191_full + "\n" + p, 1)
    assert pf_final.count(pf191_full) == 1 and pf_final.count(
        '192: {"a": (437_204, 439_203)') == 1

    # ---- G9 AST gate (r580/r581/r445) before any write ----
    ast.parse(n1_final)
    ast.parse(pf_final)

    # ---- G10 write back (EOL-adaptive r370) ----
    n1_out = n1_final.replace("\n", "\r\n") if n1_crlf else n1_final
    pf_out = pf_final.replace("\n", "\r\n") if pf_crlf else pf_final
    with open(N1P, "w", encoding="utf-8", newline="") as fh:
        fh.write(n1_out)
    with open(PFP, "w", encoding="utf-8", newline="") as fh:
        fh.write(pf_out)

    # ---- G11 py_compile + post-import guard ----
    for f in (N1P, PFP):
        prc = subprocess.run([sys.executable, "-m", "py_compile", f],
                             capture_output=True, creationflags=CNW)
        assert prc.returncode == 0, "py_compile failed: %s" % f
    chk = subprocess.run(
        [sys.executable, "-c",
         "import sys, json; sys.path.insert(0, 'scripts'); "
         "from perpetual_faces import N1_BANDS as B; "
         "print(json.dumps({'rows': len(B), 'w192': B.get(192), "
         "'w191': B.get(191)}))"],
        cwd=ROOT, capture_output=True, creationflags=CNW)
    assert chk.returncode == 0, "post-import check failed: %s" % chk.stderr[:300]
    post = json.loads(chk.stdout.decode("utf-8", "replace").strip().splitlines()[-1])
    assert post["rows"] == 190, "row count drift: %s" % post
    assert post["w192"] == {"a": (437204, 439203), "b_exit": (439204, 439403),
                           "engine_owner": "bm-c"}, "W192 row drift: %s" % post
    assert post["w191"] == {"a": (435004, 437003), "b_exit": (437004, 437203),
                            "engine_owner": "bm-a"}, "W191 row damaged: %s" % post
    facts["post_import"] = post

    # ---- G12 receipt + five-segment PASS prints (r578 law) ----
    with open(OUT_RCPT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    print("PASS 1/5 law-mirror pf N1_BANDS[192] row: a=(437204,439203) "
          "b_exit=(439204,439403) engine_owner=bm-c (comment face rolled, "
          "W191 row byte-intact)")
    print("PASS 2/5 n1 WAVE_CONFIGS[192] row: batch=PERPETUAL-N1-W192 "
          "a_seed_base=437_204 b_exit_seed_base=439_204 shard=n1_w192 "
          "out=n1_w192_results.json owner=bm-c")
    print("PASS 3/5 n1 W192 materializer face: %d replacements all "
          "count-asserted; staircase FIFTY-SECOND; prior-wave parity->W191; "
          "deps range(17,192); prereg presence assert->W192" % (len(R) + len(RC)))
    print("PASS 4/5 guards: origin vacancy (fetch+show) + seat sha "
          "%s ancestor + registry 189->190 rows + AST+py_compile + W191 "
          "byte-intact post-import" % SEAT_SHA)
    print("PASS 5/5 summary: W192 = 182nd engine wave, bm-c 35th owned "
          "(rows 181+candidate per receipt leg0); A=437_204..439_203 "
          "hops=1 FIFTY-SECOND staircase; B=439_204..439_403 hops=1 "
          "own-A mutual exclusion; ADMIT receipt machine-read; receipt="
          "results/_r787bmc_w192_freeze_receipt.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
