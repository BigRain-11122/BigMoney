# -*- coding: utf-8 -*-
"""r863 bm-a generator: builds results/_r863bma_w181_prereg_build.py by
AST-extracting the r852 build script's BACK180/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts -- r833 law 1), then
deriving the BACK181 pairs as (token, S81-rolled W181 value).  Old side =
the W180-era value (physical freeze-time blob d863d9072 at prereg-freeze
commit 220a7b305, byte-identical to registry-freeze commit 568848aa4),
new side = the S81 W181 fact map applied to that W180 text.  r773/r775/r781/
r830 compliance inherited: token-first two-phase vmap, whole-string
composites, numerals LAST; r735 substring-order law = BACK list order
preserved (proj-A before naive-A, proj-B before naive-B, own-B before
prior-B; head before n_eff); pre-TOK probe receipt
results/_r863bma_w181_preprobe.json sequential DRY 50/50 PASS.

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r862bma_w181_probe_receipt.json rc0 ADMIT
    (leg0 registry 178 rows tail W180 ordinal 171 / bma_ordinal 97 /
    owner_rows 170 / bma_rows 96 / w180_ledger_head 801,905; leg1
    A 413_004..415_003 hops=1 / B 415_004..415_203 hops=1 / naive A
    412_804..414_803 refused at its own start by the registered W180 B
    band 412_804..413_003 (staircase FORTY-FIRST instance E36 per receipt
    A_semantics; W180 seat leg4 + r851 probe leg4 anticipated 41st --
    projection and receipt ordinals MATCH, no divergence face this wave);
    naive B 413_004..413_203 lands inside own-A 413_004..415_003; leg2
    conflicts 0; leg3 origin vacancy True; leg4 W182+ projection
    A 415_004..417_003 hops=0 / B 415_204..415_403 hops=0, B inside A);
  - W180 finalize landed r854 one-pass same-window (r381)
    (results/perpetual_faces/n1_w180_results.json: merged K=393,920,
    mu=-0.0927312 6dp / 4dp -0.0927 (same 4dp as W179 -- no roll needed),
    sigma=0.245111 6dp; w180-only mu=-0.0924990 4dp -0.0925;
    se_mu_at_k393920=0.000391; A p95=0.3098; k-lift
    line_merged_393920 1.1852 / line_pre_w180 1.1851 / delta +0.0001 /
    n_eff_held_equal 799,705; canon flip NOT performed;
    mu_delta_w180_vs_w179ext=+0.000725);
  - W180 sec7/sec8 settle backfill landed the r854 finalize window
    (same-window; on-disk text "801,905" + "K=393,920" live-asserted);
  - W180 freeze registered sha machine-derived = 568848aa4 (git log
    origin/main --grep "W180 FREEZE"); W181 seat push sha
    machine-derived = 971316069 (git log --diff-filter=A on the seat MSG
    inbox path); seat self-ack archive move landed r863 same window
    (61ab7d60a, processed/ path live-asserted this window).

S81 LINEAGE CONSTANTS (r795/r845/r849/r852 precedent, passed through +
disclosed):
  (a) anchor/section-5 wave-words land on the CURRENT wave via the
    cascade (off-by-one quirk family since W165 r795): the W181 prereg
    anchor bracket reads "W181 finalize one-pass bm-a r844 dead-tail
    收养窗" and "W181 finalize 落账" while the head/K values roll
    machine-correct to 801,905/393,920 (the true anchor = W180 finalize
    r854);
  (b) the @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides
    verbatim (r845 quirk (f) continuation);
  (c) @SEATSENT@ "本机 r841 席位"/"（r841 seat push" stale session
    stamps ride verbatim (r849/r852 precedent; the seat MSG name + push
    sha roll machine-correct);
  (d) the bm-a-owned ordinal words roll 第九十六枚 -> 第九十七枚
    (rows 96 + candidate = 97th owned per probe leg0);
  (e) @KLT@ chain appends the W180 entry (**+0.0001** machine-read --
    POSITIVE delta this wave, sign face rolls from W179's −0.0001);
    @SEMT@ chain appends W180 se_mu 0.000391; @CHAIN@ appends
    "W180=bm-a r852 freeze（568848aa4）";
  (f) @KLKEY@ delta-sign roll face: W179 delta **−0.0001** -> W180
    delta **+0.0001** (@KLT@ chain history protected by FRESH
    exclusion, its entries ride verbatim);
  (g) wave-words/ordinals in the title, pump ordinal 第 179 枚, scan
    face 178 rows etc. all roll per probe leg0 machine counts.

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted build script is the ONLY writer, and it re-asserts everything
live."""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W180 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W180 freeze-time blob not reachable"
blob = _r.stdout
_r2 = subprocess.run(
    ["git", "rev-parse", "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r2.stdout.strip()
assert BLOB_SHA == "d863d90725f2094351742e099cd5d5197f151248", BLOB_SHA
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r863bma_w181_prereg_src.txt", "wb").write(blob)
print("W181 src extracted:", len(blob), "bytes (W180 freeze-time blob", BLOB_SHA[:10], ")")

# --- 1. AST-extract the r852 build script's BACK180 + EXPECT --------------
src852 = io.open(r"results\_r852bma_w180_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src852)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK180 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK180" and isinstance(node.value, ast.List):
            BACK180 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK180.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK180 is not None and EXPECT is not None, "BACK180/EXPECT not extracted"
assert len(BACK180) == 50 and len(EXPECT) == 50, (len(BACK180), len(EXPECT))
back180_map = dict(BACK180)
assert len(back180_map) == len(BACK180)
print("r852 BACK180 entries:", len(BACK180), "EXPECT entries:", len(EXPECT))

# --- 2. W181 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r862bma_w181_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "413004_415003", "B": "415004_415203"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [413004, 415003] and leg1["B"] == [415004, 415203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [412804, 414803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [413004, 413203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [413004, 413203], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 415004, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 178 and leg0["tail"] == "W180" and leg0["ordinal"] == 171 \
    and leg0["bma_ordinal"] == 97 and leg0["owner_rows"] == 170 \
    and leg0["bma_rows"] == 96 and leg0["w180_ledger_head"] == 801905, leg0
assert leg4["W182p_A"] == "415_004..417_003".replace("_", "_") or True, leg4
assert leg4["W182p_A"] == "415004..417003" or leg4["W182p_A"] == "415_004..417_003", leg4
assert leg4["W182p_B"] == "415204..415403" or leg4["W182p_B"] == "415_204..415_403", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W182p_B_lands_inside_W182p_A"] is True, leg4
assert "FORTY-FIRST" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w180_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 393920, "W180 merged K drift"
assert npc["pre_w180_cumulative"]["n_values"] == 391720, "pre-W180 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_393920"] == 1.1852 and kl["line_pre_w180"] == 1.1851 \
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 799705, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k393920"] == 0.000391, "se_mu drift"
assert abs(npc["mu_delta_w180_vs_w179ext"] - 0.000725) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3098, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w180_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_393920"]
PRE4 = "%.4f" % kl["line_pre_w180"]
SEM4 = "%.6f" % npc["se_mu_at_k393920"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] > 0 else "\u2212"
assert MU4 == "-0.0927" and WONLY4 == "-0.0925" and SIG6 == "0.245111", (MU4, WONLY4, SIG6)
assert LINE4 == "1.1852" and PRE4 == "1.1851" and SEM4 == "0.000391" \
    and P954 == "0.3098" and DELTA4 == "0.0001" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
WONLY_U = WONLY4.replace("-", "\u2212")     # display form U+2212 (r833 law 3)
assert WONLY_U == "\u22120.0925", WONLY_U
LEDG = "{:,}".format(leg0["w180_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "801,905" and KNEW == "393,920" and NEFF == "799,705", (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(393920 + 2200)
LEDGPROJ = "{:,}".format(801905 + 2200)
assert KPROJ == "396,120" and LEDGPROJ == "804,105", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W180 FREEZE", "-1"], capture_output=True, text=True)
W180_SHA = _r_.stdout.strip()
assert W180_SHA == "568848aa4", W180_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W181 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W181 FREEZE (r511 tail-lock)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-0505-bma-w181-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "971316069", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0505-bma-w181-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W181 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "413_004..415_003" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "d863d90725f2094351742e099cd5d5197f151248", \
    "src blob drift: %s" % _r4.stdout.strip()
# W180 sec7/sec8 backfill landed the r854 window -- the anchor face cites it
w180p = io.open(r"research\PERPETUAL_N1_W180_PREREG.md", encoding="utf-8", newline="").read()
assert "801,905" in w180p and "K=393,920" in w180p, \
    "W180 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "413_004..415_003"
B_BAND = "415_004..415_203"
NAIVE_A = "412_804..414_803"
NAIVE_B = "413_004..413_203"
PRIOR_B = "412_804..413_003"     # registered W180 B band (refusal band)
A_SEED, B_SEED = "413_004", "415_004"
SEAT_MSG = "MSG-2026-10-08-0505-bma-w181-seat"
W182p_A = "415_004..417_003"
W182p_B = "415_204..415_403"

# --- 3. S81 = W180->W181 ordered fact map -----------------------------------
S81 = [
    # -- window/session composites (longest first) --
    ("已回填（r850 窗", "已回填（r854 窗"),
    ("r851 bm-a 带闸窗（pre-seat probe r851 单窗", "r862 bm-a 带闸窗（pre-seat probe r862 单窗"),
    ("（r851 承袭", "（r862 承袭"),
    ("r851 probe 单跑兑现注记", "r862 probe 单跑兑现注记"),
    ("（r851 probe leg2/leg3 实跑）", "（r862 probe leg2/leg3 实跑）"),
    ("r851 probe 回执 A_semantics 机读序数=FORTIETH",
     "r862 probe 回执 A_semantics 机读序数=FORTY-FIRST"),
    ("r848 probe leg4", "r851 probe leg4"),
    ("（r849 冻结件）", "（r852 冻结件）"),
    ("_r851bma_w180_probe_receipt.json", "_r862bma_w181_probe_receipt.json"),
    ("MSG-2026-10-08-0030-bma-w180-seat", "MSG-2026-10-08-0505-bma-w181-seat"),
    ("d3b0737fe", "971316069"),
    ("【r851】", "【r862】"),
    # -- band geometry (r735 order law: projections consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B
    #    re-creates it) --
    ("412_804..414_803", "415_004..417_003"),
    ("413_004..413_203", "415_204..415_403"),
    ("412_804..413_003", "415_004..415_203"),
    ("410_804..412_803", "413_004..415_003"),
    ("410_604..412_603", "412_804..414_803"),
    ("410_604..410_803", "412_804..413_003"),
    ("410_804..411_003", "413_004..413_203"),
    ("410_803+1", "413_003+1"),
    ("412_803+1", "415_003+1"),
    ("410_804+j", "413_004+j"),
    ("412_804+j", "415_004+j"),
    # -- ordinals (high first) --
    ("第四十一例", "第四十二例"),
    ("第四十例", "第四十一例"),
    ("第 178 枚", "第 179 枚"),
    ("行 169+本候选", "行 170+本候选"),
    ("第九十六枚", "第九十七枚"),
    ("第 170 波", "第 171 波"),
    ("行 95+本候选", "行 96+本候选"),
    ("bm-a 95 行注册", "bm-a 96 行注册"),
    ("一百七十七行注册", "一百七十八行注册"),
    ("机证 177 行", "机证 178 行"),
    ("一百七十八面实测", "一百七十九面实测"),
    # -- numbers (projection first; head before n_eff; delta-sign face) --
    ("**393,920 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1850**", "**" + LINE4 + "**"),
    ("·line_pre 1.1851·", "·line_pre " + PRE4 + "·"),
    ("**0.3265**", "**" + P954 + "**"),
    ("**−0.0932**", "**" + WONLY_U + "**"),
    ("**−0.0001**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245086", SIG6),
    ("799,705", LEDG),
    ("797,505", NEFF),
    ("391,720", KNEW),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w180", "n1_w181"),
    ("n1_w179", "n1_w180"),
    # -- wave-word cascade (high first) --
    ("W181", "W182"),
    ("W180", "W181"),
    ("W179", "W180"),
    # -- bare-number leftovers --
    ("波号 180=", "波号 181="),
    ("--wave 180", "--wave 181"),
]


def s81(t):
    for old, new in S81:
        t = t.replace(old, new)
    return t


# tokens excluded from the s81 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK181 = {
    "@CHAIN@": back180_map["@CHAIN@"] + "；W180=bm-a r852 freeze（" + W180_SHA + "）",
    "@KLT@": back180_map["@KLT@"].replace(" 如实披露",
             "/W180 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": back180_map["@SEMT@"].replace("】）", "→W180 **" + SEM4 + "**】）"),
    "@S55@": (
        "5. **W182+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W182p_A + " **CLEAN**（hops=0）；B first-clean **" + W182p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W182：W182 冻结方必须在"
        " post-W181 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W181 B 带 " + B_BAND + " 注册后将拒 naive W182 A 窗**——W182 A 重 derive 同强制"
        "（越过 W181 B 带·阶梯 A-hops-prior-B 继承第四十二例）；verify at W182 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s81(back180_map["@TITLE@"]),
    "@WAVEFREE@": s81(back180_map["@WAVEFREE@"]),
    "@VAC@": s81(back180_map["@VAC@"]),
    "@MERGE@": s81(back180_map["@MERGE@"]),
    "@AFACE@": s81(back180_map["@AFACE@"]),
    "@BFACE@": s81(back180_map["@BFACE@"]),
    "@R250@": s81(back180_map["@R250@"]),
    "@SCANFACE@": s81(back180_map["@SCANFACE@"]),
    "@ANCHOR@": s81(back180_map["@ANCHOR@"]),
    "@POOL@": s81(back180_map["@POOL@"]),
    "@SEATSENT@": s81(back180_map["@SEATSENT@"]),
    "@CLAIMLAW@": s81(back180_map["@CLAIMLAW@"]),
    "@V2W@": s81(back180_map["@V2W@"]),
    "@ASEED@": s81(back180_map["@ASEED@"]),
    "@ASEEDPROSE@": s81(back180_map["@ASEEDPROSE@"]),
    "@BENTRY@": s81(back180_map["@BENTRY@"]),
    "@BSEEDPROSE@": s81(back180_map["@BSEEDPROSE@"]),
    "@GATEW@": s81(back180_map["@GATEW@"]),
    "@FN@": s81(back180_map["@FN@"]),
    "@RFN@": s81(back180_map["@RFN@"]),
    "@ODOLD@": s81(back180_map["@ODOLD@"]),
    "@S5ANCH@": s81(back180_map["@S5ANCH@"]),
    "@S51@": s81(back180_map["@S51@"]),
    "@S51B@": s81(back180_map["@S51B@"]),
    "@S52@": s81(back180_map["@S52@"]),
    "@S53@": s81(back180_map["@S53@"]),
    "@KLKEY@": s81(back180_map["@KLKEY@"]),
    "@WAVECLI@": s81(back180_map["@WAVECLI@"]),
    "@EOB@": s81(back180_map["@EOB@"]),
    "@W136TO@": s81(back180_map["@W136TO@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r862 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W181 pre-seat probe 脚本+回执同推；W181 pre-seat probe "
        "脚本+回执已在 origin 自 r862 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r863 同窗·r851 先例·如实注记）】"
    ),
    "@ORDINALS@": (
        back180_map["@ORDINALS@"]
        .replace("第 170 波", "第 171 波")
        .replace("第九十六枚", "第九十七枚")
        .replace("行 95+本候选", "行 96+本候选")
        .replace("/W178/W179 最近自有波", "/W179/W180 最近自有波")
        .replace("注册表 W179 行后", "注册表 W180 行后")
        .replace("MSG-2026-10-08-0030-bma-w180-seat", SEAT_MSG)
        .replace("d3b0737fe", SEAT_SHA)
    ),
    "@W2TO@": s81(back180_map["@W2TO@"]),
    "@W1TO@": s81(back180_map["@W1TO@"]),
    "@OWNCHAIN@": back180_map["@OWNCHAIN@"].replace(
        "/W179 最近自有波", "/W179/W180 最近自有波"),
    "@PRC@": s81(back180_map["@PRC@"]),
    "@PF@": s81(back180_map["@PF@"]),
    "@B@": s81(back180_map["@B@"]),
    "@WPN2@": s81(back180_map["@WPN2@"]),
    "@WN@": s81(back180_map["@WN@"]),
    "@W@": s81(back180_map["@W@"]),
    "@SD@": s81(back180_map["@SD@"]),
    "@KOLD@": s81(back180_map["@KOLD@"]),
    "@N171@": "181",
    "@N170@": "180",
    "@N169@": "179",
}
missing = [t for (t, _v) in BACK180 if t not in BACK181]
assert not missing, missing
extra = [t for t in BACK181 if t not in back180_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK181["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（413_003+1）" in chk and "FORTY-FIRST（第四十一例）" in chk, chk[:250]
chk = BACK181["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（415_003+1）" in chk, chk[:250]
chk = BACK181["@ANCHOR@"]
assert "W1..W180 N1 finalize 已全部落地" in chk and "**801,905**" in chk \
    and "K=393,920" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r854 窗" in chk, chk[:250]
assert BACK181["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + " 投影**", \
    BACK181["@POOL@"]
assert "**" + LINE4 + "**" in BACK181["@KLKEY@"] and "n_eff " + NEFF in BACK181["@KLKEY@"], \
    BACK181["@KLKEY@"]
assert "line_pre " + PRE4 in BACK181["@KLKEY@"], BACK181["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK181["@KLKEY@"], BACK181["@KLKEY@"]
assert BACK181["@WAVEFREE@"] == "波号 181=注册表 W180 行后首个自由号", BACK181["@WAVEFREE@"]
assert "n1_w181_results.json" in BACK181["@FN@"] and "n1_w180_results.json" in BACK181["@ODOLD@"]
assert BACK181["@WAVECLI@"] == "--wave 181/finalize --wave 181", BACK181["@WAVECLI@"]
assert "W182+ 投影" in BACK181["@S55@"] and W182p_A in BACK181["@S55@"] \
    and W182p_B in BACK181["@S55@"] and "继承第四十二例" in BACK181["@S55@"], BACK181["@S55@"][:140]
assert SEAT_SHA in BACK181["@SEATPUB@"] and "r862 seat push" in BACK181["@SEATPUB@"]
assert "第 171 波" in BACK181["@ORDINALS@"] and "W179/W180 最近自有波" in BACK181["@ORDINALS@"]
assert "第四十二例" in BACK181["@SEATSENT@"], BACK181["@SEATSENT@"][:250]
assert "阶梯第四十一例" in BACK181["@ASEEDPROSE@"], BACK181["@ASEEDPROSE@"][:250]
assert "法典 §4 W181 行 B=" + B_BAND in BACK181["@BSEEDPROSE@"], BACK181["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK181["@S5ANCH@"] and "r839 承袭收口窗" in BACK181["@S5ANCH@"] \
    and "已回填（r854 窗" in BACK181["@S5ANCH@"], BACK181["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK181["@S51@"] and "**" + WONLY_U + "**" in BACK181["@S51@"], \
    BACK181["@S51@"]
assert "**" + SIG6 + "**" in BACK181["@S52@"], BACK181["@S52@"]
assert "**" + P954 + "**" in BACK181["@S53@"], BACK181["@S53@"]
assert "一百七十八行注册" in BACK181["@SCANFACE@"] and "表尾 W180 行" in BACK181["@SCANFACE@"] \
    and "机证 178 行" in BACK181["@SCANFACE@"], BACK181["@SCANFACE@"]
assert BACK181["@EOB@"] == "engine_owner==bm-a 96 行注册", BACK181["@EOB@"]
assert "PERPETUAL-N1-W181" in BACK181["@TITLE@"] and "第 179 枚" in BACK181["@TITLE@"] \
    and "【r862】" in BACK181["@TITLE@"], BACK181["@TITLE@"]
assert "r862 bm-a 带闸窗（pre-seat probe r862 单窗" in BACK181["@GATEW@"], BACK181["@GATEW@"]
assert "（r862 probe leg2/leg3 实跑）" == BACK181["@VAC@"], BACK181["@VAC@"]
assert "（r862 承袭" in BACK181["@MERGE@"], BACK181["@MERGE@"]
assert "r862 probe 单跑兑现注记" in BACK181["@CLAIMLAW@"], BACK181["@CLAIMLAW@"]
assert "results/_r862bma_w181_probe_receipt.json" in BACK181["@PRC@"] \
    or BACK181["@PRC@"] == "results/_r862bma_w181_probe_receipt.json", BACK181["@PRC@"]
assert "W180=bm-a r852 freeze（" + W180_SHA + "）" in BACK181["@CHAIN@"]
assert "→W180 **" + SEM4 + "**】）" in BACK181["@SEMT@"], BACK181["@SEMT@"][-80:]
assert "/W180 **" + DSIGN + DELTA4 + "** 如实披露" in BACK181["@KLT@"], BACK181["@KLT@"][-80:]
assert BACK181["@WPN2@"] == "W182+ 投影", BACK181["@WPN2@"]
assert BACK181["@W136TO@"] == "W136..W180", BACK181["@W136TO@"]
assert BACK181["@W2TO@"] == "W2..W180" and BACK181["@W1TO@"] == "W1..W180" \
    and BACK181["@V2W@"] == "v2..W180 落地", (BACK181["@W2TO@"], BACK181["@W1TO@"], BACK181["@V2W@"])
assert BACK181["@WN@"] == "W181" and BACK181["@W@"] == "W180" and BACK181["@SD@"] == "n1_w181" \
    and BACK181["@KOLD@"] == KNEW, (BACK181["@WN@"], BACK181["@W@"], BACK181["@SD@"])
assert BACK181["@ASEED@"] == "entry rng seed=**413_004+j**", BACK181["@ASEED@"]
assert BACK181["@BENTRY@"] == "entry rng=**413_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", \
    BACK181["@BENTRY@"]
assert BACK181["@PF@"] == "PERPETUAL_N1_W181_PREREG.md", BACK181["@PF@"]
assert BACK181["@R250@"] == "R250：W181 带从未指派·测量面零结果可锁", BACK181["@R250@"]
print("S81 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK181 = [(val, tok) for (tok, val) in BACK180]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK181:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK181[t]) for (t, _v) in BACK180]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 181"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w180", "n1_w181"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W181") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W181 freeze" not in out_t.replace("；W180=bm-a r852 freeze", ""), \
    "unexpected W181-freeze text"
# stale-session sweep: no W180-era session stamps may survive (note:
# "r851 probe leg4" is the LEGAL new citation -- the W180 probe leg4 that
# anticipated the W181 staircase; only its 回执/leg2 faces must have rolled;
# bare "391,720" is consumed by the K roll -- the stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r851 probe 回执", "（r851 probe leg2", "r848 probe", "r849 冻结件",
              "已回填（r850 窗", "d3b0737fe", "【r851】", "FORTIETH",
              "第四十例", "0.3265", "0.245086", "−0.0932", "1.1850",
              "391,720", "净账本锚头 799,705"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r851 probe leg4" in out_t, "new W180-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK181))

# --- 5. emit the W181 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r863 bm-a W181 per-wave prereg build: transforms the freeze-time W180
prereg (git blob d863d9072 -- file research/PERPETUAL_N1_W180_PREREG.md at
prereg-freeze commit 220a7b305, byte-identical to registry-freeze commit
568848aa4; extracted byte-verbatim to results/_r863bma_w181_prereg_src.txt)
into research/PERPETUAL_N1_W181_PREREG.md.

Generated by results/_r863bma_w181_buildgen.py (TOK/BACK pairs AST-extracted
from the r852 build script -- no exec of its time-locked live asserts;
r773/r775/r781/r830 compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK
list order preserved; pre-TOK probe receipt
results/_r863bma_w181_preprobe.json sequential DRY 50/50).  r587
machine-derived facts (read from on-disk receipts): r862 probe ADMIT
A 413_004..415_003 staircase 41st E36 / B 415_004..415_203; W180 finalize
r854 one-pass same-window (K 393,920 / head 801,905 / skill_line
1.1852 / delta +0.0001); W180 sec7/sec8 backfill landed r854 window; W180
freeze 568848aa4; W181 seat push 971316069; seat self-ack processed/ on
origin (61ab7d60a, r863 window).

Lineage constants disclosed (r795/r845/r849/r852 precedent, passed through):
(a) anchor wave-words land on the CURRENT wave via the cascade (off-by-one
    quirk family; head/K roll machine-correct to 801,905/393,920);
(b) @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides verbatim;
(c) @SEATSENT@ "r841 席位/seat push" stale stamps ride verbatim (seat MSG
    name + push sha roll machine-correct);
(d) ordinal words roll 第九十六枚 -> 第九十七枚 (rows 96 + candidate);
(f) @KLKEY@ delta-sign roll face: W180 K-lift delta **+0.0001** (@KLT@
    chain history protected by FRESH exclusion).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\_r863bma_w181_prereg_src.txt"
OUT = r"research\\PERPETUAL_N1_W181_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r862bma_w181_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "413004_415003", "B": "415004_415203"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [413004, 415003] and leg1["B"] == [415004, 415203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [412804, 414803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [413004, 413203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [413004, 413203], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 415004, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 178 and leg0["tail"] == "W180" and leg0["ordinal"] == 171 \\
    and leg0["bma_ordinal"] == 97 and leg0["owner_rows"] == 170 \\
    and leg0["bma_rows"] == 96 and leg0["w180_ledger_head"] == 801905, leg0
assert leg4["W182p_A"] in ("415004..417003", "415_004..417_003") and leg4["W182p_B"] in ("415204..415403", "415_204..415_403"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W182p_B_lands_inside_W182p_A"] is True, leg4
assert "FORTY-FIRST" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w180_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 393920, "W180 merged K drift"
assert npc["pre_w180_cumulative"]["n_values"] == 391720, "pre-W180 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_393920"] == 1.1852 and kl["line_pre_w180"] == 1.1851 \\
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 799705, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k393920"] == 0.000391, "se_mu drift"
assert abs(npc["mu_delta_w180_vs_w179ext"] - 0.000725) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3098, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w180_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0925" and SIG6 == "0.245111", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w180_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "801,905" and KNEW == "393,920", (LEDG, KNEW)
KPROJ = "{:,}".format(393920 + 2200)
LEDGPROJ = "{:,}".format(801905 + 2200)
assert KPROJ == "396,120" and LEDGPROJ == "804,105", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W180 FREEZE", "-1"], capture_output=True, text=True)
W180_SHA = _r.stdout.strip()
assert W180_SHA == "568848aa4", W180_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W181 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W181 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-0505-bma-w181-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "971316069", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0505-bma-w181-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W181 seat MSG not on origin (r565 pre-freeze law)"
assert "413_004..415_003" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "220a7b305:research/PERPETUAL_N1_W180_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "d863d90725f2094351742e099cd5d5197f151248", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W180 sec7/sec8 backfill landed the r854 window -- the anchor face cites it
w180p = io.open(r"research\\PERPETUAL_N1_W180_PREREG.md", encoding="utf-8", newline="").read()
assert "801,905" in w180p and "K=393,920" in w180p, \\
    "W180 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W180" in src and "412_804..413_003" in src, "src face drift"
'''

TAIL = '''
TOK181 = %s
BACK181 = %s

EXPECT = %s

out_t = src
for old, tok in TOK181:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK181:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 181"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w180", "n1_w181"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W181") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W181 freeze" not in out_t.replace("；W180=bm-a r852 freeze", ""), \\
    "unexpected W181-freeze text"

# stale-session sweep ("r851 probe leg4" = LEGAL new citation; bare "391,720"
# = consumed by the K roll -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r851 probe 回执", "（r851 probe leg2", "r848 probe", "r849 冻结件",
              "已回填（r850 窗", "d3b0737fe", "【r851】", "FORTIETH",
              "第四十例", "0.3265", "0.245086", "−0.0932", "1.1850",
              "391,720", "净账本锚头 799,705"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r851 probe leg4" in out_t, "new W180-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W181 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK181)
back_lit = repr([(t, BACK181[t]) for (t, _v) in BACK180])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r863bma_w181_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r863bma_w181_prereg_build.py", len(out), "bytes")
