# -*- coding: utf-8 -*-
"""r888 bm-a generator: builds results/_r888bma_w188_prereg_build.py by
AST-extracting the r885 build script's BACK187/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK188
pairs as (token, rolled W188 value).  Old side = the W187-era value
(freeze-time blob 8fbae1c4f at prereg-freeze commit 8bd37a6b6,
byte-identical to registry-freeze commit 79c9a567c; extracted
byte-verbatim to results/_r888bma_w188_prereg_src.txt this window),
new side = the S85' W188 fact map applied to that W187 text.
r773/r775/r781/r830/r833 compliance inherited: token-first two-phase
vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved (projections consumed before the naive
rolls re-create them; own-B before prior-B; proj composite before the
bare K roll; LEDG head before NEFF re-creates it); pre-TOK sequential
DRY below (r833 law 2, zero writes until all green).

TWO-FACE src disclosure (bloodline of the r881/r885 two-face law):
  * the CURRENT disk face of research/PERPETUAL_N1_W187_PREREG.md
    = the POST-sec7/sec8-backfill FINAL face (r888 backfill this
    window, ~24.9KB) -- NOT usable as build src: the sec7/sec8
    regions are un-tokenized and would leak W187 finalize actuals
    into the W188 pre-registration;
  * results/_r888bma_w188_prereg_src.txt (21,625B, this extract) = the
    freeze-time PRE-backfill face (blob 8fbae1c4f at 8bd37a6b6 ==
    79c9a567c), sec7/sec8 as placeholders -- the src law.

Structural notes vs the r885 bloodline (disclosed):
  * the anchor procrastination-precedent list rides FIXED
    (W159/W168/W169/W181, restored via the 已回填 compensation pair
    writing W180 + the cascade low-end W180->W181; no NEW
    procrastination case in W187 -- sec7/sec8 landed r888 open-window
    FIRST LEG with honest next-window note, non-procrastination
    asserted in the W187 sec7 stamp itself);
  * r739-stale-stamp family: the 'bm-a r844 dead-tail 收养窗' and
    'bm-a r839 承袭收口窗' session stamps ride verbatim (off-by-one
    wave-word + stale-session lineage quirk (f) inherited; head/K
    values roll machine-correct to 818,728/409,320 this window);
  * merged-mu 4dp display ROLLS this wave (-0.0929 -> -0.0928, NEW
    pair this generation vs the S84 hold; disclosed); w-only mu rolls
    -0.1025 -> -0.0825; sigma key 0.245086 -> 0.245115; p95 anchor
    0.3004 -> 0.339;
  * K-lift display ROLLS this wave (-0.0001 -> +0.0002 sign flip
    after two consecutive negatives; DSIGN=+ this generation);
    line_pre 1.1859 HOLDS (NO pair, disclosed); line_merged 1.1858
    -> 1.1861 ROLLS;
  * cascade span 9 pairs this generation (W188->W189 down to
    W180->W181; the low end anchors the 已回填 compensation);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both
    generations) roll to 188/187/186;
  * r885 count-face note: count("r885") in the W188 output == 4
    (probe leg4 x3 + 冻结件 x1 -- the W187 probe window and the W187
    prereg-freeze window are the SAME r885 session, disclosed; prior
    generations had no such collision).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r887bma_w188_probe_receipt.json rc0 ADMIT
    (leg0 registry 185 rows tail W187 ordinal 178 / bma_ordinal 104 /
    owner_rows 177 / bma_rows 103 / w187_ledger_head 818,728; leg1
    naive A 428_204..430_203 REFUSED at its own start by the
    registered W187 B band 428_204..428_403 -> honest forward walk
    1 hop lands A 428_404..430_403 (staircase FORTY-EIGHTH instance
    E36 per receipt A_semantics; the W187 seat MSG leg4 + r885 probe
    leg4 + W187 prereg sec5.5 succession notes anticipated and
    MANDATED this re-derive -- projection and receipt ordinals MATCH,
    no divergence face); naive B 428_404..428_603 lands inside
    own-wave A 428_404..430_403 -> same-freeze mutual exclusion
    (W141 precedent leg2 law) -> reserved walk 1 hop lands
    B 430_404..430_603; leg2 conflicts 0; leg3 origin vacancy True
    at probe time (seat MSG published r887, r565 law held); leg4
    W189+ projection A 430_404..432_403 hops=0 / B 430_604..430_803
    hops=0, B inside A);
  - W187 finalize landed r887 one-pass (n1_w187_results.json
    machine-read: ledger head 816,528 + 2,200 = 818,728 EXACT
    zero-delta vs frozen projection; merged K=409,320 EXACT; merged
    mu -0.09284852 4dp -0.0928 (display ROLLS); w187-only mu
    -0.08247355 4dp -0.0825 (display ROLLS); sigma 0.24511516 6dp
    0.245115; se_mu_at_k409320 = 0.000383; skill_line line_pre_w187
    1.1859 (HOLDS) -> line_merged@409,320 1.1861 (K-lift +0.0002
    sign flip, n_eff held 816,528); A p95 = 0.339; audit finalize_only
    bm-a; voids LOWAMP-P1/P2); W187 sec7/sec8 settle backfill landed
    the r888 window (this window, first-leg, next-window note
    disclosed in the sec7 header itself; on-disk W187 prereg text
    '818,728' + 'K=409,320' + 'r888 回填窗' live-asserted below);
  - W187 freeze registered sha machine-derived = 79c9a567c (git log
    origin/main --grep "W187 five-face freeze"); W187 prereg freeze
    commit 8bd37a6b6 (r885 window, blob 8fbae1c4f at both freeze
    commits, asserted live below); W188 seat push sha
    machine-derived = 943967370 (git log --diff-filter=A on the seat
    MSG inbox path, r887 window); W188 seat self-ack archive move
    landed the bm-a r887 window (seat MSG sits in fleet/inbox/
    processed/ at build time, live-verified below)."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W187 prereg blob (LF, byte-verbatim) ----------
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "8fbae1c4fc5cc4f92708ef077914fc9256339e04", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "79c9a567c:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
assert len(blob) == 21625, len(blob)
open(r"results/_r888bma_w188_prereg_src.txt", "wb").write(blob)
ondisk = open(r"results/_r888bma_w188_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src re-write drift"
# two-face disclosure: the current face = post-backfill FINAL (r888)
_cur = io.open(r"research/PERPETUAL_N1_W187_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
print("W188 src verified (freeze face):", len(blob), "bytes (blob",
      BLOB_SHA[:10] + "); current face = post-backfill FINAL (",
      len(_cur), "bytes), disclosed two-face, build consumes freeze face")

# --- 1. AST-extract the r885 build script's BACK187 + EXPECT ---------------
src885 = io.open(r"results/_r885bma_w187_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src885)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK187 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK187" and \
           isinstance(node.value, ast.List):
            BACK187 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK187.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK187 is not None and EXPECT is not None, "BACK187/EXPECT not extracted"
assert len(BACK187) == 50 and len(EXPECT) == 50, (len(BACK187), len(EXPECT))
back187_map = dict(BACK187)
assert len(back187_map) == len(BACK187)
print("r885 BACK187 entries:", len(BACK187), "EXPECT entries:", len(EXPECT))

# --- 2. W188 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r887bma_w188_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "428404_430403", "B": "430404_430603"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [428404, 430403] and leg1["B"] == [430404, 430603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [428204, 430203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [428404, 428603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [428404, 428603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 430404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 185 and leg0["tail"] == "W187" and \
    leg0["ordinal"] == 178 and leg0["bma_ordinal"] == 104 and \
    leg0["owner_rows"] == 177 and leg0["bma_rows"] == 103 and \
    leg0["w187_ledger_head"] == 818728, leg0
assert leg4["W189p_A"] in ("430404..432403", "430_404..432_403") and \
    leg4["W189p_B"] in ("430604..430803", "430_604..430_803"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W189p_B_lands_inside_W189p_A"] is True, leg4
assert "FORTY-EIGHTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w187_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 409320, "W187 merged K drift"
assert npc["pre_w187_cumulative"]["n_values"] == 407120, "pre-W187 K drift"
assert npc["w187_only"]["n_values"] == 2200, "W187-only N drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_409320"] == 1.1861 and kl["line_pre_w187"] == 1.1859 \
    and kl["line_delta_k_lift"] == 0.0002 and kl["n_eff_held_equal"] == 816528, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k409320"] == 0.000383, "se_mu drift"
assert abs(npc["mu_delta_w187_vs_w186ext"] - 0.020041) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.339, \
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 818728 and \
    res["science_gates"]["ledger"]["prev_total"] == 816528, \
    res["science_gates"]["ledger"]
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w187_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_409320"]
PRE4 = "%.4f" % kl["line_pre_w187"]
SEM4 = "%.6f" % npc["se_mu_at_k409320"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0928" and WONLY4 == "-0.0825" and SIG6 == "0.245115", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1861" and PRE4 == "1.1859" and SEM4 == "0.000383" \
    and P954 == "0.3390" and DELTA4 == "0.0002" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0928" and WONLY_U == "\u22120.0825", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w187_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "818,728" and KNEW == "409,320" and NEFF == "816,528", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(409320 + 2200)
LEDGPROJ = "{:,}".format(818728 + 2200)
assert KPROJ == "411,520" and LEDGPROJ == "820,928", (KPROJ, LEDGPROJ)
P95D = "0.339"  # 3dp display face (W186 anchor 0.3004 4dp -> W187 0.339 rides src precision)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W187 five-face freeze", "-1"], capture_output=True,
                     text=True)
W187_SHA = _r_.stdout.strip()
assert W187_SHA == "79c9a567c", W187_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W188 FREEZE", "-1"], capture_output=True,
                     text=True)
assert _r0.stdout.strip() == "", "origin already carries a W188 FREEZE (r511)"
_r0b = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W188 five-face freeze", "-1"], capture_output=True,
                      text=True)
assert _r0b.stdout.strip() == "", "origin already carries a W188 five-face freeze"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-1717-bma-w188-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "943967370", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-1717-bma-w188-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W188 seat MSG not on origin processed/ (r565 law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "428_404..430_403" in _seat_txt and "430_404..430_603" in _seat_txt, \
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                      "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "8fbae1c4fc5cc4f92708ef077914fc9256339e04", \
    "src blob drift: %s" % _r4.stdout.strip()
# W187 sec7/sec8 settle backfill landed the r888 window (this window) --
# the anchor face cites it (the next-window note lives in the W187
# prereg's own sec7 header)
w187p = io.open(r"research/PERPETUAL_N1_W187_PREREG.md", encoding="utf-8",
                newline="").read()
assert "818,728" in w187p and "K=409,320" in w187p, \
    "W187 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r888 \u56de\u586b\u7a97" in w187p, "W187 sec7 r888 window note missing"

A_BAND = "428_404..430_403"
B_BAND = "430_404..430_603"
NAIVE_A = "428_204..430_203"
NAIVE_B = "428_404..428_603"
PRIOR_B = "428_204..428_403"     # registered W187 B band (refusal band)
A_SEED, B_SEED = "428_404", "430_404"
SEAT_MSG = "MSG-2026-10-08-1717-bma-w188-seat"
W189p_A = "430_404..432_403"
W189p_B = "430_604..430_803"

# --- 3. S85' = W187->W188 ordered fact map -----------------------------------
# (r735 substring-order law preserved from the r885 bloodline: projections
#  consumed before the naive rolls re-create them; own-B before prior-B;
#  pool projection composite before the bare K roll; LEDG head before NEFF;
#  high ordinals before low; cascade high first; bare numerals LAST.)
S85 = [
    # -- window/session composites (longest first) --
    ("已回填（r885 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
     "已回填（r888 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r885 回填窗）", "已回填（r888 回填窗）"),
    ("r885 bm-a 带闸窗（pre-seat probe r885 单窗", "r887 bm-a 带闸窗（pre-seat probe r887 单窗"),
    ("（r885 承袭", "（r888 承袭"),
    ("r885 probe 单跑兑现注记", "r887 probe 单跑兑现注记"),
    ("（r885 probe leg2/leg3 实跑）", "（r887 probe leg2/leg3 实跑）"),
    ("r885 probe 回执 A_semantics 机读序数=FORTY-SEVENTH",
     "r887 probe 回执 A_semantics 机读序数=FORTY-EIGHTH"),
    ("FORTY-SEVENTH（第四十七例）", "FORTY-EIGHTH（第四十八例）"),
    ("r880 probe leg4", "r885 probe leg4"),
    ("（r881 冻结件）", "（r885 冻结件）"),
    ("_r885bma_w187_probe_receipt.json", "_r887bma_w188_probe_receipt.json"),
    ("MSG-2026-10-08-1626-bma-w187-seat", "MSG-2026-10-08-1717-bma-w188-seat"),
    ("d176af598", "943967370"),
    ("【r885】", "【r888】"),
    ("r885 seat push", "r887 seat push"),
    ("自 r885 收口", "自 r887 收口"),
    ("bm-a r885 窗自移", "bm-a r887 窗自移"),
    ("本机 r885 席位", "本机 r887 席位"),
    ("（r885 seat push·r565 律）", "（r887 seat push·r565 律）"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B) --
    ("428_204..430_203", "430_404..432_403"),      # proj-A (W189+)
    ("428_404..428_603", "430_604..430_803"),      # proj-B (W189+)
    ("428_204..428_403", "430_404..430_603"),      # own-B (W188 B)
    ("426_204..428_203", "428_404..430_403"),      # own-A (W188 A)
    ("426_004..426_203", "428_204..428_403"),      # prior-B (W187 B)
    ("426_004..428_003", "428_204..430_203"),      # naive-A window (W188)
    ("426_204..426_403", "428_404..428_603"),      # naive-B window (W188)
    ("426_203+1", "428_403+1"),
    ("428_203+1", "430_403+1"),
    ("426_204+j", "428_404+j"),
    ("428_204+j", "430_404+j"),
    # -- ordinals (high first: succession pair before own pair) --
    ("第四十八例", "第四十九例"),
    ("第四十七例", "第四十八例"),
    ("第 185 枚", "第 186 枚"),
    ("行 176+本候选", "行 177+本候选"),
    ("第一百零三枚", "第一百零四枚"),
    ("第 177 波", "第 178 波"),
    ("行 102+本候选", "行 103+本候选"),
    ("bm-a 102 行注册", "bm-a 103 行注册"),
    ("一百八十四行注册", "一百八十五行注册"),
    ("机证 184 行", "机证 185 行"),
    ("一百八十五面实测", "一百八十六面实测"),
    # -- n1_w forms (high first) --
    ("n1_w187", "n1_w188"),
    ("n1_w186", "n1_w187"),
    # -- wave-word cascade (high first; 9 pairs this wave -- the low end
    #    W180->W181 anchors the 已回填 compensation pair above) --
    ("W188", "W189"),
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 187=", "波号 188="),
    ("--wave 187", "--wave 188"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; merged-mu 4dp display ROLLS
    #    -0.0929 -> -0.0928 this wave (NEW pair vs the S84 hold,
    #    disclosed); w-only mu rolls -0.1025 -> -0.0825; line_merged
    #    1.1858 -> 1.1861 ROLLS; line_pre 1.1859 HOLDS (NO pair,
    #    disclosed); K-lift −0.0001 -> +0.0002 sign flip ROLLS via
    #    @KLT@ construction) --
    ("**409,320 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1858**", "**" + LINE4 + "**"),
    ("**\u22120.0001**\u3010line_merged", "**" + DSIGN + DELTA4 + "**\u3010line_merged"),
    ("**0.3004**", "**0.339**"),
    ("**\u22120.1025**", "**" + WONLY_U + "**"),
    ("**\u22120.0929**", "**" + MU_U + "**"),
    ("0.245086", SIG6),
    ("816,528", LEDG),
    ("814,328", NEFF),
    ("407,120", KNEW),
]


def s85(t):
    for old, new in S85:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / session-keyed faces / vestigial)
BACK188 = {
    "@CHAIN@": back187_map["@CHAIN@"] + "；W187=bm-a r886 freeze（" + W187_SHA + "）",
    "@KLT@": r1(back187_map["@KLT@"], " 如实披露",
                "/W187 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": r1(back187_map["@SEMT@"], "**0.000384**】）",
                 "**0.000384**→W187 **" + SEM4 + "**】）"),
    "@S55@": s85(back187_map["@S55@"]),
    "@SEATPUB@": s85(back187_map["@SEATPUB@"]),
    "@ORDINALS@": (
        r1(r1(r1(r1(r1(r1(r1(back187_map["@ORDINALS@"],
            "第 177 波", "第 178 波"),
            "第一百零三枚", "第一百零四枚"),
            "行 102+本候选", "行 103+本候选"),
            "/W185/W186 最近自有波", "/W186/W187 最近自有波"),
            "注册表 W186 行后", "注册表 W187 行后"),
            "MSG-2026-10-08-1626-bma-w187-seat", SEAT_MSG),
            "d176af598", SEAT_SHA)
    ),
    "@OWNCHAIN@": r1(back187_map["@OWNCHAIN@"],
                     "/W185/W186 最近自有波", "/W186/W187 最近自有波"),
    "@N171@": "188",
    "@N170@": "187",
    "@N169@": "186",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK188[tok] = s85(back187_map[tok])
missing = [t for (t, _v) in BACK187 if t not in BACK188]
assert not missing, missing
extra = [t for t in BACK188 if t not in back187_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK188["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（428_403+1）" in chk and "FORTY-EIGHTH（第四十八例）" in chk, chk[:250]
chk = BACK188["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A 窗 " + A_BAND in chk and "（430_403+1）" in chk, chk[:250]
chk = BACK188["@ANCHOR@"]
assert "W1..W187 N1 finalize 已全部落地" in chk and "**818,728**" in chk \
    and "K=409,320 合并池" in chk and "bm-a r844 dead-tail 收养窗" in chk \
    and "已回填（r888 回填窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK188["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + \
    " 投影**", BACK188["@POOL@"]
assert "**" + LINE4 + "**" in BACK188["@KLKEY@"] and "n_eff " + NEFF in \
    BACK188["@KLKEY@"], BACK188["@KLKEY@"]
assert "line_pre " + PRE4 in BACK188["@KLKEY@"], BACK188["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK188["@KLKEY@"], BACK188["@KLKEY@"]
assert BACK188["@WAVEFREE@"] == "波号 188=注册表 W187 行后首个自由号", \
    BACK188["@WAVEFREE@"]
assert "n1_w188_results.json" in BACK188["@FN@"] and \
    "n1_w187_results.json" in BACK188["@ODOLD@"]
assert BACK188["@WAVECLI@"] == "--wave 188/finalize --wave 188", \
    BACK188["@WAVECLI@"]
assert "W189+ 投影" in BACK188["@S55@"] and W189p_A in BACK188["@S55@"] \
    and W189p_B in BACK188["@S55@"] and "继承第四十九例" in BACK188["@S55@"] \
    and "W188 B 带 " + B_BAND in BACK188["@S55@"], BACK188["@S55@"][:200]
assert "verify at W189 prereg" in BACK188["@S55@"], BACK188["@S55@"][-120:]
assert SEAT_SHA in BACK188["@SEATPUB@"] and "r887 seat push" in \
    BACK188["@SEATPUB@"] and "自 r887 收口" in BACK188["@SEATPUB@"] \
    and "bm-a r887 窗自移" in BACK188["@SEATPUB@"], BACK188["@SEATPUB@"][:200]
assert "第 178 波" in BACK188["@ORDINALS@"] and "第一百零四枚" in \
    BACK188["@ORDINALS@"] and "/W186/W187 最近自有波" in BACK188["@ORDINALS@"] \
    and "注册表 W187 行后" in BACK188["@ORDINALS@"], BACK188["@ORDINALS@"][:200]
assert "W189+ 投影" in BACK188["@SEATSENT@"] and SEAT_MSG in \
    BACK188["@SEATSENT@"] and "继承第四十九例" in BACK188["@SEATSENT@"], \
    BACK188["@SEATSENT@"][:200]
assert "本机 r887 席位" in BACK188["@SEATSENT@"] and \
    "（r887 seat push·r565 律）" in BACK188["@SEATSENT@"], \
    BACK188["@SEATSENT@"][:200]
assert "法典 §4 W188 行 A=" + A_BAND in BACK188["@ASEEDPROSE@"], \
    BACK188["@ASEEDPROSE@"][:250]
assert "法典 §4 W188 行 B=" + B_BAND in BACK188["@BSEEDPROSE@"], \
    BACK188["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK188["@S5ANCH@"] and "r839 承袭收口窗" in \
    BACK188["@S5ANCH@"] and "已回填（r888 回填窗）" in BACK188["@S5ANCH@"], \
    BACK188["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK188["@S51@"] and \
    "**" + WONLY_U + "**" in BACK188["@S51@"], BACK188["@S51@"]
assert "**" + MU_U + "**" in BACK188["@S51@"], BACK188["@S51@"]
assert "**" + SIG6 + "**" in BACK188["@S52@"], BACK188["@S52@"]
assert "**0.339**" in BACK188["@S53@"], BACK188["@S53@"]
assert "一百八十五行注册" in BACK188["@SCANFACE@"] and "表尾 W187 行" in \
    BACK188["@SCANFACE@"] and "机证 185 行" in BACK188["@SCANFACE@"], \
    BACK188["@SCANFACE@"]
assert BACK188["@EOB@"] == "engine_owner==bm-a 103 行注册", BACK188["@EOB@"]
assert "PERPETUAL-N1-W188" in BACK188["@TITLE@"] and "第 186 枚" in \
    BACK188["@TITLE@"] and "【r888】" in BACK188["@TITLE@"], BACK188["@TITLE@"]
assert "r887 bm-a 带闸窗（pre-seat probe r887 单窗" in BACK188["@GATEW@"], \
    BACK188["@GATEW@"]
assert BACK188["@VAC@"] == "（r887 probe leg2/leg3 实跑）", BACK188["@VAC@"]
assert "（r888 承袭" in BACK188["@MERGE@"], BACK188["@MERGE@"]
assert "r887 probe 单跑兑现注记" in BACK188["@CLAIMLAW@"], \
    BACK188["@CLAIMLAW@"]
assert BACK188["@PRC@"] == "results/_r887bma_w188_probe_receipt.json", \
    BACK188["@PRC@"]
assert "W187=bm-a r886 freeze（" + W187_SHA + "）" in BACK188["@CHAIN@"]
assert BACK188["@SEMT@"].endswith("**0.000384**→W187 **" + SEM4 + "**】）"), \
    BACK188["@SEMT@"][-60:]
assert BACK188["@KLT@"].endswith("/W187 **" + DSIGN + DELTA4 + "** 如实披露"), \
    BACK188["@KLT@"][-60:]
assert BACK188["@OWNCHAIN@"].endswith("/W186/W187 最近自有波"), \
    BACK188["@OWNCHAIN@"][-40:]
assert BACK188["@WPN2@"] == "W189+ 投影", BACK188["@WPN2@"]
assert BACK188["@W136TO@"] == "W136..W187", BACK188["@W136TO@"]
assert BACK188["@W2TO@"] == "W2..W187" and BACK188["@W1TO@"] == "W1..W187" \
    and BACK188["@V2W@"] == "v2..W187 落地", (BACK188["@W2TO@"],
                                               BACK188["@W1TO@"],
                                               BACK188["@V2W@"])
assert BACK188["@WN@"] == "W188" and BACK188["@W@"] == "W187" and \
    BACK188["@SD@"] == "n1_w188" and BACK188["@KOLD@"] == KNEW, \
    (BACK188["@WN@"], BACK188["@W@"], BACK188["@SD@"], BACK188["@KOLD@"])
assert BACK188["@ASEED@"] == "entry rng seed=**428_404+j**", BACK188["@ASEED@"]
assert "entry rng=**428_404+j**" in BACK188["@BENTRY@"], BACK188["@BENTRY@"]
assert BACK188["@PF@"] == "PERPETUAL_N1_W188_PREREG.md", BACK188["@PF@"]
assert BACK188["@R250@"] == "R250：W188 带从未指派·测量面零结果可锁", \
    BACK188["@R250@"]
assert BACK188["@S51B@"] == "（W2..W187 共一百八十六面实测 mu 稳定先例·单波跨键微）", \
    BACK188["@S51B@"]
print("S85' spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK188 = [(val, tok) for (tok, val) in BACK187]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK188:
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
for tok, new in [(t, BACK188[t]) for (t, _v) in BACK187]:
    if EXPECT[tok] == 0:
        continue
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})",
                                        out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 188"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w187", "n1_w188"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W188") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W188 freeze" not in out_t.replace("；W187=bm-a r886 freeze", ""), \
    "unexpected W188-freeze text"
# stale-session sweep: no W187-era session stamps may survive ("r885 probe
# leg4" is the LEGAL new citation -- the W187 probe leg4 that anticipated
# the W188 staircase; only its 回执/leg2 faces must have rolled). NOTE:
# "−0.0929" IS stale this wave (merged-mu 4dp display ROLLS to -0.0928);
# "·line_pre 1.1859·" is NOT stale (display HOLDS this wave).
for stale in ("r885 probe 回执", "（r885 probe leg2", "r880 probe", "r881 冻结件",
              "已回填（r885", "d176af598", "【r885】", "FORTY-SEVENTH",
              "第四十七例", "0.3004", "0.245086", "\u22120.1025", "\u22120.0929",
              "407,120", "净账本锚头 816,528", "814,328", "MSG-2026-10-08-1626",
              "r885 seat push", "bm-a r885 窗自移", "本机 r885 席位",
              "（r885 seat push", "_r885bma_w187_probe_receipt"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r885 probe leg4" in out_t, "new W187-probe-leg4 citation missing"
assert out_t.count("r885") == 4, "r885 residual count=%d (expect 4 = leg4 x3 + 冻结件 x1)" % \
    out_t.count("r885")
assert out_t.count("r880") == 0, "r880 residual count=%d (expect 0)" % \
    out_t.count("r880")
assert out_t.count("r875") == 0, "r875 residual count=%d (expect 0)" % \
    out_t.count("r875")
assert out_t.count("r841") == 0, "r841 residual count=%d (expect 0)" % \
    out_t.count("r841")
assert out_t.count("W188 finalize 窗") == 2 and \
    "W187 finalize 窗" not in out_t, "sec7/8 placeholder wave faces missing"
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN" % len(TOK188))

# --- 5. emit the W188 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r888 bm-a W188 per-wave prereg build: transforms the freeze-time W187
prereg (git blob 8fbae1c4f -- file research/PERPETUAL_N1_W187_PREREG.md
at prereg-freeze commit 8bd37a6b6, byte-identical to registry-freeze
commit 79c9a567c; extracted byte-verbatim to
results/_r888bma_w188_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W188_PREREG.md.  The post-sec7/sec8-backfill FINAL
face (r888 backfill, this window) is NOT the build src -- sec7/sec8
regions are un-tokenized and would leak W187 actuals; disclosed
two-face in the buildgen docstring.

Generated by results/_r888bma_w188_buildgen.py (TOK/BACK pairs
AST-extracted from the r885 build script -- no exec of its live
asserts; r773/r775/r781/r830/r833 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r887 probe ADMIT naive A 428_204..430_203 refused by W187 B
428_204..428_403 -> A 428_404..430_403 staircase 48th E36 / B
430_404..430_603 own-A reservation W141 leg2; W187 finalize r887
one-pass (K 409,320 EXACT / head 818,728 EXACT delta zero vs frozen
projection / merged mu -0.0928 4dp display ROLLS / w-only -0.0825
display ROLLS / sigma 0.245115 / skill_line 1.1859 -> 1.1861 K-lift
+0.0002 sign flip after two consecutive negatives / n_eff 816,528 /
A p95 0.339); W187 sec7/sec8 settle backfill landed the r888 window
(this window, first-leg next-window note disclosed); W187 freeze
79c9a567c (prereg freeze 8bd37a6b6 r885); W188 seat push 943967370
r887; seat self-ack archive move landed the bm-a r887 window (same-
window self-move pattern disclosed); anchor r844/r839 stale-session
lineage stamps ride (quirk (f) inherited, disclosed).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r888bma_w188_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W188_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r887bma_w188_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "428404_430403", "B": "430404_430603"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [428404, 430403] and leg1["B"] == [430404, 430603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [428204, 430203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [428404, 428603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [428404, 428603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 430404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 185 and leg0["tail"] == "W187" and \\
    leg0["ordinal"] == 178 and leg0["bma_ordinal"] == 104 and \\
    leg0["owner_rows"] == 177 and leg0["bma_rows"] == 103 and \\
    leg0["w187_ledger_head"] == 818728, leg0
assert leg4["W189p_A"] in ("430404..432403", "430_404..432_403") and \\
    leg4["W189p_B"] in ("430604..430803", "430_604..430_803"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W189p_B_lands_inside_W189p_A"] is True, leg4
assert "FORTY-EIGHTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w187_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 409320, "W187 merged K drift"
assert npc["pre_w187_cumulative"]["n_values"] == 407120, "pre-W187 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_409320"] == 1.1861 and kl["line_pre_w187"] == 1.1859 \\
    and kl["line_delta_k_lift"] == 0.0002 and kl["n_eff_held_equal"] == 816528, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k409320"] == 0.000383, "se_mu drift"
assert abs(npc["mu_delta_w187_vs_w186ext"] - 0.020041) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.339, \\
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 818728, "ledger head drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w187_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0928" and WONLY4 == "-0.0825" and SIG6 == "0.245115", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w187_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "818,728" and KNEW == "409,320", (LEDG, KNEW)
KPROJ = "{:,}".format(409320 + 2200)
LEDGPROJ = "{:,}".format(818728 + 2200)
assert KPROJ == "411,520" and LEDGPROJ == "820,928", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W187 five-face freeze", "-1"], capture_output=True, text=True)
W187_SHA = _r.stdout.strip()
assert W187_SHA == "79c9a567c", W187_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W188 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W188 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-1717-bma-w188-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "943967370", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1717-bma-w188-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W188 seat MSG not on origin processed/ (r565 law)"
assert "428_404..430_403" in _r3.stdout.decode("utf-8", "replace"), \\
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "8bd37a6b6:research/PERPETUAL_N1_W187_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "8fbae1c4fc5cc4f92708ef077914fc9256339e04", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W187 sec7/sec8 settle backfill landed the r888 window (this window) --
# the anchor face cites it (the next-window note lives in the W187
# prereg's own sec7 header)
w187p = io.open(r"research/PERPETUAL_N1_W187_PREREG.md", encoding="utf-8",
                newline="").read()
assert "818,728" in w187p and "K=409,320" in w187p, \\
    "W187 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r888 \\u56de\\u586b\\u7a97" in w187p, "W187 sec7 r888 window note missing"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W187" in src and "428_204..430_203" in src, "src face drift"
'''

TAIL = '''
TOK188 = %s
BACK188 = %s

EXPECT = %s

out_t = src
for old, tok in TOK188:
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
for tok, new in BACK188:
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
assert stale_wave == ["波号 188"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w187", "n1_w188"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W188") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W188 freeze" not in out_t.replace("；W187=bm-a r886 freeze", ""), \\
    "unexpected W188-freeze text"

# stale-session sweep ("r885 probe leg4" = LEGAL new citation -- the W187
# probe leg4 that anticipated the W188 staircase; merged-mu 4dp display
# ROLLS to -0.0928 this wave -- "−0.0929" IS a stale token; line_pre
# 1.1859 HOLDS -- NOT stale)
for stale in ("r885 probe 回执", "（r885 probe leg2", "r880 probe", "r881 冻结件",
              "已回填（r885", "d176af598", "【r885】", "FORTY-SEVENTH",
              "第四十七例", "0.3004", "0.245086", "−0.1025", "−0.0929",
              "407,120", "净账本锚头 816,528", "814,328", "MSG-2026-10-08-1626",
              "r885 seat push", "bm-a r885 窗自移", "本机 r885 席位",
              "（r885 seat push", "_r885bma_w187_probe_receipt"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r885 probe leg4" in out_t, "new W187-probe-leg4 citation missing"
assert out_t.count("r885") == 4, "r885 residual count=%%d (expect 4 = leg4 x3 + 冻结件 x1)"
assert out_t.count("r880") == 0, "r880 residual count=%%d (expect 0)"
assert out_t.count("r875") == 0, "r875 residual count=%%d (expect 0)"
assert out_t.count("r841") == 0, "r841 residual count=%%d (expect 0)"
assert out_t.count("W188 finalize 窗") == 2, "sec7/8 placeholder wave face missing"
assert "W187 finalize 窗" not in out_t, "stale sec7/8 placeholder wave face"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W188 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK188)
back_lit = repr([(t, BACK188[t]) for (t, _v) in BACK187])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results/_r888bma_w188_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r888bma_w188_prereg_build.py", len(out), "bytes")
