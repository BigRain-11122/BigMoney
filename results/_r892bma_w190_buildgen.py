# -*- coding: utf-8 -*-
"""r892 bm-a generator: builds results/_r892bma_w190_prereg_build.py by
AST-extracting the r890 build script's BACK189/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK210
pairs as (token, rolled W190 value).  Old side = the W189-era value
(freeze-time blob 735f7c288 at prereg-freeze commit 632761894,
byte-identical to five-face-registration commit 8addea3eb; extracted
byte-verbatim to results/_r892bma_w190_prereg_src.txt by the r892
first-leg preflight, re-verified below), new side = the S87 W190 fact
map applied to that W189 text.
r773/r775/r781/r830/r833 compliance inherited: token-first two-phase
vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved; pre-TOK sequential DRY 50/50 below
(r833 law 2, zero writes until all green).

TWO-FACE src disclosure (bloodline of the r881/r885/r888/r890 two-face
law):
  * the CURRENT disk face of research/PERPETUAL_N1_W189_PREREG.md
    = the POST-sec7/sec8-backfill FINAL face (r892 backfill committed
    this window, 25,317B) -- NOT usable as build src: the sec7/sec8
    regions would leak W189 finalize actuals into the W190
    pre-registration;
  * results/_r892bma_w190_prereg_src.txt (21,767B, the r892 first-leg
    extract) = the freeze-time PRE-backfill face (blob 735f7c288 at
    632761894 == 8addea3eb), sec7/sec8 as placeholders -- the src law.

Structural notes vs the r890 bloodline (disclosed):
  * the anchor procrastination-precedent list rides FIXED
    (W159/W168/W169, low-end restored via the cascade W182->W183;
    no NEW procrastination case in W189 -- sec7/sec8 landed r892
    open-window FIRST LEG (this window) with the next-window note
    disclosed in the sec7 header itself, W186/W187/W188
    second-window precedent family, non-procrastination asserted);
  * r739-stale-stamp family: the 'bm-a r844 dead-tail 收养窗' and
    'bm-a r839 承袭收口窗' session stamps ride verbatim (off-by-one
    wave-word + stale-session lineage quirk (f) inherited; head/K
    values roll machine-correct to 823,128/413,720 this window);
  * merged-mu 4dp display HOLDS this wave (-0.0929 -> -0.0929, NO
    pair, disclosed; 4dp rounding coincidence of the W189 merged
    mu); w-only mu rolls -0.0986 -> -0.0878 (display ROLLS); sigma
    key 0.245115 -> 0.245164 ROLLS this wave (NEW pair vs the S86
    hold; W189 merged sigma 0.24516370 rounds to a new 6dp display);
    p95 anchor 0.3243 -> 0.3447 (rolls);
  * K-lift display ROLLS this wave (+0.0000 -> +0.0003; W150/W151
    rise-after-flat precedent family); line_pre 1.1862 -> 1.1863
    ROLLS (n_eff growth step 818,728->820,928); line_merged
    1.1862 -> 1.1866 ROLLS;
  * se_mu chain appends W189 0.000381 (constructed token, chain
    preserved);
  * seat-face semantic change disclosed: the W189 seat was pushed
    r888 (744de26ef) and archived by the r889 window (cross-window);
    the W190 seat was pushed r891 (c177bf73b -- carried by the r891
    main commit, path-derived) and archived by the r892 window
    (cross-window archive, this window, on-disk live-verified) --
    pure-roll form preserved, 'bm-a r892 窗归档';
  * cascade span 9 pairs this generation (W190->W191 down to
    W182->W183; the low end rolls the 已回填 precedent list);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both
    generations) roll to 190/189/188.

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r891bma_w190_probe_receipt.json rc0 ADMIT
    (leg0 registry 187 rows tail W189 ordinal 180 / bma_ordinal 106 /
    owner_rows 179 / bma_rows 105 / w189_ledger_head 823,128
    finalize-LANDED same-window r891; leg1 naive A 432_604..434_603
    REFUSED at its own start by the registered W189 B band
    432_604..432_803 -> honest forward walk 1 hop lands A
    432_804..434_803 (staircase FIFTIETH instance E36 per receipt
    A_semantics; the W189 seat MSG leg4 + r891 W189-probe leg4 +
    W189 materializer W190+ projection anticipated and MANDATED this
    re-derive -- projection and receipt ordinals MATCH, no divergence
    face); naive B 432_804..433_003 lands inside own-wave A
    432_804..434_803 -> same-freeze mutual exclusion (W141 precedent
    leg2 law) -> reserved walk 1 hop lands B 434_804..435_003; leg2
    conflicts 0; leg3 origin vacancy True at probe time (seat MSG
    published r891 c177bf73b, r565 law held); leg4 W191+ projection
    A 434_804..436_803 hops=0 / B 435_004..435_203 hops=0, B inside
    A);
  - W189 finalize landed r891 one-pass (n1_w189_results.json
    machine-read: ledger head 820,928 + 2,200 = 823,128 EXACT
    zero-delta vs frozen projection; merged K=413,720 EXACT; merged
    mu -0.09285218 4dp -0.0929 (display HOLDS); w189-only mu
    -0.08776832 4dp -0.0878 (display ROLLS); sigma 0.24516370 6dp
    0.245164 (display ROLLS); se_mu_at_k413720 = 0.000381; skill_line
    line_pre_w189 1.1863 (display ROLLS) -> line_merged@413,720 1.1866
    (K-lift +0.0003, n_eff held 820,928); A p95 = 0.3447;
    audit finalize_only bm-a; voids LOWAMP-P1/P2); W189 sec7/sec8
    settle backfill landed the r892 window (this window, first-leg,
    backfill script machine-verified; on-disk W189 prereg text
    '823,128' + 'K=413,720' + 'r892 回填窗' live-asserted below);
  - W189 five-face freeze registration sha machine-derived =
    8addea3eb (GENERATION FACT CHANGE disclosed: the W189 pf/n1
    registry insertions rode the r890 round closeout commit
    8addea3eb -- no standalone anchored 'W189 five-face freeze'
    subject exists; derived content-anchored via git log -S '189:
    {"a": (430_604' -- scripts/perpetual_faces.py, r812 path-derived
    precedent); W189 prereg freeze commit 632761894 (r890 window,
    blob 735f7c288 at both commits, asserted live below); W190 seat
    push sha machine-derived = c177bf73b (git log --diff-filter=A on
    the seat MSG inbox path, r891 window); W190 seat self-ack archive
    move landed the bm-a r892 window (this window, on-disk processed/
    live-verified; the origin inbox face holds r565; cross-window
    archive, disclosed)."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W189 prereg blob (LF, byte-verbatim) ----------
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "735f7c288539d58a181cacab9b9335fc632e7a33", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "8addea3eb:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registration blob"
blob = subprocess.run(
    ["git", "show", "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
assert len(blob) == 21767, len(blob)
open(r"results/_r892bma_w190_prereg_src.txt", "wb").write(blob)
ondisk = open(r"results/_r892bma_w190_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src re-write drift"
# two-face disclosure: the current face = post-backfill FINAL (r892)
_cur = io.open(r"research/PERPETUAL_N1_W189_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
print("W190 src verified (freeze face):", len(blob), "bytes (blob",
      BLOB_SHA[:10] + "); current face = post-backfill FINAL (",
      len(_cur), "bytes), disclosed two-face, build consumes freeze face")

# --- 1. AST-extract the r890 build script's BACK189 + EXPECT ----------------
src890 = io.open(r"results/_r890bma_w189_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src890)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK189 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK189" and \
           isinstance(node.value, ast.List):
            BACK189 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK189.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK189 is not None and EXPECT is not None, "BACK189/EXPECT not extracted"
assert len(BACK189) == 50 and len(EXPECT) == 50, (len(BACK189), len(EXPECT))
back189_map = dict(BACK189)
assert len(back189_map) == len(BACK189)
print("r890 BACK189 entries:", len(BACK189), "EXPECT entries:", len(EXPECT))

# --- 2. W190 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r891bma_w190_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "432804_434803", "B": "434804_435003"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [432804, 434803] and leg1["B"] == [434804, 435003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [432604, 434603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [432804, 433003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [432804, 433003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 434804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 187 and leg0["tail"] == "W189" and \
    leg0["ordinal"] == 180 and leg0["bma_ordinal"] == 106 and \
    leg0["owner_rows"] == 179 and leg0["bma_rows"] == 105 and \
    leg0["w189_ledger_head"] == 823128, leg0
assert leg4["W191p_A"] in ("434804..436803", "434_804..436_803") and \
    leg4["W191p_B"] in ("435004..435203", "435_004..435_203"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W191p_B_lands_inside_W191p_A"] is True, leg4
assert "FIFTIETH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w189_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 413720, "W189 merged K drift"
assert npc["pre_w189_cumulative"]["n_values"] == 411520, "pre-W189 K drift"
assert npc["w189_only"]["n_values"] == 2200, "W189-only N drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_413720"] == 1.1866 and kl["line_pre_w189"] == 1.1863 \
    and abs(kl["line_delta_k_lift"] - 0.0003) < 1e-12 \
    and kl["n_eff_held_equal"] == 820928, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k413720"] == 0.000381, "se_mu drift"
assert abs(npc["mu_delta_w189_vs_w188ext"] - 0.010848) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3447, \
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 823128 and \
    res["science_gates"]["ledger"]["prev_total"] == 820928, \
    res["science_gates"]["ledger"]
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w189_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_413720"]
PRE4 = "%.4f" % kl["line_pre_w189"]
SEM4 = "%.6f" % npc["se_mu_at_k413720"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0929" and WONLY4 == "-0.0878" and SIG6 == "0.245164", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1866" and PRE4 == "1.1863" and SEM4 == "0.000381" \
    and P954 == "0.3447" and DELTA4 == "0.0003" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0929" and WONLY_U == "\u22120.0878", (MU_U, WONLY_U)
LEDG = "{:,}".format(823128)
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "823,128" and KNEW == "413,720" and NEFF == "820,928", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(413720 + 2200)
LEDGPROJ = "{:,}".format(823128 + 2200)
assert KPROJ == "415,920" and LEDGPROJ == "825,328", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h", "-n", "1",
                      "-S", '189: {"a": (430_604', "--",
                      "scripts/perpetual_faces.py"],
                     capture_output=True, text=True)
W189_SHA = _r_.stdout.strip()
assert W189_SHA == "8addea3eb", W189_SHA
_r_g = subprocess.run(["git", "log", "origin/main", "--format=%h",
                       "--grep=^W189 five-face freeze", "-1"],
                      capture_output=True, text=True)
assert _r_g.stdout.strip() == "", \
    "unexpected standalone W189 five-face-freeze subject (disclosed " \
    "generation fact: registration rode 8addea3eb)"
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W190 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W190 FREEZE (r511)"
_r0b = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W190 five-face freeze", "-1"], capture_output=True,
                     text=True)
assert _r0b.stdout.strip() == "", "origin already carries a W190 five-face freeze"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-n", "1",
                      "--diff-filter=A",
                      "--", "fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "c177bf73b", SEAT_SHA
_r3a = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/"
                      "MSG-2026-10-08-2035-bma-w190-seat.md"],
                     capture_output=True)
_r3b = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-2035-bma-w190-seat.md"],
                     capture_output=True)
assert _r3a.returncode == 0 or _r3b.returncode == 0, \
    "W190 seat MSG not on origin (inbox/processed union, r565 law + r374 dual-path)"
_seat_txt = (_r3a if _r3a.returncode == 0 else _r3b).stdout.decode(
    "utf-8", "replace")
assert "432_804..434_803" in _seat_txt and "434_804..435_003" in _seat_txt, \
    "seat band face drift"
import os
assert os.path.exists(os.path.join(
    "fleet", "inbox", "processed", "MSG-2026-10-08-2035-bma-w190-seat.md")), \
    "W190 seat MSG not in on-disk processed/ (r892-window archive move)"
_r4 = subprocess.run(["git", "rev-parse",
                     "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "735f7c288539d58a181cacab9b9335fc632e7a33", \
    "src blob drift: %s" % _r4.stdout.strip()
# W189 sec7/sec8 settle backfill landed the r892 window (this window) --
# the anchor face cites it (backfill script machine-verified numbers)
w189p = io.open(r"research/PERPETUAL_N1_W189_PREREG.md", encoding="utf-8",
                newline="").read()
assert "823,128" in w189p and "K=413,720" in w189p, \
    "W189 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r892 \u56de\u586b\u7a97" in w189p, "W189 sec7 r892 window note missing"

A_BAND = "432_804..434_803"
B_BAND = "434_804..435_003"
NAIVE_A = "432_604..434_603"
NAIVE_B = "432_804..433_003"
PRIOR_B = "432_604..432_803"     # registered W189 B band (refusal band)
A_SEED, B_SEED = "432_804", "434_804"
SEAT_MSG = "MSG-2026-10-08-2035-bma-w190-seat"
W191p_A = "434_804..436_803"
W191p_B = "435_004..435_203"

# --- 3. S87 = W189->W190 ordered fact map -------------------------------------
# (r735 substring-order law preserved: projections consumed before the
#  naive rolls re-create them; own-B before prior-B; pool projection
#  composite before the bare K roll; LEDG head before NEFF re-creates
#  it; high ordinals before low; cascade high first; bare numerals
#  LAST.)
S87 = [
    # -- window/session composites (longest first) --
    ("\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0\u00b7W159/W168/W169/W182 \u62d6\u5ef6\u7a97\u5148\u4f8b\u5bf9\u7167\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09",
     "\u5df2\u56de\u586b\uff08r892 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0\u00b7W159/W168/W169/W182 \u62d6\u5ef6\u7a97\u5148\u4f8b\u5bf9\u7167\u00b7\u5982\u5b9e\u6ce8\u8bb0\uff09"),
    ("\u5df2\u56de\u586b\uff08r890 \u56de\u586b\u7a97\uff09",
     "\u5df2\u56de\u586b\uff08r892 \u56de\u586b\u7a97\uff09"),
    ("r888 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r888 \u5355\u7a97",
     "r891 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r891 \u5355\u7a97"),
    ("\uff08r890 \u627f\u88ad", "\uff08r892 \u627f\u88ad"),
    ("r888 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0", "r891 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0"),
    ("\uff08r888 probe leg2/leg3 \u5b9e\u8dd1\uff09", "\uff08r891 probe leg2/leg3 \u5b9e\u8dd1\uff09"),
    ("r888 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=FORTY-NINTH",
     "r891 probe \u56de\u6267 A_semantics \u673a\u8bfb\u5e8f\u6570=FIFTIETH"),
    ("FORTY-NINTH\uff08\u7b2c\u56db\u5341\u4e5d\u4f8b\uff09",
     "FIFTIETH\uff08\u7b2c\u4e94\u5341\u4f8b\uff09"),
    ("r888 probe leg4", "r891 probe leg4"),
    ("\uff08r888 \u51bb\u7ed3\u4ef6\uff09", "\uff08r891 \u51bb\u7ed3\u4ef6\uff09"),
    ("_r888bma_w189_probe_receipt.json", "_r891bma_w190_probe_receipt.json"),
    ("MSG-2026-10-08-1815-bma-w189-seat", "MSG-2026-10-08-2035-bma-w190-seat"),
    ("744de26ef", "c177bf73b"),
    ("\u3010r890\u3011", "\u3010r892\u3011"),
    ("r888 seat push", "r891 seat push"),
    ("\u81ea r888 \u6536\u53e3", "\u81ea r891 \u6536\u53e3"),
    ("bm-a r889 \u7a97\u5f52\u6863", "bm-a r892 \u7a97\u5f52\u6863"),
    ("\u672c\u673a r888 \u5e2d\u4f4d", "\u672c\u673a r891 \u5e2d\u4f4d"),
    ("\uff08r888 seat push\u00b7r565 \u5f8b\uff09", "\uff08r891 seat push\u00b7r565 \u5f8b\uff09"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before
    #    the naive rolls re-create them; own-B consumed before prior-B) --
    ("432_604..434_603", "434_804..436_803"),      # proj-A (W191+)
    ("432_804..433_003", "435_004..435_203"),      # proj-B (W191+)
    ("432_604..432_803", "434_804..435_003"),      # own-B (W190 B)
    ("430_604..432_603", "432_804..434_803"),      # own-A (W190 A)
    ("430_404..430_603", "432_604..432_803"),      # prior-B (W189 B)
    ("430_404..432_403", "432_604..434_603"),      # naive-A window (W190)
    ("430_604..430_803", "432_804..433_003"),      # naive-B window (W190)
    ("430_603+1", "432_803+1"),
    ("432_603+1", "434_803+1"),
    ("430_604+j", "432_804+j"),
    ("432_604+j", "434_804+j"),
    # -- ordinals (high first: succession pair before own pair) --
    ("\u7b2c\u4e94\u5341\u4f8b", "\u7b2c\u4e94\u5341\u4e00\u4f8b"),
    ("\u7b2c\u56db\u5341\u4e5d\u4f8b", "\u7b2c\u4e94\u5341\u4f8b"),
    ("\u7b2c 187 \u679a", "\u7b2c 188 \u679a"),
    ("\u884c 178+\u672c\u5019\u9009", "\u884c 179+\u672c\u5019\u9009"),
    ("\u7b2c\u4e00\u767e\u96f6\u4e94\u679a", "\u7b2c\u4e00\u767e\u96f6\u516d\u679a"),
    ("\u7b2c 179 \u6ce2", "\u7b2c 180 \u6ce2"),
    ("\u884c 104+\u672c\u5019\u9009", "\u884c 105+\u672c\u5019\u9009"),
    ("bm-a 104 \u884c\u6ce8\u518c", "bm-a 105 \u884c\u6ce8\u518c"),
    ("\u4e00\u767e\u516b\u5341\u516d\u884c\u6ce8\u518c", "\u4e00\u767e\u516b\u5341\u4e03\u884c\u6ce8\u518c"),
    ("\u673a\u8bc1 186 \u884c", "\u673a\u8bc1 187 \u884c"),
    ("\u4e00\u767e\u516b\u5341\u4e03\u9762\u5b9e\u6d4b", "\u4e00\u767e\u516b\u5341\u516b\u9762\u5b9e\u6d4b"),
    # -- n1_w forms (high first) --
    ("n1_w189", "n1_w190"),
    ("n1_w188", "n1_w189"),
    # -- wave-word cascade (high first; 9 pairs this wave -- the low end
    #    W182->W183 rolls the 已回填 precedent-list low-end) --
    ("W190", "W191"),
    ("W189", "W190"),
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    # -- bare-number leftovers --
    ("\u6ce2\u53f7 189=", "\u6ce2\u53f7 190="),
    ("--wave 189", "--wave 190"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; merged-mu 4dp display HOLDS this
    #    wave (-0.0929 -> -0.0929, NO pair, disclosed); w-only mu
    #    rolls -0.0986 -> -0.0878; sigma 0.245115 -> 0.245164 ROLLS
    #    (NEW pair vs the S86 hold, disclosed); p95 0.3243 -> 0.3447
    #    rolls; line_pre 1.1862 -> 1.1863 ROLLS (n_eff growth step
    #    818,728->820,928); line_merged 1.1862 -> 1.1866 ROLLS; K-lift
    #    +0.0000 -> +0.0003 ROLLS via @KLT@ construction) --
    ("**" + KNEW + " \u6295\u5f71**", "**" + KPROJ + " \u6295\u5f71**"),
    ("**1.1862**", "**" + LINE4 + "**"),
    ("**+0.0000**\u3010line_merged", "**" + DSIGN + DELTA4 + "**\u3010line_merged"),
    ("**0.3243**", "**" + P954 + "**"),
    ("**\u22120.0986**", "**" + WONLY_U + "**"),
    ("0.245115", SIG6),
    ("line_pre 1.1862", "line_pre " + PRE4),
    ("820,928", LEDG),
    ("818,728", NEFF),
    ("411,520", KNEW),
]


def s87(t):
    for old, new in S87:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / session-keyed faces / vestigial)
BACK210 = {
    "@CHAIN@": back189_map["@CHAIN@"] + "\uff1bW189=bm-a r890 freeze\uff08" + W189_SHA + "\uff09",
    "@KLT@": r1(back189_map["@KLT@"],
                "/W187 **+0.0002**/W188 **+0.0000** \u5982\u5b9e\u62ab\u9732",
                "/W187 **+0.0002**/W188 **+0.0000**/W189 **" + DSIGN + DELTA4 + "** \u5982\u5b9e\u62ab\u9732"),
    "@SEMT@": r1(back189_map["@SEMT@"],
                 "**0.000384**\u2192W187 **0.000383**\u2192W188 **0.000382**\u3011\uff09",
                 "**0.000384**\u2192W187 **0.000383**\u2192W188 **0.000382**\u2192W189 **" + SEM4 + "**\u3011\uff09"),
    "@S55@": s87(back189_map["@S55@"]),
    "@SEATPUB@": s87(back189_map["@SEATPUB@"]),
    "@OWNCHAIN@": r1(back189_map["@OWNCHAIN@"],
                     "/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2", "/W188/W189 \u6700\u8fd1\u81ea\u6709\u6ce2"),
    "@N171@": "190",
    "@N170@": "189",
    "@N169@": "188",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK210[tok] = s87(back189_map[tok])
# @ORDINALS@ sequential r1 chain (r888 seven-pair bloodline, flat form)
_ordinal_base = back189_map["@ORDINALS@"]
for _old, _new in (
    ("\u7b2c 179 \u6ce2", "\u7b2c 180 \u6ce2"),
    ("\u7b2c\u4e00\u767e\u96f6\u4e94\u679a", "\u7b2c\u4e00\u767e\u96f6\u516d\u679a"),
    ("\u884c 104+\u672c\u5019\u9009", "\u884c 105+\u672c\u5019\u9009"),
    ("/W187/W188 \u6700\u8fd1\u81ea\u6709\u6ce2", "/W188/W189 \u6700\u8fd1\u81ea\u6709\u6ce2"),
    ("\u6ce8\u518c\u8868 W188 \u884c\u540e", "\u6ce8\u518c\u8868 W189 \u884c\u540e"),
    ("MSG-2026-10-08-1815-bma-w189-seat", SEAT_MSG),
    ("744de26ef", SEAT_SHA),
):
    _ordinal_base = r1(_ordinal_base, _old, _new)
BACK210["@ORDINALS@"] = _ordinal_base
missing = [t for (t, _v) in BACK189 if t not in BACK210]
assert not missing, missing
extra = [t for t in BACK210 if t not in back189_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK210["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **\u62d2**" in chk \
    and "\uff08432_803+1\uff09" in chk and "FIFTIETH\uff08\u7b2c\u4e94\u5341\u4f8b\uff09" in chk, chk[:250]
chk = BACK210["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A \u7a97 " + A_BAND in chk and "\uff08434_803+1\uff09" in chk, chk[:250]
chk = BACK210["@ANCHOR@"]
assert "W1..W189 N1 finalize \u5df2\u5168\u90e8\u843d\u5730" in chk and "**823,128**" in chk \
    and "K=413,720 \u5408\u5e76\u6c60" in chk and "bm-a r844 dead-tail \u6536\u517b\u7a97" in chk \
    and "\u5df2\u56de\u586b\uff08r892 \u56de\u586b\u7a97\u00b7\u65e0\u6f0f\u8865\u00b7r864 \u6559\u8bad\u5151\u73b0" in chk, chk[:250]
assert BACK210["@POOL@"] == "\u7d2f\u8ba1 null \u6c60=" + KNEW + "+2,200\uff08\u672c\u6ce2\uff09=**" + KPROJ + \
    " \u6295\u5f71**", BACK210["@POOL@"]
assert "**" + LINE4 + "**" in BACK210["@KLKEY@"] and "n_eff " + NEFF in \
    BACK210["@KLKEY@"], BACK210["@KLKEY@"]
assert "line_pre " + PRE4 in BACK210["@KLKEY@"], BACK210["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK210["@KLKEY@"], BACK210["@KLKEY@"]
assert BACK210["@WAVEFREE@"] == "\u6ce2\u53f7 190=\u6ce8\u518c\u8868 W189 \u884c\u540e\u9996\u4e2a\u81ea\u7531\u53f7", \
    BACK210["@WAVEFREE@"]
assert "n1_w190_results.json" in BACK210["@FN@"] and \
    "n1_w189_results.json" in BACK210["@ODOLD@"]
assert BACK210["@WAVECLI@"] == "--wave 190/finalize --wave 190", \
    BACK210["@WAVECLI@"]
assert "W191+ \u6295\u5f71" in BACK210["@S55@"] and W191p_A in BACK210["@S55@"] \
    and W191p_B in BACK210["@S55@"] and "\u7ee7\u627f\u7b2c\u4e94\u5341\u4e00\u4f8b" in BACK210["@S55@"] \
    and "W190 B \u5e26 " + B_BAND in BACK210["@S55@"], BACK210["@S55@"][:200]
assert "verify at W191 prereg" in BACK210["@S55@"], BACK210["@S55@"][-120:]
assert SEAT_SHA in BACK210["@SEATPUB@"] and "r891 seat push" in \
    BACK210["@SEATPUB@"] and "\u81ea r891 \u6536\u53e3" in BACK210["@SEATPUB@"] \
    and "bm-a r892 \u7a97\u5f52\u6863" in BACK210["@SEATPUB@"], BACK210["@SEATPUB@"][:200]
assert "\u7b2c 180 \u6ce2" in BACK210["@ORDINALS@"] and "\u7b2c\u4e00\u767e\u96f6\u516d\u679a" in \
    BACK210["@ORDINALS@"] and "/W188/W189 \u6700\u8fd1\u81ea\u6709\u6ce2" in BACK210["@ORDINALS@"] \
    and "\u6ce8\u518c\u8868 W189 \u884c\u540e" in BACK210["@ORDINALS@"], BACK210["@ORDINALS@"][:200]
assert "W191+ \u6295\u5f71" in BACK210["@SEATSENT@"] and SEAT_MSG in \
    BACK210["@SEATSENT@"] and "\u7ee7\u627f\u7b2c\u4e94\u5341\u4e00\u4f8b" in BACK210["@SEATSENT@"], \
    BACK210["@SEATSENT@"][:200]
assert "\u672c\u673a r891 \u5e2d\u4f4d" in BACK210["@SEATSENT@"] and \
    "\uff08r891 seat push\u00b7r565 \u5f8b\uff09" in BACK210["@SEATSENT@"], \
    BACK210["@SEATSENT@"][:200]
assert "\u6cd5\u5178 \u00a74 W190 \u884c A=" + A_BAND in BACK210["@ASEEDPROSE@"], \
    BACK210["@ASEEDPROSE@"][:250]
assert "\u6cd5\u5178 \u00a74 W190 \u884c B=" + B_BAND in BACK210["@BSEEDPROSE@"], \
    BACK210["@BSEEDPROSE@"][:250]
assert "\u51c0\u8d26\u672c\u951a\u5934 " + LEDG in BACK210["@S5ANCH@"] and "r839 \u627f\u88ad\u6536\u53e3\u7a97" in \
    BACK210["@S5ANCH@"] and "\u5df2\u56de\u586b\uff08r892 \u56de\u586b\u7a97\uff09" in BACK210["@S5ANCH@"], \
    BACK210["@S5ANCH@"]
assert "K=" + KNEW + " \u5408\u5e76\u6c60" in BACK210["@S51@"] and \
    "**" + WONLY_U + "**" in BACK210["@S51@"], BACK210["@S51@"]
assert "**" + MU_U + "**" in BACK210["@S51@"], BACK210["@S51@"]
assert "**" + SIG6 + "**" in BACK210["@S52@"], BACK210["@S52@"]
assert "**" + P954 + "**" in BACK210["@S53@"], BACK210["@S53@"]
assert "\u4e00\u767e\u516b\u5341\u4e03\u884c\u6ce8\u518c" in BACK210["@SCANFACE@"] and "\u8868\u5c3e W189 \u884c" in \
    BACK210["@SCANFACE@"] and "\u673a\u8bc1 187 \u884c" in BACK210["@SCANFACE@"], \
    BACK210["@SCANFACE@"]
assert BACK210["@EOB@"] == "engine_owner==bm-a 105 \u884c\u6ce8\u518c", BACK210["@EOB@"]
assert "PERPETUAL-N1-W190" in BACK210["@TITLE@"] and "\u7b2c 188 \u679a" in \
    BACK210["@TITLE@"] and "\u3010r892\u3011" in BACK210["@TITLE@"], BACK210["@TITLE@"]
assert "r891 bm-a \u5e26\u95f8\u7a97\uff08pre-seat probe r891 \u5355\u7a97" in BACK210["@GATEW@"], \
    BACK210["@GATEW@"]
assert BACK210["@VAC@"] == "\uff08r891 probe leg2/leg3 \u5b9e\u8dd1\uff09", BACK210["@VAC@"]
assert "\uff08r892 \u627f\u88ad" in BACK210["@MERGE@"], BACK210["@MERGE@"]
assert "r891 probe \u5355\u8dd1\u5151\u73b0\u6ce8\u8bb0" in BACK210["@CLAIMLAW@"], \
    BACK210["@CLAIMLAW@"]
assert BACK210["@PRC@"] == "results/_r891bma_w190_probe_receipt.json", \
    BACK210["@PRC@"]
assert "W189=bm-a r890 freeze\uff08" + W189_SHA + "\uff09" in BACK210["@CHAIN@"]
assert BACK210["@SEMT@"].endswith("**0.000384**\u2192W187 **0.000383**\u2192W188 **0.000382**\u2192W189 **" + SEM4 + "**\u3011\uff09"), \
    BACK210["@SEMT@"][-60:]
assert BACK210["@KLT@"].endswith("/W187 **+0.0002**/W188 **+0.0000**/W189 **" + DSIGN + DELTA4 + "** \u5982\u5b9e\u62ab\u9732"), \
    BACK210["@KLT@"][-60:]
assert BACK210["@OWNCHAIN@"].endswith("/W188/W189 \u6700\u8fd1\u81ea\u6709\u6ce2"), \
    BACK210["@OWNCHAIN@"][-40:]
assert BACK210["@WPN2@"] == "W191+ \u6295\u5f71", BACK210["@WPN2@"]
assert BACK210["@W136TO@"] == "W136..W189", BACK210["@W136TO@"]
assert BACK210["@W2TO@"] == "W2..W189" and BACK210["@W1TO@"] == "W1..W189" \
    and BACK210["@V2W@"] == "v2..W189 \u843d\u5730", (BACK210["@W2TO@"],
                                                     BACK210["@W1TO@"],
                                                     BACK210["@V2W@"])
assert BACK210["@WN@"] == "W190" and BACK210["@W@"] == "W189" and \
    BACK210["@SD@"] == "n1_w190" and BACK210["@KOLD@"] == KNEW, \
    (BACK210["@WN@"], BACK210["@W@"], BACK210["@SD@"], BACK210["@KOLD@"])
assert BACK210["@ASEED@"] == "entry rng seed=**432_804+j**", BACK210["@ASEED@"]
assert "entry rng=**432_804+j**" in BACK210["@BENTRY@"], BACK210["@BENTRY@"]
assert BACK210["@PF@"] == "PERPETUAL_N1_W190_PREREG.md", BACK210["@PF@"]
assert BACK210["@R250@"] == "R250\uff1aW190 \u5e26\u4ece\u672a\u6307\u6d3e\u00b7\u6d4b\u91cf\u9762\u96f6\u7ed3\u679c\u53ef\u9501", \
    BACK210["@R250@"]
assert BACK210["@S51B@"] == "\uff08W2..W189 \u5171\u4e00\u767e\u516b\u5341\u516b\u9762\u5b9e\u6d4b mu \u7a33\u5b9a\u5148\u4f8b\u00b7\u5355\u6ce2\u8de8\u952e\u5fae\uff09", \
    BACK210["@S51B@"]
print("S87 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
# registry-count face patch (NEW this generation, disclosed): the raw src
# scan-face claim "SEED_REGISTRY 全键 189 值" is NOT a token slot (it rode
# stable across the W187-W189 generations); the live registry key count
# rolled 189 -> 190 this window, so the claim must be re-derived from the
# live module BEFORE the TOK phase (also clears the @N171@ vestigial
# stray-collision with the old count).
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 190, "SEED_REGISTRY key count drift: %d" % REG_N
assert blob.decode("utf-8").count("SEED_REGISTRY \u5168\u952e 189 \u503c") == 1, \
    "registry-count face not found in src"
SRC0 = blob.decode("utf-8").replace(
    "SEED_REGISTRY \u5168\u952e 189 \u503c",
    "SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N)
TOK210 = [(val, tok) for (tok, val) in BACK189]
src = SRC0
out_t = src
for old, tok in TOK210:
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
for tok, new in [(t, BACK210[t]) for (t, _v) in BACK189]:
    if EXPECT[tok] == 0:
        continue
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})",
                                        out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"\u6ce2\u53f7 1[789][0-9]", out_t)))
assert stale_wave == ["\u6ce2\u53f7 190"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w189", "n1_w190"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W190") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W190 freeze" not in out_t.replace("\uff1bW189=bm-a r890 freeze", ""), \
    "unexpected W190-freeze text"
# stale-session sweep: no W188-era session stamps may survive ("r891
# probe leg4" is the LEGAL new citation -- the W189 probe leg4 that
# anticipated the W190 staircase; only its 回执/leg2 faces must have
# rolled). NOTE: sigma 0.245115 IS stale this wave (display ROLLS to
# 0.245164); "−0.0929" is NOT stale (merged-mu 4dp display HOLDS).
for stale in ("r888 probe \u56de\u6267", "\uff08r888 probe leg2", "r880 probe", "r881 \u51bb\u7ed3\u4ef6",
              "\u5df2\u56de\u586b\uff08r888", "\u5df2\u56de\u586b\uff08r890", "744de26ef", "\u3010r890\u3011",
              "FORTY-NINTH", "\u7b2c\u56db\u5341\u4e5d\u4f8b", "0.3004", "0.245086",
              "0.245115", "\u22120.1025", "\u22120.0825", "**\u22120.0928**", "**1.1862**",
              "line_pre 1.1862", "0.3243", "407,120", "\u51c0\u8d26\u672c\u951a\u5934 820,928",
              "814,328", "818,728", "411,520", "MSG-2026-10-08-1815", "r888 seat push",
              "bm-a r889 \u7a97\u5f52\u6863", "\u672c\u673a r888 \u5e2d\u4f4d",
              "\uff08r888 seat push", "_r888bma_w189_probe_receipt"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r891 probe leg4" in out_t, "new W189-probe-leg4 citation missing"
assert out_t.count("r891 probe leg4") == 3, \
    "r891 probe-leg4 count=%d (expect 3)" % out_t.count("r891 probe leg4")
assert out_t.count("\uff08r891 \u51bb\u7ed3\u4ef6\uff09") == 1, "r891 freeze-artifact citation missing"
assert out_t.count("r888") == 1, "r888 residual count=%d (expect 1 = chain row W188)" \
    % out_t.count("r888")
assert out_t.count("r890") == 1, "r890 residual count=%d (expect 1 = chain row W189)" \
    % out_t.count("r890")
assert out_t.count("r889") == 0, "r889 residual count=%d (expect 0)" % out_t.count("r889")
assert out_t.count("r887") == 0, "r887 residual count=%d (expect 0)" % out_t.count("r887")
assert out_t.count("r885") == 0, "r885 residual count=%d (expect 0)" % out_t.count("r885")
assert out_t.count("r880") == 0, "r880 residual count=%d (expect 0)" % out_t.count("r880")
assert out_t.count("r892") == 5, "r892 residual count=%d (expect 5 = 2x backfill-window + inherit + stamp + archive-window)" \
    % out_t.count("r892")
assert out_t.count("W190 finalize \u7a97") == 2 and \
    "W189 finalize \u7a97" not in out_t, "sec7/8 placeholder wave faces missing"
assert out_t.count("SEED_REGISTRY \u5168\u952e %d \u503c" % REG_N) == 1, \
    "registry-count face patch missing in output"
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN, registry-count face %d" % (len(TOK210), REG_N))

# --- 5. emit the W190 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r892 bm-a W190 per-wave prereg build: transforms the freeze-time W189
prereg (git blob 735f7c288 -- file research/PERPETUAL_N1_W189_PREREG.md
at prereg-freeze commit 632761894, byte-identical to five-face-
registration commit 8addea3eb; extracted byte-verbatim to
results/_r892bma_w190_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W190_PREREG.md.  The post-sec7/sec8-backfill
FINAL face (r892 backfill, this window) is NOT the build src --
sec7/sec8 regions are un-tokenized and would leak W189 actuals;
disclosed two-face in the buildgen docstring.

Generated by results/_r892bma_w190_buildgen.py (TOK/BACK pairs
AST-extracted from the r890 build script -- no exec of its live
asserts; r773/r775/r781/r830/r833 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r891 probe ADMIT naive A 432_604..434_603 refused by W189 B
432_604..432_803 -> A 432_804..434_803 staircase 50th E36 / B
434_804..435_003 own-A reservation W141 leg2; W189 finalize r891
one-pass (K 413,720 EXACT / head 823,128 EXACT delta zero vs frozen
projection / merged mu -0.0929 4dp display HOLDS / w-only -0.0878
display ROLLS / sigma 0.245164 display ROLLS / skill_line 1.1863 ->
1.1866 K-lift +0.0003 / n_eff 820,928 / A p95 0.3447); W189 sec7/sec8
settle backfill landed the r892 window (this window, first-leg,
machine-verified backfill script); W189 five-face registration
8addea3eb (no anchored subject -- rode the r890 round closeout
commit, content-anchored -S derivation, disclosed); W190 seat push
c177bf73b r891; seat self-ack archive move landed the bm-a r892
window (cross-window archive, disclosed); anchor r844/r839
stale-session lineage stamps ride (quirk (f) inherited, disclosed).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r892bma_w190_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W190_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r891bma_w190_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "432804_434803", "B": "434804_435003"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [432804, 434803] and leg1["B"] == [434804, 435003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [432604, 434603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [432804, 433003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [432804, 433003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 434804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 187 and leg0["tail"] == "W189" and \\
    leg0["ordinal"] == 180 and leg0["bma_ordinal"] == 106 and \\
    leg0["owner_rows"] == 179 and leg0["bma_rows"] == 105 and \\
    leg0["w189_ledger_head"] == 823128, leg0
assert leg4["W191p_A"] in ("434804..436803", "434_804..436_803") and \\
    leg4["W191p_B"] in ("435004..435203", "435_004..435_203"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W191p_B_lands_inside_W191p_A"] is True, leg4
assert "FIFTIETH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w189_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 413720, "W189 merged K drift"
assert npc["pre_w189_cumulative"]["n_values"] == 411520, "pre-W189 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_413720"] == 1.1866 and kl["line_pre_w189"] == 1.1863 \\
    and abs(kl["line_delta_k_lift"] - 0.0003) < 1e-12 \\
    and kl["n_eff_held_equal"] == 820928, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k413720"] == 0.000381, "se_mu drift"
assert abs(npc["mu_delta_w189_vs_w188ext"] - 0.010848) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3447, \\
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 823128, "ledger head drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w189_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0929" and WONLY4 == "-0.0878" and SIG6 == "0.245164", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(823128)
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "823,128" and KNEW == "413,720", (LEDG, KNEW)
KPROJ = "{:,}".format(413720 + 2200)
LEDGPROJ = "{:,}".format(823128 + 2200)
assert KPROJ == "415,920" and LEDGPROJ == "825,328", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h", "-n", "1",
                    "-S", '189: {"a": (430_604', "--",
                    "scripts/perpetual_faces.py"],
                   capture_output=True, text=True)
W189_SHA = _r.stdout.strip()
assert W189_SHA == "8addea3eb", W189_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W190 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W190 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-n", "1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-2035-bma-w190-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "c177bf73b", SEAT_SHA
_r3a = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/"
                      "MSG-2026-10-08-2035-bma-w190-seat.md"],
                     capture_output=True)
_r3b = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-2035-bma-w190-seat.md"],
                     capture_output=True)
assert _r3a.returncode == 0 or _r3b.returncode == 0, \\
    "W190 seat MSG not on origin (inbox/processed union, r565 law)"
assert "432_804..434_803" in (_r3a if _r3a.returncode == 0 else _r3b) \\
    .stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "632761894:research/PERPETUAL_N1_W189_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "735f7c288539d58a181cacab9b9335fc632e7a33", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W189 sec7/sec8 settle backfill landed the r892 window (this window) --
# the anchor face cites it (backfill script machine-verified numbers)
w189p = io.open(r"research/PERPETUAL_N1_W189_PREREG.md", encoding="utf-8",
                newline="").read()
assert "823,128" in w189p and "K=413,720" in w189p, \\
    "W189 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r892 \\u56de\\u586b\\u7a97" in w189p, "W189 sec7 r892 window note missing"

# registry-count face patch (r892 generation fact, disclosed): the raw
# src scan-face claim "SEED_REGISTRY 全键 189 值" is NOT a token slot; the
# live registry key count rolled 189 -> 190 this window -- re-derive the
# claim from the live module BEFORE the TOK phase (also clears the
# @N171@ vestigial stray-collision with the old count).
sys.path.insert(0, "scripts")
sys.path.insert(0, ".")
import science_gates as _sg  # noqa: E402
REG_N = len(_sg.SEED_REGISTRY)
assert REG_N == 190, "SEED_REGISTRY key count drift: %d" % REG_N

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W189" in src and "430_604..432_603" in src, "src face drift"
assert src.count("SEED_REGISTRY \\u5168\\u952e 189 \\u503c") == 1, \\
    "registry-count face not found in src"
src = src.replace("SEED_REGISTRY \\u5168\\u952e 189 \\u503c",
                  "SEED_REGISTRY \\u5168\\u952e %d \\u503c" % REG_N)
'''

TAIL = '''
TOK210 = %s
BACK210 = %s

EXPECT = %s

out_t = src
for old, tok in TOK210:
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
for tok, new in BACK210:
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
stale_wave = sorted(set(re.findall(r"波号 1[789][0-9]", out_t)))
assert stale_wave == ["波号 190"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w189", "n1_w190"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W190") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W190 freeze" not in out_t.replace("；W189=bm-a r890 freeze", ""), \\
    "unexpected W190-freeze text"

# stale-session sweep ("r891 probe leg4" = LEGAL new citation -- the W189
# probe leg4 that anticipated the W190 staircase; merged-mu 4dp display
# HOLDS this wave -- "−0.0929" is NOT stale; sigma 0.245115 IS stale
# (display ROLLS to 0.245164); line_pre 1.1862 ROLLS to 1.1863)
for stale in ("r888 probe 回执", "（r888 probe leg2", "r880 probe", "r881 冻结件",
              "已回填（r888", "已回填（r890", "744de26ef", "【r890】", "FORTY-NINTH",
              "第四十九例", "0.3004", "0.245086", "0.245115", "−0.1025", "−0.0825",
              "**−0.0928**", "**1.1862**", "line_pre 1.1862", "0.3243", "407,120",
              "净账本锚头 820,928", "814,328", "818,728", "411,520",
              "MSG-2026-10-08-1815", "r888 seat push", "bm-a r889 窗归档",
              "本机 r888 席位", "（r888 seat push", "_r888bma_w189_probe_receipt"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r891 probe leg4" in out_t, "new W189-probe-leg4 citation missing"
assert out_t.count("r891 probe leg4") == 3, "r891 probe-leg4 count=%%d (expect 3)"
assert out_t.count("（r891 冻结件）") == 1, "r891 freeze-artifact citation missing"
assert out_t.count("r888") == 1, "r888 residual count=%%d (expect 1 = chain row W188)"
assert out_t.count("r890") == 1, "r890 residual count=%%d (expect 1 = chain row W189)"
assert out_t.count("r889") == 0, "r889 residual count=%%d (expect 0)"
assert out_t.count("r887") == 0, "r887 residual count=%%d (expect 0)"
assert out_t.count("r885") == 0, "r885 residual count=%%d (expect 0)"
assert out_t.count("r880") == 0, "r880 residual count=%%d (expect 0)"
assert out_t.count("r892") == 5, "r892 residual count=%%d (expect 5 = 2x backfill-window + inherit + stamp + archive-window)"
assert out_t.count("W190 finalize 窗") == 2, "sec7/8 placeholder wave face missing"
assert "W189 finalize 窗" not in out_t, "stale sec7/8 placeholder wave face"
assert out_t.count("SEED_REGISTRY 全键 %%d 值" %% REG_N) == 1, \\
    "registry-count face patch missing in output"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W190 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK210)
back_lit = repr([(t, BACK210[t]) for (t, _v) in BACK189])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results/_r892bma_w190_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r892bma_w190_prereg_build.py", len(out), "bytes")
