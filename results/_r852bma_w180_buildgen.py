# -*- coding: utf-8 -*-
"""r852 bm-a generator: builds results/_r852bma_w180_prereg_build.py by
AST-extracting the r849 build script's BACK179/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts -- r833 law 1), then
deriving the BACK180 pairs as (token, S80-rolled W180 value).  Old side =
the W179-era value (physical freeze-time blob 27639fcf at prereg-freeze
commit 6f14c35d5, byte-identical to registry-freeze commit ef540bf8f), new
side = the S80 W180 fact map applied to that W179 text.  r773/r775/r781/r830
compliance inherited: token-first two-phase vmap, whole-string composites,
numerals LAST, pre-TOK probe done (results/_r852bma_w180_preprobe.json:
sequential DRY 50/50 PASS); r735 substring-order law = BACK list order
preserved (long composites precede short substrings; proj-A before naive-A,
proj-B before naive-B, own-B before prior-B; head before n_eff).

r587 machine-derived facts (every displayed value read from on-disk receipts
this window):
  - pre-seat probe results/_r851bma_w180_probe_receipt.json rc0 ADMIT
    (leg0 registry 177 rows tail W179 ordinal 170 / bma_ordinal 96 /
    owner_rows 169 / bma_rows 95 / w179_ledger_head 799,705; leg1
    A 410_804..412_803 hops=1 / B 412_804..413_003 hops=1 / naive A
    410_604..412_603 refused at its own start by the registered W179 B
    band 410_604..410_803 (staircase FORTIETH instance E36 per receipt
    A_semantics; W179 seat leg4 + r848 probe leg4 anticipated 40th --
    projection and receipt ordinals MATCH, no divergence face this wave);
    naive B 410_804..411_003 lands inside own-A 410_804..412_803; leg2
    conflicts 0; leg3 origin vacancy True; leg4 W181+ projection
    A 412_804..414_803 hops=0 / B 413_004..413_203 hops=0, B inside A);
  - W179 finalize landed r850 (one-pass, dead-r849 closeout-tail adoption,
    17-UU rebase-stop canon resolve; preflight three-gate GREEN half-open
    law r846 bloodline)
    (results/perpetual_faces/n1_w179_results.json: merged K=391,520,
    mu=-0.092733 6dp / 4dp -0.0927 (same 4dp as W178 -- no roll needed),
    sigma=0.245086 6dp; w179-only mu=-0.093224 4dp -0.0932;
    se_mu_at_k391720=0.000392; A p95=0.3265; k-lift
    line_merged_391720 1.1850 / line_pre_w179 1.1851 / delta -0.0001 /
    n_eff_held_equal 797,505; canon flip NOT performed;
    mu_delta_w179_vs_w178ext=-0.000971);
  - W179 sec7/sec8 settle backfill landed the r850 finalize window
    (same-window; on-disk text "r850 窗机证" + "799,705" live-asserted);
  - W179 freeze registered sha machine-derived = ef540bf8f (git log
    origin/main --grep "W179 FREEZE"); W180 seat push sha machine-derived =
    d3b0737fe (git log --diff-filter=A on the seat MSG inbox path; payload
    = seat MSG + probe script + probe receipt, verified on origin);
    seat self-ack archive move landed r851 window (e069782f7,
    processed/ path on origin).

S80 LINEAGE CONSTANTS (r795/r845/r849 precedent, passed through + disclosed):
  (a) anchor/§5 wave-words land on the CURRENT wave via the cascade
    (off-by-one quirk family since W165 r795): the W180 prereg anchor
    bracket reads "W180 finalize one-pass bm-a r844 dead-tail 收养窗" and
    "W180 finalize 落账" while the head/K values roll machine-correct
    to 799,705/391,720 (the true anchor = W179 finalize r850);
  (b) the @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides
    verbatim (r845 quirk (f) continuation);
  (c) @SEATSENT@ "本机 r841 席位"/"（r841 seat push" stale session
    stamps ride verbatim (r849 precedent: no S79/S80 pair exists; the seat
    MSG name + push sha roll machine-correct);
  (d) the bm-a-owned ordinal words roll 第九十五枚 -> 第九十六枚
    (rows 95 + candidate = 96th owned per probe leg0);
  (e) @KLT@ chain appends the W179 entry (**−0.0001** machine-read);
    @SEMT@ chain appends W179 se_mu 0.000392; @CHAIN@ appends
    "W179=bm-a r849 freeze（ef540bf8f）";
  (f) @KLKEY@ delta-sign roll face: W178 delta **+0.0001** -> W179 delta
    **−0.0001** (new pair beyond the r851 continuation skeleton -- W179's
    K-lift delta is negative; @KLT@ chain history protected by FRESH
    exclusion, its three **+0.0001** entries ride verbatim);
  (g) wave-words/ordinals in the title, pump ordinal 第 178 枚, scan face
    177 rows etc. all roll per probe leg0 machine counts.

DRY discipline (r833 law 2): zero writes until every gate green -- the
emitted build script is the ONLY writer, and it re-asserts everything live.
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W179 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "6f14c35d5:research/PERPETUAL_N1_W179_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W179 freeze-time blob not reachable"
blob = _r.stdout
_r2 = subprocess.run(
    ["git", "rev-parse", "6f14c35d5:research/PERPETUAL_N1_W179_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r2.stdout.strip()
assert BLOB_SHA == "27639fcf212834d3a4364e00b9ec6263bf3eb38b", BLOB_SHA
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r852bma_w180_prereg_src.txt", "wb").write(blob)
print("W180 src extracted:", len(blob), "bytes (W179 freeze-time blob", BLOB_SHA[:10], ")")

# --- 1. AST-extract the r849 build script's BACK179 + EXPECT ---------------
src849 = io.open(r"results\_r849bma_w179_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src849)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK179 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK179" and isinstance(node.value, ast.List):
            BACK179 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK179.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK179 is not None and EXPECT is not None, "BACK179/EXPECT not extracted"
assert len(BACK179) == 50 and len(EXPECT) == 50, (len(BACK179), len(EXPECT))
back179_map = dict(BACK179)
assert len(back179_map) == len(BACK179)
print("r849 BACK179 entries:", len(BACK179), "EXPECT entries:", len(EXPECT))

# --- 2. W180 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r851bma_w180_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "410804_412803", "B": "412804_413003"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [410804, 412803] and leg1["B"] == [412804, 413003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [410604, 412603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [410804, 411003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [410804, 411003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 412804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 177 and leg0["tail"] == "W179" and leg0["ordinal"] == 170 \
    and leg0["bma_ordinal"] == 96 and leg0["owner_rows"] == 169 \
    and leg0["bma_rows"] == 95 and leg0["w179_ledger_head"] == 799705, leg0
assert leg4["W181p_A"] == "412804..414803" and leg4["W181p_B"] == "413004..413203", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W181p_B_lands_inside_W181p_A"] is True, leg4
assert "FORTIETH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w179_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 391720, "W179 merged K drift"
assert npc["pre_w179_cumulative"]["n_values"] == 389520, "pre-W179 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_391720"] == 1.185 and kl["line_pre_w179"] == 1.1851 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 797505, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k391720"] == 0.000392, "se_mu drift"
assert abs(npc["mu_delta_w179_vs_w178ext"] - (-0.000971)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3265, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w179_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_391720"]
PRE4 = "%.4f" % kl["line_pre_w179"]
SEM4 = "%.6f" % npc["se_mu_at_k391720"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] > 0 else "\u2212"
assert MU4 == "-0.0927" and WONLY4 == "-0.0932" and SIG6 == "0.245086", (MU4, WONLY4, SIG6)
assert LINE4 == "1.1850" and PRE4 == "1.1851" and SEM4 == "0.000392" \
    and P954 == "0.3265" and DELTA4 == "0.0001" and DSIGN == "\u2212", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
WONLY_U = WONLY4.replace("-", "\u2212")     # display form U+2212 (r833 law 3)
assert WONLY_U == "\u22120.0932", WONLY_U
LEDG = "{:,}".format(leg0["w179_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "799,705" and KNEW == "391,720" and NEFF == "797,505", (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(391720 + 2200)
LEDGPROJ = "{:,}".format(799705 + 2200)
assert KPROJ == "393,920" and LEDGPROJ == "801,905", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W179 FREEZE", "-1"], capture_output=True, text=True)
W179_SHA = _r_.stdout.strip()
assert W179_SHA == "ef540bf8f", W179_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W180 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W180 FREEZE (r511 tail-lock)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-0030-bma-w180-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "d3b0737fe", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W180 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "410_804..412_803" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W179 sec7/sec8 backfill landed the r850 window -- the anchor face cites it
w179p = io.open(r"research\PERPETUAL_N1_W179_PREREG.md", encoding="utf-8", newline="").read()
assert "r850 窗机证" in w179p and "799,705" in w179p, \
    "W179 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "410_804..412_803"
B_BAND = "412_804..413_003"
NAIVE_A = "410_604..412_603"
NAIVE_B = "410_804..411_003"
PRIOR_B = "410_604..410_803"     # registered W179 B band (refusal band)
A_SEED, B_SEED = "410_804", "412_804"
SEAT_MSG = "MSG-2026-10-08-0030-bma-w180-seat"
W181p_A = "412_804..414_803"
W181p_B = "413_004..413_203"

# --- 3. S80 = W179->W180 ordered fact map -----------------------------------
S80 = [
    # -- window/session composites (longest first) --
    ("已回填（r846 窗", "已回填（r850 窗"),
    ("r848 bm-a 带闸窗（pre-seat probe r848 单窗", "r851 bm-a 带闸窗（pre-seat probe r851 单窗"),
    ("（r848 承袭", "（r851 承袭"),
    ("r848 probe 单跑兑现注记", "r851 probe 单跑兑现注记"),
    ("（r848 probe leg2/leg3 实跑）", "（r851 probe leg2/leg3 实跑）"),
    ("r848 probe 回执 A_semantics 机读序数=THIRTY-NINTH",
     "r851 probe 回执 A_semantics 机读序数=FORTIETH"),
    ("r844 probe leg4", "r848 probe leg4"),
    ("（r845 冻结件）", "（r849 冻结件）"),
    ("_r848bma_w179_probe_receipt.json", "_r851bma_w180_probe_receipt.json"),
    ("MSG-2026-10-07-2320-bma-w179-seat", "MSG-2026-10-08-0030-bma-w180-seat"),
    ("4c645c95f", "d3b0737fe"),
    ("【r849】", "【r851】"),
    # -- band geometry (proj-A, proj-B, own-B, own-A, naive-A, prior-B,
    #    naive-B -- r735 order law: projections consumed before the naive
    #    rolls re-create them; own-B consumed before prior-B re-creates it) --
    ("410_604..412_603", "412_804..414_803"),
    ("410_804..411_003", "413_004..413_203"),
    ("410_604..410_803", "412_804..413_003"),
    ("408_604..410_603", "410_804..412_803"),
    ("408_404..410_403", "410_604..412_603"),
    ("408_404..408_603", "410_604..410_803"),
    ("408_604..408_803", "410_804..411_003"),
    ("408_603+1", "410_803+1"),
    ("410_603+1", "412_803+1"),
    ("408_604+j", "410_804+j"),
    ("410_604+j", "412_804+j"),
    # -- ordinals (high first) --
    ("第四十例", "第四十一例"),
    ("第三十九例", "第四十例"),
    ("第 177 枚", "第 178 枚"),
    ("行 168+本候选", "行 169+本候选"),
    ("第九十五枚", "第九十六枚"),
    ("第 169 波", "第 170 波"),
    ("行 94+本候选", "行 95+本候选"),
    ("bm-a 94 行注册", "bm-a 95 行注册"),
    ("一百七十六行注册", "一百七十七行注册"),
    ("机证 176 行", "机证 177 行"),
    ("一百七十七面实测", "一百七十八面实测"),
    # -- numbers (projection first; head before n_eff; delta-sign face) --
    ("**391,720 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1849**", "**" + LINE4 + "**"),
    ("·line_pre 1.1848·", "·line_pre " + PRE4 + "·"),
    ("**0.3275**", "**" + P954 + "**"),
    ("**−0.0923**", "**" + WONLY_U + "**"),
    ("**+0.0001**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245104", SIG6),
    ("797,505", LEDG),
    ("795,305", NEFF),
    ("389,520", KNEW),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w179", "n1_w180"),
    ("n1_w178", "n1_w179"),
    # -- wave-word cascade (high first) --
    ("W180", "W181"),
    ("W179", "W180"),
    ("W178", "W179"),
    # -- bare-number leftovers --
    ("波号 179=", "波号 180="),
    ("--wave 179", "--wave 180"),
]


def s80(t):
    for old, new in S80:
        t = t.replace(old, new)
    return t


# tokens excluded from the s80 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK180 = {
    "@CHAIN@": back179_map["@CHAIN@"] + "；W179=bm-a r849 freeze（" + W179_SHA + "）",
    "@KLT@": back179_map["@KLT@"].replace(" 如实披露",
             "/W179 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": back179_map["@SEMT@"].replace("】）", "→W179 **" + SEM4 + "**】）"),
    "@S55@": (
        "5. **W181+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W181p_A + " **CLEAN**（hops=0）；B first-clean **" + W181p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W181：W181 冻结方必须在"
        " post-W180 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W180 B 带 " + B_BAND + " 注册后将拒 naive W181 A 窗**——W181 A 重 derive 同强制"
        "（越过 W180 B 带·阶梯 A-hops-prior-B 继承第四十一例）；verify at W181 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s80(back179_map["@TITLE@"]),
    "@WAVEFREE@": s80(back179_map["@WAVEFREE@"]),
    "@VAC@": s80(back179_map["@VAC@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r851 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W180 pre-seat probe 脚本+回执同推；W180 pre-seat probe "
        "脚本+回执已在 origin 自 r851 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r851 同窗·r841 先例·如实注记）】"
    ),
    "@MERGE@": s80(back179_map["@MERGE@"]),
    "@AFACE@": s80(back179_map["@AFACE@"]),
    "@BFACE@": s80(back179_map["@BFACE@"]),
    "@R250@": s80(back179_map["@R250@"]),
    "@SCANFACE@": s80(back179_map["@SCANFACE@"]),
    "@ANCHOR@": s80(back179_map["@ANCHOR@"]),
    "@POOL@": s80(back179_map["@POOL@"]),
    "@SEATSENT@": s80(back179_map["@SEATSENT@"]),
    "@CLAIMLAW@": s80(back179_map["@CLAIMLAW@"]),
    "@ORDINALS@": (
        back179_map["@ORDINALS@"]
        .replace("第 169 波", "第 170 波")
        .replace("第九十五枚", "第九十六枚")
        .replace("行 94+本候选", "行 95+本候选")
        .replace("/W177/W178 最近自有波", "/W178/W179 最近自有波")
        .replace("注册表 W178 行后", "注册表 W179 行后")
        .replace("MSG-2026-10-07-2320-bma-w179-seat", SEAT_MSG)
        .replace("4c645c95f", SEAT_SHA)
    ),
    "@V2W@": s80(back179_map["@V2W@"]),
    "@ASEED@": s80(back179_map["@ASEED@"]),
    "@ASEEDPROSE@": s80(back179_map["@ASEEDPROSE@"]),
    "@BENTRY@": s80(back179_map["@BENTRY@"]),
    "@BSEEDPROSE@": s80(back179_map["@BSEEDPROSE@"]),
    "@GATEW@": s80(back179_map["@GATEW@"]),
    "@FN@": s80(back179_map["@FN@"]),
    "@RFN@": s80(back179_map["@RFN@"]),
    "@ODOLD@": s80(back179_map["@ODOLD@"]),
    "@S5ANCH@": s80(back179_map["@S5ANCH@"]),
    "@S51@": s80(back179_map["@S51@"]),
    "@S51B@": s80(back179_map["@S51B@"]),
    "@S52@": s80(back179_map["@S52@"]),
    "@S53@": s80(back179_map["@S53@"]),
    "@KLKEY@": s80(back179_map["@KLKEY@"]),
    "@WAVECLI@": s80(back179_map["@WAVECLI@"]),
    "@EOB@": s80(back179_map["@EOB@"]),
    "@W136TO@": s80(back179_map["@W136TO@"]),
    "@OWNCHAIN@": back179_map["@OWNCHAIN@"].replace(
        "/W178 最近自有波", "/W178/W179 最近自有波"),
    "@W2TO@": s80(back179_map["@W2TO@"]),
    "@W1TO@": s80(back179_map["@W1TO@"]),
    "@PRC@": s80(back179_map["@PRC@"]),
    "@PF@": s80(back179_map["@PF@"]),
    "@B@": s80(back179_map["@B@"]),
    "@WPN2@": s80(back179_map["@WPN2@"]),
    "@WN@": s80(back179_map["@WN@"]),
    "@W@": s80(back179_map["@W@"]),
    "@SD@": s80(back179_map["@SD@"]),
    "@KOLD@": s80(back179_map["@KOLD@"]),
    "@N171@": "180",
    "@N170@": "179",
    "@N169@": "178",
}
missing = [t for (t, _v) in BACK179 if t not in BACK180]
assert not missing, missing
extra = [t for t in BACK180 if t not in back179_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK180["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（410_803+1）" in chk and "FORTIETH（第四十例）" in chk, chk[:200]
chk = BACK180["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（412_803+1）" in chk, chk[:200]
chk = BACK180["@ANCHOR@"]
assert "W1..W179 N1 finalize 已全部落地" in chk and "**799,705**" in chk \
    and "K=391,720" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r850 窗" in chk, chk[:200]
assert BACK180["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + " 投影**", \
    BACK180["@POOL@"]
assert "**" + LINE4 + "**" in BACK180["@KLKEY@"] and "n_eff " + NEFF in BACK180["@KLKEY@"], \
    BACK180["@KLKEY@"]
assert "line_pre " + PRE4 in BACK180["@KLKEY@"], BACK180["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK180["@KLKEY@"], BACK180["@KLKEY@"]
assert BACK180["@WAVEFREE@"] == "波号 180=注册表 W179 行后首个自由号", BACK180["@WAVEFREE@"]
assert "n1_w180_results.json" in BACK180["@FN@"] and "n1_w179_results.json" in BACK180["@ODOLD@"]
assert BACK180["@WAVECLI@"] == "--wave 180/finalize --wave 180", BACK180["@WAVECLI@"]
assert "W181+ 投影" in BACK180["@S55@"] and W181p_A in BACK180["@S55@"] \
    and W181p_B in BACK180["@S55@"] and "继承第四十一例" in BACK180["@S55@"], BACK180["@S55@"][:120]
assert SEAT_SHA in BACK180["@SEATPUB@"] and "r851 seat push" in BACK180["@SEATPUB@"]
assert "第 170 波" in BACK180["@ORDINALS@"] and "W178/W179 最近自有波" in BACK180["@ORDINALS@"]
assert "第四十一例" in BACK180["@SEATSENT@"], BACK180["@SEATSENT@"][:200]
assert "阶梯第四十例" in BACK180["@ASEEDPROSE@"], BACK180["@ASEEDPROSE@"][:200]
assert "法典 §4 W180 行 B=" + B_BAND in BACK180["@BSEEDPROSE@"], BACK180["@BSEEDPROSE@"][:200]
assert "净账本锚头 " + LEDG in BACK180["@S5ANCH@"] and "r839 承袭收口窗" in BACK180["@S5ANCH@"] \
    and "已回填（r850 窗" in BACK180["@S5ANCH@"], BACK180["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK180["@S51@"] and "**" + WONLY_U + "**" in BACK180["@S51@"], \
    BACK180["@S51@"]
assert "**" + SIG6 + "**" in BACK180["@S52@"], BACK180["@S52@"]
assert "**" + P954 + "**" in BACK180["@S53@"], BACK180["@S53@"]
assert "一百七十七行注册" in BACK180["@SCANFACE@"] and "表尾 W179 行" in BACK180["@SCANFACE@"] \
    and "机证 177 行" in BACK180["@SCANFACE@"], BACK180["@SCANFACE@"]
assert BACK180["@EOB@"] == "engine_owner==bm-a 95 行注册", BACK180["@EOB@"]
assert "PERPETUAL-N1-W180" in BACK180["@TITLE@"] and "第 178 枚" in BACK180["@TITLE@"] \
    and "【r851】" in BACK180["@TITLE@"], BACK180["@TITLE@"]
assert "r851 bm-a 带闸窗（pre-seat probe r851 单窗" in BACK180["@GATEW@"], BACK180["@GATEW@"]
assert "（r851 probe leg2/leg3 实跑）" == BACK180["@VAC@"], BACK180["@VAC@"]
assert "（r851 承袭" in BACK180["@MERGE@"], BACK180["@MERGE@"]
assert "r851 probe 单跑兑现注记" in BACK180["@CLAIMLAW@"], BACK180["@CLAIMLAW@"]
assert "results/_r851bma_w180_probe_receipt.json" in BACK180["@PRC@"] \
    or BACK180["@PRC@"] == "results/_r851bma_w180_probe_receipt.json", BACK180["@PRC@"]
assert "W179=bm-a r849 freeze（" + W179_SHA + "）" in BACK180["@CHAIN@"]
assert "→W179 **" + SEM4 + "**】）" in BACK180["@SEMT@"], BACK180["@SEMT@"][-80:]
assert "/W179 **" + DSIGN + DELTA4 + "** 如实披露" in BACK180["@KLT@"], BACK180["@KLT@"][-80:]
assert BACK180["@WPN2@"] == "W181+ 投影", BACK180["@WPN2@"]
assert BACK180["@W136TO@"] == "W136..W179", BACK180["@W136TO@"]
assert BACK180["@W2TO@"] == "W2..W179" and BACK180["@W1TO@"] == "W1..W179" \
    and BACK180["@V2W@"] == "v2..W179 落地", (BACK180["@W2TO@"], BACK180["@W1TO@"])
assert BACK180["@WN@"] == "W180" and BACK180["@W@"] == "W179" and BACK180["@SD@"] == "n1_w180" \
    and BACK180["@KOLD@"] == KNEW, (BACK180["@WN@"], BACK180["@W@"], BACK180["@SD@"])
assert BACK180["@ASEED@"] == "entry rng seed=**410_804+j**", BACK180["@ASEED@"]
assert BACK180["@BENTRY@"] == "entry rng=**410_804+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", \
    BACK180["@BENTRY@"]
assert BACK180["@PF@"] == "PERPETUAL_N1_W180_PREREG.md", BACK180["@PF@"]
assert BACK180["@R250@"] == "R250：W180 带从未指派·测量面零结果可锁", BACK180["@R250@"]
print("S80 spot-checks: PASS (30 composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK180 = [(val, tok) for (tok, val) in BACK179]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK180:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK180[t]) for (t, _v) in BACK179]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 180"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w179", "n1_w180"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W180") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W180 freeze" not in out_t.replace("；W179=bm-a r849 freeze", ""), \
    "unexpected W180-freeze text"
# stale-session sweep: no W179-era session stamps may survive (note:
# "r848 probe leg4" is the LEGAL new citation -- the W179 probe leg4 that
# anticipated the W180 staircase; only its 回执/leg2 faces must have rolled;
# bare "797,505" is the LEGAL new n_eff value in @KLKEY@ -- the stale probe
# uses the whole-string 净账本锚头 form)
for stale in ("r848 probe 回执", "（r848 probe leg2", "r844 probe", "r845 冻结件",
              "已回填（r846 窗", "4c645c95f", "【r849】", "THIRTY-NINTH",
              "第三十九例", "0.3275", "0.245104", "−0.0923", "1.1849",
              "389,520", "净账本锚头 797,505"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r848 probe leg4" in out_t, "new W179-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK180))

# --- 5. emit the W180 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r852 bm-a W180 per-wave prereg build: transforms the freeze-time W179
prereg (git blob 27639fcf -- file research/PERPETUAL_N1_W179_PREREG.md at
prereg-freeze commit 6f14c35d5, byte-identical to registry-freeze commit
ef540bf8f; extracted byte-verbatim to results/_r852bma_w180_prereg_src.txt)
into research/PERPETUAL_N1_W180_PREREG.md.

Generated by results/_r852bma_w180_buildgen.py (TOK/BACK pairs AST-extracted
from the r849 build script -- no exec of its time-locked live asserts;
r773/r775/r781/r830 compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK
list order preserved; pre-TOK probe receipt
results/_r852bma_w180_preprobe.json sequential DRY 50/50).  r587
machine-derived facts (read from on-disk receipts): r851 probe ADMIT
A 410_804..412_803 staircase 40th E36 / B 412_804..413_003; W179 finalize
r850 one-pass adoption closeout (K 391,720 / head 799,705 / skill_line
1.1850 / delta -0.0001); W179 sec7/sec8 backfill landed r850 window; W179
freeze ef540bf8f; W180 seat push d3b0737fe; seat self-ack processed/ on
origin (e069782f7, r851 window).

Lineage constants disclosed (r795/r845/r849 precedent, passed through):
(a) anchor wave-words land on the CURRENT wave via the cascade (off-by-one
    quirk family; head/K roll machine-correct to 799,705/391,720);
(b) @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides verbatim;
(c) @SEATSENT@ "r841 席位/seat push" stale stamps ride verbatim (seat MSG
    name + push sha roll machine-correct);
(d) ordinal words roll 第九十五枚 -> 第九十六枚 (rows 95 + candidate);
(f) @KLKEY@ delta-sign roll face: W179 K-lift delta **−0.0001** (@KLT@
    chain history protected by FRESH exclusion).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\_r852bma_w180_prereg_src.txt"
OUT = r"research\\PERPETUAL_N1_W180_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r851bma_w180_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "410804_412803", "B": "412804_413003"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [410804, 412803] and leg1["B"] == [412804, 413003], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [410604, 412603], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [410804, 411003], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [410804, 411003], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 412804, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 177 and leg0["tail"] == "W179" and leg0["ordinal"] == 170 \\
    and leg0["bma_ordinal"] == 96 and leg0["owner_rows"] == 169 \\
    and leg0["bma_rows"] == 95 and leg0["w179_ledger_head"] == 799705, leg0
assert leg4["W181p_A"] == "412804..414803" and leg4["W181p_B"] == "413004..413203", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W181p_B_lands_inside_W181p_A"] is True, leg4
assert "FORTIETH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w179_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 391720, "W179 merged K drift"
assert npc["pre_w179_cumulative"]["n_values"] == 389520, "pre-W179 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_391720"] == 1.185 and kl["line_pre_w179"] == 1.1851 \\
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 797505, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k391720"] == 0.000392, "se_mu drift"
assert abs(npc["mu_delta_w179_vs_w178ext"] - (-0.000971)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3265, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w179_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0932" and SIG6 == "0.245086", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w179_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "799,705" and KNEW == "391,720", (LEDG, KNEW)
KPROJ = "{:,}".format(391720 + 2200)
LEDGPROJ = "{:,}".format(799705 + 2200)
assert KPROJ == "393,920" and LEDGPROJ == "801,905", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W179 FREEZE", "-1"], capture_output=True, text=True)
W179_SHA = _r.stdout.strip()
assert W179_SHA == "ef540bf8f", W179_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W180 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W180 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-0030-bma-w180-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "d3b0737fe", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W180 seat MSG not on origin (r565 pre-freeze law)"
assert "410_804..412_803" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "6f14c35d5:research/PERPETUAL_N1_W179_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "27639fcf212834d3a4364e00b9ec6263bf3eb38b", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W179 sec7/sec8 backfill landed the r850 window -- the anchor face cites it
w179p = io.open(r"research\\PERPETUAL_N1_W179_PREREG.md", encoding="utf-8", newline="").read()
assert "r850 窗机证" in w179p and "799,705" in w179p, \\
    "W179 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W179" in src and "410_604..410_803" in src, "src face drift"
'''

TAIL = '''
TOK180 = %s
BACK180 = %s

EXPECT = %s

out_t = src
for old, tok in TOK180:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK180:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 180"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w179", "n1_w180"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W180") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W180 freeze" not in out_t.replace("；W179=bm-a r849 freeze", ""), \\
    "unexpected W180-freeze text"

# stale-session sweep ("r848 probe leg4" = LEGAL new citation; bare "797,505"
# = LEGAL new n_eff value in @KLKEY@ -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r848 probe 回执", "（r848 probe leg2", "r844 probe", "r845 冻结件",
              "已回填（r846 窗", "4c645c95f", "【r849】", "THIRTY-NINTH",
              "第三十九例", "0.3275", "0.245104", "−0.0923", "1.1849",
              "389,520", "净账本锚头 797,505"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r848 probe leg4" in out_t, "new W179-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W180 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK180)
back_lit = repr([(t, BACK180[t]) for (t, _v) in BACK179])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r852bma_w180_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r852bma_w180_prereg_build.py", len(out), "bytes")
