# -*- coding: utf-8 -*-
"""r890 bm-a generator: builds results/_r890bma_w189_prereg_build.py by
AST-extracting the r888 build script's BACK188/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK189
pairs as (token, rolled W189 value).  Old side = the W188-era value
(freeze-time blob b2608fe43 at prereg-freeze commit edec49746,
byte-identical to five-face-freeze commit b66117659; extracted
byte-verbatim to results/_r890bma_w189_prereg_src.txt by the r890
first-leg preflight, re-verified below), new side = the S86 W189 fact
map applied to that W188 text.
r773/r775/r781/r830/r833 compliance inherited: token-first two-phase
vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved; pre-TOK sequential DRY below
(r833 law 2, zero writes until all green).

TWO-FACE src disclosure (bloodline of the r881/r885/r888 two-face law):
  * the CURRENT disk face of research/PERPETUAL_N1_W188_PREREG.md
    = the POST-sec7/sec8-backfill FINAL face (r890 backfill committed
    this window 43322a984, 25,206B) -- NOT usable as build src: the
    sec7/sec8 regions are un-tokenized and would leak W188 finalize
    actuals into the W189 pre-registration;
  * results/_r890bma_w189_prereg_src.txt (21,697B, the r890 first-leg
    extract) = the freeze-time PRE-backfill face (blob b2608fe43 at
    edec49746 == b66117659), sec7/sec8 as placeholders -- the src law.

Structural notes vs the r888 bloodline (disclosed):
  * the anchor procrastination-precedent list rides FIXED
    (W159/W168/W169, low-end restored via the cascade W181->W182;
    no NEW procrastination case in W188 -- sec7/sec8 landed r890
    open-window FIRST LEG (43322a984) with the next-window note
    disclosed in the sec7 header itself, W186/W187 second-window
    precedent family, non-procrastination asserted);
  * r739-stale-stamp family: the 'bm-a r844 dead-tail 收养窗' and
    'bm-a r839 承袭收口窗' session stamps ride verbatim (off-by-one
    wave-word + stale-session lineage quirk (f) inherited; head/K
    values roll machine-correct to 820,928/411,520 this window);
  * merged-mu 4dp display ROLLS this wave (-0.0928 -> -0.0929, rolls
    BACK toward the W186-era display, pure coincidence of the 4dp
    rounding, disclosed); w-only mu rolls -0.0825 -> -0.0986; sigma
    key 0.245115 HOLDS (NO pair, disclosed; W188 sigma 0.24511487
    rounds to the same 6dp display); p95 anchor 0.339 -> 0.3243
    (display precision 3dp->4dp face change, disclosed);
  * K-lift display ROLLS this wave (+0.0002 -> +0.0000; DSIGN=+
    at zero, two-consecutive-positive then flat, disclosed);
    line_pre 1.1859 -> 1.1862 ROLLS (NEW pair vs the S85 hold; the
    W188 n_eff 816,528->818,728 growth step, disclosed); line_merged
    1.1861 -> 1.1862 ROLLS;
  * se_mu chain appends W188 0.000382 (r888 chain-face narrowed);
  * seat-face semantic change disclosed: the W188 seat was pushed and
    self-archived in the SAME r887 window ('bm-a r887 窗自移'); the
    W189 seat was pushed r888 (744de26ef) and archived by the r889
    window ('bm-a r889 窗归档', cross-window archive, honest note) --
    the only non-pure-roll pair this generation;
  * cascade span 9 pairs this generation (W189->W190 down to
    W181->W182; the low end rolls the 已回填 precedent list);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both
    generations) roll to 189/188/187.

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r888bma_w189_probe_receipt.json rc0 ADMIT
    (leg0 registry 186 rows tail W188 ordinal 179 / bma_ordinal 105 /
    owner_rows 178 / bma_rows 104 / w187_ledger_head 818,728
    probe-time anchor pre-W188-finalize, r307 two-state burn-in-flight
    note; leg1 naive A 430_404..432_403 REFUSED at its own start by
    the registered W188 B band 430_404..430_603 -> honest forward
    walk 1 hop lands A 430_604..432_603 (staircase FORTY-NINTH
    instance E36 per receipt A_semantics; the W188 seat MSG leg4 +
    r887 W188-probe leg4 + W188 prereg sec5.5 succession notes
    anticipated and MANDATED this re-derive -- projection and receipt
    ordinals MATCH, no divergence face); naive B 430_604..430_803
    lands inside own-wave A 430_604..432_603 -> same-freeze mutual
    exclusion (W141 precedent leg2 law) -> reserved walk 1 hop lands
    B 432_604..432_803; leg2 conflicts 0; leg3 origin vacancy True at
    probe time (seat MSG published r888 744de26ef, r565 law held);
    leg4 W190+ projection A 432_604..434_603 hops=0 / B
    432_804..433_003 hops=0, B inside A);
  - W188 finalize landed r889 one-pass (n1_w188_results.json
    machine-read: ledger head 818,728 + 2,200 = 820,928 EXACT
    zero-delta vs frozen projection; merged K=411,520 EXACT; merged
    mu -0.09287936 4dp -0.0929 (display ROLLS); w188-only mu
    -0.098616 4dp -0.0986 (display ROLLS); sigma 0.24511487 6dp
    0.245115 (display HOLDS); se_mu_at_k411520 = 0.000382; skill_line
    line_pre_w188 1.1862 (display ROLLS) -> line_merged@411,520
    1.1862 (K-lift +0.0000, n_eff held 818,728); A p95 = 0.3243;
    audit finalize_only bm-a; voids LOWAMP-P1/P2); W188 sec7/sec8
    settle backfill landed the r890 window (this window, first-leg,
    commit 43322a984, next-window family note disclosed in the sec7
    header itself; on-disk W188 prereg text '820,928' + 'K=411,520' +
    'r890 回填窗' live-asserted below);
  - W188 freeze registered sha machine-derived = b66117659 (git log
    origin/main --grep "W188 five-face freeze"); W188 prereg freeze
    commit edec49746 (r888 window, blob b2608fe43 at both freeze
    commits, asserted live below); W189 seat push sha
    machine-derived = 744de26ef (git log --diff-filter=A on the seat
    MSG inbox path, r888 window); W189 seat self-ack archive move
    landed the bm-a r889 window (r889 round commit 0061ab8c7 'W189
    seat inbox processed'; cross-window archive, disclosed)."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W188 prereg blob (LF, byte-verbatim) ----------
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "edec49746:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "b2608fe43e9d51553a4a2ef4203342f2f787af5a", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "b66117659:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != five-face-freeze blob"
blob = subprocess.run(
    ["git", "show", "edec49746:research/PERPETUAL_N1_W188_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
assert len(blob) == 21697, len(blob)
open(r"results/_r890bma_w189_prereg_src.txt", "wb").write(blob)
ondisk = open(r"results/_r890bma_w189_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src re-write drift"
# two-face disclosure: the current face = post-backfill FINAL (r890)
_cur = io.open(r"research/PERPETUAL_N1_W188_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
print("W189 src verified (freeze face):", len(blob), "bytes (blob",
      BLOB_SHA[:10] + "); current face = post-backfill FINAL (",
      len(_cur), "bytes), disclosed two-face, build consumes freeze face")

# --- 1. AST-extract the r888 build script's BACK188 + EXPECT ---------------
src888 = io.open(r"results/_r888bma_w188_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src888)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK188 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK188" and \
           isinstance(node.value, ast.List):
            BACK188 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK188.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK188 is not None and EXPECT is not None, "BACK188/EXPECT not extracted"
assert len(BACK188) == 50 and len(EXPECT) == 50, (len(BACK188), len(EXPECT))
back188_map = dict(BACK188)
assert len(back188_map) == len(BACK188)
print("r888 BACK188 entries:", len(BACK188), "EXPECT entries:", len(EXPECT))

# --- 2. W189 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r888bma_w189_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "430604_432603", "B": "432604_432803"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [430604, 432603] and leg1["B"] == [432604, 432803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [430404, 432403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [430604, 430803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [430604, 430803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 432604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 186 and leg0["tail"] == "W188" and \
    leg0["ordinal"] == 179 and leg0["bma_ordinal"] == 105 and \
    leg0["owner_rows"] == 178 and leg0["bma_rows"] == 104 and \
    leg0["w187_ledger_head"] == 818728, leg0
assert leg4["W190p_A"] in ("432604..434603", "432_604..434_603") and \
    leg4["W190p_B"] in ("432804..433003", "432_804..433_003"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W190p_B_lands_inside_W190p_A"] is True, leg4
assert "FORTY-NINTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w188_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 411520, "W188 merged K drift"
assert npc["pre_w188_cumulative"]["n_values"] == 409320, "pre-W188 K drift"
assert npc["w188_only"]["n_values"] == 2200, "W188-only N drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_411520"] == 1.1862 and kl["line_pre_w188"] == 1.1862 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 818728, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k411520"] == 0.000382, "se_mu drift"
assert abs(npc["mu_delta_w188_vs_w187ext"] - (-0.016142)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3243, \
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 820928 and \
    res["science_gates"]["ledger"]["prev_total"] == 818728, \
    res["science_gates"]["ledger"]
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w188_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_411520"]
PRE4 = "%.4f" % kl["line_pre_w188"]
SEM4 = "%.6f" % npc["se_mu_at_k411520"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0929" and WONLY4 == "-0.0986" and SIG6 == "0.245115", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1862" and PRE4 == "1.1862" and SEM4 == "0.000382" \
    and P954 == "0.3243" and DELTA4 == "0.0000" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0929" and WONLY_U == "\u22120.0986", (MU_U, WONLY_U)
LEDG = "{:,}".format(820928)
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "820,928" and KNEW == "411,520" and NEFF == "818,728", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(411520 + 2200)
LEDGPROJ = "{:,}".format(820928 + 2200)
assert KPROJ == "413,720" and LEDGPROJ == "823,128", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=^W188 five-face freeze", "-1"], capture_output=True,
                    text=True)
W188_SHA = _r_.stdout.strip()
assert W188_SHA == "b66117659", W188_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W189 FREEZE", "-1"], capture_output=True,
                    text=True)
assert _r0.stdout.strip() == "", "origin already carries a W189 FREEZE (r511)"
_r0b = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W189 five-face freeze", "-1"], capture_output=True,
                     text=True)
assert _r0b.stdout.strip() == "", "origin already carries a W189 five-face freeze"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                      "--diff-filter=A",
                      "--", "fleet/inbox/MSG-2026-10-08-1815-bma-w189-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "744de26ef", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1815-bma-w189-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W189 seat MSG not on origin processed/ (r565 law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "430_604..432_603" in _seat_txt and "432_604..432_803" in _seat_txt, \
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "edec49746:research/PERPETUAL_N1_W188_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "b2608fe43e9d51553a4a2ef4203342f2f787af5a", \
    "src blob drift: %s" % _r4.stdout.strip()
# W188 sec7/sec8 settle backfill landed the r890 window (this window) --
# the anchor face cites it (commit 43322a984, first-leg family note)
w188p = io.open(r"research/PERPETUAL_N1_W188_PREREG.md", encoding="utf-8",
                newline="").read()
assert "820,928" in w188p and "K=411,520" in w188p, \
    "W188 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r890 \u56de\u586b\u7a97" in w188p, "W188 sec7 r890 window note missing"

A_BAND = "430_604..432_603"
B_BAND = "432_604..432_803"
NAIVE_A = "430_404..432_403"
NAIVE_B = "430_604..430_803"
PRIOR_B = "430_404..430_603"     # registered W188 B band (refusal band)
A_SEED, B_SEED = "430_604", "432_604"
SEAT_MSG = "MSG-2026-10-08-1815-bma-w189-seat"
W190p_A = "432_604..434_603"
W190p_B = "432_804..433_003"

# --- 3. S86 = W188->W189 ordered fact map ------------------------------------
# (r735 substring-order law preserved: projections consumed before the
#  naive rolls re-create them; own-B before prior-B; pool projection
#  composite before the bare K roll; LEDG head before NEFF re-creates
#  it; high ordinals before low; cascade high first; bare numerals
#  LAST.)
S86 = [
    # -- window/session composites (longest first) --
    ("\u5df2\u56de\u586b\uff08r888 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0\u00b7W159/W168/W169/W181 \u62d6\u5ef6\u7a97\u5148\u4f8b\u5bf9\u7167\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09",
     "\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0\u00b7W159/W168/W169/W181 \u62d6\u5ef6\u7a97\u5148\u4f8b\u5bf9\u7167\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09"),
    ("\u5df2\u56de\u586b\uff08r888 \u56de\u586b\u7a97\uff09",
     "\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\uff09"),
    ("r887 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r887 \u5355\u7a97",
     "r888 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r888 \u5355\u7a97"),
    ("\uff08r888 \u627f\u88ad", "\uff08r890 \u627f\u88ad"),
    ("r887 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0", "r888 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0"),
    ("\uff08r887 probe leg2/leg3 \u5b9e\u8dd1\uff09", "\uff08r888 probe leg2/leg3 \u5b9e\u8dd1\uff09"),
    ("r887 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=FORTY-EIGHTH",
     "r888 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=FORTY-NINTH"),
    ("FORTY-EIGHTH\uff08\u7b2c\u56db\u5341\u516b\u4f8b\uff09",
     "FORTY-NINTH\uff08\u7b2c\u56db\u5341\u4e5d\u4f8b\uff09"),
    ("r885 probe leg4", "r888 probe leg4"),
    ("\uff08r885 \u51bb\u7ed3\u4ef6\uff09", "\uff08r888 \u51bb\u7ed3\u4ef6\uff09"),
    ("_r887bma_w188_probe_receipt.json", "_r888bma_w189_probe_receipt.json"),
    ("MSG-2026-10-08-1717-bma-w188-seat", "MSG-2026-10-08-1815-bma-w189-seat"),
    ("943967370", "744de26ef"),
    ("\u3010r888\u3011", "\u3010r890\u3011"),
    ("r887 seat push", "r888 seat push"),
    ("\u81ea r887 \u6536\u53e3", "\u81ea r888 \u6536\u53e3"),
    ("bm-a r887 \u7a97\u81ea\u79fb", "bm-a r889 \u7a97\u5f52\u6863"),
    ("\u672c\u673a r887 \u5e2d\u4f4d", "\u672c\u673a r888 \u5e2d\u4f4d"),
    ("\uff08r887 seat push\u00b7r565 \u5f8b\uff09", "\uff08r888 seat push\u00b7r565 \u5f8b\uff09"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before
    #    the naive rolls re-create them; own-B consumed before prior-B) --
    ("430_404..432_403", "432_604..434_603"),      # proj-A (W190+)
    ("430_604..430_803", "432_804..433_003"),      # proj-B (W190+)
    ("430_404..430_603", "432_604..432_803"),      # own-B (W189 B)
    ("428_404..430_403", "430_604..432_603"),      # own-A (W189 A)
    ("428_204..428_403", "430_404..430_603"),      # prior-B (W188 B)
    ("428_204..430_203", "430_404..432_403"),      # naive-A window (W189)
    ("428_404..428_603", "430_604..430_803"),      # naive-B window (W189)
    ("428_403+1", "430_603+1"),
    ("430_403+1", "432_603+1"),
    ("428_404+j", "430_604+j"),
    ("430_404+j", "432_604+j"),
    # -- ordinals (high first: succession pair before own pair) --
    ("\u7b2c\u56db\u5341\u4e5d\u4f8b", "\u7b2c\u4e94\u5341\u4f8b"),
    ("\u7b2c\u56db\u5341\u516b\u4f8b", "\u7b2c\u56db\u5341\u4e5d\u4f8b"),
    ("\u7b2c 186 \u679a", "\u7b2c 187 \u679a"),
    ("\u884c 177+\u672c\u5019\u9009", "\u884c 178+\u672c\u5019\u9009"),
    ("\u7b2c\u4e00\u767e\u96f6\u56db\u679a", "\u7b2c\u4e00\u767e\u96f6\u4e94\u679a"),
    ("\u7b2c 178 \u6ce2", "\u7b2c 179 \u6ce2"),
    ("\u884c 103+\u672c\u5019\u9009", "\u884c 104+\u672c\u5019\u9009"),
    ("bm-a 103 \u884c\u6ce8\u518c", "bm-a 104 \u884c\u6ce8\u518c"),
    ("\u4e00\u767e\u516b\u5341\u4e94\u884c\u6ce8\u518c", "\u4e00\u767e\u516b\u5341\u516d\u884c\u6ce8\u518c"),
    ("\u673a\u8bc1 185 \u884c", "\u673a\u8bc1 186 \u884c"),
    ("\u4e00\u767e\u516b\u5341\u516d\u9762\u5b9e\u6d4b", "\u4e00\u767e\u516b\u5341\u4e03\u9762\u5b9e\u6d4b"),
    # -- n1_w forms (high first) --
    ("n1_w188", "n1_w189"),
    ("n1_w187", "n1_w188"),
    # -- wave-word cascade (high first; 9 pairs this wave -- the low end
    #    W181->W182 rolls the 已回填 precedent-list low-end) --
    ("W189", "W190"),
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    # -- bare-number leftovers --
    ("\u6ce2\u53f7 188=", "\u6ce2\u53f7 189="),
    ("--wave 188", "--wave 189"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; merged-mu 4dp display ROLLS
    #    -0.0928 -> -0.0929 this wave (rolls back toward the W186-era
    #    display, 4dp rounding coincidence, disclosed); w-only mu
    #    rolls -0.0825 -> -0.0986; p95 0.339 -> 0.3243 display
    #    precision change; line_pre 1.1859 -> 1.1862 ROLLS (NEW pair
    #    vs the S85 hold, n_eff growth step, disclosed); line_merged
    #    1.1861 -> 1.1862 ROLLS; K-lift +0.0002 -> +0.0000 ROLLS via
    #    @KLT@ construction; sigma 0.245115 HOLDS (NO pair,
    #    disclosed)) --
    ("**411,520 \u6295\u5f71**", "**" + KPROJ + " \u6295\u5f71**"),
    ("**1.1861**", "**" + LINE4 + "**"),
    ("**+0.0002**\u3010line_merged", "**" + DSIGN + DELTA4 + "**\u3010line_merged"),
    ("**0.339**", "**" + P954 + "**"),
    ("**\u22120.0825**", "**" + WONLY_U + "**"),
    ("**\u22120.0928**", "**" + MU_U + "**"),
    ("line_pre 1.1859", "line_pre " + PRE4),
    ("818,728", LEDG),
    ("816,528", NEFF),
    ("409,320", KNEW),
]


def s86(t):
    for old, new in S86:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / session-keyed faces / vestigial)
BACK189 = {
    "@CHAIN@": back188_map["@CHAIN@"] + "\uff1bW188=bm-a r888 freeze\uff08" + W188_SHA + "\uff09",
    "@KLT@": r1(back188_map["@KLT@"], "/W187 **+0.0002** \u5982\u5b9e\u62ab\u9732",
                "/W187 **+0.0002**/W188 **" + DSIGN + DELTA4 + "** \u5982\u5b9e\u62ab\u9732"),
    "@SEMT@": r1(back188_map["@SEMT@"], "**0.000384**\u2192W187 **0.000383**\u3011\uff09",
                 "**0.000384**\u2192W187 **0.000383**\u2192W188 **" + SEM4 + "**\u3011\uff09"),
    "@S55@": s86(back188_map["@S55@"]),
    "@SEATPUB@": s86(back188_map["@SEATPUB@"]),
    "@OWNCHAIN@": r1(back188_map["@OWNCHAIN@"],
                     "/W186/W187 \u6700\u8fd1\u81ea\u6709\u6ce2", "/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2"),
    "@N171@": "189",
    "@N170@": "188",
    "@N169@": "187",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK189[tok] = s86(back188_map[tok])
# @ORDINALS@ sequential r1 chain (r888 seven-pair bloodline, flat form)
_ordinal_base = back188_map["@ORDINALS@"]
for _old, _new in (
    ("\u7b2c 178 \u6ce2", "\u7b2c 179 \u6ce2"),
    ("\u7b2c\u4e00\u767e\u96f6\u56db\u679a", "\u7b2c\u4e00\u767e\u96f6\u4e94\u679a"),
    ("\u884c 103+\u672c\u5019\u9009", "\u884c 104+\u672c\u5019\u9009"),
    ("/W186/W187 \u6700\u8fd1\u81ea\u6709\u6ce2", "/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2"),
    ("\u6ce8\u518c\u8868 W187 \u884c\u540e", "\u6ce8\u518c\u8868 W188 \u884c\u540e"),
    ("MSG-2026-10-08-1717-bma-w188-seat", SEAT_MSG),
    ("943967370", SEAT_SHA),
):
    _ordinal_base = r1(_ordinal_base, _old, _new)
BACK189["@ORDINALS@"] = _ordinal_base
missing = [t for (t, _v) in BACK188 if t not in BACK189]
assert not missing, missing
extra = [t for t in BACK189 if t not in back188_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK189["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **\u62d2**" in chk \
    and "\uff08430_603+1\uff09" in chk and "FORTY-NINTH\uff08\u7b2c\u56db\u5341\u4e5d\u4f8b\uff09" in chk, chk[:250]
chk = BACK189["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A \u7a97 " + A_BAND in chk and "\uff08432_603+1\uff09" in chk, chk[:250]
chk = BACK189["@ANCHOR@"]
assert "W1..W188 N1 finalize \u5df2\u5168\u90e8\u843d\u5730" in chk and "**820,928**" in chk \
    and "K=411,520 \u5408\u5e76\u6c60" in chk and "bm-a r844 dead-tail \u6536\u517b\u7a97" in chk \
    and "\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0" in chk, chk[:250]
assert BACK189["@POOL@"] == "\u7d2f\u8ba1 null \u6c60=" + KNEW + "+2,200\uff08\u672c\u6ce2\uff09=**" + KPROJ + \
    " \u6295\u5f71**", BACK189["@POOL@"]
assert "**" + LINE4 + "**" in BACK189["@KLKEY@"] and "n_eff " + NEFF in \
    BACK189["@KLKEY@"], BACK189["@KLKEY@"]
assert "line_pre " + PRE4 in BACK189["@KLKEY@"], BACK189["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK189["@KLKEY@"], BACK189["@KLKEY@"]
assert BACK189["@WAVEFREE@"] == "\u6ce2\u53f7 189=\u6ce8\u518c\u8868 W188 \u884c\u540e\u9996\u4e2a\u81ea\u7531\u53f7", \
    BACK189["@WAVEFREE@"]
assert "n1_w189_results.json" in BACK189["@FN@"] and \
    "n1_w188_results.json" in BACK189["@ODOLD@"]
assert BACK189["@WAVECLI@"] == "--wave 189/finalize --wave 189", \
    BACK189["@WAVECLI@"]
assert "W190+ \u6295\u5f71" in BACK189["@S55@"] and W190p_A in BACK189["@S55@"] \
    and W190p_B in BACK189["@S55@"] and "\u7ee7\u627f\u7b2c\u4e94\u5341\u4f8b" in BACK189["@S55@"] \
    and "W189 B \u5e26 " + B_BAND in BACK189["@S55@"], BACK189["@S55@"][:200]
assert "verify at W190 prereg" in BACK189["@S55@"], BACK189["@S55@"][-120:]
assert SEAT_SHA in BACK189["@SEATPUB@"] and "r888 seat push" in \
    BACK189["@SEATPUB@"] and "\u81ea r888 \u6536\u53e3" in BACK189["@SEATPUB@"] \
    and "bm-a r889 \u7a97\u5f52\u6863" in BACK189["@SEATPUB@"], BACK189["@SEATPUB@"][:200]
assert "\u7b2c 179 \u6ce2" in BACK189["@ORDINALS@"] and "\u7b2c\u4e00\u767e\u96f6\u4e94\u679a" in \
    BACK189["@ORDINALS@"] and "/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2" in BACK189["@ORDINALS@"] \
    and "\u6ce8\u518c\u8868 W188 \u884c\u540e" in BACK189["@ORDINALS@"], BACK189["@ORDINALS@"][:200]
assert "W190+ \u6295\u5f71" in BACK189["@SEATSENT@"] and SEAT_MSG in \
    BACK189["@SEATSENT@"] and "\u7ee7\u627f\u7b2c\u4e94\u5341\u4f8b" in BACK189["@SEATSENT@"], \
    BACK189["@SEATSENT@"][:200]
assert "\u672c\u673a r888 \u5e2d\u4f4d" in BACK189["@SEATSENT@"] and \
    "\uff08r888 seat push\u00b7r565 \u5f8b\uff09" in BACK189["@SEATSENT@"], \
    BACK189["@SEATSENT@"][:200]
assert "\u6cd5\u5178 \u00a74 W189 \u884c A=" + A_BAND in BACK189["@ASEEDPROSE@"], \
    BACK189["@ASEEDPROSE@"][:250]
assert "\u6cd5\u5178 \u00a74 W189 \u884c B=" + B_BAND in BACK189["@BSEEDPROSE@"], \
    BACK189["@BSEEDPROSE@"][:250]
assert "\u51c0\u8d26\u672c\u951a\u5934 " + LEDG in BACK189["@S5ANCH@"] and "r839 \u627f\u88ad\u6536\u53e3\u7a97" in \
    BACK189["@S5ANCH@"] and "\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\uff09" in BACK189["@S5ANCH@"], \
    BACK189["@S5ANCH@"]
assert "K=" + KNEW + " \u5408\u5e76\u6c60" in BACK189["@S51@"] and \
    "**" + WONLY_U + "**" in BACK189["@S51@"], BACK189["@S51@"]
assert "**" + MU_U + "**" in BACK189["@S51@"], BACK189["@S51@"]
assert "**" + SIG6 + "**" in BACK189["@S52@"], BACK189["@S52@"]
assert "**" + P954 + "**" in BACK189["@S53@"], BACK189["@S53@"]
assert "\u4e00\u767e\u516b\u5341\u516d\u884c\u6ce8\u518c" in BACK189["@SCANFACE@"] and "\u8868\u5c3e W188 \u884c" in \
    BACK189["@SCANFACE@"] and "\u673a\u8bc1 186 \u884c" in BACK189["@SCANFACE@"], \
    BACK189["@SCANFACE@"]
assert BACK189["@EOB@"] == "engine_owner==bm-a 104 \u884c\u6ce8\u518c", BACK189["@EOB@"]
assert "PERPETUAL-N1-W189" in BACK189["@TITLE@"] and "\u7b2c 187 \u679a" in \
    BACK189["@TITLE@"] and "\u3010r890\u3011" in BACK189["@TITLE@"], BACK189["@TITLE@"]
assert "r888 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r888 \u5355\u7a97" in BACK189["@GATEW@"], \
    BACK189["@GATEW@"]
assert BACK189["@VAC@"] == "\uff08r888 probe leg2/leg3 \u5b9e\u8dd1\uff09", BACK189["@VAC@"]
assert "\uff08r890 \u627f\u88ad" in BACK189["@MERGE@"], BACK189["@MERGE@"]
assert "r888 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0" in BACK189["@CLAIMLAW@"], \
    BACK189["@CLAIMLAW@"]
assert BACK189["@PRC@"] == "results/_r888bma_w189_probe_receipt.json", \
    BACK189["@PRC@"]
assert "W188=bm-a r888 freeze\uff08" + W188_SHA + "\uff09" in BACK189["@CHAIN@"]
assert BACK189["@SEMT@"].endswith("**0.000384**\u2192W187 **0.000383**\u2192W188 **" + SEM4 + "**\u3011\uff09"), \
    BACK189["@SEMT@"][-60:]
assert BACK189["@KLT@"].endswith("/W187 **+0.0002**/W188 **" + DSIGN + DELTA4 + "** \u5982\u5b9e\u62ab\u9732"), \
    BACK189["@KLT@"][-60:]
assert BACK189["@OWNCHAIN@"].endswith("/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2"), \
    BACK189["@OWNCHAIN@"][-40:]
assert BACK189["@WPN2@"] == "W190+ \u6295\u5f71", BACK189["@WPN2@"]
assert BACK189["@W136TO@"] == "W136..W188", BACK189["@W136TO@"]
assert BACK189["@W2TO@"] == "W2..W188" and BACK189["@W1TO@"] == "W1..W188" \
    and BACK189["@V2W@"] == "v2..W188 \u843d\u5730", (BACK189["@W2TO@"],
                                                    BACK189["@W1TO@"],
                                                    BACK189["@V2W@"])
assert BACK189["@WN@"] == "W189" and BACK189["@W@"] == "W188" and \
    BACK189["@SD@"] == "n1_w189" and BACK189["@KOLD@"] == KNEW, \
    (BACK189["@WN@"], BACK189["@W@"], BACK189["@SD@"], BACK189["@KOLD@"])
assert BACK189["@ASEED@"] == "entry rng seed=**430_604+j**", BACK189["@ASEED@"]
assert "entry rng=**430_604+j**" in BACK189["@BENTRY@"], BACK189["@BENTRY@"]
assert BACK189["@PF@"] == "PERPETUAL_N1_W189_PREREG.md", BACK189["@PF@"]
assert BACK189["@R250@"] == "R250\uff1aW189 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9501", \
    BACK189["@R250@"]
assert BACK189["@S51B@"] == "\uff08W2..W188 \u5171\u4e00\u767e\u516b\u5341\u4e03\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff09", \
    BACK189["@S51B@"]
print("S86 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK189 = [(val, tok) for (tok, val) in BACK188]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK189:
    exp = EXPECT[tok]
    if exp == 0:
        # vestigial token (no slots since its generation); strays allowed
        # only inside the fixed historical MSG-183x references
        stripped = out_t.replace("MSG-183x", "")
        n = stripped.count(old)
        assert n == 0, "DRY vestigial %s: stray count=%d: %r" % (tok, n, old[:50])
        continue
    n = out_t.count(old)
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK189[t]) for (t, _v) in BACK188]:
    if EXPECT[tok] == 0:
        continue
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})",
                                        out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"\u6ce2\u53f7 1[78][0-9]", out_t)))
assert stale_wave == ["\u6ce2\u53f7 189"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w188", "n1_w189"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W189") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W189 freeze" not in out_t.replace("\uff1bW188=bm-a r888 freeze", ""), \
    "unexpected W189-freeze text"
# stale-session sweep: no W188-era session stamps may survive ("r888
# probe leg4" is the LEGAL new citation -- the W188 probe leg4 that
# anticipated the W189 staircase; only its 回执/leg2 faces must have
# rolled). NOTE: "−0.0928" IS stale this wave (merged-mu 4dp display
# ROLLS to -0.0929); "line_pre 1.1859" IS stale (display ROLLS to
# 1.1862); sigma 0.245115 HOLDS (NOT stale).
for stale in ("r887 probe \u56de\u6267", "\uff08r887 probe leg2", "r880 probe", "r881 \u51bb\u7ed3\u4ef6",
              "\u5df2\u56de\u586b\uff08r885", "\u5df2\u56de\u586b\uff08r888", "943967370", "\u3010r888\u3011",
              "FORTY-EIGHTH", "\u7b2c\u56db\u5341\u516b\u4f8b", "0.3004", "0.245086",
              "\u22120.1025", "\u22120.0825", "**\u22120.0928**", "**1.1861**",
              "line_pre 1.1859", "0.339", "407,120", "\u51c0\u8d26\u672c\u951a\u5934 818,728",
              "814,328", "MSG-2026-10-08-1717", "r887 seat push", "bm-a r887 \u7a97\u81ea\u79fb",
              "\u672c\u673a r887 \u5e2d\u4f4d", "\uff08r887 seat push",
              "_r887bma_w188_probe_receipt"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r888 probe leg4" in out_t, "new W188-probe-leg4 citation missing"
assert out_t.count("r888 probe leg4") == 3, \
    "r888 probe-leg4 count=%d (expect 3)" % out_t.count("r888 probe leg4")
assert out_t.count("\uff08r888 \u51bb\u7ed3\u4ef6\uff09") == 1, "r888 freeze-artifact citation missing"
assert out_t.count("r887") == 0, "r887 residual count=%d (expect 0)" % out_t.count("r887")
assert out_t.count("r885") == 0, "r885 residual count=%d (expect 0)" % out_t.count("r885")
assert out_t.count("r889") == 1, "r889 residual count=%d (expect 1 = seat archive window)" \
    % out_t.count("r889")
assert out_t.count("r880") == 0, "r880 residual count=%d (expect 0)" % out_t.count("r880")
assert out_t.count("r875") == 0, "r875 residual count=%d (expect 0)" % out_t.count("r875")
assert out_t.count("r841") == 0, "r841 residual count=%d (expect 0)" % out_t.count("r841")
assert out_t.count("W189 finalize \u7a97") == 2 and \
    "W188 finalize \u7a97" not in out_t, "sec7/8 placeholder wave faces missing"
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN" % len(TOK189))

# --- 5. emit the W189 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r890 bm-a W189 per-wave prereg build: transforms the freeze-time W188
prereg (git blob b2608fe43 -- file research/PERPETUAL_N1_W188_PREREG.md
at prereg-freeze commit edec49746, byte-identical to five-face-freeze
commit b66117659; extracted byte-verbatim to
results/_r890bma_w189_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W189_PREREG.md.  The post-sec7/sec8-backfill
FINAL face (r890 backfill commit 43322a984, this window) is NOT the
build src -- sec7/sec8 regions are un-tokenized and would leak W188
actuals; disclosed two-face in the buildgen docstring.

Generated by results/_r890bma_w189_buildgen.py (TOK/BACK pairs
AST-extracted from the r888 build script -- no exec of its live
asserts; r773/r775/r781/r830/r833 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r888 probe ADMIT naive A 430_404..432_403 refused by W188 B
430_404..430_603 -> A 430_604..432_603 staircase 49th E36 / B
432_604..432_803 own-A reservation W141 leg2; W188 finalize r889
one-pass (K 411,520 EXACT / head 820,928 EXACT delta zero vs frozen
projection / merged mu -0.0929 4dp display ROLLS back / w-only -0.0986
display ROLLS / sigma 0.245115 HOLDS / skill_line 1.1862 -> 1.1862
K-lift +0.0000 flat / n_eff 818,728 / A p95 0.3243); W188 sec7/sec8
settle backfill landed the r890 window (this window, commit 43322a984,
first-leg family note disclosed); W188 freeze b66117659 (prereg freeze
edec49746 r888); W189 seat push 744de26ef r888; seat self-ack archive
move landed the bm-a r889 window (cross-window archive, disclosed);
anchor r844/r839 stale-session lineage stamps ride (quirk (f)
inherited, disclosed).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r890bma_w189_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W189_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r888bma_w189_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "430604_432603", "B": "432604_432803"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [430604, 432603] and leg1["B"] == [432604, 432803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [430404, 432403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [430604, 430803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [430604, 430803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 432604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 186 and leg0["tail"] == "W188" and \\
    leg0["ordinal"] == 179 and leg0["bma_ordinal"] == 105 and \\
    leg0["owner_rows"] == 178 and leg0["bma_rows"] == 104 and \\
    leg0["w187_ledger_head"] == 818728, leg0
assert leg4["W190p_A"] in ("432604..434603", "432_604..434_603") and \\
    leg4["W190p_B"] in ("432804..433003", "432_804..433_003"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W190p_B_lands_inside_W190p_A"] is True, leg4
assert "FORTY-NINTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w188_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 411520, "W188 merged K drift"
assert npc["pre_w188_cumulative"]["n_values"] == 409320, "pre-W188 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_411520"] == 1.1862 and kl["line_pre_w188"] == 1.1862 \\
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 818728, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k411520"] == 0.000382, "se_mu drift"
assert abs(npc["mu_delta_w188_vs_w187ext"] - (-0.016142)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3243, \\
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 820928, "ledger head drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w188_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0929" and WONLY4 == "-0.0986" and SIG6 == "0.245115", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(820928)
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "820,928" and KNEW == "411,520", (LEDG, KNEW)
KPROJ = "{:,}".format(411520 + 2200)
LEDGPROJ = "{:,}".format(820928 + 2200)
assert KPROJ == "413,720" and LEDGPROJ == "823,128", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=^W188 five-face freeze", "-1"], capture_output=True, text=True)
W188_SHA = _r.stdout.strip()
assert W188_SHA == "b66117659", W188_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W189 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W189 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-1815-bma-w189-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "744de26ef", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1815-bma-w189-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W189 seat MSG not on origin processed/ (r565 law)"
assert "430_604..432_603" in _r3.stdout.decode("utf-8", "replace"), \\
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "edec49746:research/PERPETUAL_N1_W188_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "b2608fe43e9d51553a4a2ef4203342f2f787af5a", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W188 sec7/sec8 settle backfill landed the r890 window (this window) --
# the anchor face cites it (commit 43322a984, first-leg family note)
w188p = io.open(r"research/PERPETUAL_N1_W188_PREREG.md", encoding="utf-8",
                newline="").read()
assert "820,928" in w188p and "K=411,520" in w188p, \\
    "W188 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r890 \\u56de\\u586b\\u7a97" in w188p, "W188 sec7 r890 window note missing"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W188" in src and "428_404..430_403" in src, "src face drift"
'''

TAIL = '''
TOK189 = %s
BACK189 = %s

EXPECT = %s

out_t = src
for old, tok in TOK189:
    exp = EXPECT[tok]
    if exp == 0:
        stripped = out_t.replace("MSG-183x", "")
        n = stripped.count(old)
        assert n == 0, f"vestigial token {tok}: stray count={n}"
        continue
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK189:
    if EXPECT[tok] == 0:
        continue
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 189"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w188", "n1_w189"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W189") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W189 freeze" not in out_t.replace("；W188=bm-a r888 freeze", ""), \\
    "unexpected W189-freeze text"

# stale-session sweep ("r888 probe leg4" = LEGAL new citation -- the W188
# probe leg4 that anticipated the W189 staircase; merged-mu 4dp display
# ROLLS to -0.0929 this wave -- "−0.0928" IS a stale token; line_pre
# 1.1859 -> 1.1862 ROLLS; sigma 0.245115 HOLDS -- NOT stale)
for stale in ("r887 probe 回执", "（r887 probe leg2", "r880 probe", "r881 冻结件",
              "已回填（r885", "已回填（r888", "943967370", "【r888】", "FORTY-EIGHTH",
              "第四十八例", "0.3004", "0.245086", "−0.1025", "−0.0825", "**−0.0928**",
              "**1.1861**", "line_pre 1.1859", "0.339", "407,120", "净账本锚头 818,728",
              "814,328", "MSG-2026-10-08-1717", "r887 seat push", "bm-a r887 窗自移",
              "本机 r887 席位", "（r887 seat push", "_r887bma_w188_probe_receipt"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r888 probe leg4" in out_t, "new W188-probe-leg4 citation missing"
assert out_t.count("r888 probe leg4") == 3, "r888 probe-leg4 count=%%d (expect 3)"
assert out_t.count("（r888 冻结件）") == 1, "r888 freeze-artifact citation missing"
assert out_t.count("r887") == 0, "r887 residual count=%%d (expect 0)"
assert out_t.count("r885") == 0, "r885 residual count=%%d (expect 0)"
assert out_t.count("r889") == 1, "r889 residual count=%%d (expect 1 = seat archive window)"
assert out_t.count("r880") == 0, "r880 residual count=%%d (expect 0)"
assert out_t.count("r875") == 0, "r875 residual count=%%d (expect 0)"
assert out_t.count("r841") == 0, "r841 residual count=%%d (expect 0)"
assert out_t.count("W189 finalize 窗") == 2, "sec7/8 placeholder wave face missing"
assert "W188 finalize 窗" not in out_t, "stale sec7/8 placeholder wave face"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W189 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK189)
back_lit = repr([(t, BACK189[t]) for (t, _v) in BACK188])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results/_r890bma_w189_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r890bma_w189_prereg_build.py", len(out), "bytes")
