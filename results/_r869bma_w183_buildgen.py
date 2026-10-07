# -*- coding: utf-8 -*-
"""r869 bm-a generator: builds results/_r869bma_w183_prereg_build.py by
AST-extracting the r867 build script's BACK182/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts -- r833 law 1), then
deriving the BACK183 pairs as (token, S82-rolled W183 value).  Old side =
the W182-era value (freeze-time blob ad57292a4 at prereg-freeze commit
f543c161c, byte-identical to registry-freeze commit 385dbafd8; extracted
byte-verbatim to results/_r869bma_w183_prereg_src.txt), new side = the S82
W183 fact map applied to that W182 text.  r773/r775/r781/r830 compliance
inherited: token-first two-phase vmap, whole-string composites, numerals
LAST; r735 substring-order law = BACK list order preserved (proj-A before
naive-A, proj-B before naive-B, own-B before prior-B; head before n_eff);
pre-TOK sequential DRY below (r833 law 2, zero writes until every gate
green).

r587 machine-derived facts (every displayed value read from on-disk
receipts this window):
  - pre-seat probe results/_r868bma_w183_probe_receipt.json rc0 ADMIT
    (leg0 registry 180 rows tail W182 ordinal 173 / bma_ordinal 99 /
    owner_rows 172 / bma_rows 98 / w182_ledger_head 806,718; leg1
    naive A 417_204..419_203 REFUSED at its own start by the registered
    W182 B band 417_204..417_403 -> honest forward walk 1 hop lands
    A 417_404..419_403 (staircase FORTY-THIRD instance E36 per receipt
    A_semantics; W182 seat leg4 + r865 probe leg4 + W182 prereg
    sec5.5/sec8 anticipated and MANDATED this re-derive -- projection
    and receipt ordinals MATCH, no divergence face); naive B 417_404..
    417_603 lands inside own-A 417_404..419_403 -> same-freeze mutual
    exclusion (W141 precedent leg2 law) -> reserved walk 1 hop lands
    B 419_404..419_603; leg2 conflicts 0; leg3 origin vacancy True;
    leg4 W184+ projection A 419_404..421_403 hops=0 / B 419_604..
    419_803 hops=0, B inside A);
  - W182 finalize landed r868 one-pass SAME-WINDOW (r381+r864 lesson
    honored) commit 2263238f9 face
    (results/perpetual_faces/n1_w182_results.json: ledger head 806,718
    EXACT with proj delta +0; merged K=398,320 EXACT; merged mu
    -0.0927609 4dp -0.0928 NO-ROLL (W181 display -0.0928 held);
    w182-only mu=-0.0921012 4dp -0.0921; sigma=0.2450925 6dp 0.245092;
    se_mu_at_k398320=0.000388; skill_line line_pre 1.1854 ->
    line_merged@398,320 1.1854 (K-lift +0.0000 EXACT-ZERO, n_eff
    804,518); canon flip NOT performed; A p95=0.3071);
  - W182 sec7/sec8 settle backfill landed the r868 SAME window
    (r864 lesson welded into process -- no heal window needed; on-disk
    W182 prereg text "806,718" + "K=398,320" live-asserted below);
  - W182 freeze registered sha machine-derived = 385dbafd8 (git log
    origin/main --grep "W182 FREEZE"); W183 seat push sha
    machine-derived = ccd18034e (git log --diff-filter=A on the seat
    MSG inbox path); seat self-ack archive move landed bm-c r741
    window (processed/ path live-asserted this window).

S82 LINEAGE CONSTANTS (r795/r845/r849/r852/r863/r867 precedent, passed
through + disclosed):
  (a) anchor/section-5 wave-words land on the CURRENT wave via the
    cascade (off-by-one quirk family since W165 r795): the W183 prereg
    anchor bracket reads "W183 finalize one-pass bm-a r844 dead-tail
    收养窗" and "W183 finalize 落账" while the head/K values roll
    machine-correct to 806,718/398,320 (the true anchor = W182 finalize
    r868);
  (b) the @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides
    verbatim (r845 quirk (f) continuation);
  (c) @SEATSENT@ "本机 r841 席位"/"（r841 seat push" stale session
    stamps ride verbatim (r849/r852/r863/r867 precedent; the seat MSG
    name + push sha roll machine-correct);
  (d) the bm-a-owned ordinal words roll 第九十八枚 -> 第九十九枚
    (rows 98 + candidate = 99th owned per probe leg0);
  (e) @KLT@ chain appends the W182 entry (**+0.0000** machine-read --
    EXACT-ZERO delta this wave; sign face "+" per the r868 same-window
    sec7 record and the chain's historical zero-display convention
    W136/W137/W139/W140 族; DSIGN law widened >0 -> >=0 this wave,
    disclosed); @SEMT@ chain appends W182 se_mu 0.000388; @CHAIN@
    appends "W182=bm-a r867 freeze（385dbafd8）";
  (f) @KLKEY@ delta-sign roll face: W181 delta **−0.0001** -> W182
    delta **+0.0000** (@KLT@ chain history protected by FRESH
    exclusion, its entries ride verbatim);
  (g) wave-words/ordinals in the title, pump ordinal 第 181 枚, scan
    face 180 rows etc. all roll per probe leg0 machine counts;
  (h) line_pre face 1.1854 -> 1.1854 NO-ROLL (W182 line_pre display ==
    W181 line_merged display; n_eff basis moved 802,318 -> 804,518 =
    post-freeze ledger head per W16 increment).

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

# --- 0. extract the freeze-time W182 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "f543c161c:research/PERPETUAL_N1_W182_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W182 freeze-time blob not reachable"
blob = _r.stdout
_r2 = subprocess.run(
    ["git", "rev-parse", "f543c161c:research/PERPETUAL_N1_W182_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r2.stdout.strip()
assert BLOB_SHA == "ad57292a4cd0fe8305d49a08cd3a2808818ef70d", BLOB_SHA
_r2b = subprocess.run(
    ["git", "rev-parse", "385dbafd8:research/PERPETUAL_N1_W182_PREREG.md"],
    capture_output=True, text=True)
assert _r2b.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r869bma_w183_prereg_src.txt", "wb").write(blob)
print("W183 src extracted:", len(blob), "bytes (W182 freeze-time blob", BLOB_SHA[:10], ")")

# --- 1. AST-extract the r867 build script's BACK182 + EXPECT ---------------
src867 = io.open(r"results\_r867bma_w182_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src867)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK182 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK182" and isinstance(node.value, ast.List):
            BACK182 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK182.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK182 is not None and EXPECT is not None, "BACK182/EXPECT not extracted"
assert len(BACK182) == 50 and len(EXPECT) == 50, (len(BACK182), len(EXPECT))
back182_map = dict(BACK182)
assert len(back182_map) == len(BACK182)
print("r867 BACK182 entries:", len(BACK182), "EXPECT entries:", len(EXPECT))

# --- 2. W183 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r868bma_w183_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "417404_419403", "B": "419404_419603"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [417404, 419403] and leg1["B"] == [419404, 419603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [417204, 419203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [417404, 417603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [417404, 417603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 419404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 180 and leg0["tail"] == "W182" and leg0["ordinal"] == 173 \
    and leg0["bma_ordinal"] == 99 and leg0["owner_rows"] == 172 \
    and leg0["bma_rows"] == 98 and leg0["w182_ledger_head"] == 806718, leg0
assert leg4["W184p_A"] == "419404..421403" or leg4["W184p_A"] == "419_404..421_403", leg4
assert leg4["W184p_B"] == "419604..419803" or leg4["W184p_B"] == "419_604..419_803", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W184p_B_lands_inside_W184p_A"] is True, leg4
assert "FORTY-THIRD" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w182_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 398320, "W182 merged K drift"
assert npc["pre_w182_cumulative"]["n_values"] == 396120, "pre-W182 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_398320"] == 1.1854 and kl["line_pre_w182"] == 1.1854 \
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 804518, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k398320"] == 0.000388, "se_mu drift"
assert abs(npc["mu_delta_w182_vs_w181ext"] - 0.006629) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3071, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w182_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_398320"]
PRE4 = "%.4f" % kl["line_pre_w182"]
SEM4 = "%.6f" % npc["se_mu_at_k398320"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0928" and WONLY4 == "-0.0921" and SIG6 == "0.245092", (MU4, WONLY4, SIG6)
assert LINE4 == "1.1854" and PRE4 == "1.1854" and SEM4 == "0.000388" \
    and P954 == "0.3071" and DELTA4 == "0.0000" and DSIGN == "+", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")      # display form U+2212 (r833 law 3)
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0928" and WONLY_U == "\u22120.0921", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w182_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "806,718" and KNEW == "398,320" and NEFF == "804,518", (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(398320 + 2200)
LEDGPROJ = "{:,}".format(806718 + 2200)
assert KPROJ == "400,520" and LEDGPROJ == "808,918", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W182 FREEZE", "-1"], capture_output=True, text=True)
W182_SHA = _r_.stdout.strip()
assert W182_SHA == "385dbafd8", W182_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W183 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W183 FREEZE (r511 tail-lock)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-0741-bma-w183-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "ccd18034e", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0741-bma-w183-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W183 seat MSG not on origin processed/ (r565 pre-freeze law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "417_404..419_403" in _seat_txt and "419_404..419_603" in _seat_txt, "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "f543c161c:research/PERPETUAL_N1_W182_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "ad57292a4cd0fe8305d49a08cd3a2808818ef70d", \
    "src blob drift: %s" % _r4.stdout.strip()
# W182 sec7/sec8 settle backfill landed the r868 SAME window (r864 lesson
# welded) -- the anchor face cites it (no heal-window disclosure needed)
w182p = io.open(r"research\PERPETUAL_N1_W182_PREREG.md", encoding="utf-8", newline="").read()
assert "806,718" in w182p and "K=398,320" in w182p, \
    "W182 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "417_404..419_403"
B_BAND = "419_404..419_603"
NAIVE_A = "417_204..419_203"
NAIVE_B = "417_404..417_603"
PRIOR_B = "417_204..417_403"     # registered W182 B band (refusal band)
A_SEED, B_SEED = "417_404", "419_404"
SEAT_MSG = "MSG-2026-10-08-0741-bma-w183-seat"
W184p_A = "419_404..421_403"
W184p_B = "419_604..419_803"

# --- 3. S82 = W182->W183 ordered fact map -----------------------------------
S82 = [
    # -- window/session composites (longest first) --
    ("已回填（r867 补窗·r864 finalize 窗漏补·W159/W168/W169/W181 拖延窗先例同律·如实注记）",
     "已回填（r868 同窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r867 补窗）", "已回填（r868 同窗）"),
    ("r865 bm-a 带闸窗（pre-seat probe r865 单窗", "r868 bm-a 带闸窗（pre-seat probe r868 单窗"),
    ("（r865 承袭", "（r868 承袭"),
    ("r865 probe 单跑兑现注记", "r868 probe 单跑兑现注记"),
    ("（r865 probe leg2/leg3 实跑）", "（r868 probe leg2/leg3 实跑）"),
    ("r865 probe 回执 A_semantics 机读序数=FORTY-SECOND",
     "r868 probe 回执 A_semantics 机读序数=FORTY-THIRD"),
    ("FORTY-SECOND（第四十二例）", "FORTY-THIRD（第四十三例）"),
    ("r862 probe leg4", "r865 probe leg4"),
    ("（r863 冻结件）", "（r867 冻结件）"),
    ("_r865bma_w182_probe_receipt.json", "_r868bma_w183_probe_receipt.json"),
    ("MSG-2026-10-08-0603-bma-w182-seat", "MSG-2026-10-08-0741-bma-w183-seat"),
    ("df062c5c1", "ccd18034e"),
    ("【r865】", "【r868】"),
    # -- band geometry (r735 order law: projections consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B
    #    re-creates it) --
    ("417_204..419_203", "419_404..421_403"),
    ("417_404..417_603", "419_604..419_803"),
    ("417_204..417_403", "419_404..419_603"),
    ("415_204..417_203", "417_404..419_403"),
    ("415_004..415_203", "417_204..417_403"),
    ("415_004..417_003", "417_204..419_203"),
    ("415_204..415_403", "417_404..417_603"),
    ("415_203+1", "417_403+1"),
    ("417_203+1", "419_403+1"),
    ("415_204+j", "417_404+j"),
    ("417_204+j", "419_404+j"),
    # -- ordinals (high first) --
    ("第四十三例", "第四十四例"),
    ("第四十二例", "第四十三例"),
    ("第 180 枚", "第 181 枚"),
    ("行 171+本候选", "行 172+本候选"),
    ("第九十八枚", "第九十九枚"),
    ("第 172 波", "第 173 波"),
    ("行 97+本候选", "行 98+本候选"),
    ("bm-a 97 行注册", "bm-a 98 行注册"),
    ("一百七十九行注册", "一百八十行注册"),
    ("机证 179 行", "机证 180 行"),
    ("一百八十面实测", "一百八十一面实测"),
    # -- numbers (projection first; head before n_eff; delta-sign face;
    #    merged-mu 4dp NO-ROLL this wave -0.0928 held) --
    ("**398,320 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1853**", "**" + LINE4 + "**"),
    ("·line_pre 1.1854·", "·line_pre " + PRE4 + "·"),
    ("**0.3073**", "**" + P954 + "**"),
    ("**\u22120.0928**", "**" + MU_U + "**"),
    ("**\u22120.0987**", "**" + WONLY_U + "**"),
    ("**\u22120.0001**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245101", SIG6),
    ("804,518", LEDG),
    ("802,318", NEFF),
    ("396,120", KNEW),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w182", "n1_w183"),
    ("n1_w181", "n1_w182"),
    # -- wave-word cascade (high first) --
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 182=", "波号 183="),
    ("--wave 182", "--wave 183"),
]


def s82(t):
    for old, new in S82:
        t = t.replace(old, new)
    return t


# tokens excluded from the s82 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK183 = {
    "@CHAIN@": back182_map["@CHAIN@"] + "；W182=bm-a r867 freeze（" + W182_SHA + "）",
    "@KLT@": back182_map["@KLT@"].replace(" 如实披露",
             "/W182 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": back182_map["@SEMT@"].replace("】）", "→W182 **" + SEM4 + "**】）"),
    "@S55@": (
        "5. **W184+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W184p_A + " **CLEAN**（hops=0）；B first-clean **" + W184p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W184：W184 冻结方必须在"
        " post-W183 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W183 B 带 " + B_BAND + " 注册后将拒 naive W184 A 窗**——W184 A 重 derive 同强制"
        "（越过 W183 B 带·阶梯 A-hops-prior-B 继承第四十四例）；verify at W184 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s82(back182_map["@TITLE@"]),
    "@WAVEFREE@": s82(back182_map["@WAVEFREE@"]),
    "@VAC@": s82(back182_map["@VAC@"]),
    "@MERGE@": s82(back182_map["@MERGE@"]),
    "@AFACE@": s82(back182_map["@AFACE@"]),
    "@BFACE@": s82(back182_map["@BFACE@"]),
    "@R250@": s82(back182_map["@R250@"]),
    "@SCANFACE@": s82(back182_map["@SCANFACE@"]),
    "@ANCHOR@": s82(back182_map["@ANCHOR@"]),
    "@POOL@": s82(back182_map["@POOL@"]),
    "@SEATSENT@": s82(back182_map["@SEATSENT@"]),
    "@CLAIMLAW@": s82(back182_map["@CLAIMLAW@"]),
    "@V2W@": s82(back182_map["@V2W@"]),
    "@ASEED@": s82(back182_map["@ASEED@"]),
    "@ASEEDPROSE@": s82(back182_map["@ASEEDPROSE@"]),
    "@BENTRY@": s82(back182_map["@BENTRY@"]),
    "@BSEEDPROSE@": s82(back182_map["@BSEEDPROSE@"]),
    "@GATEW@": s82(back182_map["@GATEW@"]),
    "@FN@": s82(back182_map["@FN@"]),
    "@RFN@": s82(back182_map["@RFN@"]),
    "@ODOLD@": s82(back182_map["@ODOLD@"]),
    "@S5ANCH@": s82(back182_map["@S5ANCH@"]),
    "@S51@": s82(back182_map["@S51@"]),
    "@S51B@": s82(back182_map["@S51B@"]),
    "@S52@": s82(back182_map["@S52@"]),
    "@S53@": s82(back182_map["@S53@"]),
    "@KLKEY@": s82(back182_map["@KLKEY@"]),
    "@WAVECLI@": s82(back182_map["@WAVECLI@"]),
    "@EOB@": s82(back182_map["@EOB@"]),
    "@W136TO@": s82(back182_map["@W136TO@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r868 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W183 pre-seat probe 脚本+回执同推；W183 pre-seat probe "
        "脚本+回执已在 origin 自 r868 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（bm-c r741 窗代移·r566 先例·如实注记）】"
    ),
    "@ORDINALS@": (
        back182_map["@ORDINALS@"]
        .replace("第 172 波", "第 173 波")
        .replace("第九十八枚", "第九十九枚")
        .replace("行 97+本候选", "行 98+本候选")
        .replace("/W180/W181 最近自有波", "/W181/W182 最近自有波")
        .replace("注册表 W181 行后", "注册表 W182 行后")
        .replace("MSG-2026-10-08-0603-bma-w182-seat", SEAT_MSG)
        .replace("df062c5c1", SEAT_SHA)
    ),
    "@W2TO@": s82(back182_map["@W2TO@"]),
    "@W1TO@": s82(back182_map["@W1TO@"]),
    "@OWNCHAIN@": back182_map["@OWNCHAIN@"].replace(
        "/W181 最近自有波", "/W181/W182 最近自有波"),
    "@PRC@": s82(back182_map["@PRC@"]),
    "@PF@": s82(back182_map["@PF@"]),
    "@B@": s82(back182_map["@B@"]),
    "@WPN2@": s82(back182_map["@WPN2@"]),
    "@WN@": s82(back182_map["@WN@"]),
    "@W@": s82(back182_map["@W@"]),
    "@SD@": s82(back182_map["@SD@"]),
    "@KOLD@": s82(back182_map["@KOLD@"]),
    "@N171@": "183",
    "@N170@": "182",
    "@N169@": "181",
}
missing = [t for (t, _v) in BACK182 if t not in BACK183]
assert not missing, missing
extra = [t for t in BACK183 if t not in back182_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK183["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（417_403+1）" in chk and "FORTY-THIRD（第四十三例）" in chk, chk[:250]
chk = BACK183["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（419_403+1）" in chk, chk[:250]
chk = BACK183["@ANCHOR@"]
assert "W1..W182 N1 finalize 已全部落地" in chk and "**806,718**" in chk \
    and "K=398,320 合并池" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r868 同窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK183["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + " 投影**", \
    BACK183["@POOL@"]
assert "**" + LINE4 + "**" in BACK183["@KLKEY@"] and "n_eff " + NEFF in BACK183["@KLKEY@"], \
    BACK183["@KLKEY@"]
assert "line_pre " + PRE4 in BACK183["@KLKEY@"], BACK183["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK183["@KLKEY@"], BACK183["@KLKEY@"]
assert BACK183["@WAVEFREE@"] == "波号 183=注册表 W182 行后首个自由号", BACK183["@WAVEFREE@"]
assert "n1_w183_results.json" in BACK183["@FN@"] and "n1_w182_results.json" in BACK183["@ODOLD@"]
assert BACK183["@WAVECLI@"] == "--wave 183/finalize --wave 183", BACK183["@WAVECLI@"]
assert "W184+ 投影" in BACK183["@S55@"] and W184p_A in BACK183["@S55@"] \
    and W184p_B in BACK183["@S55@"] and "继承第四十四例" in BACK183["@S55@"], BACK183["@S55@"][:140]
assert SEAT_SHA in BACK183["@SEATPUB@"] and "r868 seat push" in BACK183["@SEATPUB@"]
assert "第 173 波" in BACK183["@ORDINALS@"] and "W181/W182 最近自有波" in BACK183["@ORDINALS@"]
assert "第四十四例" in BACK183["@SEATSENT@"], BACK183["@SEATSENT@"][:250]
assert "阶梯第四十三例" in BACK183["@ASEEDPROSE@"], BACK183["@ASEEDPROSE@"][:250]
assert "法典 §4 W183 行 B=" + B_BAND in BACK183["@BSEEDPROSE@"], BACK183["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK183["@S5ANCH@"] and "r839 承袭收口窗" in BACK183["@S5ANCH@"] \
    and "已回填（r868 同窗）" in BACK183["@S5ANCH@"], BACK183["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK183["@S51@"] and "**" + WONLY_U + "**" in BACK183["@S51@"], \
    BACK183["@S51@"]
assert "**" + MU_U + "**" in BACK183["@S51@"], BACK183["@S51@"]
assert "**" + SIG6 + "**" in BACK183["@S52@"], BACK183["@S52@"]
assert "**" + P954 + "**" in BACK183["@S53@"], BACK183["@S53@"]
assert "一百八十行注册" in BACK183["@SCANFACE@"] and "表尾 W182 行" in BACK183["@SCANFACE@"] \
    and "机证 180 行" in BACK183["@SCANFACE@"], BACK183["@SCANFACE@"]
assert BACK183["@EOB@"] == "engine_owner==bm-a 98 行注册", BACK183["@EOB@"]
assert "PERPETUAL-N1-W183" in BACK183["@TITLE@"] and "第 181 枚" in BACK183["@TITLE@"] \
    and "【r868】" in BACK183["@TITLE@"], BACK183["@TITLE@"]
assert "r868 bm-a 带闸窗（pre-seat probe r868 单窗" in BACK183["@GATEW@"], BACK183["@GATEW@"]
assert "（r868 probe leg2/leg3 实跑）" == BACK183["@VAC@"], BACK183["@VAC@"]
assert "（r868 承袭" in BACK183["@MERGE@"], BACK183["@MERGE@"]
assert "r868 probe 单跑兑现注记" in BACK183["@CLAIMLAW@"], BACK183["@CLAIMLAW@"]
assert "results/_r868bma_w183_probe_receipt.json" in BACK183["@PRC@"] \
    or BACK183["@PRC@"] == "results/_r868bma_w183_probe_receipt.json", BACK183["@PRC@"]
assert "W182=bm-a r867 freeze（" + W182_SHA + "）" in BACK183["@CHAIN@"]
assert "→W182 **" + SEM4 + "**】）" in BACK183["@SEMT@"], BACK183["@SEMT@"][-80:]
assert "/W182 **" + DSIGN + DELTA4 + "** 如实披露" in BACK183["@KLT@"], BACK183["@KLT@"][-80:]
assert BACK183["@WPN2@"] == "W184+ 投影", BACK183["@WPN2@"]
assert BACK183["@W136TO@"] == "W136..W182", BACK183["@W136TO@"]
assert BACK183["@W2TO@"] == "W2..W182" and BACK183["@W1TO@"] == "W1..W182" \
    and BACK183["@V2W@"] == "v2..W182 落地", (BACK183["@W2TO@"], BACK183["@W1TO@"], BACK183["@V2W@"])
assert BACK183["@WN@"] == "W183" and BACK183["@W@"] == "W182" and BACK183["@SD@"] == "n1_w183" \
    and BACK183["@KOLD@"] == KNEW, (BACK183["@WN@"], BACK183["@W@"], BACK183["@SD@"])
assert BACK183["@ASEED@"] == "entry rng seed=**417_404+j**", BACK183["@ASEED@"]
assert BACK183["@BENTRY@"] == "entry rng=**417_404+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", \
    BACK183["@BENTRY@"]
assert BACK183["@PF@"] == "PERPETUAL_N1_W183_PREREG.md", BACK183["@PF@"]
assert BACK183["@R250@"] == "R250：W183 带从未指派·测量面零结果可锁", BACK183["@R250@"]
assert BACK183["@S51B@"] == "（W2..W182 共一百八十一面实测 mu 稳定先例·单波跨键微）", \
    BACK183["@S51B@"]
print("S82 spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK183 = [(val, tok) for (tok, val) in BACK182]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK183:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK183[t]) for (t, _v) in BACK182]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 183"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w182", "n1_w183"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W183") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W183 freeze" not in out_t.replace("；W182=bm-a r867 freeze", ""), \
    "unexpected W183-freeze text"
# stale-session sweep: no W182-era session stamps may survive (note:
# "r865 probe leg4" is the LEGAL new citation -- the W182 probe leg4 that
# anticipated the W183 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r865 probe 回执", "（r865 probe leg2", "r862 probe", "r863 冻结件",
              "已回填（r867", "df062c5c1", "【r865】", "FORTY-SECOND",
              "第四十二例", "0.3073", "0.245101", "\u22120.0987", "1.1853",
              "396,120", "净账本锚头 804,518", "802,318", "MSG-2026-10-08-0603",
              "r865 seat push"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r865 probe leg4" in out_t, "new W182-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK183))

# --- 5. emit the W183 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r869 bm-a W183 per-wave prereg build: transforms the freeze-time W182
prereg (git blob ad57292a4 -- file research/PERPETUAL_N1_W182_PREREG.md at
prereg-freeze commit f543c161c, byte-identical to registry-freeze commit
385dbafd8; extracted byte-verbatim to results/_r869bma_w183_prereg_src.txt)
into research/PERPETUAL_N1_W183_PREREG.md.

Generated by results/_r869bma_w183_buildgen.py (TOK/BACK pairs AST-extracted
from the r867 build script -- no exec of its time-locked live asserts;
r773/r775/r781/r830 compliance inherited: token-first two-phase vmap,
whole-string composites, numerals LAST; r735 substring-order law = BACK
list order preserved; pre-TOK sequential DRY 50/50).  r587
machine-derived facts (read from on-disk receipts): r868 probe ADMIT
naive A 417_204..419_203 refused by W182 B -> A 417_404..419_403
staircase 43rd E36 / B 419_404..419_603 own-A reservation W141 leg2;
W182 finalize r868 one-pass same-window (K 398,320 EXACT / head 806,718
EXACT delta +0 / merged mu -0.0928 no-roll / w-only -0.0921 / sigma
0.245092 / skill_line 1.1854 -> 1.1854 K-lift +0.0000 exact-zero /
n_eff 804,518 / A p95 0.3071); W182 sec7/sec8 settle backfill landed
r868 SAME window (r864 lesson welded -- no heal window); W182 freeze
385dbafd8; W183 seat push ccd18034e; seat self-ack processed/ on
origin (bm-c r741 window move).

Lineage constants disclosed (r795/r845/r849/r852/r863/r867 precedent,
passed through):
(a) anchor wave-words land on the CURRENT wave via the cascade (off-by-one
    quirk family; head/K roll machine-correct to 806,718/398,320);
(b) @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides verbatim;
(c) @SEATSENT@ "r841 席位/seat push" stale stamps ride verbatim (seat MSG
    name + push sha roll machine-correct);
(d) ordinal words roll 第九十八枚 -> 第九十九枚 (rows 98 + candidate);
(f) @KLKEY@ delta-sign roll face: W182 K-lift delta **+0.0000** (exact
    zero, DSIGN law widened >=0 this wave per r868 sec7 same-window
    record; @KLT@ chain history protected by FRESH exclusion).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\\\_r869bma_w183_prereg_src.txt"
OUT = r"research\\\\PERPETUAL_N1_W183_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r868bma_w183_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "417404_419403", "B": "419404_419603"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [417404, 419403] and leg1["B"] == [419404, 419603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [417204, 419203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [417404, 417603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [417404, 417603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 419404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 180 and leg0["tail"] == "W182" and leg0["ordinal"] == 173 \\
    and leg0["bma_ordinal"] == 99 and leg0["owner_rows"] == 172 \\
    and leg0["bma_rows"] == 98 and leg0["w182_ledger_head"] == 806718, leg0
assert leg4["W184p_A"] in ("419404..421403", "419_404..421_403") and leg4["W184p_B"] in ("419604..419803", "419_604..419_803"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W184p_B_lands_inside_W184p_A"] is True, leg4
assert "FORTY-THIRD" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w182_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 398320, "W182 merged K drift"
assert npc["pre_w182_cumulative"]["n_values"] == 396120, "pre-W182 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_398320"] == 1.1854 and kl["line_pre_w182"] == 1.1854 \\
    and kl["line_delta_k_lift"] == 0.0 and kl["n_eff_held_equal"] == 804518, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k398320"] == 0.000388, "se_mu drift"
assert abs(npc["mu_delta_w182_vs_w181ext"] - 0.006629) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3071, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w182_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0928" and WONLY4 == "-0.0921" and SIG6 == "0.245092", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w182_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "806,718" and KNEW == "398,320", (LEDG, KNEW)
KPROJ = "{:,}".format(398320 + 2200)
LEDGPROJ = "{:,}".format(806718 + 2200)
assert KPROJ == "400,520" and LEDGPROJ == "808,918", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W182 FREEZE", "-1"], capture_output=True, text=True)
W182_SHA = _r.stdout.strip()
assert W182_SHA == "385dbafd8", W182_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W183 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W183 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-0741-bma-w183-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "ccd18034e", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-08-0741-bma-w183-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W183 seat MSG not on origin (r565 pre-freeze law)"
assert "417_404..419_403" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "f543c161c:research/PERPETUAL_N1_W182_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "ad57292a4cd0fe8305d49a08cd3a2808818ef70d", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W182 sec7/sec8 settle backfill landed the r868 SAME window (r864 lesson
# welded) -- the anchor face cites it (no heal-window disclosure needed)
w182p = io.open(r"research\\\\PERPETUAL_N1_W182_PREREG.md", encoding="utf-8", newline="").read()
assert "806,718" in w182p and "K=398,320" in w182p, \\
    "W182 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W182" in src and "415_004..417_003" in src, "src face drift"
'''

TAIL = '''
TOK183 = %s
BACK183 = %s

EXPECT = %s

out_t = src
for old, tok in TOK183:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK183:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 1[78][0-9]", out_t)))
assert stale_wave == ["波号 183"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w182", "n1_w183"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W183") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W183 freeze" not in out_t.replace("；W182=bm-a r867 freeze", ""), \\
    "unexpected W183-freeze text"

# stale-session sweep ("r865 probe leg4" = LEGAL new citation; bare "396,120"
# = consumed by the K roll -- head-face stale probe uses the
# whole-string 净账本锚头 form)
for stale in ("r865 probe 回执", "（r865 probe leg2", "r862 probe", "r863 冻结件",
              "已回填（r867", "df062c5c1", "【r865】", "FORTY-SECOND",
              "第四十二例", "0.3073", "0.245101", "−0.0987", "1.1853",
              "396,120", "净账本锚头 804,518", "802,318", "MSG-2026-10-08-0603",
              "r865 seat push"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r865 probe leg4" in out_t, "new W182-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W183 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK183)
back_lit = repr([(t, BACK183[t]) for (t, _v) in BACK182])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r869bma_w183_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r869bma_w183_prereg_build.py", len(out), "bytes")
