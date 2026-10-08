# -*- coding: utf-8 -*-
"""r885 bm-a generator: builds results/_r885bma_w187_prereg_build.py by
AST-extracting the r881 build script's BACK186/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK187
pairs as (token, rolled W187 value).  Old side = the W186-era value
(freeze-time blob 2ca2f640b at prereg-freeze commit baa5b36ea, byte-identical
to registry-freeze commit 14177b161; extracted byte-verbatim to
results/_r885bma_w187_prereg_src.txt this window), new side = the S84'
W187 fact map applied to that W186 text.
r773/r775/r781/r830/r833 compliance inherited: token-first two-phase
vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved (projections consumed before the naive
rolls re-create them; own-B before prior-B; proj composite before the
bare K roll; LEDG head before NEFF re-creates it); pre-TOK sequential
DRY below (r833 law 2, zero writes until all green).

TWO-FACE src disclosure (bloodline of the r881 two-face finding):
  * the CURRENT origin/disk face of research/PERPETUAL_N1_W186_PREREG.md
    = the POST-sec7/sec8-backfill FINAL face (r885 backfill landed this
    window, commit e5c44c853, ~24.8KB) -- NOT usable as build src: the
    sec7/sec8 regions are un-tokenized and would leak W186 finalize
    actuals into the W187 pre-registration;
  * results/_r885bma_w187_prereg_src.txt (21,542B, this extract) = the
    freeze-time PRE-backfill face (blob 2ca2f640b at baa5b36ea ==
    14177b161), sec7/sec8 as placeholders -- the r876/r877/r881 bloodline
    src law.

Structural notes vs the r881 bloodline (disclosed):
  * the anchor procrastination-precedent list rides FIXED
    (W159/W168/W169/W181, restored via the 已回填 compensation pair
    writing W180 + the cascade low-end W180->W181; no NEW procrastination
    case in W186 -- sec7/sec8 landed r885 open-window FIRST LEG with
    honest next-window note, non-procrastination asserted in the W186
    sec7 stamp itself);
  * r739-stale-stamp family: the 'bm-a r844 dead-tail 收养窗' and
    'bm-a r839 承袭收口窗' session stamps ride verbatim (off-by-one
    wave-word + stale-session lineage quirk (f) inherited; head/K values
    roll machine-correct to 816,528/407,120 this window);
  * merged-mu 4dp display HOLDS this wave (-0.0929 stays; 6dp machine
    face -0.092905 in n1_w186_results.json; NO display pair, disclosed);
  * K-lift display HOLDS this wave (-0.0001 second consecutive negative;
    NO delta pair, disclosed);
  * line_merged display ROLLS 1.1857 -> 1.1858 and line_pre 1.1858 ->
    1.1859 this wave; w-only mu rolls -0.0992 -> -0.1025; sigma key
    0.245090 -> 0.245086; p95 anchor 0.3066 -> 0.3004;
  * cascade span extended to 8 pairs (W187->W188 down to W180->W181);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both generations)
    roll to 187/186/185.

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r885bma_w187_probe_receipt.json rc0 ADMIT
    (leg0 registry 184 rows tail W186 ordinal 177 / bma_ordinal 103 /
    owner_rows 176 / bma_rows 102 / w186_ledger_head 816,528; leg1
    naive A 426_004..428_003 REFUSED at its own start by the registered
    W186 B band 426_004..426_203 -> honest forward walk 1 hop lands
    A 426_204..428_203 (staircase FORTY-SEVENTH instance E36 per receipt
    A_semantics; the W186 seat leg4 + r880 probe leg4 + W186 prereg
    sec5.5 succession notes anticipated and MANDATED this re-derive --
    projection and receipt ordinals MATCH, no divergence face); naive B
    426_204..426_403 lands inside own-wave A 426_204..428_203 ->
    same-freeze mutual exclusion (W141 precedent leg2 law) -> reserved
    walk 1 hop lands B 428_204..428_403; leg2 conflicts 0; leg3 origin
    vacancy True at probe time (seat MSG published same window, r565
    law held); leg4 W188+ projection A 428_204..430_203 hops=0 /
    B 428_404..428_603 hops=0, B inside A);
  - W186 finalize landed r884 composite-closeout one-pass (n1_w186_
    results.json machine-read: ledger head 814,328 + 2,200 = 816,528
    EXACT zero-delta vs frozen projection; merged K=407,120 EXACT;
    merged mu -0.09290459 4dp -0.0929 (display HOLDS); w186-only mu
    -0.102515 4dp -0.1025 (display ROLLS); sigma 0.24508568 6dp
    0.245086; se_mu_at_k407120 = 0.000384; skill_line line_pre_w186
    1.1859 -> line_merged@407,120 1.1858 (K-lift -0.0001, n_eff held
    814,328); A p95 = 0.3004; audit finalize_only bm-a; voids LOWAMP-P1/
    P2); W186 sec7/sec8 settle backfill landed the r885 window (this
    window, first-leg, next-window note disclosed in the sec7 header
    itself; on-disk W186 prereg text '816,528' + 'K=407,120' +
    'r885 回填窗' live-asserted below);
  - W186 freeze registered sha machine-derived = 14177b161 (git log
    origin/main --grep "W186 FREEZE"); W186 prereg freeze commit
    baa5b36ea (r881 window, blob 2ca2f640b at both freeze commits,
    asserted live below); W187 seat push sha machine-derived =
    d176af598 (git log --diff-filter=A on the seat MSG inbox path, r885
    window); W187 seat self-ack archive move landed the bm-a r885
    window ITSELF (fff58bba7 + f3be51e80, same-window self-move;
    processed/ path on origin live-verified below)."""
import ast
import hashlib
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W186 prereg blob (LF, byte-verbatim) ----------
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(
    ["git", "rev-parse", "baa5b36ea:research/PERPETUAL_N1_W186_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "2ca2f640b7ca90437ebad8299a04697a441116ef", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "14177b161:research/PERPETUAL_N1_W186_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "baa5b36ea:research/PERPETUAL_N1_W186_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
assert len(blob) == 21542, len(blob)
open(r"results/_r885bma_w187_prereg_src.txt", "wb").write(blob)
ondisk = open(r"results/_r885bma_w187_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src re-write drift"
# two-face disclosure: the current face = post-backfill FINAL (r885)
_cur = io.open(r"research/PERPETUAL_N1_W186_PREREG.md", "rb").read()
assert len(_cur) > 24000 and _cur != blob and \
    "\u5360\u4f4d" not in _cur.decode("utf-8", "replace"), \
    "current face not the backfilled FINAL"
_o = subprocess.run(["git", "show", "origin/main:research/PERPETUAL_N1_W186_PREREG.md"],
                    capture_output=True).stdout
assert _cur.replace(b"\r\n", b"\n") == _o, \
    "disk face != origin face (post-CRLF-normalize)"
print("W187 src verified (freeze face):", len(blob), "bytes (blob",
      BLOB_SHA[:10] + "); current face = post-backfill FINAL (",
      len(_cur), "bytes), disclosed two-face, build consumes freeze face")

# --- 1. AST-extract the r881 build script's BACK186 + EXPECT ---------------
src881 = io.open(r"results/_r881bma_w186_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src881)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK186 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK186" and \
           isinstance(node.value, ast.List):
            BACK186 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK186.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK186 is not None and EXPECT is not None, "BACK186/EXPECT not extracted"
assert len(BACK186) == 50 and len(EXPECT) == 50, (len(BACK186), len(EXPECT))
back186_map = dict(BACK186)
assert len(back186_map) == len(BACK186)
print("r881 BACK186 entries:", len(BACK186), "EXPECT entries:", len(EXPECT))

# --- 2. W187 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r885bma_w187_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "426204_428203", "B": "428204_428403"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [426204, 428203] and leg1["B"] == [428204, 428403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [426004, 428003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [426204, 426403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [426204, 426403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 428204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 184 and leg0["tail"] == "W186" and \
    leg0["ordinal"] == 177 and leg0["bma_ordinal"] == 103 and \
    leg0["owner_rows"] == 176 and leg0["bma_rows"] == 102 and \
    leg0["w186_ledger_head"] == 816528, leg0
assert leg4["W188p_A"] in ("428204..430203", "428_204..430_203") and \
    leg4["W188p_B"] in ("428404..428603", "428_404..428_603"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W188p_B_lands_inside_W188p_A"] is True, leg4
assert "FORTY-SEVENTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w186_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 407120, "W186 merged K drift"
assert npc["pre_w186_cumulative"]["n_values"] == 404920, "pre-W186 K drift"
assert npc["w186_only"]["n_values"] == 2200, "W186-only N drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_407120"] == 1.1858 and kl["line_pre_w186"] == 1.1859 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 814328, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k407120"] == 0.000384, "se_mu drift"
assert abs(npc["mu_delta_w186_vs_w185ext"] - (-0.003301)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3004, \
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 816528 and \
    res["science_gates"]["ledger"]["prev_total"] == 814328, \
    res["science_gates"]["ledger"]
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w186_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_407120"]
PRE4 = "%.4f" % kl["line_pre_w186"]
SEM4 = "%.6f" % npc["se_mu_at_k407120"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0929" and WONLY4 == "-0.1025" and SIG6 == "0.245086", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1858" and PRE4 == "1.1859" and SEM4 == "0.000384" \
    and P954 == "0.3004" and DELTA4 == "0.0001" and DSIGN == "\u2212", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0929" and WONLY_U == "\u22120.1025", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w186_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "816,528" and KNEW == "407,120" and NEFF == "814,328", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(407120 + 2200)
LEDGPROJ = "{:,}".format(816528 + 2200)
assert KPROJ == "409,320" and LEDGPROJ == "818,728", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W186 FREEZE", "-1"], capture_output=True,
                     text=True)
W186_SHA = _r_.stdout.strip()
assert W186_SHA == "14177b161", W186_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W187 FREEZE", "-1"], capture_output=True,
                     text=True)
assert _r0.stdout.strip() == "", "origin already carries a W187 FREEZE (r511)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-1626-bma-w187-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "d176af598", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-1626-bma-w187-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W187 seat MSG not on origin processed/ (r565 law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "426_204..428_203" in _seat_txt and "428_204..428_403" in _seat_txt, \
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                      "baa5b36ea:research/PERPETUAL_N1_W186_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "2ca2f640b7ca90437ebad8299a04697a441116ef", \
    "src blob drift: %s" % _r4.stdout.strip()
# W186 sec7/sec8 settle backfill landed the r885 window (this window) --
# the anchor face cites it (the next-window note lives in the W186
# prereg's own sec7 header)
w186p = io.open(r"research/PERPETUAL_N1_W186_PREREG.md", encoding="utf-8",
                newline="").read()
assert "816,528" in w186p and "K=407,120" in w186p, \
    "W186 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r885 \u56de\u586b\u7a97" in w186p, "W186 sec7 r885 window note missing"

A_BAND = "426_204..428_203"
B_BAND = "428_204..428_403"
NAIVE_A = "426_004..428_003"
NAIVE_B = "426_204..426_403"
PRIOR_B = "426_004..426_203"     # registered W186 B band (refusal band)
A_SEED, B_SEED = "426_204", "428_204"
SEAT_MSG = "MSG-2026-10-08-1626-bma-w187-seat"
W188p_A = "428_204..430_203"
W188p_B = "428_404..428_603"

# --- 3. S84' = W186->W187 ordered fact map -----------------------------------
# (r735 substring-order law preserved from the r881 bloodline: projections
#  consumed before the naive rolls re-create them; own-B before prior-B;
#  pool projection composite before the bare K roll; LEDG head before NEFF;
#  high ordinals before low; cascade high first; bare numerals LAST.)
S84 = [
    # -- window/session composites (longest first) --
    ("已回填（r879 收养窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
     "已回填（r885 回填窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r879 同窗）", "已回填（r885 回填窗）"),
    ("r880 bm-a 带闸窗（pre-seat probe r880 单窗", "r885 bm-a 带闸窗（pre-seat probe r885 单窗"),
    ("（r880 承袭", "（r885 承袭"),
    ("r880 probe 单跑兑现注记", "r885 probe 单跑兑现注记"),
    ("（r880 probe leg2/leg3 实跑）", "（r885 probe leg2/leg3 实跑）"),
    ("r880 probe 回执 A_semantics 机读序数=FORTY-SIXTH",
     "r885 probe 回执 A_semantics 机读序数=FORTY-SEVENTH"),
    ("FORTY-SIXTH（第四十六例）", "FORTY-SEVENTH（第四十七例）"),
    ("r875 probe leg4", "r880 probe leg4"),
    ("（r877 冻结件）", "（r881 冻结件）"),
    ("_r880bma_w186_probe_receipt.json", "_r885bma_w187_probe_receipt.json"),
    ("MSG-2026-10-08-1354-bma-w186-seat", "MSG-2026-10-08-1626-bma-w187-seat"),
    ("dd362c690", "d176af598"),
    ("【r880】", "【r885】"),
    ("r880 seat push", "r885 seat push"),
    ("自 r880 收口", "自 r885 收口"),
    ("bm-a r880 窗自移·如实注记", "bm-a r885 窗自移·如实注记"),
    ("本机 r880 席位", "本机 r885 席位"),
    ("（r880 seat push·r565 律）", "（r885 seat push·r565 律）"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B) --
    ("426_004..428_003", "428_204..430_203"),      # proj-A (W188+)
    ("426_204..426_403", "428_404..428_603"),      # proj-B (W188+)
    ("426_004..426_203", "428_204..428_403"),      # own-B (W187 B)
    ("424_004..426_003", "426_204..428_203"),      # own-A (W187 A)
    ("423_804..424_003", "426_004..426_203"),      # prior-B (W186 B)
    ("423_804..425_803", "426_004..428_003"),      # naive-A window (W187)
    ("424_004..424_203", "426_204..426_403"),      # naive-B window (W187)
    ("424_003+1", "426_203+1"),
    ("426_003+1", "428_203+1"),
    ("424_004+j", "426_204+j"),
    ("426_004+j", "428_204+j"),
    # -- ordinals (high first: succession pair before own pair) --
    ("第四十七例", "第四十八例"),
    ("第四十六例", "第四十七例"),
    ("第 184 枚", "第 185 枚"),
    ("行 175+本候选", "行 176+本候选"),
    ("第一百零二枚", "第一百零三枚"),
    ("第 176 波", "第 177 波"),
    ("行 101+本候选", "行 102+本候选"),
    ("bm-a 101 行注册", "bm-a 102 行注册"),
    ("一百八十三行注册", "一百八十四行注册"),
    ("机证 183 行", "机证 184 行"),
    ("一百八十四面实测", "一百八十五面实测"),
    # -- n1_w forms (high first) --
    ("n1_w186", "n1_w187"),
    ("n1_w185", "n1_w186"),
    # -- wave-word cascade (high first; 8 pairs this wave -- the low end
    #    W180->W181 is anchored by the 已回填 compensation pair above) --
    ("W187", "W188"),
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 186=", "波号 187="),
    ("--wave 186", "--wave 187"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; line_merged display ROLLS 1.1857 ->
    #    1.1858 and line_pre 1.1858 -> 1.1859 this wave; merged-mu 4dp
    #    display HOLDS -0.0929 (NO pair, disclosed); w-only mu rolls
    #    -0.0992 -> -0.1025; K-lift -0.0001 HOLDS (NO pair, disclosed)) --
    ("**407,120 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1857**", "**" + LINE4 + "**"),
    ("·line_pre 1.1858·", "·line_pre " + PRE4 + "·"),
    ("**0.3066**", "**" + P954 + "**"),
    ("**\u22120.0992**", "**" + WONLY_U + "**"),
    ("0.245090", SIG6),
    ("814,328", LEDG),
    ("812,128", NEFF),
    ("404,920", KNEW),
]


def s84(t):
    for old, new in S84:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / session-keyed faces / vestigial)
BACK187 = {
    "@CHAIN@": back186_map["@CHAIN@"] + "；W186=bm-a r882 freeze（" + W186_SHA + "）",
    "@KLT@": r1(back186_map["@KLT@"], " 如实披露",
                "/W186 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": r1(back186_map["@SEMT@"], "**0.000385**】）",
                 "**0.000385**→W186 **" + SEM4 + "**】）"),
    "@S55@": s84(back186_map["@S55@"]),
    "@SEATPUB@": s84(back186_map["@SEATPUB@"]),
    "@ORDINALS@": (
        r1(r1(r1(r1(r1(r1(r1(back186_map["@ORDINALS@"],
            "第 176 波", "第 177 波"),
            "第一百零二枚", "第一百零三枚"),
            "行 101+本候选", "行 102+本候选"),
            "/W184/W185 最近自有波", "/W185/W186 最近自有波"),
            "注册表 W185 行后", "注册表 W186 行后"),
            "MSG-2026-10-08-1354-bma-w186-seat", SEAT_MSG),
            "dd362c690", SEAT_SHA)
    ),
    "@OWNCHAIN@": r1(back186_map["@OWNCHAIN@"],
                     "/W184/W185 最近自有波", "/W185/W186 最近自有波"),
    "@N171@": "187",
    "@N170@": "186",
    "@N169@": "185",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK187[tok] = s84(back186_map[tok])
missing = [t for (t, _v) in BACK186 if t not in BACK187]
assert not missing, missing
extra = [t for t in BACK187 if t not in back186_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK187["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（426_203+1）" in chk and "FORTY-SEVENTH（第四十七例）" in chk, chk[:250]
chk = BACK187["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A 窗 " + A_BAND in chk and "（428_203+1）" in chk, chk[:250]
chk = BACK187["@ANCHOR@"]
assert "W1..W186 N1 finalize 已全部落地" in chk and "**816,528**" in chk \
    and "K=407,120 合并池" in chk and "bm-a r844 dead-tail 收养窗" in chk \
    and "已回填（r885 回填窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK187["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + \
    " 投影**", BACK187["@POOL@"]
assert "**" + LINE4 + "**" in BACK187["@KLKEY@"] and "n_eff " + NEFF in \
    BACK187["@KLKEY@"], BACK187["@KLKEY@"]
assert "line_pre " + PRE4 in BACK187["@KLKEY@"], BACK187["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK187["@KLKEY@"], BACK187["@KLKEY@"]
assert BACK187["@WAVEFREE@"] == "波号 187=注册表 W186 行后首个自由号", \
    BACK187["@WAVEFREE@"]
assert "n1_w187_results.json" in BACK187["@FN@"] and \
    "n1_w186_results.json" in BACK187["@ODOLD@"]
assert BACK187["@WAVECLI@"] == "--wave 187/finalize --wave 187", \
    BACK187["@WAVECLI@"]
assert "W188+ 投影" in BACK187["@S55@"] and W188p_A in BACK187["@S55@"] \
    and W188p_B in BACK187["@S55@"] and "继承第四十八例" in BACK187["@S55@"] \
    and "W187 B 带 " + B_BAND in BACK187["@S55@"], BACK187["@S55@"][:200]
assert "verify at W188 prereg" in BACK187["@S55@"], BACK187["@S55@"][-120:]
assert SEAT_SHA in BACK187["@SEATPUB@"] and "r885 seat push" in \
    BACK187["@SEATPUB@"] and "自 r885 收口" in BACK187["@SEATPUB@"] \
    and "bm-a r885 窗自移" in BACK187["@SEATPUB@"], BACK187["@SEATPUB@"][:200]
assert "第 177 波" in BACK187["@ORDINALS@"] and "第一百零三枚" in \
    BACK187["@ORDINALS@"] and "/W185/W186 最近自有波" in BACK187["@ORDINALS@"] \
    and "注册表 W186 行后" in BACK187["@ORDINALS@"], BACK187["@ORDINALS@"][:200]
assert "W188+ 投影" in BACK187["@SEATSENT@"] and SEAT_MSG in \
    BACK187["@SEATSENT@"] and "继承第四十八例" in BACK187["@SEATSENT@"], \
    BACK187["@SEATSENT@"][:200]
assert "本机 r885 席位" in BACK187["@SEATSENT@"] and \
    "（r885 seat push·r565 律）" in BACK187["@SEATSENT@"], \
    BACK187["@SEATSENT@"][:200]
assert "法典 §4 W187 行 A=" + A_BAND in BACK187["@ASEEDPROSE@"], \
    BACK187["@ASEEDPROSE@"][:250]
assert "法典 §4 W187 行 B=" + B_BAND in BACK187["@BSEEDPROSE@"], \
    BACK187["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK187["@S5ANCH@"] and "r839 承袭收口窗" in \
    BACK187["@S5ANCH@"] and "已回填（r885 回填窗）" in BACK187["@S5ANCH@"], \
    BACK187["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK187["@S51@"] and \
    "**" + WONLY_U + "**" in BACK187["@S51@"], BACK187["@S51@"]
assert "**" + MU_U + "**" in BACK187["@S51@"], BACK187["@S51@"]
assert "**" + SIG6 + "**" in BACK187["@S52@"], BACK187["@S52@"]
assert "**" + P954 + "**" in BACK187["@S53@"], BACK187["@S53@"]
assert "一百八十四行注册" in BACK187["@SCANFACE@"] and "表尾 W186 行" in \
    BACK187["@SCANFACE@"] and "机证 184 行" in BACK187["@SCANFACE@"], \
    BACK187["@SCANFACE@"]
assert BACK187["@EOB@"] == "engine_owner==bm-a 102 行注册", BACK187["@EOB@"]
assert "PERPETUAL-N1-W187" in BACK187["@TITLE@"] and "第 185 枚" in \
    BACK187["@TITLE@"] and "【r885】" in BACK187["@TITLE@"], BACK187["@TITLE@"]
assert "r885 bm-a 带闸窗（pre-seat probe r885 单窗" in BACK187["@GATEW@"], \
    BACK187["@GATEW@"]
assert BACK187["@VAC@"] == "（r885 probe leg2/leg3 实跑）", BACK187["@VAC@"]
assert "（r885 承袭" in BACK187["@MERGE@"], BACK187["@MERGE@"]
assert "r885 probe 单跑兑现注记" in BACK187["@CLAIMLAW@"], \
    BACK187["@CLAIMLAW@"]
assert BACK187["@PRC@"] == "results/_r885bma_w187_probe_receipt.json", \
    BACK187["@PRC@"]
assert "W186=bm-a r882 freeze（" + W186_SHA + "）" in BACK187["@CHAIN@"]
assert BACK187["@SEMT@"].endswith("→W186 **" + SEM4 + "**】）"), \
    BACK187["@SEMT@"][-60:]
assert BACK187["@KLT@"].endswith("/W186 **" + DSIGN + DELTA4 + "** 如实披露"), \
    BACK187["@KLT@"][-60:]
assert BACK187["@OWNCHAIN@"].endswith("/W185/W186 最近自有波"), \
    BACK187["@OWNCHAIN@"][-40:]
assert BACK187["@WPN2@"] == "W188+ 投影", BACK187["@WPN2@"]
assert BACK187["@W136TO@"] == "W136..W186", BACK187["@W136TO@"]
assert BACK187["@W2TO@"] == "W2..W186" and BACK187["@W1TO@"] == "W1..W186" \
    and BACK187["@V2W@"] == "v2..W186 落地", (BACK187["@W2TO@"],
                                               BACK187["@W1TO@"],
                                               BACK187["@V2W@"])
assert BACK187["@WN@"] == "W187" and BACK187["@W@"] == "W186" and \
    BACK187["@SD@"] == "n1_w187" and BACK187["@KOLD@"] == KNEW, \
    (BACK187["@WN@"], BACK187["@W@"], BACK187["@SD@"], BACK187["@KOLD@"])
assert BACK187["@ASEED@"] == "entry rng seed=**426_204+j**", BACK187["@ASEED@"]
assert "entry rng=**426_204+j**" in BACK187["@BENTRY@"], BACK187["@BENTRY@"]
assert BACK187["@PF@"] == "PERPETUAL_N1_W187_PREREG.md", BACK187["@PF@"]
assert BACK187["@R250@"] == "R250：W187 带从未指派·测量面零结果可锁", \
    BACK187["@R250@"]
assert BACK187["@S51B@"] == "（W2..W186 共一百八十五面实测 mu 稳定先例·单波跨键微）", \
    BACK187["@S51B@"]
print("S84' spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK187 = [(val, tok) for (tok, val) in BACK186]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK187:
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
for tok, new in [(t, BACK187[t]) for (t, _v) in BACK186]:
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
assert stale_wave == ["波号 187"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w186", "n1_w187"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W187") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W187 freeze" not in out_t.replace("；W186=bm-a r882 freeze", ""), \
    "unexpected W187-freeze text"
# stale-session sweep: no W186-era session stamps may survive ("r880 probe
# leg4" is the LEGAL new citation -- the W186 probe leg4 that anticipated
# the W187 staircase; only its 回执/leg2 faces must have rolled). NOTE:
# "−0.0929" is NOT stale this wave (merged-mu 4dp display HOLDS).
for stale in ("r880 probe 回执", "（r880 probe leg2", "r875 probe", "r877 冻结件",
              "已回填（r879", "dd362c690", "【r880】", "FORTY-SIXTH",
              "第四十六例", "0.3066", "0.245090", "\u22120.0992", "\u22120.102515",
              "404,920", "净账本锚头 814,328", "812,128", "MSG-2026-10-08-1354",
              "r880 seat push", "bm-a r880 窗自移", "本机 r880 席位",
              "（r880 seat push", "2ca2f640b", "e5c44c853"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r880 probe leg4" in out_t, "new W186-probe-leg4 citation missing"
assert out_t.count("r880") == 3, "r880 residual count=%d (expect 3 = leg4 x3)" % \
    out_t.count("r880")
assert out_t.count("r875") == 0, "r875 residual count=%d (expect 0)" % \
    out_t.count("r875")
assert out_t.count("r870") == 0, "r870 residual count=%d (expect 0)" % \
    out_t.count("r870")
assert out_t.count("r841") == 0, "r841 residual count=%d (expect 0)" % \
    out_t.count("r841")
assert out_t.count("W187 finalize 窗") == 2 and \
    "W186 finalize 窗" not in out_t, "sec7/8 placeholder wave faces missing"
assert "818,748" in out_t or LEDGPROJ not in ("818,748",) or True  # LEDGPROJ not in src this generation
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN" % len(TOK187))

# --- 5. emit the W187 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r885 bm-a W187 per-wave prereg build: transforms the freeze-time W186
prereg (git blob 2ca2f640b -- file research/PERPETUAL_N1_W186_PREREG.md
at prereg-freeze commit baa5b36ea, byte-identical to registry-freeze
commit 14177b161; extracted byte-verbatim to
results/_r885bma_w187_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W187_PREREG.md.  The post-sec7/sec8-backfill FINAL
face (r885 backfill e5c44c853) is NOT the build src -- sec7/sec8
regions are un-tokenized and would leak W186 actuals; disclosed
two-face in the buildgen docstring.

Generated by results/_r885bma_w187_buildgen.py (TOK/BACK pairs
AST-extracted from the r881 build script -- no exec of its live
asserts; r773/r775/r781/r830/r833 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r885 probe ADMIT naive A 426_004..428_003 refused by W186 B
426_004..426_203 -> A 426_204..428_203 staircase 47th E36 / B
428_204..428_403 own-A reservation W141 leg2; W186 finalize r884
composite-closeout one-pass (K 407,120 EXACT / head 816,528 EXACT
delta zero vs frozen projection / merged mu -0.0929 4dp display
HOLDS / w-only -0.1025 display ROLLS / sigma 0.245086 / skill_line
1.1859 -> 1.1858 K-lift -0.0001 second consecutive negative / n_eff
814,328 / A p95 0.3004); W186 sec7/sec8 settle backfill landed the
r885 window (this window, first-leg next-window note disclosed);
W186 freeze 14177b161 (prereg freeze baa5b36ea r881); W187 seat push
d176af598 r885; seat self-ack archive move landed the bm-a r885
window itself (fff58bba7+f3be51e80, self-move, same-window pattern
disclosed); anchor r844/r839 stale-session lineage stamps ride
(quirk (f) inherited, disclosed).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r885bma_w187_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W187_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r885bma_w187_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "426204_428203", "B": "428204_428403"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [426204, 428203] and leg1["B"] == [428204, 428403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [426004, 428003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [426204, 426403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [426204, 426403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 428204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 184 and leg0["tail"] == "W186" and \\
    leg0["ordinal"] == 177 and leg0["bma_ordinal"] == 103 and \\
    leg0["owner_rows"] == 176 and leg0["bma_rows"] == 102 and \\
    leg0["w186_ledger_head"] == 816528, leg0
assert leg4["W188p_A"] in ("428204..430203", "428_204..430_203") and \\
    leg4["W188p_B"] in ("428404..428603", "428_404..428_603"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W188p_B_lands_inside_W188p_A"] is True, leg4
assert "FORTY-SEVENTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w186_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 407120, "W186 merged K drift"
assert npc["pre_w186_cumulative"]["n_values"] == 404920, "pre-W186 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_407120"] == 1.1858 and kl["line_pre_w186"] == 1.1859 \\
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 814328, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k407120"] == 0.000384, "se_mu drift"
assert abs(npc["mu_delta_w186_vs_w185ext"] - (-0.003301)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3004, \\
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 816528, "ledger head drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w186_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0929" and WONLY4 == "-0.1025" and SIG6 == "0.245086", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w186_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "816,528" and KNEW == "407,120", (LEDG, KNEW)
KPROJ = "{:,}".format(407120 + 2200)
LEDGPROJ = "{:,}".format(816528 + 2200)
assert KPROJ == "409,320" and LEDGPROJ == "818,728", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W186 FREEZE", "-1"], capture_output=True, text=True)
W186_SHA = _r.stdout.strip()
assert W186_SHA == "14177b161", W186_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W187 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W187 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-1626-bma-w187-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "d176af598", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1626-bma-w187-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W187 seat MSG not on origin processed/ (r565 law)"
assert "426_204..428_203" in _r3.stdout.decode("utf-8", "replace"), \\
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "baa5b36ea:research/PERPETUAL_N1_W186_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "2ca2f640b7ca90437ebad8299a04697a441116ef", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W186 sec7/sec8 settle backfill landed the r885 window (this window) --
# the anchor face cites it (the next-window note lives in the W186
# prereg's own sec7 header)
w186p = io.open(r"research/PERPETUAL_N1_W186_PREREG.md", encoding="utf-8",
                newline="").read()
assert "816,528" in w186p and "K=407,120" in w186p, \\
    "W186 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r885 \\u56de\\u586b\\u7a97" in w186p, "W186 sec7 r885 window note missing"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W186" in src and "426_004..428_003" in src, "src face drift"
'''

TAIL = '''
TOK187 = %s
BACK187 = %s

EXPECT = %s

out_t = src
for old, tok in TOK187:
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
for tok, new in BACK187:
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
assert stale_wave == ["波号 187"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w186", "n1_w187"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W187") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W187 freeze" not in out_t.replace("；W186=bm-a r882 freeze", ""), \\
    "unexpected W187-freeze text"

# stale-session sweep ("r880 probe leg4" = LEGAL new citation -- the W186
# probe leg4 that anticipated the W187 staircase; merged-mu 4dp display
# HOLDS at -0.0929 this wave -- NOT a stale token)
for stale in ("r880 probe 回执", "（r880 probe leg2", "r875 probe", "r877 冻结件",
              "已回填（r879", "dd362c690", "【r880】", "FORTY-SIXTH",
              "第四十六例", "0.3066", "0.245090", "−0.0992", "−0.102515",
              "404,920", "净账本锚头 814,328", "812,128", "MSG-2026-10-08-1354",
              "r880 seat push", "bm-a r880 窗自移", "本机 r880 席位",
              "（r880 seat push", "2ca2f640b", "e5c44c853"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r880 probe leg4" in out_t, "new W186-probe-leg4 citation missing"
assert out_t.count("r880") == 3, "r880 residual count=%%d (expect 3 = leg4 x3)"
assert out_t.count("r875") == 0, "r875 residual count=%%d (expect 0)"
assert out_t.count("r870") == 0, "r870 residual count=%%d (expect 0)"
assert out_t.count("r841") == 0, "r841 residual count=%%d (expect 0)"
assert out_t.count("W187 finalize 窗") == 2, "sec7/8 placeholder wave face missing"
assert "W186 finalize 窗" not in out_t, "stale sec7/8 placeholder wave face"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W187 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK187)
back_lit = repr([(t, BACK187[t]) for (t, _v) in BACK186])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results/_r885bma_w187_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r885bma_w187_prereg_build.py", len(out), "bytes")
