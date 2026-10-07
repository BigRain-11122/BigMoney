# -*- coding: utf-8 -*-
"""r867 bm-a generator: builds results/_r867bma_w182_prereg_build.py by
AST-extracting the r863 build script's BACK181/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts -- r833 law 1), then
deriving the BACK182 pairs as (token, S82-rolled W182 value).  Old side =
the W181-era value (freeze-time blob fce370dca at prereg-freeze commit
ce136b627, byte-identical to registry-freeze commit de699e8cd; extracted
byte-verbatim to results/_r867bma_w182_prereg_src.txt), new side = the S82
W182 fact map applied to that W181 text.  r773/r775/r781/r830 compliance
inherited: token-first two-phase vmap, whole-string composites, numerals
LAST; r735 substring-order law = BACK list order preserved (proj-A before
naive-A, proj-B before naive-B, own-B before prior-B; head before n_eff);
pre-TOK probe receipt results/_r867bma_w182_preprobe.json sequential DRY.

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r865bma_w182_probe_receipt.json rc0 ADMIT
    (leg0 registry 179 rows tail W181 ordinal 172 / bma_ordinal 98 /
    owner_rows 171 / bma_rows 97 / w181_ledger_head 804,518; leg1
    A 415_204..417_203 hops=1 / B 417_204..417_403 hops=1 / naive A
    415_004..417_003 refused at its own start by the registered W181 B
    band 415_004..415_203 (staircase FORTY-SECOND instance E36 per
    receipt A_semantics; W181 seat leg4 + r862 probe leg4 anticipated
    42nd -- projection and receipt ordinals MATCH, no divergence face);
    naive B 415_204..415_403 lands inside own-A 415_204..417_203; leg2
    conflicts 0; leg3 origin vacancy True; leg4 W183+ projection
    A 417_204..419_203 hops=0 / B 417_404..417_603 hops=0, B inside A);
  - W181 finalize landed r864 one-pass (r381) commit 4f710354d
    (results/perpetual_faces/n1_w181_results.json: merged K=396,120,
    mu=-0.0927645 4dp -0.0928 (ROLL needed: W180 -0.0927 -> -0.0928),
    sigma=0.245101 6dp; w181-only mu=-0.098730 4dp -0.0987;
    se_mu_at_k396120=0.000389; A p95=0.3073; k-lift
    line_merged_396120 1.1853 / line_pre_w181 1.1854 (n_eff basis moved
    799,705 -> 802,318 = post-freeze W16 increment head) / delta
    -0.0001 sign-roll per r863 buildgen disclosure (f) / n_eff_held_equal
    802,318; canon flip NOT performed; mu_delta_w181_vs_w180ext=-0.006231);
  - W181 sec7/sec8 settle backfill landed the r867 HEAL window
    (r864 finalize window miss, disclosed; on-disk W181 prereg text
    "804,518" + "K=396,120" live-asserted; W159/W168/W169/r854
    delayed-window precedent family);
  - W181 freeze registered sha machine-derived = de699e8cd (git log
    origin/main --grep "W181 FREEZE"); W182 seat push sha
    machine-derived = df062c5c1 (git log --diff-filter=A on the seat MSG
    inbox path); seat self-ack archive move landed r866 window
    (processed/ path live-asserted this window).

S82 LINEAGE CONSTANTS (r795/r845/r849/r852/r863 precedent, passed
through + disclosed):
  (a) anchor/section-5 wave-words land on the CURRENT wave via the
    cascade (off-by-one quirk family since W165 r795): the W182 prereg
    anchor bracket reads "W182 finalize one-pass bm-a r844 dead-tail
    收养窗" and "W182 finalize 落账" while the head/K values roll
    machine-correct to 804,518/396,120 (the true anchor = W181 finalize
    r864);
  (b) the @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides
    verbatim (r845 quirk (f) continuation);
  (c) @SEATSENT@ "本机 r841 席位"/"（r841 seat push" stale session
    stamps ride verbatim (r849/r852/r863 precedent; the seat MSG name +
    push sha roll machine-correct);
  (d) the bm-a-owned ordinal words roll 第九十七枚 -> 第九十八枚
    (rows 97 + candidate = 98th owned per probe leg0);
  (e) @KLT@ chain appends the W181 entry (**-0.0001** machine-read --
    NEGATIVE delta this wave, sign face rolls from W180's +0.0001);
    @SEMT@ chain appends W181 se_mu 0.000389; @CHAIN@ appends
    "W181=bm-a r863 freeze（de699e8cd）";
  (f) @KLKEY@ delta-sign roll face: W180 delta **+0.0001** -> W181
    delta **-0.0001** (@KLT@ chain history protected by FRESH
    exclusion, its entries ride verbatim);
  (g) wave-words/ordinals in the title, pump ordinal 第 180 枚, scan
    face 179 rows etc. all roll per probe leg0 machine counts;
  (h) line_pre face rolls 1.1851 -> 1.1854 (n_eff basis moved to the
    post-freeze ledger head 802,318 per W16 increment -- machine-read
    from the results file, not extrapolated).

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

# --- 0. extract the freeze-time W181 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "ce136b627:research/PERPETUAL_N1_W181_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W181 freeze-time blob not reachable"
blob = _r.stdout
_r2 = subprocess.run(
    ["git", "rev-parse", "ce136b627:research/PERPETUAL_N1_W181_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r2.stdout.strip()
assert BLOB_SHA == "fce370dca52a8a0b6bffe2df2bdfa44b51db237e", BLOB_SHA
_r2b = subprocess.run(
    ["git", "rev-parse", "de699e8cd:research/PERPETUAL_N1_W181_PREREG.md"],
    capture_output=True, text=True)
assert _r2b.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r867bma_w182_prereg_src.txt", "wb").write(blob)
print("W182 src extracted:", len(blob), "bytes (W181 freeze-time blob", BLOB_SHA[:10], ")")

# --- 1. AST-extract the r863 build script's BACK181 + EXPECT ---------------
src863 = io.open(r"results\_r863bma_w181_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src863)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK181 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK181" and isinstance(node.value, ast.List):
            BACK181 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK181.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK181 is not None and EXPECT is not None, "BACK181/EXPECT not extracted"
assert len(BACK181) == 50 and len(EXPECT) == 50, (len(BACK181), len(EXPECT))
back181_map = dict(BACK181)
assert len(back181_map) == len(BACK181)
print("r863 BACK181 entries:", len(BACK181), "EXPECT entries:", len(EXPECT))

# --- 2. W182 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r865bma_w182_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "415204_417203", "B": "417204_417403"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [415204, 417203] and leg1["B"] == [417204, 417403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [415004, 417003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [415204, 415403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [415204, 415403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 417204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 179 and leg0["tail"] == "W181" and leg0["ordinal"] == 172 \
    and leg0["bma_ordinal"] == 98 and leg0["owner_rows"] == 171 \
    and leg0["bma_rows"] == 97 and leg0["w181_ledger_head"] == 804518, leg0
assert leg4["W183p_A"] == "417204..419203" or leg4["W183p_A"] == "417_204..419_203", leg4
assert leg4["W183p_B"] == "417404..417603" or leg4["W183p_B"] == "417_404..417_603", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W183p_B_lands_inside_W183p_A"] is True, leg4
assert "FORTY-SECOND" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w181_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 396120, "W181 merged K drift"
assert npc["pre_w181_cumulative"]["n_values"] == 393920, "pre-W181 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_396120"] == 1.1853 and kl["line_pre_w181"] == 1.1854 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 802318, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k396120"] == 0.000389, "se_mu drift"
assert abs(npc["mu_delta_w181_vs_w180ext"] - (-0.006231)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3073, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w181_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_396120"]
PRE4 = "%.4f" % kl["line_pre_w181"]
SEM4 = "%.6f" % npc["se_mu_at_k396120"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] > 0 else "\u2212"
assert MU4 == "-0.0928" and WONLY4 == "-0.0987" and SIG6 == "0.245101", (MU4, WONLY4, SIG6)
assert LINE4 == "1.1853" and PRE4 == "1.1854" and SEM4 == "0.000389" \
    and P954 == "0.3073" and DELTA4 == "0.0001" and DSIGN == "\u2212", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")      # display form U+2212 (r833 law 3)
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0928" and WONLY_U == "\u22120.0987", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w181_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "804,518" and KNEW == "396,120" and NEFF == "802,318", (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(396120 + 2200)
LEDGPROJ = "{:,}".format(804518 + 2200)
assert KPROJ == "398,320" and LEDGPROJ == "806,718", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W181 FREEZE", "-1"], capture_output=True, text=True)
W181_SHA = _r_.stdout.strip()
assert W181_SHA == "de699e8cd", W181_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W182 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W182 FREEZE (r511 tail-lock)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-0603-bma-w182-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "df062c5c1", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0603-bma-w182-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W182 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "415_204..417_203" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "ce136b627:research/PERPETUAL_N1_W181_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "fce370dca52a8a0b6bffe2df2bdfa44b51db237e", \
    "src blob drift: %s" % _r4.stdout.strip()
# W181 sec7/sec8 settle backfill landed the r867 HEAL window -- the anchor
# face cites it (delayed-window precedent family disclosed)
w181p = io.open(r"research\PERPETUAL_N1_W181_PREREG.md", encoding="utf-8", newline="").read()
assert "804,518" in w181p and "K=396,120" in w181p, \
    "W181 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "415_204..417_203"
B_BAND = "417_204..417_403"
NAIVE_A = "415_004..417_003"
NAIVE_B = "415_204..415_403"
PRIOR_B = "415_004..415_203"     # registered W181 B band (refusal band)
A_SEED, B_SEED = "415_204", "417_204"
SEAT_MSG = "MSG-2026-10-08-0603-bma-w182-seat"
W183p_A = "417_204..419_203"
W183p_B = "417_404..417_603"

# --- 3. S82 = W181->W182 ordered fact map -----------------------------------
S82 = [
    # -- window/session composites (longest first) --
    ("已回填（r854 窗·W159/W168/W169 拖延窗先例同律·如实注记）",
     "已回填（r867 补窗·r864 finalize 窗漏补·W159/W168/W169/W180 拖延窗先例同律·如实注记）"),
    ("已回填（r854 窗）", "已回填（r867 补窗）"),
    ("r862 bm-a 带闸窗（pre-seat probe r862 单窗", "r865 bm-a 带闸窗（pre-seat probe r865 单窗"),
    ("（r862 承袭", "（r865 承袭"),
    ("r862 probe 单跑兑现注记", "r865 probe 单跑兑现注记"),
    ("（r862 probe leg2/leg3 实跑）", "（r865 probe leg2/leg3 实跑）"),
    ("r862 probe 回执 A_semantics 机读序数=FORTY-FIRST",
     "r865 probe 回执 A_semantics 机读序数=FORTY-SECOND"),
    ("FORTY-FIRST（第四十一例）", "FORTY-SECOND（第四十二例）"),
    ("r851 probe leg4", "r862 probe leg4"),
    ("（r852 冻结件）", "（r863 冻结件）"),
    ("_r862bma_w181_probe_receipt.json", "_r865bma_w182_probe_receipt.json"),
    ("MSG-2026-10-08-0505-bma-w181-seat", "MSG-2026-10-08-0603-bma-w182-seat"),
    ("971316069", "df062c5c1"),
    ("【r862】", "【r865】"),
    # -- band geometry (r735 order law: projections consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B
    #    re-creates it) --
    ("415_004..417_003", "417_204..419_203"),
    ("415_204..415_403", "417_404..417_603"),
    ("415_004..415_203", "417_204..417_403"),
    ("413_004..415_003", "415_204..417_203"),
    ("412_804..414_803", "415_004..417_003"),
    ("412_804..413_003", "415_004..415_203"),
    ("413_004..413_203", "415_204..415_403"),
    ("413_003+1", "415_203+1"),
    ("415_003+1", "417_203+1"),
    ("413_004+j", "415_204+j"),
    ("415_004+j", "417_204+j"),
    # -- ordinals (high first) --
    ("第四十二例", "第四十三例"),
    ("第四十一例", "第四十二例"),
    ("第 179 枚", "第 180 枚"),
    ("行 170+本候选", "行 171+本候选"),
    ("第九十七枚", "第九十八枚"),
    ("第 171 波", "第 172 波"),
    ("行 96+本候选", "行 97+本候选"),
    ("bm-a 96 行注册", "bm-a 97 行注册"),
    ("一百七十八行注册", "一百七十九行注册"),
    ("机证 178 行", "机证 179 行"),
    ("一百七十九面实测", "一百八十面实测"),
    # -- numbers (projection first; head before n_eff; delta-sign face;
    #    merged-mu 4dp ROLLS this wave -0.0927 -> -0.0928) --
    ("**396,120 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1852**", "**" + LINE4 + "**"),
    ("·line_pre 1.1851·", "·line_pre " + PRE4 + "·"),
    ("**0.3098**", "**" + P954 + "**"),
    ("**\u22120.0927**", "**" + MU_U + "**"),
    ("**\u22120.0925**", "**" + WONLY_U + "**"),
    ("**+0.0001**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245111", SIG6),
    ("801,905", LEDG),
    ("799,705", NEFF),
    ("393,920", KNEW),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w181", "n1_w182"),
    ("n1_w180", "n1_w181"),
    # -- wave-word cascade (high first) --
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 181=", "波号 182="),
    ("--wave 181", "--wave 182"),
]


def s82(t):
    for old, new in S82:
        t = t.replace(old, new)
    return t


# tokens excluded from the s82 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK182 = {
    "@CHAIN@": back181_map["@CHAIN@"] + "；W181=bm-a r863 freeze（" + W181_SHA + "）",
    "@KLT@": back181_map["@KLT@"].replace(" 如实披露",
             "/W181 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": back181_map["@SEMT@"].replace("】）", "→W181 **" + SEM4 + "**】）"),
    "@S55@": (
        "5. **W183+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W183p_A + " **CLEAN**（hops=0）；B first-clean **" + W183p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W183：W183 冻结方必须在"
        " post-W182 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W182 B 带 " + B_BAND + " 注册后将拒 naive W183 A 窗**——W183 A 重 derive 同强制"
        "（越过 W182 B 带·阶梯 A-hops-prior-B 继承第四十三例）；verify at W183 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s82(back181_map["@TITLE@"]),
    "@WAVEFREE@": s82(back181_map["@WAVEFREE@"]),
    "@VAC@": s82(back181_map["@VAC@"]),
    "@MERGE@": s82(back181_map["@MERGE@"]),
    "@AFACE@": s82(back181_map["@AFACE@"]),
    "@BFACE@": s82(back181_map["@BFACE@"]),
    "@R250@": s82(back181_map["@R250@"]),
    "@SCANFACE@": s82(back181_map["@SCANFACE@"]),
    "@ANCHOR@": s82(back181_map["@ANCHOR@"]),
    "@POOL@": s82(back181_map["@POOL@"]),
    "@SEATSENT@": s82(back181_map["@SEATSENT@"]),
    "@CLAIMLAW@": s82(back181_map["@CLAIMLAW@"]),
    "@V2W@": s82(back181_map["@V2W@"]),
    "@ASEED@": s82(back181_map["@ASEED@"]),
    "@ASEEDPROSE@": s82(back181_map["@ASEEDPROSE@"]),
    "@BENTRY@": s82(back181_map["@BENTRY@"]),
    "@BSEEDPROSE@": s82(back181_map["@BSEEDPROSE@"]),
    "@GATEW@": s82(back181_map["@GATEW@"]),
    "@FN@": s82(back181_map["@FN@"]),
    "@RFN@": s82(back181_map["@RFN@"]),
    "@ODOLD@": s82(back181_map["@ODOLD@"]),
    "@S5ANCH@": s82(back181_map["@S5ANCH@"]),
    "@S51@": s82(back181_map["@S51@"]),
    "@S51B@": s82(back181_map["@S51B@"]),
    "@S52@": s82(back181_map["@S52@"]),
    "@S53@": s82(back181_map["@S53@"]),
    "@KLKEY@": s82(back181_map["@KLKEY@"]),
    "@WAVECLI@": s82(back181_map["@WAVECLI@"]),
    "@EOB@": s82(back181_map["@EOB@"]),
    "@W136TO@": s82(back181_map["@W136TO@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r865 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W182 pre-seat probe 脚本+回执同推；W182 pre-seat probe "
        "脚本+回执已在 origin 自 r865 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r866 同窗·r851 先例·如实注记）】"
    ),
    "@ORDINALS@": (
        back181_map["@ORDINALS@"]
        .replace("第 171 波", "第 172 波")
        .replace("第九十七枚", "第九十八枚")
        .replace("行 96+本候选", "行 97+本候选")
        .replace("/W179/W180 最近自有波", "/W180/W181 最近自有波")
        .replace("注册表 W180 行后", "注册表 W181 行后")
        .replace("MSG-2026-10-08-0505-bma-w181-seat", SEAT_MSG)
        .replace("971316069", SEAT_SHA)
    ),
    "@W2TO@": s82(back181_map["@W2TO@"]),
    "@W1TO@": s82(back181_map["@W1TO@"]),
    "@OWNCHAIN@": back181_map["@OWNCHAIN@"].replace(
        "/W180 最近自有波", "/W180/W181 最近自有波"),
    "@PRC@": s82(back181_map["@PRC@"]),
    "@PF@": s82(back181_map["@PF@"]),
    "@B@": s82(back181_map["@B@"]),
    "@WPN2@": s82(back181_map["@WPN2@"]),
    "@WN@": s82(back181_map["@WN@"]),
    "@W@": s82(back181_map["@W@"]),
    "@SD@": s82(back181_map["@SD@"]),
    "@KOLD@": s82(back181_map["@KOLD@"]),
    "@N171@": "182",
    "@N170@": "181",
    "@N169@": "180",
}
missing = [t for (t, _v) in BACK181 if t not in BACK182]
assert not missing, missing
extra = [t for t in BACK182 if t not in back181_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK182["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（415_203+1）" in chk and "FORTY-SECOND（第四十二例）" in chk, chk[:250]
chk = BACK182["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（417_203+1）" in chk, chk[:250]
chk = BACK182["@ANCHOR@"]
assert "W1..W181 N1 finalize 已全部落地" in chk and "**804,518**" in chk \
    and "K=396,120 合并池" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r867 补窗·r864 finalize 窗漏补" in chk, chk[:250]
assert BACK182["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + " 投影**", \
    BACK182["@POOL@"]
assert "**" + LINE4 + "**" in BACK182["@KLKEY@"] and "n_eff " + NEFF in BACK182["@KLKEY@"], \
    BACK182["@KLKEY@"]
assert "line_pre " + PRE4 in BACK182["@KLKEY@"], BACK182["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK182["@KLKEY@"], BACK182["@KLKEY@"]
assert BACK182["@WAVEFREE@"] == "波号 182=注册表 W181 行后首个自由号", BACK182["@WAVEFREE@"]
assert "n1_w182_results.json" in BACK182["@FN@"] and "n1_w181_results.json" in BACK182["@ODOLD@"]
assert BACK182["@WAVECLI@"] == "--wave 182/finalize --wave 182", BACK182["@WAVECLI@"]
assert "W183+ 投影" in BACK182["@S55@"] and W183p_A in BACK182["@S55@"] \
    and W183p_B in BACK182["@S55@"] and "继承第四十三例" in BACK182["@S55@"], BACK182["@S55@"][:140]
assert SEAT_SHA in BACK182["@SEATPUB@"] and "r865 seat push" in BACK182["@SEATPUB@"]
assert "第 172 波" in BACK182["@ORDINALS@"] and "W180/W181 最近自有波" in BACK182["@ORDINALS@"]
assert "第四十三例" in BACK182["@SEATSENT@"], BACK182["@SEATSENT@"][:250]
assert "阶梯第四十二例" in BACK182["@ASEEDPROSE@"], BACK182["@ASEEDPROSE@"][:250]
assert "法典 §4 W182 行 B=" + B_BAND in BACK182["@BSEEDPROSE@"], BACK182["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK182["@S5ANCH@"] and "r839 承袭收口窗" in BACK182["@S5ANCH@"] \
    and "已回填（r867 补窗）" in BACK182["@S5ANCH@"], BACK182["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK182["@S51@"] and "**" + WONLY_U + "**" in BACK182["@S51@"], \
    BACK182["@S51@"]
assert "**" + MU_U + "**" in BACK182["@S51@"], BACK182["@S51@"]
assert "**" + SIG6 + "**" in BACK182["@S52@"], BACK182["@S52@"]
assert "**" + P954 + "**" in BACK182["@S53@"], BACK182["@S53@"]
assert "一百七十九行注册" in BACK182["@SCANFACE@"] and "表尾 W181 行" in BACK182["@SCANFACE@"] \
    and "机证 179 行" in BACK182["@SCANFACE@"], BACK182["@SCANFACE@"]
assert BACK182["@EOB@"] == "engine_owner==bm-a 97 行注册", BACK182["@EOB@"]
assert "PERPETUAL-N1-W182" in BACK182["@TITLE@"] and "第 180 枚" in BACK182["@TITLE@"] \
    and "【r865】" in BACK182["@TITLE@"], BACK182["@TITLE@"]
assert "r865 bm-a 带闸窗（pre-seat probe r865 单窗" in BACK182["@GATEW@"], BACK182["@GATEW@"]
assert "（r865 probe leg2/leg3 实跑）" == BACK182["@VAC@"], BACK182["@VAC@"]
assert "（r865 承袭" in BACK182["@MERGE@"], BACK182["@MERGE@"]
assert "r865 probe 单跑兑现注记" in BACK182["@CLAIMLAW@"], BACK182["@CLAIMLAW@"]
assert "results/_r865bma_w182_probe_receipt.json" in BACK182["@PRC@"] \
    or BACK182["@PRC@"] == "results/_r865bma_w182_probe_receipt.json", BACK182["@PRC@"]
assert "W181=bm-a r863 freeze（" + W181_SHA + "）" in BACK182["@CHAIN@"]
assert "→W181 **" + SEM4 + "**】）" in BACK182["@SEMT@"], BACK182["@SEMT@"][-80:]
assert "/W181 **" + DSIGN + DELTA4 + "** 如实披露" in BACK182["@KLT@"], BACK182["@KLT@"][-80:]
assert BACK182["@WPN2@"] == "W183+ 投影", BACK182["@WPN2@"]
assert BACK182["@W136TO@"] == "W136..W181", BACK182["@W136TO@"]
assert BACK182["@W2TO@"] == "W2..W181" and BACK182["@W1TO@"] == "W1..W181" \
    and BACK182["@V2W@"] == "v2..W181 落地", (BACK182["@W2TO@"], BACK182["@W1TO@"], BACK182["@V2W@"])
assert BACK182["@WN@"] == "W182" and BACK182["@W@"] == "W181" and BACK182["@SD@"] == "n1_w182" \
    and BACK182["@KOLD@"] == KNEW, (BACK182["@WN@"], BACK182["@W@"], BACK182["@SD@"])
assert BACK182["@ASEED@"] == "entry rng seed=**415_204+j**", BACK182["@ASEED@"]
assert BACK182["@BENTRY@"] == "entry rng=**415_204+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", \
    BACK182["@BENTRY@"]
assert BACK182["@PF@"] == "PERPETUAL_N1_W182_PREREG.md", BACK182["@PF@"]
assert BACK182["@R250@"] == "R250：W182 带从未指派·测量面零结果可锁", BACK182["@R250@"]
print("S82 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK182 = [(val, tok) for (tok, val) in BACK181]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK182:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK182[t]) for (t, _v) in BACK181]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 182"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w181", "n1_w182"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W182") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W182 freeze" not in out_t.replace("；W181=bm-a r863 freeze", ""), \
    "unexpected W182-freeze text"
# stale-session sweep: no W181-era session stamps may survive (note:
# "r862 probe leg4" is the LEGAL new citation -- the W181 probe leg4 that
# anticipated the W182 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r862 probe 回执", "（r862 probe leg2", "r851 probe", "r852 冻结件",
              "已回填（r854 窗", "971316069", "【r862】", "FORTY-FIRST",
              "第四十一例", "0.3098", "0.245111", "\u22120.0925", "1.1852",
              "393,920", "净账本锚头 801,905"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r862 probe leg4" in out_t, "new W181-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK182))

# --- 5. emit the W182 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r867 bm-a W182 per-wave prereg build: transforms the freeze-time W181
prereg (git blob fce370dca -- file research/PERPETUAL_N1_W181_PREREG.md at
prereg-freeze commit ce136b627, byte-identical to registry-freeze commit
de699e8cd; extracted byte-verbatim to results/_r867bma_w182_prereg_src.txt)
into research/PERPETUAL_N1_W182_PREREG.md.

Generated by results/_r867bma_w182_buildgen.py (TOK/BACK pairs AST-extracted
from the r863 build script -- no exec of its time-locked live asserts;
r773/r775/r781/r830 compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK
list order preserved; pre-TOK probe receipt
results/_r867bma_w182_preprobe.json sequential DRY 50/50).  r587
machine-derived facts (read from on-disk receipts): r865 probe ADMIT
A 415_204..417_203 staircase 42nd E36 / B 417_204..417_403; W181 finalize
r864 one-pass same-window (K 396,120 / head 804,518 / skill_line
1.1853 / delta -0.0001·line_pre 1.1854 n_eff 802,318); W181 sec7/sec8
settle backfill landed r867 HEAL window (r864 miss disclosed·W159/W168/
W169/W180 delayed-window precedent family); W181 freeze de699e8cd; W182
seat push df062c5c1; seat self-ack processed/ on origin (r866 window).

Lineage constants disclosed (r795/r845/r849/r852/r863 precedent, passed
through):
(a) anchor wave-words land on the CURRENT wave via the cascade (off-by-one
    quirk family; head/K roll machine-correct to 804,518/396,120);
(b) @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides verbatim;
(c) @SEATSENT@ "r841 席位/seat push" stale stamps ride verbatim (seat MSG
    name + push sha roll machine-correct);
(d) ordinal words roll 第九十七枚 -> 第九十八枚 (rows 97 + candidate);
(f) @KLKEY@ delta-sign roll face: W181 K-lift delta **\\u22120.0001** (@KLT@
    chain history protected by FRESH exclusion).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\_r867bma_w182_prereg_src.txt"
OUT = r"research\\PERPETUAL_N1_W182_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r865bma_w182_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "415204_417203", "B": "417204_417403"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [415204, 417203] and leg1["B"] == [417204, 417403], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [415004, 417003], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [415204, 415403], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [415204, 415403], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 417204, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 179 and leg0["tail"] == "W181" and leg0["ordinal"] == 172 \\
    and leg0["bma_ordinal"] == 98 and leg0["owner_rows"] == 171 \\
    and leg0["bma_rows"] == 97 and leg0["w181_ledger_head"] == 804518, leg0
assert leg4["W183p_A"] in ("417204..419203", "417_204..419_203") and leg4["W183p_B"] in ("417404..417603", "417_404..417_603"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W183p_B_lands_inside_W183p_A"] is True, leg4
assert "FORTY-SECOND" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w181_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 396120, "W181 merged K drift"
assert npc["pre_w181_cumulative"]["n_values"] == 393920, "pre-W181 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_396120"] == 1.1853 and kl["line_pre_w181"] == 1.1854 \\
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 802318, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k396120"] == 0.000389, "se_mu drift"
assert abs(npc["mu_delta_w181_vs_w180ext"] - (-0.006231)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3073, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w181_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0928" and WONLY4 == "-0.0987" and SIG6 == "0.245101", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w181_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "804,518" and KNEW == "396,120", (LEDG, KNEW)
KPROJ = "{:,}".format(396120 + 2200)
LEDGPROJ = "{:,}".format(804518 + 2200)
assert KPROJ == "398,320" and LEDGPROJ == "806,718", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W181 FREEZE", "-1"], capture_output=True, text=True)
W181_SHA = _r.stdout.strip()
assert W181_SHA == "de699e8cd", W181_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W182 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W182 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-0603-bma-w182-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "df062c5c1", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0603-bma-w182-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W182 seat MSG not on origin (r565 pre-freeze law)"
assert "415_204..417_203" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "ce136b627:research/PERPETUAL_N1_W181_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "fce370dca52a8a0b6bffe2df2bdfa44b51db237e", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W181 sec7/sec8 settle backfill landed the r867 HEAL window -- the anchor
# face cites it (delayed-window precedent family disclosed)
w181p = io.open(r"research\\PERPETUAL_N1_W181_PREREG.md", encoding="utf-8", newline="").read()
assert "804,518" in w181p and "K=396,120" in w181p, \\
    "W181 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W181" in src and "413_004..415_003" in src, "src face drift"
'''

TAIL = '''
TOK182 = %s
BACK182 = %s

EXPECT = %s

out_t = src
for old, tok in TOK182:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK182:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 182"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w181", "n1_w182"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W182") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W182 freeze" not in out_t.replace("；W181=bm-a r863 freeze", ""), \\
    "unexpected W182-freeze text"

# stale-session sweep ("r862 probe leg4" = LEGAL new citation; bare "393,920"
# = consumed by the K roll -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r862 probe 回执", "（r862 probe leg2", "r851 probe", "r852 冻结件",
              "已回填（r854 窗", "971316069", "【r862】", "FORTY-FIRST",
              "第四十一例", "0.3098", "0.245111", "−0.0925", "1.1852",
              "393,920", "净账本锚头 801,905"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r862 probe leg4" in out_t, "new W181-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W182 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK182)
back_lit = repr([(t, BACK182[t]) for (t, _v) in BACK181])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r867bma_w182_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r867bma_w182_prereg_build.py", len(out), "bytes")
