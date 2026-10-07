# -*- coding: utf-8 -*-
"""r849 bm-a generator: builds results/_r849bma_w179_prereg_build.py by
AST-extracting the r845 W178 build script's BACK178/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts), then deriving the
BACK179 pairs as (token, S79-rolled W179 value) -- old side = the W178-era
value (physical freeze-blob text at de4716da2), new side = the S79 W179 fact
map applied to that W178 text.  r773 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved (long composites precede short substrings;
proj-A before arith-A, proj-B before naive-B, B-band before prior-B).

r587 machine-derived facts (every displayed value read from on-disk receipts
this window):
  - pre-seat probe results/_r848bma_w179_probe_receipt.json rc0 ADMIT
    (leg0 registry 176 rows tail W178 ordinal 169 / bma_ordinal 95 /
    owner_rows 168 / bma_rows 94 / w178_ledger_head 797,505; leg1
    A 408_604..410_603 hops=1 / B 410_604..410_803 hops=1 / naive A
    408_404..410_403 refused at its own start by the registered W178 B
    band 408_404..408_603 (staircase THIRTY-NINTH instance E36 per receipt
    A_semantics; W178 seat leg4 + r844 probe leg4 anticipated 39th --
    projection and receipt ordinals MATCH, no divergence face this wave);
    naive B 408_604..408_803 lands inside own-A 408_604..410_603; leg2
    conflicts 0; leg3 origin vacancy True; leg4 W180+ projection
    A 410_604..412_603 hops=0 / B 410_804..411_003 hops=0, B inside A);
  - W178 finalize landed r846 (one-pass, dead-r845 adoption closeout,
    preflight three-gate GREEN half-open law)
    (results/perpetual_faces/n1_w178_results.json: merged K=389,520,
    mu=-0.092730 6dp / 4dp -0.0927, sigma=0.245104 6dp; w178-only
    mu=-0.0923 4dp; se_mu_at_k389520=0.000393; A p95=0.3275; k-lift
    line_merged_389520 1.1849 / line_pre_w178 1.1848 / delta +0.0001 /
    n_eff_held_equal 795,305; canon flip NOT performed;
    mu_delta_w178_vs_w177ext=+0.001369);
  - W178 sec7/sec8 settle backfill landed the r846 finalize window
    (same-window; on-disk text "【finalize 收口机械回填·r846 窗机证】"
    + "797,505" live-asserted);
  - W178 freeze registered sha machine-derived = de4716da2 (git log
    origin/main --grep "W178 FREEZE"); W179 seat push sha machine-derived =
    4c645c95f (git log --diff-filter=A on the seat MSG inbox path; payload
    = seat MSG + probe script + probe receipt); seat self-ack archive move
    landed r848 window (processed/ path on origin).

S79 LINEAGE CONSTANTS (r795/r845 precedent, passed through + disclosed):
  (a) anchor/§5 wave-words land on the CURRENT wave via the cascade
    (off-by-one quirk family since W165 r795): the W179 prereg anchor
    bracket reads "W179 finalize one-pass bm-a r844 dead-tail 收养窗"
    and "W179 finalize 落账" while the head/K values roll machine-correct
    to 797,505/389,520 (the true anchor = W178 finalize r846);
  (b) the @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides
    verbatim (r845 quirk (f) continuation);
  (c) @SEATSENT@ "本机 r841 席位"/"（r841 seat push" stale session
    stamps ride verbatim (r845 precedent: no S78 pair existed; the seat
    MSG name + push sha roll machine-correct);
  (d) the bm-a-owned ordinal words roll 第九十四枚 -> 第九十五枚
    (rows 94 + candidate = 95th owned per probe leg0);
  (e) @KLT@ chain appends the W178 entry (+0.0001 machine-read);
    @SEMT@ chain appends W178 se_mu 0.000393; @CHAIN@ appends
    "W178=bm-a r845 freeze（de4716da2）";
  (f) wave-words/ordinals in the title, pump ordinal 第 177 枚, scan
    face 176 rows etc. all roll per probe leg0 machine counts.
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W178 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "de4716da2:research/PERPETUAL_N1_W178_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W178 freeze-time blob not reachable"
blob = _r.stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r849bma_w179_prereg_src.txt", "wb").write(blob)
print("W179 src extracted:", len(blob), "bytes (W178 freeze-time blob de4716da2)")

# --- 1. AST-extract the r845 build script's BACK178 + EXPECT ---------------
src845 = io.open(r"results\_r845bma_w178_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src845)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK178 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK178" and isinstance(node.value, ast.List):
            BACK178 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK178.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK178 is not None and EXPECT is not None, "BACK178/EXPECT not extracted"
print("r845 BACK178 entries:", len(BACK178), "EXPECT entries:", len(EXPECT))
back178_map = dict(BACK178)
assert len(back178_map) == len(BACK178)

# --- 2. W179 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r848bma_w179_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "408604_410603", "B": "410604_410803"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [408604, 410603] and leg1["B"] == [410604, 410803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [408404, 410403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [408604, 408803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [408604, 408803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 410604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 176 and leg0["tail"] == "W178" and leg0["ordinal"] == 169 \
    and leg0["bma_ordinal"] == 95 and leg0["owner_rows"] == 168 \
    and leg0["bma_rows"] == 94 and leg0["w178_ledger_head"] == 797505, leg0
assert leg4["W180p_A"] == "410604..412603" and leg4["W180p_B"] == "410804..411003", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W180p_B_lands_inside_W180p_A"] is True, leg4
assert "THIRTY-NINTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w178_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 389520, "W178 merged K drift"
assert npc["pre_w178_cumulative"]["n_values"] == 387320, "pre-W178 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_389520"] == 1.1849 and kl["line_pre_w178"] == 1.1848 \
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 795305, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k389520"] == 0.000393, "se_mu drift"
assert abs(npc["mu_delta_w178_vs_w177ext"] - 0.001369) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3275, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w178_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0923" and SIG6 == "0.245104", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w178_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "797,505" and KNEW == "389,520", (LEDG, KNEW)
KPROJ = "{:,}".format(389520 + 2200)
LEDGPROJ = "{:,}".format(797505 + 2200)
assert KPROJ == "391,720" and LEDGPROJ == "799,705", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r590 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W178 FREEZE", "-1"], capture_output=True, text=True)
W178_SHA = _r_.stdout.strip()
assert W178_SHA == "de4716da2", W178_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W179 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W179 FREEZE (r511 tail-lock)"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                      "--diff-filter=A",
                      "--", "fleet/inbox/MSG-2026-10-07-2320-bma-w179-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "4c645c95f", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/MSG-2026-10-07-2320-bma-w179-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W179 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "408_604..410_603" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W178 sec7/sec8 backfill landed the r846 window -- the anchor face cites it
w178p = io.open(r"research\PERPETUAL_N1_W178_PREREG.md", encoding="utf-8", newline="").read()
assert "r846 窗机证" in w178p and "797,505" in w178p, \
    "W178 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "408_604..410_603"
B_BAND = "410_604..410_803"
NAIVE_A = "408_404..410_403"
NAIVE_B = "408_604..408_803"
PRIOR_B = "408_404..408_603"     # registered W178 B band (refusal band)
A_SEED, B_SEED = "408_604", "410_604"
SEAT_MSG = "MSG-2026-10-07-2320-bma-w179-seat"
W180p_A = "410_604..412_603"
W180p_B = "410_804..411_003"

# --- 3. S79 = W178->W179 ordered fact map -----------------------------------
S79 = [
    # -- window/session composites (longest first) --
    ("已回填（r845 窗", "已回填（r846 窗"),
    ("r844 bm-a 带闸窗（pre-seat probe r844 单窗", "r848 bm-a 带闸窗（pre-seat probe r848 单窗"),
    ("（r844 承袭", "（r848 承袭"),
    ("r844 probe 单跑兑现注记", "r848 probe 单跑兑现注记"),
    ("（r844 probe leg2/leg3 实跑）", "（r848 probe leg2/leg3 实跑）"),
    ("r844 probe 回执 A_semantics 机读序数=THIRTY-EIGHTH",
     "r848 probe 回执 A_semantics 机读序数=THIRTY-NINTH"),
    ("r841 probe leg4", "r844 probe leg4"),
    ("（r843 冻结件）", "（r845 冻结件）"),
    ("_r844bma_w178_probe_receipt.json", "_r848bma_w179_probe_receipt.json"),
    ("MSG-2026-10-07-2157-bma-w178-seat", "MSG-2026-10-07-2320-bma-w179-seat"),
    ("5b9284c79", "4c645c95f"),
    ("【r845】", "【r849】"),
    # -- band geometry (proj-A, proj-B, B-band, A-band, naive-A, prior-B,
    #    naive-B -- r735 order law: projections consumed before the naive
    #    rolls re-create them; B-band consumed before prior-B re-creates it) --
    ("408_404..410_403", "410_604..412_603"),
    ("408_604..408_803", "410_804..411_003"),
    ("408_404..408_603", "410_604..410_803"),
    ("406_404..408_403", "408_604..410_603"),
    ("406_204..408_203", "408_404..410_403"),
    ("406_204..406_403", "408_404..408_603"),
    ("406_404..406_603", "408_604..408_803"),
    ("406_403+1", "408_603+1"),
    ("408_403+1", "410_603+1"),
    ("406_404+j", "408_604+j"),
    ("408_404+j", "410_604+j"),
    # -- ordinals (high first) --
    ("第三十九例", "第四十例"),
    ("第三十八例", "第三十九例"),
    ("第 176 枚", "第 177 枚"),
    ("行 167+本候选", "行 168+本候选"),
    ("第九十四枚", "第九十五枚"),
    ("第 168 波", "第 169 波"),
    ("行 93+本候选", "行 94+本候选"),
    ("bm-a 93 行注册", "bm-a 94 行注册"),
    ("一百七十五行注册", "一百七十六行注册"),
    ("机证 175 行", "机证 176 行"),
    ("一百七十六面实测", "一百七十七面实测"),
    # -- numbers (projection before old-head roll; head before n_eff) --
    ("**389,520 投影**", "**391,720 投影**"),
    ("**1.1847**", "**1.1849**"),
    ("·line_pre 1.1846·", "·line_pre 1.1848·"),
    ("**0.3116**", "**0.3275**"),
    ("**−0.0936**", "**−0.0923**"),
    ("0.245080", "0.245104"),
    ("795,305", "797,505"),
    ("793,105", "795,305"),
    ("387,320", "389,520"),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w178", "n1_w179"),
    ("n1_w177", "n1_w178"),
    # -- wave-word cascade (high first) --
    ("W179", "W180"),
    ("W178", "W179"),
    ("W177", "W178"),
    # -- bare-number leftovers --
    ("波号 178=", "波号 179="),
    ("--wave 178", "--wave 179"),
]


def s79(t):
    for old, new in S79:
        t = t.replace(old, new)
    return t


# tokens excluded from the s79 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK179 = {
    "@CHAIN@": back178_map["@CHAIN@"] + "；W178=bm-a r845 freeze（" + W178_SHA + "）",
    "@KLT@": back178_map["@KLT@"].replace(" 如实披露", "/W178 **+0.0001** 如实披露"),
    "@SEMT@": back178_map["@SEMT@"].replace("】）", "→W178 **0.000393**】）"),
    "@S55@": (
        "5. **W180+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W180p_A + " **CLEAN**（hops=0）；B first-clean **" + W180p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W180：W180 冻结方必须在"
        " post-W179 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W179 B 带 " + B_BAND + " 注册后将拒 naive W180 A 窗**——W180 A 重 derive 同强制"
        "（越过 W179 B 带·阶梯 A-hops-prior-B 继承第四十例）；verify at W180 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s79(back178_map["@TITLE@"]),
    "@WAVEFREE@": s79(back178_map["@WAVEFREE@"]),
    "@VAC@": s79(back178_map["@VAC@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r848 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W179 pre-seat probe 脚本+回执同推；W179 pre-seat probe "
        "脚本+回执已在 origin 自 r848 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r848 同窗·r841 先例·如实注记）】"
    ),
    "@MERGE@": s79(back178_map["@MERGE@"]),
    "@AFACE@": s79(back178_map["@AFACE@"]),
    "@BFACE@": s79(back178_map["@BFACE@"]),
    "@R250@": s79(back178_map["@R250@"]),
    "@SCANFACE@": s79(back178_map["@SCANFACE@"]),
    "@ANCHOR@": s79(back178_map["@ANCHOR@"]),
    "@POOL@": s79(back178_map["@POOL@"]),
    "@SEATSENT@": s79(back178_map["@SEATSENT@"]),
    "@CLAIMLAW@": s79(back178_map["@CLAIMLAW@"]),
    "@ORDINALS@": (
        back178_map["@ORDINALS@"]
        .replace("第 168 波", "第 169 波")
        .replace("第九十四枚", "第九十五枚")
        .replace("行 93+本候选", "行 94+本候选")
        .replace("/W175/W176/W177 最近自有波", "/W175/W176/W177/W178 最近自有波")
        .replace("注册表 W177 行后", "注册表 W178 行后")
        .replace("MSG-2026-10-07-2157-bma-w178-seat", SEAT_MSG)
        .replace("5b9284c79", SEAT_SHA)
    ),
    "@V2W@": s79(back178_map["@V2W@"]),
    "@ASEED@": s79(back178_map["@ASEED@"]),
    "@ASEEDPROSE@": s79(back178_map["@ASEEDPROSE@"]),
    "@BENTRY@": s79(back178_map["@BENTRY@"]),
    "@BSEEDPROSE@": s79(back178_map["@BSEEDPROSE@"]),
    "@GATEW@": s79(back178_map["@GATEW@"]),
    "@FN@": s79(back178_map["@FN@"]),
    "@RFN@": s79(back178_map["@RFN@"]),
    "@ODOLD@": s79(back178_map["@ODOLD@"]),
    "@S5ANCH@": s79(back178_map["@S5ANCH@"]),
    "@S51@": s79(back178_map["@S51@"]),
    "@S51B@": s79(back178_map["@S51B@"]),
    "@S52@": s79(back178_map["@S52@"]),
    "@S53@": s79(back178_map["@S53@"]),
    "@KLKEY@": s79(back178_map["@KLKEY@"]),
    "@WAVECLI@": s79(back178_map["@WAVECLI@"]),
    "@EOB@": s79(back178_map["@EOB@"]),
    "@W136TO@": s79(back178_map["@W136TO@"]),
    "@OWNCHAIN@": back178_map["@OWNCHAIN@"].replace(
        "/W177 最近自有波", "/W177/W178 最近自有波"),
    "@W2TO@": s79(back178_map["@W2TO@"]),
    "@W1TO@": s79(back178_map["@W1TO@"]),
    "@PRC@": s79(back178_map["@PRC@"]),
    "@PF@": s79(back178_map["@PF@"]),
    "@B@": s79(back178_map["@B@"]),
    "@WPN2@": s79(back178_map["@WPN2@"]),
    "@WN@": s79(back178_map["@WN@"]),
    "@W@": s79(back178_map["@W@"]),
    "@SD@": s79(back178_map["@SD@"]),
    "@KOLD@": s79(back178_map["@KOLD@"]),
    "@N171@": "179",
    "@N170@": "178",
    "@N169@": "177",
}
missing = [t for (t, _v) in BACK178 if t not in BACK179]
assert not missing, missing

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK179["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（408_603+1）" in chk and "THIRTY-NINTH（第三十九例）" in chk, chk[:200]
chk = BACK179["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（410_603+1）" in chk, chk[:200]
chk = BACK179["@ANCHOR@"]
assert "W1..W178 N1 finalize 已全部落地" in chk and "797,505" in chk \
    and "K=389,520" in chk, chk[:200]
assert BACK179["@POOL@"] == "累计 null 池=389,520+2,200（本波）=**391,720 投影**", BACK179["@POOL@"]
assert "**1.1849**" in BACK179["@KLKEY@"] and "n_eff 795,305" in BACK179["@KLKEY@"], BACK179["@KLKEY@"]
assert "line_pre 1.1848" in BACK179["@KLKEY@"], BACK179["@KLKEY@"]
assert BACK179["@WAVEFREE@"] == "波号 179=注册表 W178 行后首个自由号", BACK179["@WAVEFREE@"]
assert "n1_w179_results.json" in BACK179["@FN@"] and "n1_w178_results.json" in BACK179["@ODOLD@"]
assert BACK179["@WAVECLI@"] == "--wave 179/finalize --wave 179", BACK179["@WAVECLI@"]
assert "W180+ 投影" in BACK179["@S55@"] and "410_604..412_603" in BACK179["@S55@"]
assert "4c645c95f" in BACK179["@SEATPUB@"] and "r848 seat push" in BACK179["@SEATPUB@"]
assert "第 169 波" in BACK179["@ORDINALS@"] and "W177/W178 最近自有波" in BACK179["@ORDINALS@"]
assert "第四十例" in BACK179["@SEATSENT@"], BACK179["@SEATSENT@"][:200]
assert "阶梯第三十九例" in BACK179["@ASEEDPROSE@"], BACK179["@ASEEDPROSE@"][:200]
print("S79 spot-checks: PASS (14 composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK179 = [(val, tok) for (tok, val) in BACK178]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK179:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK179[t]) for (t, _v) in BACK178]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))
assert stale_wave == ["波号 179"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w178", "n1_w179"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W179") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W179 freeze" not in out_t.replace("；W178=bm-a r845 freeze", ""), \
    "unexpected W179-freeze text"
# stale-session sweep: no W178-era session stamps may survive (note:
# "r844 probe leg4" is the LEGAL new citation -- the W178 probe leg4 that
# anticipated the W179 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r844 probe 回执", "（r844 probe leg2", "r841 probe", "r843 冻结件",
              "已回填（r845 窗", "5b9284c79", "【r845】", "THIRTY-EIGHTH",
              "第三十八例", "0.3116", "0.245080", "−0.0936", "1.1847",
              "387,320", "793,105"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r844 probe leg4" in out_t, "new W178-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK179))

# --- 5. emit the W179 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r849 bm-a W179 per-wave prereg build: transforms the freeze-time W178
prereg (git blob de4716da2:research/PERPETUAL_N1_W178_PREREG.md, extracted
byte-verbatim to results/_r849bma_w179_prereg_src.txt) into
research/PERPETUAL_N1_W179_PREREG.md.

Generated by results/_r849bma_w179_buildgen.py (TOK/BACK pairs AST-extracted
from the r845 build script -- no exec of its time-locked live asserts;
r773 compliance inherited: token-first two-phase vmap, whole-string
composites, numerals LAST; r735 substring-order law = BACK list order
preserved).  r587 machine-derived facts (read from on-disk receipts):
r848 probe ADMIT A 408_604..410_603 staircase 39th E36 / B 410_604..410_803;
W178 finalize r846 one-pass adoption closeout (K 389,520 / head 797,505 /
skill_line 1.1849); W178 sec7/sec8 backfill landed r846 window; W178 freeze
de4716da2; W179 seat push 4c645c95f; seat self-ack processed/ on origin.

Lineage constants disclosed (r795/r845 precedent, passed through):
(a) anchor wave-words land on the CURRENT wave via the cascade (off-by-one
    quirk family; head/K roll machine-correct to 797,505/389,520);
(b) @S5ANCH@ "bm-a r839 承袭收口窗" stale session stamp rides verbatim;
(c) @SEATSENT@ "r841 席位/seat push" stale stamps ride verbatim (seat MSG
    name + push sha roll machine-correct);
(d) ordinal words roll 第九十四枚 -> 第九十五枚 (rows 94 + candidate).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = r"results\\_r849bma_w179_prereg_src.txt"
OUT = r"research\\PERPETUAL_N1_W179_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r848bma_w179_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "408604_410603", "B": "410604_410803"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [408604, 410603] and leg1["B"] == [410604, 410803], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [408404, 410403], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [408604, 408803], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [408604, 408803], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 410604, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 176 and leg0["tail"] == "W178" and leg0["ordinal"] == 169 \\
    and leg0["bma_ordinal"] == 95 and leg0["owner_rows"] == 168 \\
    and leg0["bma_rows"] == 94 and leg0["w178_ledger_head"] == 797505, leg0
assert leg4["W180p_A"] == "410604..412603" and leg4["W180p_B"] == "410804..411003", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W180p_B_lands_inside_W180p_A"] is True, leg4
assert "THIRTY-NINTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w178_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 389520, "W178 merged K drift"
assert npc["pre_w178_cumulative"]["n_values"] == 387320, "pre-W178 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_389520"] == 1.1849 and kl["line_pre_w178"] == 1.1848 \\
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 795305, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k389520"] == 0.000393, "se_mu drift"
assert abs(npc["mu_delta_w178_vs_w177ext"] - 0.001369) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3275, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w178_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0923" and SIG6 == "0.245104", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w178_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "797,505" and KNEW == "389,520", (LEDG, KNEW)
KPROJ = "{:,}".format(389520 + 2200)
LEDGPROJ = "{:,}".format(797505 + 2200)
assert KPROJ == "391,720" and LEDGPROJ == "799,705", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r590 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W178 FREEZE", "-1"], capture_output=True, text=True)
W178_SHA = _r.stdout.strip()
assert W178_SHA == "de4716da2", W178_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W179 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W179 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-07-2320-bma-w179-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "4c645c95f", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-2320-bma-w179-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W179 seat MSG not on origin (r565 pre-freeze law)"
assert "408_604..410_603" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W178 sec7/sec8 backfill landed the r846 window -- the anchor face cites it
w178p = io.open(r"research\\PERPETUAL_N1_W178_PREREG.md", encoding="utf-8", newline="").read()
assert "r846 窗机证" in w178p and "797,505" in w178p, \\
    "W178 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
'''

TAIL = '''
TOK179 = %s
BACK179 = %s

EXPECT = %s

out_t = src
for old, tok in TOK179:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK179:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))
assert stale_wave == ["波号 179"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w178", "n1_w179"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W179") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W179 freeze" not in out_t.replace("；W178=bm-a r845 freeze", ""), \\
    "unexpected W179-freeze text"

for stale in ("r844 probe 回执", "（r844 probe leg2", "r841 probe", "r843 冻结件",
              "已回填（r845 窗", "5b9284c79", "【r845】", "THIRTY-EIGHTH",
              "第三十八例", "0.3116", "0.245080", "−0.0936", "1.1847",
              "387,320", "793,105"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r844 probe leg4" in out_t, "new W178-probe-leg4 citation missing"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W179 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK179)
back_lit = repr([(t, BACK179[t]) for (t, _v) in BACK178])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r849bma_w179_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r849bma_w179_prereg_build.py", len(out), "bytes")
