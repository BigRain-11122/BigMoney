# -*- coding: utf-8 -*-

"""r872 bm-a generator: builds results/_r872bma_w184_prereg_build.py by
AST-extracting the r869 build script's BACK183/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts -- r833 law 1), then
deriving the BACK184 pairs as (token, rolled W184 value).  Old side = the
W183-era value (freeze-time blob 7be9ca473b at prereg-freeze commit
678da52e2, byte-identical to registry-freeze commit 481da4d78; extracted
byte-verbatim to results/_r872bma_w184_prereg_src.txt), new side = the S82
W184 fact map applied to that W183 text.  r773/r775/r781/r830 compliance
inherited: token-first two-phase vmap, whole-string composites, numerals
LAST; r735 substring-order law = BACK list order preserved (proj-A before
naive-A, proj-B before naive-B, own-B before prior-B; LEDG 806,718 consumed
before NEFF re-creates it; projection composites before KNEW bare roll);
pre-TOK sequential DRY below (r833 law 2, zero writes until every gate
green).

Structural notes vs the r869 bloodline (disclosed):
  * @S55@ and @SEATPUB@ are s82-ROLLED this wave (not fresh-constructed):
    every constituent of their W183 values is covered by map pairs (proj
    bands, own-B, cascade, MSG/sha, "r868 seat push"/"zi r868 shoukou"
    dedicated pairs).  Result byte-equal to a fresh construction; the DRY
    + stale sweeps verify.
  * @N171@/@N170@/@N169@ are vestigial tokens (EXPECT=0 in this and the
    prior generation): phase 1 skips them with a stray-check (the only
    legal bare-"183" strays are the two fixed historical "MSG-183x"
    references, which ride verbatim every wave).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r870bma_w184_probe_receipt.json rc0 ADMIT
    (leg0 registry 181 rows tail W183 ordinal 174 / bma_ordinal 100 /
    owner_rows 173 / bma_rows 99 / w183_ledger_head 808,918; leg1
    naive A 419_404..421_403 REFUSED at its own start by the registered
    W183 B band 419_404..419_603 -> honest forward walk 1 hop lands
    A 419_604..421_603 (staircase FORTY-FOURTH instance E36 per receipt
    A_semantics; the W183 seat leg4 + r868 probe leg4 + W183 prereg
    sec5.5/sec8 anticipated and MANDATED this re-derive -- projection
    and receipt ordinals MATCH, no divergence face); naive B 419_604..
    419_803 lands inside own-A 419_604..421_603 -> same-freeze mutual
    exclusion (W141 precedent leg2 law) -> reserved walk 1 hop lands
    B 421_604..421_803; leg2 conflicts 0; leg3 origin vacancy True at
    probe time (seat MSG published same window AFTER the probe, r565
    law held); leg4 W185+ projection A 421_604..423_603 hops=0 / B
    421_804..422_003 hops=0, B inside A);
  - W183 finalize landed r870 one-pass SAME-WINDOW (r381+r864 lesson
    honored) commit face results/perpetual_faces/n1_w183_results.json:
    ledger head 808,918 EXACT with proj delta +0; merged K=400,520
    EXACT; merged mu -0.09281502 4dp -0.0928 NO-ROLL (W182 display
    -0.0928 held); w183-only mu=-0.10262204 4dp -0.1026; sigma=
    0.24509857 6dp 0.245099; se_mu_at_k400520=0.000387; skill_line
    line_pre_w183 1.1855 -> line_merged@400,520 1.1855 (K-lift +0.0000
    EXACT-ZERO, n_eff_held_equal 806,718); canon flip NOT performed;
    A p95=0.3018;
  - W183 sec7/sec8 settle backfill landed the r870 SAME window (r864
    lesson welded; on-disk W183 prereg text "808,918" + "K=400,520"
    live-asserted below);
  - W183 freeze registered sha machine-derived = 481da4d78 (git log
    origin/main --grep "W183 FREEZE"); W184 seat push sha
    machine-derived = d1f15ebf9 (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed r870 window
    (processed/ path live-asserted this window).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W183 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "678da52e2:research/PERPETUAL_N1_W183_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W183 freeze-time blob not reachable"
blob = _r.stdout
_r2 = subprocess.run(
    ["git", "rev-parse", "678da52e2:research/PERPETUAL_N1_W183_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r2.stdout.strip()
assert BLOB_SHA == "7be9ca473b45e72cdefb304e766a534cc7046831", BLOB_SHA
_r2b = subprocess.run(
    ["git", "rev-parse", "481da4d78:research/PERPETUAL_N1_W183_PREREG.md"],
    capture_output=True, text=True)
assert _r2b.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r872bma_w184_prereg_src.txt", "wb").write(blob)
print("W184 src extracted:", len(blob), "bytes (W183 freeze-time blob", BLOB_SHA[:10], ")")

# --- 1. AST-extract the r869 build script's BACK183 + EXPECT ---------------
src869 = io.open(r"results\_r869bma_w183_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src869)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK183 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK183" and isinstance(node.value, ast.List):
            BACK183 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK183.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK183 is not None and EXPECT is not None, "BACK183/EXPECT not extracted"
assert len(BACK183) == 50 and len(EXPECT) == 50, (len(BACK183), len(EXPECT))
back183_map = dict(BACK183)
assert len(back183_map) == len(BACK183)
print("r869 BACK183 entries:", len(BACK183), "EXPECT entries:", len(EXPECT))

# --- 2. W184 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r870bma_w184_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "419604_421603", "B": "421604_421803"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [419604, 421603] and leg1["B"] == [421604, 421803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [419404, 421403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [419604, 419803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [419604, 419803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 421604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 181 and leg0["tail"] == "W183" and leg0["ordinal"] == 174 \
    and leg0["bma_ordinal"] == 100 and leg0["owner_rows"] == 173 \
    and leg0["bma_rows"] == 99 and leg0["w183_ledger_head"] == 808918, leg0
assert leg4["W185p_A"] == "421604..423603" or leg4["W185p_A"] == "421_604..423_603", leg4
assert leg4["W185p_B"] == "421804..422003" or leg4["W185p_B"] == "421_804..422_003", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W185p_B_lands_inside_W185p_A"] is True, leg4
assert "FORTY-FOURTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w183_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 400520, "W183 merged K drift"
assert npc["pre_w183_cumulative"]["n_values"] == 398320, "pre-W183 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_400520"] == 1.1855 and kl["line_pre_w183"] == 1.1855 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 806718, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k400520"] == 0.000387, "se_mu drift"
assert abs(npc["mu_delta_w183_vs_w182ext"] - (-0.010521)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3018, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w183_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_400520"]
PRE4 = "%.4f" % kl["line_pre_w183"]
SEM4 = "%.6f" % npc["se_mu_at_k400520"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0928" and WONLY4 == "-0.1026" and SIG6 == "0.245099", (MU4, WONLY4, SIG6)
assert LINE4 == "1.1855" and PRE4 == "1.1855" and SEM4 == "0.000387" \
    and P954 == "0.3018" and DELTA4 == "0.0000" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")      # display form U+2212 (r833 law 3)
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0928" and WONLY_U == "\u22120.1026", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w183_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "808,918" and KNEW == "400,520" and NEFF == "806,718", (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(400520 + 2200)
LEDGPROJ = "{:,}".format(808918 + 2200)
assert KPROJ == "402,720" and LEDGPROJ == "811,118", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W183 FREEZE", "-1"], capture_output=True, text=True)
W183_SHA = _r_.stdout.strip()
assert W183_SHA == "481da4d78", W183_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W184 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W184 FREEZE (r511 tail-lock)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "d1f15ebf9", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0826-bma-w184-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W184 seat MSG not on origin processed/ (r565 pre-freeze law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "419_604..421_603" in _seat_txt and "421_604..421_803" in _seat_txt, "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "678da52e2:research/PERPETUAL_N1_W183_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "7be9ca473b45e72cdefb304e766a534cc7046831", \
    "src blob drift: %s" % _r4.stdout.strip()
# W183 sec7/sec8 settle backfill landed the r870 SAME window (r864 lesson
# welded) -- the anchor face cites it (no heal-window disclosure needed)
w183p = io.open(r"research\PERPETUAL_N1_W183_PREREG.md", encoding="utf-8", newline="").read()
assert "808,918" in w183p and "K=400,520" in w183p, \
    "W183 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "419_604..421_603"
B_BAND = "421_604..421_803"
NAIVE_A = "419_404..421_403"
NAIVE_B = "419_604..419_803"
PRIOR_B = "419_404..419_603"     # registered W183 B band (refusal band)
A_SEED, B_SEED = "419_604", "421_604"
SEAT_MSG = "MSG-2026-10-08-0826-bma-w184-seat"
W185p_A = "421_604..423_603"
W185p_B = "421_804..422_003"

# --- 3. S82' = W183->W184 ordered fact map -----------------------------------
# (r735 substring-order law preserved from the r869 bloodline: projections
#  consumed before the naive rolls re-create them; own-B before prior-B;
#  composite numbers before bare rolls; LEDG before NEFF; cascade last,
#  W180 placeholder fixed by the cascade as in the r869 generation.)
S82 = [
    # -- window/session composites (longest first) --
    ("已回填（r868 同窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
     "已回填（r870 同窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r868 同窗）", "已回填（r870 同窗）"),
    ("r868 bm-a 带闸窗（pre-seat probe r868 单窗", "r870 bm-a 带闸窗（pre-seat probe r870 单窗"),
    ("（r868 承袭", "（r870 承袭"),
    ("r868 probe 单跑兑现注记", "r870 probe 单跑兑现注记"),
    ("（r868 probe leg2/leg3 实跑）", "（r870 probe leg2/leg3 实跑）"),
    ("r868 probe 回执 A_semantics 机读序数=FORTY-THIRD",
     "r870 probe 回执 A_semantics 机读序数=FORTY-FOURTH"),
    ("FORTY-THIRD（第四十三例）", "FORTY-FOURTH（第四十四例）"),
    ("r865 probe leg4", "r868 probe leg4"),
    ("（r867 冻结件）", "（r869 冻结件）"),
    ("_r868bma_w183_probe_receipt.json", "_r870bma_w184_probe_receipt.json"),
    ("MSG-2026-10-08-0741-bma-w183-seat", "MSG-2026-10-08-0826-bma-w184-seat"),
    ("ccd18034e", "d1f15ebf9"),
    ("【r868】", "【r870】"),
    ("r868 seat push", "r870 seat push"),
    ("自 r868 收口", "自 r870 收口"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B) --
    ("419_404..421_403", "421_604..423_603"),      # proj-A (W185+)
    ("419_604..419_803", "421_804..422_003"),      # proj-B (W185+)
    ("419_404..419_603", "421_604..421_803"),      # own-B (W184 B)
    ("417_404..419_403", "419_604..421_603"),      # own-A (W184 A)
    ("417_204..417_403", "419_404..419_603"),      # prior-B (W183 B)
    ("417_204..419_203", "419_404..421_403"),      # naive-A window (W184)
    ("417_404..417_603", "419_604..419_803"),      # naive-B window (W184)
    ("417_403+1", "419_603+1"),
    ("419_403+1", "421_603+1"),
    ("417_404+j", "419_604+j"),
    ("419_404+j", "421_604+j"),
    # -- ordinals (high first: projection pair before own pair) --
    ("第四十四例", "第四十五例"),
    ("第四十三例", "第四十四例"),
    ("第 181 枚", "第 182 枚"),
    ("行 172+本候选", "行 173+本候选"),
    ("第九十九枚", "第一百枚"),
    ("第 173 波", "第 174 波"),
    ("行 98+本候选", "行 99+本候选"),
    ("bm-a 98 行注册", "bm-a 99 行注册"),
    ("一百八十行注册", "一百八十一行注册"),
    ("机证 180 行", "机证 181 行"),
    ("一百八十一面实测", "一百八十二面实测"),
    # -- n1_w forms (high first) --
    ("n1_w183", "n1_w184"),
    ("n1_w182", "n1_w183"),
    # -- wave-word cascade (high first; W180 placeholder fixed by the tail) --
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 183=", "波号 184="),
    ("--wave 183", "--wave 184"),
    # -- numbers (projection composite first; LEDG 806,718 consumed before
    #    NEFF re-creates it; merged-mu 4dp NO-ROLL this wave -0.0928 held) --
    ("**400,520 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1854**", "**" + LINE4 + "**"),
    ("·line_pre 1.1854·", "·line_pre " + PRE4 + "·"),
    ("**0.3071**", "**" + P954 + "**"),
    ("**\u22120.0928**", "**" + MU_U + "**"),
    ("**\u22120.0921**", "**" + WONLY_U + "**"),
    ("**+0.0000**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245092", SIG6),
    ("806,718", LEDG),
    ("804,518", NEFF),
    ("398,320", KNEW),
]


def s82(t):
    for old, new in S82:
        t = t.replace(old, new)
    return t


def r1(text, old, new):
    n = text.count(old)
    assert n == 1, "r1 target count=%d for %r" % (n, old[:60])
    return text.replace(old, new)


# constructed tokens (chain appends / window-list rolls / vestigial numerals)
BACK184 = {
    "@CHAIN@": back183_map["@CHAIN@"] + "；W183=bm-a r869 freeze（" + W183_SHA + "）",
    "@KLT@": r1(back183_map["@KLT@"], " 如实披露",
                "/W183 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": r1(back183_map["@SEMT@"], "**0.000388**】）",
                 "**0.000388**→W183 **" + SEM4 + "**】）"),
    "@S55@": s82(back183_map["@S55@"]),
    "@SEATPUB@": s82(back183_map["@SEATPUB@"]),
    "@ORDINALS@": (
        r1(r1(r1(r1(r1(r1(r1(back183_map["@ORDINALS@"],
            "第 173 波", "第 174 波"),
            "第九十九枚", "第一百枚"),
            "行 98+本候选", "行 99+本候选"),
            "/W181/W182 最近自有波", "/W182/W183 最近自有波"),
            "注册表 W182 行后", "注册表 W183 行后"),
            "MSG-2026-10-08-0741-bma-w183-seat", SEAT_MSG),
            "ccd18034e", SEAT_SHA)
    ),
    "@OWNCHAIN@": r1(back183_map["@OWNCHAIN@"],
                     "/W182 最近自有波", "/W182/W183 最近自有波"),
    "@N171@": "184",
    "@N170@": "183",
    "@N169@": "182",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK184[tok] = s82(back183_map[tok])
missing = [t for (t, _v) in BACK183 if t not in BACK184]
assert not missing, missing
extra = [t for t in BACK184 if t not in back183_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK184["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（419_603+1）" in chk and "FORTY-FOURTH（第四十四例）" in chk, chk[:250]
chk = BACK184["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A 窗 " + A_BAND in chk and "（421_603+1）" in chk, chk[:250]
chk = BACK184["@ANCHOR@"]
assert "W1..W183 N1 finalize 已全部落地" in chk and "**808,918**" in chk \
    and "K=400,520 合并池" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r870 同窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK184["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + " 投影**", \
    BACK184["@POOL@"]
assert "**" + LINE4 + "**" in BACK184["@KLKEY@"] and "n_eff " + NEFF in BACK184["@KLKEY@"], \
    BACK184["@KLKEY@"]
assert "line_pre " + PRE4 in BACK184["@KLKEY@"], BACK184["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK184["@KLKEY@"], BACK184["@KLKEY@"]
assert BACK184["@WAVEFREE@"] == "波号 184=注册表 W183 行后首个自由号", BACK184["@WAVEFREE@"]
assert "n1_w184_results.json" in BACK184["@FN@"] and "n1_w183_results.json" in BACK184["@ODOLD@"]
assert BACK184["@WAVECLI@"] == "--wave 184/finalize --wave 184", BACK184["@WAVECLI@"]
assert "W185+ 投影" in BACK184["@S55@"] and W185p_A in BACK184["@S55@"] \
    and W185p_B in BACK184["@S55@"] and "继承第四十五例" in BACK184["@S55@"] \
    and "W184 B 带 " + B_BAND in BACK184["@S55@"], BACK184["@S55@"][:200]
assert SEAT_SHA in BACK184["@SEATPUB@"] and "r870 seat push" in BACK184["@SEATPUB@"] \
    and "自 r870 收口" in BACK184["@SEATPUB@"], BACK184["@SEATPUB@"][:200]
assert "第 174 波" in BACK184["@ORDINALS@"] and "第一百枚" in BACK184["@ORDINALS@"] \
    and "/W182/W183 最近自有波" in BACK184["@ORDINALS@"] \
    and "注册表 W183 行后" in BACK184["@ORDINALS@"], BACK184["@ORDINALS@"][:200]
assert "W185+ 投影" in BACK184["@SEATSENT@"] and SEAT_MSG in BACK184["@SEATSENT@"] \
    and "继承第四十五例" in BACK184["@SEATSENT@"], BACK184["@SEATSENT@"][:200]
assert "法典 §4 W184 行 A=" + A_BAND in BACK184["@ASEEDPROSE@"], BACK184["@ASEEDPROSE@"][:250]
assert "法典 §4 W184 行 B=" + B_BAND in BACK184["@BSEEDPROSE@"], BACK184["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK184["@S5ANCH@"] and "r839 承袭收口窗" in BACK184["@S5ANCH@"] \
    and "已回填（r870 同窗）" in BACK184["@S5ANCH@"], BACK184["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK184["@S51@"] and "**" + WONLY_U + "**" in BACK184["@S51@"], \
    BACK184["@S51@"]
assert "**" + MU_U + "**" in BACK184["@S51@"], BACK184["@S51@"]
assert "**" + SIG6 + "**" in BACK184["@S52@"], BACK184["@S52@"]
assert "**" + P954 + "**" in BACK184["@S53@"], BACK184["@S53@"]
assert "一百八十一行注册" in BACK184["@SCANFACE@"] and "表尾 W183 行" in BACK184["@SCANFACE@"] \
    and "机证 181 行" in BACK184["@SCANFACE@"], BACK184["@SCANFACE@"]
assert BACK184["@EOB@"] == "engine_owner==bm-a 99 行注册", BACK184["@EOB@"]
assert "PERPETUAL-N1-W184" in BACK184["@TITLE@"] and "第 182 枚" in BACK184["@TITLE@"] \
    and "【r870】" in BACK184["@TITLE@"], BACK184["@TITLE@"]
assert "r870 bm-a 带闸窗（pre-seat probe r870 单窗" in BACK184["@GATEW@"], BACK184["@GATEW@"]
assert BACK184["@VAC@"] == "（r870 probe leg2/leg3 实跑）", BACK184["@VAC@"]
assert "（r870 承袭" in BACK184["@MERGE@"], BACK184["@MERGE@"]
assert "r870 probe 单跑兑现注记" in BACK184["@CLAIMLAW@"], BACK184["@CLAIMLAW@"]
assert BACK184["@PRC@"] == "results/_r870bma_w184_probe_receipt.json", BACK184["@PRC@"]
assert "W183=bm-a r869 freeze（" + W183_SHA + "）" in BACK184["@CHAIN@"]
assert BACK184["@SEMT@"].endswith("→W183 **" + SEM4 + "**】）"), BACK184["@SEMT@"][-60:]
assert BACK184["@KLT@"].endswith("/W183 **" + DSIGN + DELTA4 + "** 如实披露"), BACK184["@KLT@"][-60:]
assert BACK184["@OWNCHAIN@"].endswith("/W182/W183 最近自有波"), BACK184["@OWNCHAIN@"][-40:]
assert BACK184["@WPN2@"] == "W185+ 投影", BACK184["@WPN2@"]
assert BACK184["@W136TO@"] == "W136..W183", BACK184["@W136TO@"]
assert BACK184["@W2TO@"] == "W2..W183" and BACK184["@W1TO@"] == "W1..W183" \
    and BACK184["@V2W@"] == "v2..W183 落地", (BACK184["@W2TO@"], BACK184["@W1TO@"], BACK184["@V2W@"])
assert BACK184["@WN@"] == "W184" and BACK184["@W@"] == "W183" and BACK184["@SD@"] == "n1_w184" \
    and BACK184["@KOLD@"] == KNEW, (BACK184["@WN@"], BACK184["@W@"], BACK184["@SD@"])
assert BACK184["@ASEED@"] == "entry rng seed=**419_604+j**", BACK184["@ASEED@"]
assert "entry rng=**419_604+j**" in BACK184["@BENTRY@"], BACK184["@BENTRY@"]
assert BACK184["@PF@"] == "PERPETUAL_N1_W184_PREREG.md", BACK184["@PF@"]
assert BACK184["@R250@"] == "R250：W184 带从未指派·测量面零结果可锁", BACK184["@R250@"]
assert BACK184["@S51B@"] == "（W2..W183 共一百八十二面实测 mu 稳定先例·单波跨键微）", \
    BACK184["@S51B@"]
print("S82 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK184 = [(val, tok) for (tok, val) in BACK183]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK184:
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
for tok, new in [(t, BACK184[t]) for (t, _v) in BACK183]:
    if EXPECT[tok] == 0:
        continue
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 184"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w183", "n1_w184"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W184") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W184 freeze" not in out_t.replace("；W183=bm-a r869 freeze", ""), \
    "unexpected W184-freeze text"
# stale-session sweep: no W183-era session stamps may survive (note: "r868
# probe leg4" is the LEGAL new citation -- the W183 probe leg4 that
# anticipated the W184 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r868 probe 回执", "（r868 probe leg2", "r865 probe", "r867 冻结件",
              "已回填（r868", "ccd18034e", "【r868】", "FORTY-THIRD",
              "第四十三例", "0.3071", "0.245092", "\u22120.0921", "1.1854",
              "398,320", "净账本锚头 806,718", "804,518", "MSG-2026-10-08-0741",
              "r868 seat push"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r868 probe leg4" in out_t, "new W183-probe-leg4 citation missing"
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, residue-zero, "
      "malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK184))

# --- 5. emit the W184 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r872 bm-a W184 per-wave prereg build: transforms the freeze-time W183
prereg (git blob 7be9ca473b -- file research/PERPETUAL_N1_W183_PREREG.md at
prereg-freeze commit 678da52e2, byte-identical to registry-freeze commit
481da4d78; extracted byte-verbatim to results/_r872bma_w184_prereg_src.txt)
into research/PERPETUAL_N1_W184_PREREG.md.

Generated by results/_r872bma_w184_buildgen.py (TOK/BACK pairs AST-extracted
from the r869 build script -- no exec of its time-locked live asserts;
r773/r775/r781/r830 compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK
list order preserved; pre-TOK sequential DRY 50/50).  r587
machine-derived facts (read from on-disk receipts): r870 probe ADMIT
naive A 419_404..421_403 refused by W183 B -> A 419_604..421_603
staircase 44th E36 / B 421_604..421_803 own-A reservation W141 leg2;
W183 finalize r870 one-pass same-window (K 400,520 EXACT / head 808,918
EXACT delta +0 / merged mu -0.0928 no-roll / w-only -0.1026 / sigma
0.245099 / skill_line 1.1855 -> 1.1855 K-lift +0.0000 exact-zero /
n_eff 806,718 / A p95 0.3018); W183 sec7/sec8 settle backfill landed
r870 SAME window (r864 lesson welded -- no heal window); W183 freeze
481da4d78; W184 seat push d1f15ebf9; seat self-ack processed/ on
origin (r870 window move).

Structural notes vs the r869 bloodline (disclosed):
  * @S55@/@SEATPUB@ s82-rolled this wave (all constituents map-covered);
  * @N171@/@N170@/@N169@ vestigial (EXPECT=0): phase 1 skips with a
    stray-check (the only legal bare-"183" strays are the fixed
    historical "MSG-183x" references);
  * cascade W180->W181 fixes the composite window-list placeholder
    (W159/W168/W169 stay fixed -- no new procrastination case in
    W182/W183, both same-window).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\\\_r872bma_w184_prereg_src.txt"
OUT = r"research\\\\PERPETUAL_N1_W184_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r870bma_w184_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "419604_421603", "B": "421604_421803"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [419604, 421603] and leg1["B"] == [421604, 421803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [419404, 421403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [419604, 419803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [419604, 419803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 421604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 181 and leg0["tail"] == "W183" and leg0["ordinal"] == 174 \\
    and leg0["bma_ordinal"] == 100 and leg0["owner_rows"] == 173 \\
    and leg0["bma_rows"] == 99 and leg0["w183_ledger_head"] == 808918, leg0
assert leg4["W185p_A"] in ("421604..423603", "421_604..423_603") and leg4["W185p_B"] in ("421804..422003", "421_804..422_003"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W185p_B_lands_inside_W185p_A"] is True, leg4
assert "FORTY-FOURTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w183_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 400520, "W183 merged K drift"
assert npc["pre_w183_cumulative"]["n_values"] == 398320, "pre-W183 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_400520"] == 1.1855 and kl["line_pre_w183"] == 1.1855 \\
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 806718, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k400520"] == 0.000387, "se_mu drift"
assert abs(npc["mu_delta_w183_vs_w182ext"] - (-0.010521)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3018, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w183_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0928" and WONLY4 == "-0.1026" and SIG6 == "0.245099", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w183_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "808,918" and KNEW == "400,520", (LEDG, KNEW)
KPROJ = "{:,}".format(400520 + 2200)
LEDGPROJ = "{:,}".format(808918 + 2200)
assert KPROJ == "402,720" and LEDGPROJ == "811,118", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W183 FREEZE", "-1"], capture_output=True, text=True)
W183_SHA = _r.stdout.strip()
assert W183_SHA == "481da4d78", W183_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W184 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W184 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-0826-bma-w184-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "d1f15ebf9", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0826-bma-w184-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W184 seat MSG not on origin (r565 pre-freeze law)"
assert "419_604..421_603" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "678da52e2:research/PERPETUAL_N1_W183_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "7be9ca473b45e72cdefb304e766a534cc7046831", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W183 sec7/sec8 settle backfill landed the r870 SAME window (r864 lesson
# welded) -- the anchor face cites it (no heal-window disclosure needed)
w183p = io.open(r"research\\\\PERPETUAL_N1_W183_PREREG.md", encoding="utf-8", newline="").read()
assert "808,918" in w183p and "K=400,520" in w183p, \\
    "W183 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W183" in src and "419_404..421_403" in src, "src face drift"
'''

TAIL = '''
TOK184 = %s
BACK184 = %s

EXPECT = %s

out_t = src
for old, tok in TOK184:
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
for tok, new in BACK184:
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
assert stale_wave == ["波号 184"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w183", "n1_w184"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W184") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W184 freeze" not in out_t.replace("；W183=bm-a r869 freeze", ""), \\
    "unexpected W184-freeze text"

# stale-session sweep ("r868 probe leg4" = LEGAL new citation; bare "398,320"
# = consumed by the K roll -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r868 probe 回执", "（r868 probe leg2", "r865 probe", "r867 冻结件",
              "已回填（r868", "ccd18034e", "【r868】", "FORTY-THIRD",
              "第四十三例", "0.3071", "0.245092", "−0.0921", "1.1854",
              "398,320", "净账本锚头 806,718", "804,518", "MSG-2026-10-08-0741",
              "r868 seat push"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r868 probe leg4" in out_t, "new W183-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W184 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK184)
back_lit = repr([(t, BACK184[t]) for (t, _v) in BACK183])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r872bma_w184_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r872bma_w184_prereg_build.py", len(out), "bytes")
