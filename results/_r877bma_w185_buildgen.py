# -*- coding: utf-8 -*-
"""r877 bm-a generator: builds results/_r877bma_w185_prereg_build.py by
AST-extracting the r872 build script's BACK184/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK185
pairs as (token, rolled W185 value).  Old side = the W184-era value
(freeze-time blob a9925eac6a at prereg-freeze commit f908433c4,
byte-identical to registry-freeze commit 7e791a87f; extracted
byte-verbatim to results/_r876bma_w185_prereg_src.txt at r876,
re-verified byte-identical this window), new side = the S83 W185 fact
map applied to that W184 text.  r773/r775/r781/r830 compliance
inherited: token-first two-phase vmap, whole-string composites,
numerals LAST; r735 substring-order law = BACK list order preserved
(projections consumed before the naive rolls re-create them; own-B
before prior-B; LEDG head before NEFF re-creates it; pool projection
composite before the bare K roll); pre-TOK sequential DRY below
(r833 law 2, zero writes until every gate green).

Structural notes vs the r872 bloodline (disclosed):
  * @S55@/@SEATPUB@/@SEATSENT@ are s83-ROLLED this wave (all their
    constituents map-covered: proj bands, own-B, cascade, MSG/sha,
    session composites, '（r869 冻结件）' dedicated pair);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both generations):
    phase 1 skips them with a stray-check (legal bare-183 strays = the
    two fixed historical "MSG-183x" references, riding verbatim);
  * self-ack archive citation honestly re-derived this wave: the W184
    prereg face carried "bm-c r741 窗代移·r566 先例" (stale for W184
    itself, superseded r874 disclosure); the W185 seat MSG self-ack
    move landed the bm-a r876 window (commit b0ce85956, self-move, not
    a cross-machine consume) -- dedicated pair, disclosed;
  * the anchor procrastination-precedent list "W159/W168/W169/W180"
    rides FIXED (no new procrastination case in W184 -- sec7/8 landed
    r875 same-window, r864 lesson 3rd consecutive);
  * cascade W181->W182 kept from the bloodline (window-list placeholder
    law, r872 generation note).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r875bma_w185_probe_receipt.json rc0 ADMIT
    (leg0 registry 182 rows tail W184 ordinal 175 / bma_ordinal 101 /
    owner_rows 174 / bma_rows 100 / w184_ledger_head 812,128; leg1
    naive A 421_604..423_603 REFUSED at its own start by the registered
    W184 B band 421_604..421_803 -> honest forward walk 1 hop lands
    A 421_804..423_803 (staircase FORTY-FIFTH instance E36 per receipt
    A_semantics; the W184 seat leg4 + r870 probe leg4 + W184 prereg
    sec5.5/sec8 anticipated and MANDATED this re-derive -- projection
    and receipt ordinals MATCH, no divergence face); naive B
    421_804..422_003 lands inside own-wave A 421_804..423_803 ->
    same-freeze mutual exclusion (W141 precedent leg2 law) -> reserved
    walk 1 hop lands B 423_804..424_003; leg2 conflicts 0; leg3 origin
    vacancy True at probe time (seat MSG published same window AFTER
    the probe, r565 law held); leg4 W186+ projection A 423_804..425_803
    hops=0 / B 424_004..424_203 hops=0, B inside A);
  - W184 finalize landed r875 one-pass SAME-window (r381+r864 lesson
    honored; ledger head 812,128 = 809,928 + 2,200 EXACT, includes the
    +1,010 REGIME5 post-freeze chain entry per r518 disclosure in the
    r875 commit face; merged K=402,720 EXACT; merged mu -0.09281762
    4dp -0.0928 NO-ROLL (3rd consecutive display hold); w184-only mu
    -0.09329114 4dp -0.0933; sigma 0.24509364 6dp 0.245094;
    se_mu_at_k402720=0.000386; skill_line line_pre_w184 1.1857 ->
    line_merged@402,720 1.1857 (K-lift +0.0000 EXACT-ZERO, n_eff held
    809,928); canon flip NOT performed; A p95=0.3194);
  - W184 sec7/sec8 settle backfill landed the r875 SAME window (r864
    lesson 3rd consecutive; on-disk W184 prereg text "812,128" +
    "K=402,720" live-asserted below);
  - W184 freeze registered sha machine-derived = 7e791a87f (git log
    origin/main --grep "W184 FREEZE"); W184 prereg freeze f908433c4
    (r872 window, blob a9925eac6a at both freeze commits, asserted
    live below); W185 seat push sha machine-derived = 304909e0e (git
    log --diff-filter=A on the seat MSG inbox path, r875 window);
    W185 seat self-ack archive move landed the bm-a r876 window
    (b0ce85956, self-move; processed/ path on origin live-verified
    below).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W184 prereg blob (LF, byte-verbatim) ----------
_r = subprocess.run(
    ["git", "rev-parse", "f908433c4:research/PERPETUAL_N1_W184_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "a9925eac6a82ec0aef89667639a664225091c232", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "7e791a87f:research/PERPETUAL_N1_W184_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "f908433c4:research/PERPETUAL_N1_W184_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
ondisk = io.open(r"results\_r876bma_w185_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src != freeze-time blob (r876 extract drift)"
print("W185 src verified:", len(blob), "bytes (W184 freeze-time blob",
      BLOB_SHA[:10] + ", on-disk byte-identical)")

# --- 1. AST-extract the r872 build script's BACK184 + EXPECT ---------------
src872 = io.open(r"results\_r872bma_w184_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src872)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK184 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK184" and \
           isinstance(node.value, ast.List):
            BACK184 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK184.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK184 is not None and EXPECT is not None, "BACK184/EXPECT not extracted"
assert len(BACK184) == 50 and len(EXPECT) == 50, (len(BACK184), len(EXPECT))
back184_map = dict(BACK184)
assert len(back184_map) == len(BACK184)
print("r872 BACK184 entries:", len(BACK184), "EXPECT entries:", len(EXPECT))

# --- 2. W185 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r875bma_w185_probe_receipt.json",
                       encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "421804_423803", "B": "423804_424003"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [421804, 423803] and leg1["B"] == [423804, 424003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [421604, 423603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [421804, 422003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [421804, 422003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 423804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 182 and leg0["tail"] == "W184" and \
    leg0["ordinal"] == 175 and leg0["bma_ordinal"] == 101 and \
    leg0["owner_rows"] == 174 and leg0["bma_rows"] == 100 and \
    leg0["w184_ledger_head"] == 812128, leg0
assert leg4["W186p_A"] in ("423804..425803", "423_804..425_803") and \
    leg4["W186p_B"] in ("424004..424203", "424_004..424_203"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W186p_B_lands_inside_W186p_A"] is True, leg4
assert "FORTY-FIFTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w184_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 402720, "W184 merged K drift"
assert npc["pre_w184_cumulative"]["n_values"] == 400520, "pre-W184 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_402720"] == 1.1857 and kl["line_pre_w184"] == 1.1857 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 809928, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k402720"] == 0.000386, "se_mu drift"
assert abs(npc["mu_delta_w184_vs_w183ext"] - 0.009331) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3194, \
    "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w184_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_402720"]
PRE4 = "%.4f" % kl["line_pre_w184"]
SEM4 = "%.6f" % npc["se_mu_at_k402720"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0928" and WONLY4 == "-0.0933" and SIG6 == "0.245094", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1857" and PRE4 == "1.1857" and SEM4 == "0.000386" \
    and P954 == "0.3194" and DELTA4 == "0.0000" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")      # display form U+2212 (r833 law 3)
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0928" and WONLY_U == "\u22120.0933", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w184_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "812,128" and KNEW == "402,720" and NEFF == "809,928", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(402720 + 2200)
LEDGPROJ = "{:,}".format(812128 + 2200)
assert KPROJ == "404,920" and LEDGPROJ == "814,328", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W184 FREEZE", "-1"], capture_output=True,
                     text=True)
W184_SHA = _r_.stdout.strip()
assert W184_SHA == "7e791a87f", W184_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W185 FREEZE", "-1"], capture_output=True,
                     text=True)
assert _r0.stdout.strip() == "", "origin already carries a W185 FREEZE (r511)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-1032-bma-w185-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "304909e0e", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-1032-bma-w185-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W185 seat MSG not on origin processed/ (r565 law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "421_804..423_803" in _seat_txt and "423_804..424_003" in _seat_txt, \
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                      "f908433c4:research/PERPETUAL_N1_W184_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "a9925eac6a82ec0aef89667639a664225091c232", \
    "src blob drift: %s" % _r4.stdout.strip()
# W184 sec7/sec8 settle backfill landed the r875 SAME window (r864
# lesson 3rd consecutive) -- the anchor face cites it (no heal-window
# disclosure needed)
w184p = io.open(r"research\PERPETUAL_N1_W184_PREREG.md", encoding="utf-8",
                newline="").read()
assert "812,128" in w184p and "K=402,720" in w184p, \
    "W184 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "421_804..423_803"
B_BAND = "423_804..424_003"
NAIVE_A = "421_604..423_603"
NAIVE_B = "421_804..422_003"
PRIOR_B = "421_604..421_803"     # registered W184 B band (refusal band)
A_SEED, B_SEED = "421_804", "423_804"
SEAT_MSG = "MSG-2026-10-08-1032-bma-w185-seat"
W186p_A = "423_804..425_803"
W186p_B = "424_004..424_203"

# --- 3. S83' = W184->W185 ordered fact map -----------------------------------
# (r735 substring-order law preserved from the r872 bloodline: projections
#  consumed before the naive rolls re-create them; own-B before prior-B;
#  pool projection composite before the bare K roll; LEDG head before NEFF;
#  high ordinals before low (第四十五例 before 第四十四例); cascade high
#  first; bare numerals LAST.)
S83 = [
    # -- window/session composites (longest first) --
    ("已回填（r870 同窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
     "已回填（r875 同窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r870 同窗）", "已回填（r875 同窗）"),
    ("r870 bm-a 带闸窗（pre-seat probe r870 单窗", "r875 bm-a 带闸窗（pre-seat probe r875 单窗"),
    ("（r870 承袭", "（r875 承袭"),
    ("r870 probe 单跑兑现注记", "r875 probe 单跑兑现注记"),
    ("（r870 probe leg2/leg3 实跑）", "（r875 probe leg2/leg3 实跑）"),
    ("r870 probe 回执 A_semantics 机读序数=FORTY-FOURTH",
     "r875 probe 回执 A_semantics 机读序数=FORTY-FIFTH"),
    ("FORTY-FOURTH（第四十四例）", "FORTY-FIFTH（第四十五例）"),
    ("r868 probe leg4", "r870 probe leg4"),
    ("（r869 冻结件）", "（r872 冻结件）"),
    ("_r870bma_w184_probe_receipt.json", "_r875bma_w185_probe_receipt.json"),
    ("MSG-2026-10-08-0826-bma-w184-seat", "MSG-2026-10-08-1032-bma-w185-seat"),
    ("d1f15ebf9", "304909e0e"),
    ("【r870】", "【r875】"),
    ("r870 seat push", "r875 seat push"),
    ("自 r870 收口", "自 r875 收口"),
    ("bm-c r741 窗代移·r566 先例·如实注记", "bm-a r876 窗自移·如实注记"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B) --
    ("421_604..423_603", "423_804..425_803"),      # proj-A (W186+)
    ("421_804..422_003", "424_004..424_203"),      # proj-B (W186+)
    ("421_604..421_803", "423_804..424_003"),      # own-B (W185 B)
    ("419_604..421_603", "421_804..423_803"),      # own-A (W185 A)
    ("419_404..419_603", "421_604..421_803"),      # prior-B (W184 B)
    ("419_404..421_403", "421_604..423_603"),      # naive-A window (W185)
    ("419_604..419_803", "421_804..422_003"),      # naive-B window (W185)
    ("419_603+1", "421_803+1"),
    ("421_603+1", "423_803+1"),
    ("419_604+j", "421_804+j"),
    ("421_604+j", "423_804+j"),
    # -- ordinals (high first: projection pair before own pair) --
    ("第四十五例", "第四十六例"),
    ("第四十四例", "第四十五例"),
    ("第 182 枚", "第 183 枚"),
    ("行 173+本候选", "行 174+本候选"),
    ("第一百枚", "第一百零一枚"),
    ("第 174 波", "第 175 波"),
    ("行 99+本候选", "行 100+本候选"),
    ("bm-a 99 行注册", "bm-a 100 行注册"),
    ("一百八十一行注册", "一百八十二行注册"),
    ("机证 181 行", "机证 182 行"),
    ("一百八十二面实测", "一百八十三面实测"),
    # -- n1_w forms (high first) --
    ("n1_w184", "n1_w185"),
    ("n1_w183", "n1_w184"),
    # -- wave-word cascade (high first) --
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 184=", "波号 185="),
    ("--wave 184", "--wave 185"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; merged-mu 4dp NO-ROLL 3rd consecutive;
    #    w-only mu rolls -0.1026 -> -0.0933 this wave) --
    ("**402,720 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1855**", "**" + LINE4 + "**"),
    ("·line_pre 1.1855·", "·line_pre " + PRE4 + "·"),
    ("**0.3018**", "**" + P954 + "**"),
    ("**\u22120.0928**", "**" + MU_U + "**"),
    ("**\u22120.1026**", "**" + WONLY_U + "**"),
    ("**+0.0000**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245099", SIG6),
    ("808,918", LEDG),
    ("806,718", NEFF),
    ("400,520", KNEW),
]


def s83(t):
    for old, new in S83:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / session-keyed faces / vestigial)
BACK185 = {
    "@CHAIN@": back184_map["@CHAIN@"] + "；W184=bm-a r874 freeze（" + W184_SHA + "）",
    "@KLT@": r1(back184_map["@KLT@"], " 如实披露",
                "/W184 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": r1(back184_map["@SEMT@"], "**0.000387**】）",
                 "**0.000387**→W184 **" + SEM4 + "**】）"),
    "@S55@": s83(back184_map["@S55@"]),
    "@SEATPUB@": s83(back184_map["@SEATPUB@"]),
    "@ORDINALS@": (
        r1(r1(r1(r1(r1(r1(r1(back184_map["@ORDINALS@"],
            "第 174 波", "第 175 波"),
            "第一百枚", "第一百零一枚"),
            "行 99+本候选", "行 100+本候选"),
            "/W182/W183 最近自有波", "/W183/W184 最近自有波"),
            "注册表 W183 行后", "注册表 W184 行后"),
            "MSG-2026-10-08-0826-bma-w184-seat", SEAT_MSG),
            "d1f15ebf9", SEAT_SHA)
    ),
    "@OWNCHAIN@": r1(back184_map["@OWNCHAIN@"],
                     "/W182/W183 最近自有波", "/W183/W184 最近自有波"),
    "@N171@": "185",
    "@N170@": "184",
    "@N169@": "183",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK185[tok] = s83(back184_map[tok])
missing = [t for (t, _v) in BACK184 if t not in BACK185]
assert not missing, missing
extra = [t for t in BACK185 if t not in back184_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK185["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（421_803+1）" in chk and "FORTY-FIFTH（第四十五例）" in chk, chk[:250]
chk = BACK185["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A 窗 " + A_BAND in chk and "（423_803+1）" in chk, chk[:250]
chk = BACK185["@ANCHOR@"]
assert "W1..W184 N1 finalize 已全部落地" in chk and "**812,128**" in chk \
    and "K=402,720 合并池" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r875 同窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK185["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + \
    " 投影**", BACK185["@POOL@"]
assert "**" + LINE4 + "**" in BACK185["@KLKEY@"] and "n_eff " + NEFF in \
    BACK185["@KLKEY@"], BACK185["@KLKEY@"]
assert "line_pre " + PRE4 in BACK185["@KLKEY@"], BACK185["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK185["@KLKEY@"], BACK185["@KLKEY@"]
assert BACK185["@WAVEFREE@"] == "波号 185=注册表 W184 行后首个自由号", \
    BACK185["@WAVEFREE@"]
assert "n1_w185_results.json" in BACK185["@FN@"] and \
    "n1_w184_results.json" in BACK185["@ODOLD@"]
assert BACK185["@WAVECLI@"] == "--wave 185/finalize --wave 185", \
    BACK185["@WAVECLI@"]
assert "W186+ 投影" in BACK185["@S55@"] and W186p_A in BACK185["@S55@"] \
    and W186p_B in BACK185["@S55@"] and "继承第四十六例" in BACK185["@S55@"] \
    and "W185 B 带 " + B_BAND in BACK185["@S55@"], BACK185["@S55@"][:200]
assert SEAT_SHA in BACK185["@SEATPUB@"] and "r875 seat push" in \
    BACK185["@SEATPUB@"] and "自 r875 收口" in BACK185["@SEATPUB@"] \
    and "bm-a r876 窗自移" in BACK185["@SEATPUB@"], BACK185["@SEATPUB@"][:200]
assert "第 175 波" in BACK185["@ORDINALS@"] and "第一百零一枚" in \
    BACK185["@ORDINALS@"] and "/W183/W184 最近自有波" in BACK185["@ORDINALS@"] \
    and "注册表 W184 行后" in BACK185["@ORDINALS@"], BACK185["@ORDINALS@"][:200]
assert "W186+ 投影" in BACK185["@SEATSENT@"] and SEAT_MSG in \
    BACK185["@SEATSENT@"] and "继承第四十六例" in BACK185["@SEATSENT@"], \
    BACK185["@SEATSENT@"][:200]
assert "法典 §4 W185 行 A=" + A_BAND in BACK185["@ASEEDPROSE@"], \
    BACK185["@ASEEDPROSE@"][:250]
assert "法典 §4 W185 行 B=" + B_BAND in BACK185["@BSEEDPROSE@"], \
    BACK185["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK185["@S5ANCH@"] and "r839 承袭收口窗" in \
    BACK185["@S5ANCH@"] and "已回填（r875 同窗）" in BACK185["@S5ANCH@"], \
    BACK185["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK185["@S51@"] and \
    "**" + WONLY_U + "**" in BACK185["@S51@"], BACK185["@S51@"]
assert "**" + MU_U + "**" in BACK185["@S51@"], BACK185["@S51@"]
assert "**" + SIG6 + "**" in BACK185["@S52@"], BACK185["@S52@"]
assert "**" + P954 + "**" in BACK185["@S53@"], BACK185["@S53@"]
assert "一百八十二行注册" in BACK185["@SCANFACE@"] and "表尾 W184 行" in \
    BACK185["@SCANFACE@"] and "机证 182 行" in BACK185["@SCANFACE@"], \
    BACK185["@SCANFACE@"]
assert BACK185["@EOB@"] == "engine_owner==bm-a 100 行注册", BACK185["@EOB@"]
assert "PERPETUAL-N1-W185" in BACK185["@TITLE@"] and "第 183 枚" in \
    BACK185["@TITLE@"] and "【r875】" in BACK185["@TITLE@"], BACK185["@TITLE@"]
assert "r875 bm-a 带闸窗（pre-seat probe r875 单窗" in BACK185["@GATEW@"], \
    BACK185["@GATEW@"]
assert BACK185["@VAC@"] == "（r875 probe leg2/leg3 实跑）", BACK185["@VAC@"]
assert "（r875 承袭" in BACK185["@MERGE@"], BACK185["@MERGE@"]
assert "r875 probe 单跑兑现注记" in BACK185["@CLAIMLAW@"], \
    BACK185["@CLAIMLAW@"]
assert BACK185["@PRC@"] == "results/_r875bma_w185_probe_receipt.json", \
    BACK185["@PRC@"]
assert "W184=bm-a r874 freeze（" + W184_SHA + "）" in BACK185["@CHAIN@"]
assert BACK185["@SEMT@"].endswith("→W184 **" + SEM4 + "**】）"), \
    BACK185["@SEMT@"][-60:]
assert BACK185["@KLT@"].endswith("/W184 **" + DSIGN + DELTA4 + "** 如实披露"), \
    BACK185["@KLT@"][-60:]
assert BACK185["@OWNCHAIN@"].endswith("/W183/W184 最近自有波"), \
    BACK185["@OWNCHAIN@"][-40:]
assert BACK185["@WPN2@"] == "W186+ 投影", BACK185["@WPN2@"]
assert BACK185["@W136TO@"] == "W136..W184", BACK185["@W136TO@"]
assert BACK185["@W2TO@"] == "W2..W184" and BACK185["@W1TO@"] == "W1..W184" \
    and BACK185["@V2W@"] == "v2..W184 落地", (BACK185["@W2TO@"],
                                               BACK185["@W1TO@"],
                                               BACK185["@V2W@"])
assert BACK185["@WN@"] == "W185" and BACK185["@W@"] == "W184" and \
    BACK185["@SD@"] == "n1_w185" and BACK185["@KOLD@"] == KNEW, \
    (BACK185["@WN@"], BACK185["@W@"], BACK185["@SD@"], BACK185["@KOLD@"])
assert BACK185["@ASEED@"] == "entry rng seed=**421_804+j**", BACK185["@ASEED@"]
assert "entry rng=**421_804+j**" in BACK185["@BENTRY@"], BACK185["@BENTRY@"]
assert BACK185["@PF@"] == "PERPETUAL_N1_W185_PREREG.md", BACK185["@PF@"]
assert BACK185["@R250@"] == "R250：W185 带从未指派·测量面零结果可锁", \
    BACK185["@R250@"]
assert BACK185["@S51B@"] == "（W2..W184 共一百八十三面实测 mu 稳定先例·单波跨键微）", \
    BACK185["@S51B@"]
print("S83 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK185 = [(val, tok) for (tok, val) in BACK184]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK185:
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
for tok, new in [(t, BACK185[t]) for (t, _v) in BACK184]:
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
assert stale_wave == ["波号 185"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w184", "n1_w185"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W185") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W185 freeze" not in out_t.replace("；W184=bm-a r874 freeze", ""), \
    "unexpected W185-freeze text"
# stale-session sweep: no W184-era session stamps may survive ("r870 probe
# leg4" is the LEGAL new citation -- the W184 probe leg4 that anticipated
# the W185 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r870 probe 回执", "（r870 probe leg2", "r868 probe", "r869 冻结件",
              "已回填（r870", "d1f15ebf9", "【r870】", "FORTY-FOURTH",
              "第四十四例", "0.3018", "0.245099", "\u22120.1026", "1.1855",
              "400,520", "净账本锚头 808,918", "806,718", "MSG-2026-10-08-0826",
              "r870 seat push", "bm-c r741"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r870 probe leg4" in out_t, "new W184-probe-leg4 citation missing"
assert out_t.count("r870") == 3, "r870 residual count=%d (expect 3 = leg4 x3)" % \
    out_t.count("r870")
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN" % len(TOK185))

# --- 5. emit the W185 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r877 bm-a W185 per-wave prereg build: transforms the freeze-time W184
prereg (git blob a9925eac6a -- file research/PERPETUAL_N1_W184_PREREG.md
at prereg-freeze commit f908433c4, byte-identical to registry-freeze
commit 7e791a87f; extracted byte-verbatim to
results/_r876bma_w185_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W185_PREREG.md.

Generated by results/_r877bma_w185_buildgen.py (TOK/BACK pairs
AST-extracted from the r872 build script -- no exec of its live
asserts; r773/r775/r781/r830 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r875 probe ADMIT naive A 421_604..423_603 refused by W184 B ->
A 421_804..423_803 staircase 45th E36 / B 423_804..424_003 own-A
reservation W141 leg2; W184 finalize r875 one-pass same-window (K
402,720 EXACT / head 812,128 EXACT delta +0 / merged mu -0.0928
no-roll 3rd consecutive / w-only -0.0933 / sigma 0.245094 /
skill_line 1.1857 -> 1.1857 K-lift +0.0000 exact-zero / n_eff
809,928 / A p95 0.3194); W184 sec7/sec8 settle backfill landed r875
SAME window (r864 lesson 3rd consecutive); W184 freeze 7e791a87f
(prereg freeze f908433c4 r872); W185 seat push 304909e0e r875; seat
self-ack archive move landed the bm-a r876 window (b0ce85956,
self-move; the W184 prereg's "bm-c r741" citation was its own stale
face, superseded r874 -- this face honestly re-derived).

Structural notes vs the r872 bloodline (disclosed):
  * @S55@/@SEATPUB@/@SEATSENT@ s83-rolled this wave (all constituents
    map-covered);
  * @N171@/@N170@/@N169@ vestigial (EXPECT=0): phase 1 skips with a
    stray-check (the only legal bare-"183" strays are the fixed
    historical "MSG-183x" references);
  * self-ack citation pair "bm-c r741 窗代移·r566 先例" ->
    "bm-a r876 窗自移" (self-move, dedicated pair, disclosed);
  * anchor procrastination-precedent list "W159/W168/W169/W180" rides
    FIXED (W184 sec7/8 landed r875 same-window, no new case).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\\\_r876bma_w185_prereg_src.txt"
OUT = r"research\\\\PERPETUAL_N1_W185_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r875bma_w185_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "421804_423803", "B": "423804_424003"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [421804, 423803] and leg1["B"] == [423804, 424003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [421604, 423603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [421804, 422003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [421804, 422003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 423804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 182 and leg0["tail"] == "W184" and \\
    leg0["ordinal"] == 175 and leg0["bma_ordinal"] == 101 and \\
    leg0["owner_rows"] == 174 and leg0["bma_rows"] == 100 and \\
    leg0["w184_ledger_head"] == 812128, leg0
assert leg4["W186p_A"] in ("423804..425803", "423_804..425_803") and \\
    leg4["W186p_B"] in ("424004..424203", "424_004..424_203"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W186p_B_lands_inside_W186p_A"] is True, leg4
assert "FORTY-FIFTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w184_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 402720, "W184 merged K drift"
assert npc["pre_w184_cumulative"]["n_values"] == 400520, "pre-W184 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_402720"] == 1.1857 and kl["line_pre_w184"] == 1.1857 \\
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 809928, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k402720"] == 0.000386, "se_mu drift"
assert abs(npc["mu_delta_w184_vs_w183ext"] - 0.009331) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3194, \\
    "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w184_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0928" and WONLY4 == "-0.0933" and SIG6 == "0.245094", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w184_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "812,128" and KNEW == "402,720", (LEDG, KNEW)
KPROJ = "{:,}".format(402720 + 2200)
LEDGPROJ = "{:,}".format(812128 + 2200)
assert KPROJ == "404,920" and LEDGPROJ == "814,328", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W184 FREEZE", "-1"], capture_output=True, text=True)
W184_SHA = _r.stdout.strip()
assert W184_SHA == "7e791a87f", W184_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W185 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W185 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-1032-bma-w185-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "304909e0e", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1032-bma-w185-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W185 seat MSG not on origin (r565 pre-freeze law)"
assert "421_804..423_803" in _r3.stdout.decode("utf-8", "replace"), \\
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "f908433c4:research/PERPETUAL_N1_W184_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "a9925eac6a82ec0aef89667639a664225091c232", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W184 sec7/sec8 settle backfill landed the r875 SAME window (r864
# lesson 3rd consecutive) -- the anchor face cites it (no heal-window
# disclosure needed)
w184p = io.open(r"research\\\\PERPETUAL_N1_W184_PREREG.md", encoding="utf-8",
                newline="").read()
assert "812,128" in w184p and "K=402,720" in w184p, \\
    "W184 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W184" in src and "421_604..423_603" in src, "src face drift"
'''

TAIL = '''
TOK185 = %s
BACK185 = %s

EXPECT = %s

out_t = src
for old, tok in TOK185:
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
for tok, new in BACK185:
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
assert stale_wave == ["波号 185"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w184", "n1_w185"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W185") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W185 freeze" not in out_t.replace("；W184=bm-a r874 freeze", ""), \\
    "unexpected W185-freeze text"

# stale-session sweep ("r870 probe leg4" = LEGAL new citation; bare
# "400,520" = consumed by the K roll -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r870 probe 回执", "（r870 probe leg2", "r868 probe", "r869 冻结件",
              "已回填（r870", "d1f15ebf9", "【r870】", "FORTY-FOURTH",
              "第四十四例", "0.3018", "0.245099", "−0.1026", "1.1855",
              "400,520", "净账本锚头 808,918", "806,718", "MSG-2026-10-08-0826",
              "r870 seat push", "bm-c r741"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r870 probe leg4" in out_t, "new W184-probe-leg4 citation missing"
assert out_t.count("r870") == 3, "r870 residual count=%%d (expect 3 = leg4 x3)"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W185 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK185)
back_lit = repr([(t, BACK185[t]) for (t, _v) in BACK184])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r877bma_w185_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r877bma_w185_prereg_build.py", len(out), "bytes")
