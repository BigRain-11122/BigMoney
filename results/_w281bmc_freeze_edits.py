# -*- coding: utf-8 -*-
# 2026-10-20 02:5x bm-c r1134 splice window: W281 five-face freeze splice editor.
# Lineage = results/_w280bmc_freeze_edits.py (proven live-fire freeze, bm-c r1131;
# engine self-burn 12/12 + finalize one-pass verified r1131-continuation) with the
# r787 preflight law, r609 origin-verbatim base, r761 programmatic quote wrapping,
# r909 physical-byte anchors, r838 per-file EOL detection, and the family-#6
# LHS/RHS/comment atomic triple gate carried forward at the new wave (the W281
# block's own w<281> boundary is a legitimate prior-wave boundary; it moves from
# the template's w<280> by exactly one).
# Facts are LIVE-DERIVED: registered W280 row from the pf import, W279 row likewise,
# own bundle shas via pickaxe, chain anchors machine-read from the W280 finalize
# product. Zero transcription (r587).
#
# BANDS (frozen research/PERPETUAL_N1_W281_PREREG.md sec.3, re-derived live this
# window): A 633_501..635_500 (STAIRCASE-AFFECTS-A 1-hop walk, THIRTY-FIRST
# consecutive A-hop; naive 633_301..635_300 refused at start by the registered
# W280 B band 633_301..633_500; A base == registered prior-wave B tail+1 EXACT)
# and B 635_501..635_700 (1-hop own-A RESERVATION CASCADE above own-A, THIRTY-SECOND
# consecutive above-own-A; naive 633_501..633_700 lands inside the own-wave A
# first-clean window; B base == own-A tail+1 EXACT). ADMIT receipt
# results/_w281bmc_20261020_probe_receipt.json.
import json, hashlib, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PF = os.path.join(REPO, "scripts", "perpetual_faces.py")
N1 = os.path.join(REPO, "scripts", "perpetual_faces_n1.py")
RECEIPT_IN = os.path.join(REPO, "results", "_w281bmc_20261020_probe_receipt.json")
RECEIPT_OUT = os.path.join(REPO, "results", "_w281bmc_freeze_receipt.json")
SEAT_MSG = "MSG-20261020-0225-bmc-w281-seat.md"
SEAT_ORIGIN = "1c9ff56dcd"
PY = sys.executable
NEW_W = 281          # the wave being spliced
PREV_W = 280         # the last REGISTERED wave (freshness face)
PRIOR_W = 279        # prior band face used for freshness suppression in fresh legs


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True)


# ---------- gate 0: fresh origin, working == origin (r609 law) ----------
git("fetch", "origin")
head = git("rev-parse", "HEAD").stdout.decode().strip()
omain = git("rev-parse", "origin/main").stdout.decode().strip()
assert git("merge-base", "--is-ancestor", "origin/main", "HEAD").returncode == 0, \
    f"origin/main {omain} not contained in HEAD {head} -- rebase first (r609)"
for path in ("scripts/perpetual_faces.py", "scripts/perpetual_faces_n1.py"):
    b = git("show", f"origin/main:{path}").stdout
    w = open(os.path.join(REPO, path), "rb").read()
    assert b.replace(b"\r\n", b"\n") == w.replace(b"\r\n", b"\n"), \
        f"working {path} != origin blob (EOL-normalized) -- stale base (r609 abort)"

sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces as pf_mod

# ---------- gate 0.5: W280 five-face landed + W280 finalize product present ----------
assert NEW_W not in pf_mod.N1_BANDS, "W281 row already registered -- not a first freeze, abort"
W280 = dict(pf_mod.N1_BANDS.get(PREV_W) or {})
assert W280.get("engine_owner") == "bm-c", f"W280 row not landed as declared: {W280}"
w280_out_path = os.path.join(REPO, "results", "perpetual_faces", "n1_w280_results.json")
assert os.path.exists(w280_out_path), "W280 finalize product missing -- chain dep not met"
for _w in range(277, 269, -1):
    assert os.path.exists(os.path.join(REPO, "results", "perpetual_faces", f"n1_w{_w}_results.json")), \
        f"W{_w} finalize product missing (transitive chain dep) -- abort"
w280_out = json.load(open(w280_out_path, encoding="utf-8"))
w280_led = (w280_out.get("science_gates") or {}).get("ledger") or {}
w280_total = w280_led.get("total")
w280_merged_n = (w280_out.get("null_pool_cumulative") or {}).get("merged", {}).get("n_values")
assert w280_total == 1_040_335 and w280_merged_n == 613_920, \
    f"W280 finalize anchors drift: total={w280_total} merged={w280_merged_n} (expect 1,040,335 / 613,920)"
w280_freeze_sha = (git("log", "--format=%H", "-S", '280: {"a"', "--", "scripts/perpetual_faces.py")
                   .stdout.decode().strip().splitlines() or ["n/a"])[0]
w280_prereg_sha = (git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W280_PREREG.md")
                   .stdout.decode().strip().splitlines() or ["n/a"])[0]
w281_prereg_sha = (git("log", "--diff-filter=A", "--format=%H", "--", "research/PERPETUAL_N1_W281_PREREG.md")
                   .stdout.decode().strip().splitlines() or ["n/a"])[0]
w281_pre_path = os.path.join(REPO, "research", "PERPETUAL_N1_W281_PREREG.md")
assert os.path.exists(w281_pre_path), "W281 per-wave prereg missing on disk -- abort"
with open(w281_pre_path, encoding="utf-8") as _fh:
    _pre_head = _fh.read(2000)
assert "DRAFT-NOT-FROZEN" not in _pre_head, "W281 prereg still DRAFT -- abort"
assert "@@SEAT_HHMM@@" not in _pre_head and "@@SEAT_SHA@@" not in _pre_head, \
    "W281 prereg carries unfilled seat placeholders -- frozen face incomplete, abort"

owner_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bma_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-a"]
bmc_rows_live = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
assert len(owner_rows_live) == 270 and len(bma_rows_live) == 130 and len(bmc_rows_live) == 99, \
    f"leg0 ordinal drift: owner={len(owner_rows_live)} bma={len(bma_rows_live)} bmc={len(bmc_rows_live)} (expect 270/130/99)"
print(f"gate0.5 OK: W280 landed (freeze {w280_freeze_sha[:10]}, finalize ledger {w280_total}, merged n={w280_merged_n}); "
      f"owner rows {len(owner_rows_live)} + candidate, bm-c rows {len(bmc_rows_live)} + candidate")

# ---------- band facts from the committed ADMIT receipt (never transcribed) ----------
rec = json.load(open(RECEIPT_IN, encoding="utf-8"))
assert rec["verdict"] == "ADMIT"
bd = rec["bands"]
a_lo, a_hi, b_lo, b_hi = bd["a_lo"], bd["a_hi"], bd["b_lo"], bd["b_hi"]
leg1 = rec["legs"]["leg1"]
assert [a_lo, a_hi] == leg1["A"] and [b_lo, b_hi] == leg1["B"], "receipt band mismatch"
assert (a_lo, a_hi) == (633_501, 635_500) and (b_lo, b_hi) == (635_501, 635_700), \
    f"W281 band drift vs frozen prereg/ADMIT: {(a_lo, a_hi)} {(b_lo, b_hi)}"
w280_b_tail = W280["b_exit"][1]
w280_a_tail = W280["a"][1]
assert w280_b_tail + 1 == a_lo, "A staircase-hop landing base relation (A base == registered prior-wave B tail+1)"
assert b_lo == a_hi + 1, "B base == own-A tail+1 EXACT (own-A reservation cascade)"
assert W280["b_exit"][0] == W280["a"][1] + 1, "upstream W280 above-own-A relation broken"
assert leg1.get("hops_A") == 1 and leg1.get("hops_B") == 1, "hop-count drift vs probe receipt"
assert leg1.get("B_naive_refused_at_start") is True, "B naive-start refusal face drift"
assert leg1.get("B_lands_above_own_A") is True, "B landing face drift"
assert len(leg1.get("A_hop_chain") or []) == 1, "A hop-chain face drift"
assert len(leg1.get("B_hop_chain") or []) == 1, "B hop-chain face drift"
ra = leg1.get("relation_asserts") or {}
assert ra.get("A_staircase_hop_past_registered_W280_B") and ra.get("A_base_ge_priorB_tail_plus1") \
    and ra.get("B_naive_clean_vs_registered") and ra.get("B_hop_lands_inside_A") \
    and ra.get("B_lands_above_own_A") and ra.get("AB_mutual_exclusion") \
    and ra.get("B_base_eq_own_A_tail_plus1"), f"probe receipt relation face drift: {ra}"
assert [w280_a_tail + 1, w280_a_tail + 2_000] == leg1["ARITH_A"], "A naive-arithmetic drift"
assert [w280_b_tail + 1, w280_b_tail + 200] == leg1["ARITH_B"], "B naive-arithmetic drift"

w281_receipt_sha = (git("log", "--diff-filter=A", "--format=%H", "--",
                        "results/_w281bmc_20261020_probe_receipt.json")
                    .stdout.decode().strip().splitlines() or ["n/a"])[0]
seat_found = None
for _p in ("fleet/inbox", "fleet/inbox/processed"):
    if os.path.exists(os.path.join(REPO, _p, SEAT_MSG)):
        seat_found = _p + "/" + SEAT_MSG
        break
assert seat_found, f"W281 seat MSG missing from both inbox paths: {SEAT_MSG}"

# ---------- re-run discipline gates at freeze window ----------
g = subprocess.run([PY, os.path.join(REPO, "Tools", "banned_direction_gate.py"),
                    "--prereg", "research/PERPETUAL_N1_W281_PREREG.md"],
                   cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
assert g.returncode == 0, f"banned gate FAIL: {g.stdout} {g.stderr}"
gate_lines = []
for base, span in ((a_lo, 2_000), (b_lo, 200)):
    g2 = subprocess.run([PY, os.path.join(REPO, "Tools", "seed_admit_gate.py"), str(base), "--span", str(span)],
                        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert g2.returncode == 0, f"seed_admit_gate FAIL base={base}: {g2.stdout} {g2.stderr}"
    gate_lines.append(g2.stdout.strip().splitlines()[-1] if g2.stdout.strip() else f"rc0 base={base} span={span}")
print("gates OK:", " | ".join(gate_lines))

# ---------- read files, EOL (r838 law) ----------
pf_b = open(PF, "rb").read(); pf_t = pf_b.decode("utf-8")
n1_b = open(N1, "rb").read(); n1_t = n1_b.decode("utf-8")


def detect_eol(t):
    crlf = t.count("\r\n")
    return "\r\n" if crlf > (t.count("\n") - crlf) else "\n"


EOL = detect_eol(n1_t); PF_EOL = detect_eol(pf_t)


def must(t, s, n, what):
    c = t.count(s)
    assert c == n, f"anchor {what}: count {c} != {n}"
    return s


def fmt(n):
    return f"{n // 1000}_{n % 1000:03d}"


# ---------- extract parity estate + kept legs (physical bytes) ----------
a_prev_block = f'    # --- W{PREV_W} materializer face'
a_t141 = '    # --- T-141 s2 lane face'
prev_start = n1_t.find(a_prev_block); t141_pos = n1_t.find(a_t141)
assert prev_start > 0 and t141_pos > prev_start, "W280 materializer block face not found"
blk = n1_t[prev_start:t141_pos]
m_first_row = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first_row and m_disj and m_disj.start() > m_first_row.start(), "parity span markers not found"
_row_ls = blk.rfind(EOL, 0, m_first_row.start()) + len(EOL)
par_full = blk[_row_ls:m_disj.start()]
m211 = re.search(r" *assert pf\.N1_BANDS\[211\] ==", par_full)
assert m211, "W211 boundary not found inside the W280 parity span"
par_sec = par_full[:m211.start()]
legs_sec = par_full[m211.start():]
assert par_sec.endswith(EOL) and legs_sec.endswith(EOL), "segments must end with EOL"
_estate_ws = [int(w) for w in re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)]
assert [int(w) for w in _estate_ws] == list(range(138, 207)), "estate segment not W138..W206 (69 rows)"
_legs_ws = [int(w) for w in re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_sec)]
assert _legs_ws == list(range(211, PREV_W)), f"legs segment not W211..W{PREV_W - 1}: n={len(_legs_ws)}"
m248 = re.search(r" *assert pf\.N1_BANDS\[248\] ==", legs_sec)
assert m248, "W248 split boundary not found"
legs_kept = legs_sec[:m248.start()]
legs_dropped = legs_sec[m248.start():]
assert legs_kept.endswith(EOL) and legs_dropped.endswith(EOL)
assert [int(w) for w in re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_kept)] == list(range(211, 248)), \
    "kept segment not W211..W247"
assert [int(w) for w in re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", legs_dropped)] == list(range(248, PREV_W)), \
    "dropped segment not W248..W279"

fresh_leg_lines = []
for _w in range(248, NEW_W):
    _row = dict(pf_mod.N1_BANDS[_w])
    _owner = _row["engine_owner"]
    _msg = (f'"registered W{_w} row parity drift (r307; engine_owner={_owner}; '
            f'W{NEW_W} freeze fresh-derive from live registry)"')
    fresh_leg_lines += [
        f'        assert pf.N1_BANDS[{_w}] == {{"a": ({fmt(_row["a"][0])}, {fmt(_row["a"][1])}),',
        f'                                    "b_exit": ({fmt(_row["b_exit"][0])}, {fmt(_row["b_exit"][1])}),',
        f'                                    "engine_owner": "{_owner}"}}, \\',
        f'            {_msg}',
    ]
fresh_legs = EOL.join(fresh_leg_lines)
assert fresh_leg_lines[0].startswith('        assert pf.N1_BANDS[248] == {"a": (')


def line_indent(t, needle, eol):
    i = t.find(needle)
    assert i >= 0, f"indent needle not found: {needle[:40]}"
    ls = t.rfind(eol, 0, i) + len(eol)
    line = t[ls:t.find(eol, ls)]
    return line[:len(line) - len(line.lstrip(" "))]


CFG_I = line_indent(n1_t, f'{PREV_W}: {{"batch"', EOL)
PRE_KEY_I = line_indent(n1_t, f'"prereg": ("research/PERPETUAL_N1_W{PREV_W}_PREREG.md', EOL)
PRE_I = line_indent(n1_t, '"pre-run; design = frozen v1 null calibration verbatim, "', EOL)
_cprev = n1_t.find(f'{PREV_W}: {{"batch"')
assert _cprev > 0, "W280 cfg entry not found"
MEM_I = line_indent(n1_t, '"a_seed_base": ' + str(W280["a"][0]), EOL)
ROW_I = line_indent(pf_t, f'{PREV_W}: {{"a"', PF_EOL)

w280_row_start = pf_t.find(f'    {PREV_W}: {{"a"')
assert w280_row_start > 0, "W280 row literal not found in pf source"
_own_ls = pf_t.find(PF_EOL, w280_row_start) + len(PF_EOL)
_own_le = pf_t.find(PF_EOL, _own_ls)
w280_own_line = pf_t[_own_ls:_own_le]
assert '"engine_owner": "bm-c"' in w280_own_line, f"W280 owner line unexpected: {w280_own_line!r}"
ROWC_I = w280_own_line[:len(w280_own_line) - len(w280_own_line.lstrip(" "))]

# ---------- pf comment + row ----------
pf_comment = PF_EOL.join([
    "    # W281 (bm-c loop five-face freeze splice -- OWN-SEAT face, seat",
    "    # MSG-20261020-0225-bmc-w281-seat published=reserved by bm-c itself @",
    "    # origin " + SEAT_ORIGIN + " (r1132, queue-head seat-first supply -- W280 registered+FINALIZED",
    "    # at publish, W281 FREEZE UNBLOCKED at seat time); the SPLICE gate0.5 = GREEN at seat",
    "    # (W280 five-face + finalize product both in-place; prereg",
    "    # research/PERPETUAL_N1_W281_PREREG.md bm-c r1133 window derive landed",
    "    # pre-freeze, freeze-time gate " + w281_prereg_sha[:10] + "; probe receipt",
    "    # results/_w281bmc_20261020_probe_receipt.json @ " + w281_receipt_sha[:10] + ");",
    "    # CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10",
    "    # ~23:1x; deletion-set EMPTY; splice AFTER the bm-c W280 five-face",
    "    # (freeze " + w280_freeze_sha[:10] + ") + W280 finalize product landed (ledger head",
    "    # " + str(w280_total) + " machine-read); zero --no-verify; the W281 seat MSG sits in",
    "    # " + seat_found + " at freeze time (honest archived per S7 law);",
    "    # band gate ADMIT results/_w281bmc_20261020_probe_receipt.json: A = 1-HOP",
    "    # STAIRCASE-AFFECTS-A walk THIRTY-FIRST consecutive A-hop (naive " + fmt(w280_a_tail + 1) + ".." + fmt(w280_a_tail + 2_000) + " REFUSED",
    "    # at start by the registered W280 B band; walk past the W280 B tail ->",
    "    # A first-clean, hops=1; A base == registered prior-wave B tail+1 (" + fmt(w280_b_tail) + "+1) EXACT)",
    "    # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive " + fmt(w280_b_tail + 1) + ".." + fmt(w280_b_tail + 200) + " CLEAN vs",
    "    # the registered universe BUT lands INSIDE the own-wave A first-clean window;",
    "    # walk past the own-A tail -> B lands ABOVE own-A at tail+1 -- THIRTY-SECOND",
    "    # consecutive above-own-A; B base == own-A tail+1 (" + fmt(a_hi) + "+1) EXACT)",
    "    # single-window derive (gate legs merged INTO the probe, r812);",
    "    # seed_admit_gate (O-20261010-1945-bm-a ADMIT convention):",
    "    # " + gate_lines[0] + ";",
    "    # " + gate_lines[1] + ".",
    "    # W282+ projection (pre-seat probe leg4, pre-W281 universe):",
    "    # A naive first-clean " + rec["legs"]["leg4"]["W282p_A_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_A"]) + " / B naive "
    + rec["legs"]["leg4"]["W282p_B_naive"] + " hops=" + str(rec["legs"]["leg4"]["hops_B"])
    + " BUT lands INSIDE the projection A window",
    "    # (staircase face continuing since W251); the W282 freezer MUST",
    "    # re-derive on the post-W281 universe AND reserve the own-wave A window",
    "    # when deriving B; never transcribe r587.",
])
pf_row = (f'{ROW_I}281: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), '
          f'"b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'
          + PF_EOL + f'{ROWC_I}"engine_owner": "bm-c"}},' + PF_EOL)
assert pf_row.split(PF_EOL)[0].strip() == \
    f'281: {{"a": ({fmt(a_lo)}, {fmt(a_hi)}), "b_exit": ({fmt(b_lo)}, {fmt(b_hi)}),'

old_pf = must(pf_t, (w280_own_line + PF_EOL + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1, "pf_close")
new_pf = (w280_own_line + PF_EOL + pf_comment + PF_EOL + pf_row
          + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands')
pf_t2 = pf_t.replace(old_pf, new_pf, 1)

# ---------- n1 cfg entry ----------
fin_face = (f"W1..W280 finalize ALL LANDED (W280 finalize product present at splice, "
            f"net chain head {w280_total} machine-read, merged pool K={w280_merged_n} "
            f"machine-read) -- ZERO in-flight upstream seats at splice time, clean precondition; "
            f"downstream W282 seat NOT YET PUBLISHED at this freeze window (the next freezer must "
            f"seat-first publish per O-20261010-2350 sec.2; the W282 freezer MUST re-derive live on "
            f"the post-W281 universe + reserve the own-wave A window when deriving B, never transcribe r587)")
cfg_lines = [
    f'{CFG_I}281: {{"batch": "PERPETUAL-N1-W281",',
    f'{PRE_KEY_I}"prereg": ("research/PERPETUAL_N1_W281_PREREG.md (wave-level frozen "',
]
PRE = [
    "pre-run; design = frozen v1 null calibration verbatim, ",
    "new seed bands only; TWO HUNDRED AND EIGHTY-FIRST ENGINE-OWNED WAVE ",
    f"BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate), ",
    "own-series continuation per O-20260101-2355 sec.2 (first-free-",
    "number law after the REGISTERED W280 row five-face freeze (bm-c own seat executed at the bm-c r1131 splice window; engine self-burn 12/12; finalize one-pass ledger 1,040,335 / K=613,920 machine-read), ",
    f"{w280_freeze_sha[:10]} (prereg {w280_prereg_sha[:10]}), SINGLE STATE zero seat gap W2..W280 all ",
    "registered; " + fin_face + "; ",
    "seat published=reserved ",
    "MSG-20261020-0225-bmc-w281-seat PUSHED to origin " + SEAT_ORIGIN + " ",
    "BEFORE this freeze per r565 early-visibility law; per-wave prereg ",
    "research/PERPETUAL_N1_W281_PREREG.md derived by the bm-c r1133 window, ",
    f"freeze-time commit {w281_prereg_sha[:10]} @ probe receipt {w281_receipt_sha[:10]}; ",
    "deletion-set EMPTY; delivery window = chain-order splice ",
    "after the W280 five-face + W280 finalize product landed ",
    "(CEO fill-order standing 2026-10-08 ~23:5x RE-ISSUED 2026-10-10 ~23:1x); ",
    "zero merge at freeze delivery, zero --no-verify; single-window derive), ",
    "engine_owner=bm-c (bm-c's HUNDREDTH owned claim per machine-derive ",
    f"(engine_owner==bm-c rows {len(bmc_rows_live)} + candidate), own-seat continuity)), ",
    "wave 281: ",
    "A = 1-HOP STAIRCASE-AFFECTS-A walk THIRTY-FIRST consecutive A-hop (naive continuation ",
    f"{fmt(w280_a_tail + 1)}..{fmt(w280_a_tail + 2_000)} REFUSED at own start -- hops=1, ",
    "A_hop_chain verbatim in the probe receipt, A_clean_at_naive_start=false; the walk hops ",
    "past the W280 B tail -> A first-clean; A base == registered prior-wave B tail+1 (",
    f"{fmt(w280_b_tail)}+1) machine-checkable) ",
    "+ B = 1-HOP own-A RESERVATION CASCADE above own-A (naive continuation ",
    f"{fmt(w280_b_tail + 1)}..{fmt(w280_b_tail + 200)} CLEAN vs the registered universe BUT lands ",
    "INSIDE the own-wave A first-clean window; hops=1, ",
    "B_naive_refused_at_start=true, B_hop_chain verbatim; the walk hops past the own-wave A ",
    f"tail -> B lands ABOVE own-A {fmt(a_lo)}..{fmt(a_hi)} at tail+1 EXACT; THIRTY-SECOND consecutive ",
    f"above-own-A landing; B base == own-A tail+1 ({fmt(a_hi)}+1) machine-checkable; ADMIT receipt ",
    "results/_w281bmc_20261020_probe_receipt.json + seed_admit_gate rc0 both bands FREE ",
    "(O-20261010-1945-bm-a ADMIT convention); W282+ projection per this window gate: ",
    f"A naive first-clean {rec['legs']['leg4']['W282p_A_naive']} CLEAN (hops=0) / B naive ",
    f"{rec['legs']['leg4']['W282p_B_naive']} hops={rec['legs']['leg4']['hops_B']} BUT lands INSIDE the projection A window; ",
    "W282 freezer MUST re-derive on the post-W281 universe AND reserve the own-wave A window ",
    "when deriving B (the finalize merge loop still derives the wave set from registry keys ",
    "at run time, FAIL-CLOSED r307 always on)",
]
for i, s in enumerate(PRE):
    if i == len(PRE) - 1:
        cfg_lines.append(f'{PRE_I}"{s}"),')
    else:
        cfg_lines.append(f'{PRE_I}"{s}"')
cfg_lines += [
    f'{MEM_I}"a_seed_base": {a_lo},        # law sec.4 W281 A: {fmt(a_lo)}..{fmt(a_hi)} (1-HOP STAIRCASE-AFFECTS-A walk THIRTY-FIRST consecutive A-hop; naive {fmt(w280_a_tail + 1)}..{fmt(w280_a_tail + 2_000)} REFUSED at start -- hops=1; A base == registered prior-wave B tail+1)',
    f'{MEM_I}"b_exit_seed_base": {b_lo},   # law sec.4 W281 B: {fmt(b_lo)}..{fmt(b_hi)} (1-HOP own-A RESERVATION CASCADE above own-A; naive {fmt(w280_b_tail + 1)}..{fmt(w280_b_tail + 200)} CLEAN vs registered BUT lands inside own-wave A -- hops=1; B lands ABOVE own-A at tail+1 EXACT -- thirty-second consecutive above-own-A)',
    f'{MEM_I}"shard_subdir": "n1_w281", "out_name": "n1_w281_results.json",',
    f'{MEM_I}"engine_owner": "bm-c"}},',
]
cfg_block = EOL.join(cfg_lines)
old_cfg = must(n1_t, ('                       }' + EOL + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1, "n1_cfg_close")
new_cfg = (cfg_block + EOL + '                       }' + EOL + 'PREREG = WAVE_CONFIGS[2]["prereg"]')
assert new_cfg.count('281: {"batch": "PERPETUAL-N1-W281"') == 1
n1_t2 = n1_t.replace(old_cfg, new_cfg, 1)

# ---------- n1 materializer block ----------
hdr = [
    f"    # --- W{NEW_W} materializer face (bm-c loop splice -- OWN-SEAT face, seat",
    "    #     MSG-20261020-0225-bmc-w281-seat published=reserved by bm-c",
    "    #     itself @ origin " + SEAT_ORIGIN + " r1132 BEFORE the freeze (r565 law);",
    "    #     upstream W280 complete incl finalize: bm-c five-face splice",
    "    #     " + w280_freeze_sha[:10] + " + engine self-burn 12/12 + finalize one-pass (ledger",
    "    #     " + str(w280_total) + " / K=" + str(w280_merged_n) + " machine-read at freeze). Chatty",
    "    #     chain-order splice from the committed ADMIT receipt",
    "    #     results/_w281bmc_20261020_probe_receipt.json + seed_admit_gate rc0",
    "    #     both bands FREE (O-20261010-1945-bm-a ADMIT convention);",
    "    #     banned gate ADMIT 0 (re-run at freeze window);",
    "    #     not a re-pick (W281 bands were never assigned).",
    "    #     PARITY STRUCTURAL CHOICE (W280 template lineage):",
    "    #     estate 69 rows (W138..W206 full-span, r858 absorb generation) +",
    "    #     W211..W247 legs (37) extracted verbatim from the OWN W280 block",
    "    #     physical bytes; the W280 block's own W248..W279 legs (32) are",
    "    #     EXCLUDED from the estate path per the template mandate; fresh",
    "    #     W248..W280 legs (33) added, machine-derived from the live pf",
    "    #     registry at freeze time -> 139 parity rows.",
    "    _set_wave(%d)" % NEW_W,
    "    try:",
    f'        assert WAVE_CONFIGS[{PREV_W}]["a_seed_base"] == pf.N1_BANDS[{PREV_W}]["a"][0], \\',
    f'            "W{NEW_W} upstream W{PREV_W} mirror drift (a)"',
    f'        assert WAVE_CONFIGS[{PREV_W}]["b_exit_seed_base"] == \\',
    f'            pf.N1_BANDS[{PREV_W}]["b_exit"][0], "W{NEW_W} upstream W{PREV_W} mirror drift (b)"',
    f'        assert WAVE_CONFIGS[{PREV_W}].get("engine_owner") == \\',
    f'            pf.N1_BANDS[{PREV_W}].get("engine_owner") == "bm-c", \\',
    f'            "W{NEW_W} upstream W{PREV_W} engine_owner mirror drift"',
    f"        wnew_a = {{A_SEED_BASE + j for j in range(A_N)}}",
    f"        wnew_b = {{B_EXIT_SEED_BASE + j for j in range(B_N)}}",
    f'        assert not (wnew_a & wnew_b), "W{NEW_W} A/B band overlap"',
    "        assert not (wnew_a & reg_ints) and not (wnew_b & reg_ints), \\",
    f'            "W{NEW_W} hits SEED_REGISTRY"',
    '        for nm, band in (("A", wnew_a), ("B", wnew_b)):',
    f'            assert not (band & v1_a) and not (band & v1_b), f"W{NEW_W} {{nm}} hits v1"',
    f'            assert not (band & w1_a) and not (band & w1_b), f"W{NEW_W} {{nm}} hits W1"',
    f'            assert not (band & probes), f"W{NEW_W} {{nm}} hits probe seeds"',
]
tail = [
    f"        # prior-wave disjointness W2..W{PREV_W} (single state: all",
    f"        # registered, dynamic registry derive, r511 law)",
    f"        for wprev in sorted(w for w in WAVE_CONFIGS if w < {NEW_W}):",
    '            assert not (wnew_a & {WAVE_CONFIGS[wprev]["a_seed_base"] + j',
    f'                                 for j in range(A_N)}}), f"W{NEW_W} A hits W" + str(wprev)',
    '            assert not (wnew_b & {WAVE_CONFIGS[wprev]["b_exit_seed_base"] + j',
    f'                                  for j in range(B_N)}}), f"W{NEW_W} B hits W" + str(wprev)',
    "        n3r1_used = set(range(70_000, 70_006))",
    '        assert not (wnew_a & n3r1_used) and not (wnew_b & n3r1_used), \\',
    f'            "W{NEW_W} bands hit the N3-R1 used-seed band 70_000..70_005 (MSG-183x)"',
    '        assert not (wnew_a & lfc_actual12) and not (wnew_b & lfc_actual12), \\',
    f'            "W{NEW_W} bands must clear the lfc actual draw range"',
    "        assert not (wnew_a & options_actual12) and \\",
    "            not (wnew_b & options_actual12), \\",
    f'            "W{NEW_W} bands must clear the options_wave2 actual draw range"',
    f"        # band facts (law sec.4 W{NEW_W} row): A = 1-HOP STAIRCASE-AFFECTS-A",
    "        # walk THIRTY-FIRST consecutive A-hop (naive continuation",
    f"        # {fmt(w280_a_tail + 1)}..{fmt(w280_a_tail + 2_000)} REFUSED at naive start by the registered W280 B band;",
    "        # hops=1, A_clean_at_naive_start=false; A base ==",
    f"        # registered prior-wave B tail+1 ({fmt(w280_b_tail)}+1) machine-checkable;",
    "        # B = 1-HOP own-A RESERVATION CASCADE above own-A (naive continuation",
    f"        # {fmt(w280_b_tail + 1)}..{fmt(w280_b_tail + 200)} CLEAN vs registered but lands INSIDE the own-wave A first-clean window);",
    f"        # B base == own-A tail+1 ({fmt(a_hi)}+1) EXACT; THIRTY-SECOND consecutive above-own-A landing.",
    f'        assert WAVE_CONFIGS[{NEW_W}]["a_seed_base"] == {a_lo} == {w280_b_tail} + 1, (',
    f'            "W{NEW_W} A staircase-affects-A walk THIRTY-FIRST consecutive A-hop: naive "',
    '            "continuation REFUSED at own start (the registered W280 B band sits INSIDE "',
    '            "the naive A window; hops=1, A_clean_at_naive_start=false); A base == "',
    '            "registered prior-wave B tail+1 machine-checkable")',
    f"        arith_new_a = set(range({a_lo}, {a_hi + 1}))",
    "        assert not (arith_new_a & reg_ints), \\",
    f'            "W{NEW_W} A window must be CLEAN (first-clean ADMIT face)"',
    f'        assert WAVE_CONFIGS[{NEW_W}]["b_exit_seed_base"] == {b_lo} == {a_hi} + 1, (',
    f'            "W{NEW_W} B 1-HOP own-A RESERVATION CASCADE face: naive continuation lands "',
    '            "INSIDE the own-wave A first-clean window -- B hops past the own-wave A tail; "',
    '            "B base == own-A tail+1 EXACT; B_hop_lands_inside_A=false")',
    f"        assert {b_lo} > {w280_b_tail}, \\",
    f'            "W{NEW_W} B walk base must sit above the prior-wave B tail"',
    f"        arith_new_b = set(range({b_lo}, {b_hi + 1}))",
    "        assert not (arith_new_b & reg_ints), \\",
    f'            "W{NEW_W} B window must be CLEAN (first-clean ADMIT face)"',
    "        assert not (arith_new_b & arith_new_a), \\",
    f'            "W{NEW_W} A/B same-freeze mutual exclusion (zero overlap)"',
    f'        assert _entry_shard_of(0, 12) == ("PERPETUAL-N1-W{NEW_W}-SHARD-0",',
    f'                                          "n1w{NEW_W}-0of12"), "W{NEW_W} entry identity"',
    f'        assert _entry_shard_of(11, 12) == ("PERPETUAL-N1-W{NEW_W}-SHARD-11",',
    f'                                           "n1w{NEW_W}-11of12")',
    f'        assert SHARD_DIR.endswith("n1_w{NEW_W}") and OUT.endswith(',
    f'            "n1_w{NEW_W}_results.json"), "W{NEW_W} path drift"',
    f"        for wprev in sorted(w for w in WAVE_CONFIGS if w < {NEW_W}):",
    "            assert os.path.abspath(SHARD_DIR) != os.path.abspath(os.path.join(",
    '                PATHS.results_dir, "p2cal_ext",',
    '                WAVE_CONFIGS[wprev]["shard_subdir"])), \\',
    f'                f"W{NEW_W} shard dir collides with W{{wprev}}"',
    f"        # W{NEW_W} finalize cumulative deps: W17..W{PREV_W} outputs ALL PRESENT",
    f"        # (landed net chain head {w280_total} machine-read at freeze time)",
    "        # -- ZERO in-flight upstream seats at splice, clean precondition",
    "        # freeze window; the finalize merge loop derives the wave",
    "        # set from registry keys at run time and stays",
    "        # FAIL-CLOSED, r307 two-state law).",
    f"        for _depw in range(17, {NEW_W}):",
    "            assert os.path.exists(os.path.join(",
    '                OUT_DIR, WAVE_CONFIGS[_depw]["out_name"])), \\',
    f'                f"W{NEW_W} finalize cumulative dep (W{{_depw}} output) missing"',
    "        # finalize wave-set derivation face (r511 derive law): every",
    f"        # registered wave below {NEW_W} composes; wave 15 excluded by",
    "        # design; SINGLE STATE (W2..W280 all registered).",
    f"        assert sorted(w for w in WAVE_CONFIGS if w < {NEW_W}) == \\",
    "            [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] + \\",
    f"            [w for w in range(16, {NEW_W})], \\",
    f'            "W{NEW_W} prior-wave set must derive from registry keys (no 15)"',
    "        assert os.path.exists(os.path.join(",
    f'            PATHS.root, "research", "PERPETUAL_N1_W{NEW_W}_PREREG.md")), \\',
    f'            "W{NEW_W} per-wave prereg missing (materializer requirement)"',
    '        assert pickle.dumps(_worker_init), "spawn-carrier unpicklable"',
    "    finally:",
    "        _set_wave(2)",
]
block = EOL.join(hdr) + EOL + par_sec + legs_kept + fresh_legs + EOL + EOL.join(tail) + EOL
# family #6 triple gate at the new wave (the block's own boundary is w<NEW_W>)
_n = str(NEW_W)
assert block.count(f"if w < {_n})") == 3, f"family-6 triple: w<{_n} count {block.count(f'if w < {_n})')} != 3"
assert block.count(f"if w < {NEW_W - 1})") == 0, "family-6 triple: stale boundary leaked"
assert block.count(f"range(16, {_n})") == 1 and block.count(f"range(17, {_n})") == 1, "family-6 triple: RHS ranges wrong"
assert block.count(f"registered wave below {_n} composes") == 1, "family-6 triple: comment face wrong"
old_blk_anchor = must(n1_t2, "    # --- T-141 s2 lane face", 1, "t141_marker")
n1_t3 = n1_t2.replace(old_blk_anchor, block + old_blk_anchor, 1)

# ---------- n1 print line ----------
pr = [
    f'          "+ W{NEW_W} materializer face [same guard set, dep=W17..W{PREV_W} "',
    f'          "outputs ALL PRESENT (landed net chain head {w280_total} = W280 bm-c finalize one-pass, K={w280_merged_n}) -- "',
    f'          "TWO HUNDRED AND EIGHTY-FIRST ENGINE-OWNED WAVE BY MACHINE-DERIVE (engine_owner rows {len(owner_rows_live)} + candidate) "',
    f'          "bm-c\'s HUNDREDTH owned claim per machine-derive (engine_owner==bm-c rows {len(bmc_rows_live)} + candidate), "',
    '          "A=1-HOP STAIRCASE-AFFECTS-A walk (hops=1, THIRTY-FIRST consecutive) "',
    '          "+ B=1-HOP own-A RESERVATION CASCADE above own-A (hops=1, THIRTY-SECOND consecutive), "',
    '          "chain-order splice from the committed ADMIT receipt + seed_admit_gate rc0 both bands FREE, "',
    '          "law sec.4 W281 row, bm-c loop CEO fill-order RE-ISSUE 23:1x] "',
]
old_pr = must(n1_t3, '          "+ T-141 s2 ', 1, "print_t141")
n1_t4 = n1_t3.replace(old_pr, EOL.join(pr) + EOL + old_pr, 1)

# ---------- post-edit count gates ----------
assert n1_t4.count('"batch": "PERPETUAL-N1-W281"') == 1
assert n1_t4.count("# --- W281 materializer face") == 1
assert n1_t4.count('"+ W281 materializer face') == 1
assert n1_t4.count('281: {"batch": "PERPETUAL-N1-W281"') == 1
assert pf_t2.count(ROW_I + '281: {"a"') == 1
assert n1_t4.count('    # --- T-141 s2 lane face') == 1
assert n1_t4.count('"PERPETUAL-N1-W281-SHARD-0"') == 1
for _lw in range(248, NEW_W):
    _first = (f'assert pf.N1_BANDS[{_lw}] == {{"a": '
              f'({fmt(pf_mod.N1_BANDS[_lw]["a"][0])}, {fmt(pf_mod.N1_BANDS[_lw]["a"][1])}),')
    _got = n1_t4.count(_first)
    assert _got == NEW_W - _lw, f"W{_lw} leg count drift: {_got} != {NEW_W - _lw}"
for _b in range(209, NEW_W + 1):
    assert n1_t4.count(f"    # --- W{_b} materializer face") == 1, f"W{_b} block kept-count drift"
for seg in (pf_comment, cfg_block, block, EOL.join(pr)):
    for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", seg):
        lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
        assert lo <= hi, f"malformed window {m.group(0)} in inserted prose"

# ---------- write + AST gate ----------
open(PF, "wb").write(pf_t2.encode("utf-8"))
open(N1, "wb").write(n1_t4.encode("utf-8"))
import py_compile
py_compile.compile(PF, doraise=True)
py_compile.compile(N1, doraise=True)

receipt = {
    "machine": "bm-c", "wave": 280, "spliced_wave": NEW_W,
    "phase": "five-face freeze chain-order splice (bm-c own-seat freeze window, upstream W280 ALL LANDED clean precondition incl finalize)",
    "origin_base": omain,
    "pf_sha16_pre": hashlib.sha256(pf_b).hexdigest()[:16],
    "n1_sha16_pre": hashlib.sha256(n1_b).hexdigest()[:16],
    "pf_sha16_post": hashlib.sha256(pf_t2.encode("utf-8")).hexdigest()[:16],
    "n1_sha16_post": hashlib.sha256(n1_t4.encode("utf-8")).hexdigest()[:16],
    "bands": {"A": [a_lo, a_hi], "B": [b_lo, b_hi]},
    "admit_receipt": "results/_w281bmc_20261020_probe_receipt.json",
    "seed_admit_gate": gate_lines,
    "banned_gate": "ADMIT rc0 (re-run at freeze window)",
    "band_semantics": {
        "A": "1-HOP STAIRCASE-AFFECTS-A walk THIRTY-FIRST consecutive A-hop (naive 633_301..635_300 refused at start by the registered W280 B band 633_301..633_500; hops=1; A base == registered prior-wave B tail+1 EXACT)",
        "B": "1-HOP own-A RESERVATION CASCADE above own-A (naive 633_501..633_700 clean vs registered but lands inside the own-wave A first-clean window; hops=1; B base == own-A tail+1 EXACT; THIRTY-SECOND consecutive above-own-A)"},
    "upstream_w280": {"freeze_sha": w280_freeze_sha, "prereg_sha": w280_prereg_sha,
                      "ledger_total": w280_total, "merged_n": w280_merged_n},
    "own_seat_face": {"seat_msg": SEAT_MSG, "seat_origin": SEAT_ORIGIN,
                      "prereg_commit": w281_prereg_sha, "probe_receipt_sha": w281_receipt_sha},
    "downstream_seat": rec["legs"]["leg4"]["note"],
    "seat": seat_found,
    "parity": {"bytes": len(par_sec) + len(legs_kept),
               "estate_row_asserts": par_sec.count("assert pf.N1_BANDS["),
               "kept_legs_row_asserts": legs_kept.count("assert pf.N1_BANDS["),
               "dropped_legs_row_asserts": legs_dropped.count("assert pf.N1_BANDS["),
               "fresh_legs_row_asserts": NEW_W - 248,
               "total_parity_rows": par_sec.count("assert pf.N1_BANDS[")
                                    + legs_kept.count("assert pf.N1_BANDS[") + (NEW_W - 248)},
    "family6_triple_gate": {"absorbed": True, "boundary": NEW_W},
    "eol": {"n1_crlf": EOL == "\r\n", "pf_crlf": PF_EOL == "\r\n"},
    "prereg_placeholder_heal": "research/PERPETUAL_N1_W281_PREREG.md seat placeholders @@SEAT_HHMM@@->0225 / @@SEAT_SHA@@->1c9ff56dcd and the mislabelled bmc-w282-seat->bmc-w281-seat (r1133 frozen face left them unfilled; healed at this splice window per the W280 gate0.5 placeholder law, judging criteria untouched)",
}
open(RECEIPT_OUT, "w", encoding="utf-8").write(json.dumps(receipt, indent=1))
print(json.dumps({k: receipt[k] for k in ("phase", "origin_base", "pf_sha16_post", "n1_sha16_post",
                                          "bands", "upstream_w280", "parity")}, indent=1))
print("SPLICE OK -- py_compile both green; NEXT: selftest -> pathspec commit+push -> engine self-ignite W281")