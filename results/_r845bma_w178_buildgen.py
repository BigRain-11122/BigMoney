# -*- coding: utf-8 -*-
"""r845 bm-a generator: builds results/_r845bma_w178_prereg_build.py by
AST-extracting the r842 W177 build script's BACK177/EXPECT pairs (all values
machine-read, zero exec of its time-locked live asserts), then deriving the
BACK178 pairs as (token, S78-rolled W178 value) -- old side = the W177-era
value (physical freeze-blob text at c06cc230f), new side = the S78 W178 fact
map applied to that W177 text.  r773 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved (long composites precede short substrings).

r587 machine-derived facts (every displayed value read from on-disk receipts
this window):
  - pre-seat probe results/_r844bma_w178_probe_receipt.json rc0 ADMIT
    (leg0 registry 175 rows tail W177 ordinal 168 / bma_ordinal 94 /
    owner_rows 167 / bma_rows 93 / w177_ledger_head 795,305; leg1
    A 406_404..408_403 hops=1 / B 408_404..408_603 hops=1 / naive A
    406_204..408_203 refused at its own start by the registered W177 B
    band 406_204..406_403 (staircase THIRTY-EIGHTH instance E36 per receipt
    A_semantics; W177 sec5.5 anticipated 38th -- projection and receipt
    ordinals MATCH, no divergence face this wave); naive B 406_404..406_603
    lands inside own-A 406_404..408_403; leg2 conflicts 0; leg3 origin
    vacancy True; leg4 W179+ projection A 408_404..410_403 hops=0 / B
    408_604..408_803 hops=0, B inside A);
  - W177 finalize landed r844 (dead-tail adopted, three-gate verified)
    (results/perpetual_faces/n1_w177_results.json: merged K=387,320,
    mu=-0.092732 -> 4dp -0.0927, sigma=0.245080 6dp; w177-only mu=-0.0936
    4dp; se_mu_at_k387320=0.000394; A p95=0.3116; k-lift line_merged 1.1847 /
    line_pre 1.1846 / delta +0.0001 / n_eff 793,105; canon flip NOT
    performed; mu_delta_w177_vs_w176ext=-0.004716);
  - W177 sec7/sec8 settle backfill landed r845 window (this round; the
    r844 dead-tail adoption window ran the three gates inline but the
    mechanical backfill slipped -- delayed-window precedent W159/W168/W169;
    on-disk text "已回填 r845 窗" + mu_delta key live-asserted);
  - W177 freeze registered sha machine-derived = c06cc230f (git log
    origin/main --grep "W177 FREEZE"); W178 seat push sha machine-derived =
    5b9284c79 (git log --diff-filter=A on the seat MSG inbox path); seat
    self-ack archive move landed r845 window (processed/ path on origin).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. extract the freeze-time W177 prereg blob (LF, byte-verbatim) -------
_r = subprocess.run(
    ["git", "show", "c06cc230f:research/PERPETUAL_N1_W177_PREREG.md"],
    capture_output=True)
assert _r.returncode == 0, "W177 freeze-time blob not reachable"
blob = _r.stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
io.open(r"results\_r845bma_w178_prereg_src.txt", "wb").write(blob)
print("W178 src extracted:", len(blob), "bytes (W177 freeze-time blob c06cc230f)")

# --- 1. AST-extract the r842 build script's BACK177 + EXPECT --------------
src842 = io.open(r"results\_r842bma_w177_prereg_build.py", encoding="utf-8").read()
tree = ast.parse(src842)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK177 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK177" and isinstance(node.value, ast.List):
            BACK177 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK177.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK177 is not None and EXPECT is not None, "BACK177/EXPECT not extracted"
print("r842 BACK177 entries:", len(BACK177), "EXPECT entries:", len(EXPECT))
back_map = dict(BACK177)
assert len(back_map) == len(BACK177)

# --- 2. W178 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r844bma_w178_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "406404_408403", "B": "408404_408603"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [406404, 408403] and leg1["B"] == [408404, 408603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [406204, 408203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [406404, 406603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [406404, 406603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 408404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 175 and leg0["tail"] == "W177" and leg0["ordinal"] == 168 \
    and leg0["bma_ordinal"] == 94 and leg0["owner_rows"] == 167 \
    and leg0["bma_rows"] == 93 and leg0["w177_ledger_head"] == 795305, leg0
W179p_A = "408_404..410_403"
W179p_B = "408_604..408_803"
assert leg4["W179p_A"] == "408404..410403" and leg4["W179p_B"] == "408604..408803", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W179p_B_lands_inside_W179p_A"] is True, leg4
assert "THIRTY-EIGHTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w177_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 387320, "W177 merged K drift"
assert npc["pre_w177_cumulative"]["n_values"] == 385120, "pre-W177 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_387320"] == 1.1847 and kl["line_pre_w177"] == 1.1846 \
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 793105, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k387320"] == 0.000394, "se_mu drift"
assert abs(npc["mu_delta_w177_vs_w176ext"] - (-0.004716)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3116, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w177_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0936" and SIG6 == "0.245080", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w177_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "795,305" and KNEW == "387,320", (LEDG, KNEW)
KPROJ = "{:,}".format(387320 + 2200)
LEDGPROJ = "{:,}".format(795305 + 2200)
assert KPROJ == "389,520" and LEDGPROJ == "797,505", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W177 FREEZE", "-1"], capture_output=True, text=True)
W177_SHA = _r_.stdout.strip()
assert W177_SHA == "c06cc230f", W177_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                      "--diff-filter=A",
                      "--", "fleet/inbox/MSG-2026-10-07-2157-bma-w178-seat.md"],
                     capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "5b9284c79", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/MSG-2026-10-07-2157-bma-w178-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W178 seat MSG not on origin processed/ (r565 pre-freeze law)"
assert "406_404..408_403" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W177 sec7/sec8 backfill landed this window -- the anchor face cites it
w177p = io.open(r"research\PERPETUAL_N1_W177_PREREG.md", encoding="utf-8", newline="").read()
assert "mu_delta_w177_vs_w176ext" in w177p and "已回填 r845 窗" in w177p, \
    "W177 sec7/sec8 backfill missing (anchor-face citation would be false)"

A_BAND = "406_404..408_403"
B_BAND = "408_404..408_603"
NAIVE_A = "406_204..408_203"
NAIVE_B = "406_404..406_603"
PRIOR_B = "406_204..406_403"     # registered W177 B band (refusal band)
A_SEED, B_SEED = "406_404", "408_404"
SEAT_MSG = "MSG-2026-10-07-2157-bma-w178-seat"
MIN = "\u2212"

# --- 3. S78 = W177->W178 ordered fact map -----------------------------------
S78 = [
    # -- window/session composites (longest first) --
    ("W176 finalize one-pass bm-a r839 承袭收口窗", "W177 finalize one-pass bm-a r844 dead-tail 收养窗"),
    ("已回填（r839 one-pass 窗", "已回填（r845 窗"),
    ("W176 finalize 落账", "W177 finalize 落账"),
    ("r841 bm-a 带闸窗（pre-seat probe r841 单窗", "r844 bm-a 带闸窗（pre-seat probe r844 单窗"),
    ("（r841 承袭", "（r844 承袭"),
    ("r841 probe 单跑兑现注记", "r844 probe 单跑兑现注记"),
    ("（r841 probe leg2/leg3 实跑）", "（r844 probe leg2/leg3 实跑）"),
    ("r841 probe 回执 A_semantics 机读序数=THIRTY-SEVENTH",
     "r844 probe 回执 A_semantics 机读序数=THIRTY-EIGHTH"),
    ("r832 probe leg4", "r841 probe leg4"),
    ("（r834 冻结件）", "（r843 冻结件）"),
    ("_r841bma_w177_probe_receipt.json", "_r844bma_w178_probe_receipt.json"),
    ("MSG-2026-10-07-2031-bma-w177-seat", "MSG-2026-10-07-2157-bma-w178-seat"),
    ("780a0cd30", "5b9284c79"),
    ("【r842】", "【r845】"),
    # -- band geometry (proj-A, proj-B, B-band, A-band, naive-A, prior-B,
    #    naive-B -- r735 order law: projections consumed before the naive
    #    rolls re-create them; B-band before prior-B) --
    ("406_204..408_203", "408_404..410_403"),
    ("406_404..406_603", "408_604..408_803"),
    ("406_204..406_403", "408_404..408_603"),
    ("404_204..406_203", "406_404..408_403"),
    ("404_004..406_003", "406_204..408_203"),
    ("404_004..404_203", "406_204..406_403"),
    ("404_204..404_403", "406_404..406_603"),
    ("404_203+1", "406_403+1"),
    ("406_203+1", "408_403+1"),
    ("404_204+j", "406_404+j"),
    ("406_204+j", "408_404+j"),
    # -- ordinals (high first) --
    ("第三十八例", "第三十九例"),
    ("第三十七例", "第三十八例"),
    ("第 175 枚", "第 176 枚"),
    ("行 166+本候选", "行 167+本候选"),
    ("第九十三枚", "第九十四枚"),
    ("第 167 波", "第 168 波"),
    ("行 92+本候选", "行 93+本候选"),
    ("bm-a 92 行注册", "bm-a 93 行注册"),
    ("一百七十四行注册", "一百七十五行注册"),
    ("机证 174 行", "机证 175 行"),
    ("一百七十五面实测", "一百七十六面实测"),
    # -- numbers (projection before old-head roll; head before n_eff) --
    ("**387,320 投影**", "**389,520 投影**"),
    ("**−0.0001**", "**+0.0001**"),
    ("**1.1845**", "**1.1847**"),
    ("**0.3118**", "**0.3116**"),
    ("**−0.0889**", "**−0.0936**"),
    ("0.245060", "0.245080"),
    ("793,105", "795,305"),
    ("790,905", "793,105"),
    ("385,120", "387,320"),
    # -- n1_w forms (high first: consume then re-create) --
    ("n1_w177", "n1_w178"),
    ("n1_w176", "n1_w177"),
    # -- wave-word cascade (high first) --
    ("W178", "W179"),
    ("W177", "W178"),
    ("W176", "W177"),
    # -- bare-number leftovers --
    ("波号 177=", "波号 178="),
    ("--wave 177", "--wave 178"),
]


def s78(t):
    for old, new in S78:
        t = t.replace(old, new)
    return t


# tokens excluded from the s78 vmap (fresh constructions / chain appends)
FRESH = {"@S55@", "@SEATPUB@", "@CHAIN@", "@KLT@", "@SEMT@", "@OWNCHAIN@",
         "@ORDINALS@", "@N171@", "@N170@", "@N169@"}

BACK78 = {
    "@CHAIN@": back_map["@CHAIN@"] + "；W177=bm-a r843 freeze（" + W177_SHA + "）",
    "@KLT@": back_map["@KLT@"].replace(" 如实披露", "/W177 **+0.0001** 如实披露"),
    "@SEMT@": back_map["@SEMT@"].replace("】）", "→W177 **0.000394**】）"),
    "@S55@": (
        "5. **W179+ 投影（probe 机证·下波冻结方复核非转抄 r587 律）**：A first-clean "
        + W179p_A + " **CLEAN**（hops=0）；B first-clean **" + W179p_B + " CLEAN**（hops=0）"
        "——**naive B 落在 naive A 窗内**（W141 同窗互斥先例适用于 W179：W179 冻结方必须在"
        " post-W178 注册宇宙重 derive 且 derive B 时预留本波 A 窗——leg2 律/E36 卡）；"
        "**W178 B 带 " + B_BAND + " 注册后将拒 naive W179 A 窗**——W179 A 重 derive 同强制"
        "（越过 W178 B 带·阶梯 A-hops-prior-B 继承第三十九例）；verify at W179 prereg，"
        "hop 链逐跳在 probe 回执。"
    ),
    "@TITLE@": s78(back_map["@TITLE@"]),
    "@WAVEFREE@": s78(back_map["@WAVEFREE@"]),
    "@VAC@": s78(back_map["@VAC@"]),
    "@SEATPUB@": (
        "本机席位公示=" + SEAT_MSG + " 已推 origin " + SEAT_SHA
        + " 先于本冻结【r565 律·推送窗=r845 seat push 直接快进送达 " + SEAT_SHA
        + "（payload=seat MSG+W177 §7/§8 机械回填件+三闸回执=W146 同推先例族·W178 "
        "pre-seat probe 脚本+回执已在 origin 自 r844 收口投送不再重送）；"
        "self-ack inbox→processed 移位已收档（r845 同窗·r828 先例·如实注记）】"
    ),
    "@MERGE@": s78(back_map["@MERGE@"]),
    "@AFACE@": s78(back_map["@AFACE@"]),
    "@BFACE@": s78(back_map["@BFACE@"]),
    "@R250@": s78(back_map["@R250@"]),
    "@SCANFACE@": s78(back_map["@SCANFACE@"]),
    "@ANCHOR@": s78(back_map["@ANCHOR@"]),
    "@POOL@": s78(back_map["@POOL@"]),
    "@SEATSENT@": s78(back_map["@SEATSENT@"]),
    "@CLAIMLAW@": s78(back_map["@CLAIMLAW@"]),
    "@ORDINALS@": (
        back_map["@ORDINALS@"]
        .replace("第 167 波", "第 168 波")
        .replace("第九十三枚", "第九十四枚")
        .replace("行 92+本候选", "行 93+本候选")
        .replace("/W175/W176 最近自有波", "/W175/W176/W177 最近自有波")
        .replace("注册表 W176 行后", "注册表 W177 行后")
        .replace("MSG-2026-10-07-2031-bma-w177-seat", SEAT_MSG)
        .replace("780a0cd30", SEAT_SHA)
    ),
    "@V2W@": s78(back_map["@V2W@"]),
    "@ASEED@": s78(back_map["@ASEED@"]),
    "@ASEEDPROSE@": s78(back_map["@ASEEDPROSE@"]),
    "@BENTRY@": s78(back_map["@BENTRY@"]),
    "@BSEEDPROSE@": s78(back_map["@BSEEDPROSE@"]),
    "@GATEW@": s78(back_map["@GATEW@"]),
    "@FN@": s78(back_map["@FN@"]),
    "@RFN@": s78(back_map["@RFN@"]),
    "@ODOLD@": s78(back_map["@ODOLD@"]),
    "@S5ANCH@": s78(back_map["@S5ANCH@"]),
    "@S51@": s78(back_map["@S51@"]),
    "@S51B@": s78(back_map["@S51B@"]),
    "@S52@": s78(back_map["@S52@"]),
    "@S53@": s78(back_map["@S53@"]),
    "@KLKEY@": s78(back_map["@KLKEY@"]),
    "@WAVECLI@": s78(back_map["@WAVECLI@"]),
    "@EOB@": s78(back_map["@EOB@"]),
    "@W136TO@": s78(back_map["@W136TO@"]),
    "@OWNCHAIN@": back_map["@OWNCHAIN@"].replace(
        "/W176 最近自有波", "/W176/W177 最近自有波"),
    "@W2TO@": s78(back_map["@W2TO@"]),
    "@W1TO@": s78(back_map["@W1TO@"]),
    "@PRC@": s78(back_map["@PRC@"]),
    "@PF@": s78(back_map["@PF@"]),
    "@B@": s78(back_map["@B@"]),
    "@WPN2@": s78(back_map["@WPN2@"]),
    "@WN@": s78(back_map["@WN@"]),
    "@W@": s78(back_map["@W@"]),
    "@SD@": s78(back_map["@SD@"]),
    "@KOLD@": s78(back_map["@KOLD@"]),
    "@N171@": "178",
    "@N170@": "177",
    "@N169@": "176",
}
missing = [t for (t, _v) in BACK177 if t not in BACK78]
assert not missing, missing

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK78["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（406_403+1）" in chk and "THIRTY-EIGHTH（第三十八例）" in chk, chk[:200]
chk = BACK78["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "本波 A 窗 " + A_BAND + " 内" in chk and "（408_403+1）" in chk, chk[:200]
chk = BACK78["@ANCHOR@"]
assert "W1..W177 N1 finalize 已全部落地" in chk and "795,305" in chk \
    and "dead-tail 收养窗" in chk and "K=387,320" in chk, chk[:200]
assert BACK78["@POOL@"] == "累计 null 池=387,320+2,200（本波）=**389,520 投影**", BACK78["@POOL@"]
assert "**1.1847**" in BACK78["@KLKEY@"] and "n_eff 793,105" in BACK78["@KLKEY@"], BACK78["@KLKEY@"]
assert BACK78["@WAVEFREE@"] == "波号 178=注册表 W177 行后首个自由号", BACK78["@WAVEFREE@"]
assert "n1_w178_results.json" in BACK78["@FN@"] and "n1_w177_results.json" in BACK78["@ODOLD@"]
assert BACK78["@WAVECLI@"] == "--wave 178/finalize --wave 178", BACK78["@WAVECLI@"]
assert "W179+ 投影" in BACK78["@S55@"] and "408_404..410_403" in BACK78["@S55@"]
assert "5b9284c79" in BACK78["@SEATPUB@"] and "r845 seat push" in BACK78["@SEATPUB@"]
assert "第 168 波" in BACK78["@ORDINALS@"] and "W176/W177 最近自有波" in BACK78["@ORDINALS@"]
print("S78 spot-checks: PASS (11 composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK178 = [(val, tok) for (tok, val) in BACK177]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK178:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, "DRY TOK %s: count=%d expect=%d: %r" % (tok, n, exp, old[:70])
    out_t = out_t.replace(old, tok)
for tok, new in [(t, BACK78[t]) for (t, _v) in BACK177]:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, "DRY unsubstituted tokens remain: %r" % (resid[:5],)
bad = [mm.group() for mm in re.finditer(r"(\d{3})_(\d{3})\.\.(\d{3})_(\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, "DRY malformed windows: %r" % (bad[:4],)
stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))
assert stale_wave == ["波号 178"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w177", "n1_w178"], "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W178") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W178 freeze" not in out_t.replace("；W177=bm-a r843 freeze", ""), \
    "unexpected W178-freeze text"
# stale-session sweep: no W177-era session stamps may survive (note:
# "r841 probe leg4" is the LEGAL new citation -- the W177 probe leg4 that
# anticipated the W178 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r841 probe 回执", "（r841 probe leg2", "r832 probe", "r834 冻结件",
              "（r839 one-pass 窗", "780a0cd30", "【r842】", "THIRTY-SEVENTH",
              "第三十七例", "0.3118", "0.245060", "−0.0889"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r841 probe leg4" in out_t, "new W177-probe-leg4 citation missing"
print("DRY GATE PASS: all %d TOK counts, residue-zero, malformed-window CLEAN, "
      "r754 two-form CLEAN, stale-session sweep CLEAN" % len(TOK178))

# --- 5. emit the W178 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r845 bm-a W178 per-wave prereg build: transforms the freeze-time W177
prereg (git blob c06cc230f:research/PERPETUAL_N1_W177_PREREG.md, extracted
byte-verbatim to results/_r845bma_w178_prereg_src.txt) into
research/PERPETUAL_N1_W178_PREREG.md.

Generated by results/_r845bma_w178_buildgen.py (TOK/BACK pairs AST-extracted
from the r842 build script -- no exec of its time-locked live asserts;
r773 compliance inherited: token-first two-phase vmap, whole-string
composites, numerals LAST; r735 substring-order law = BACK list order
preserved).  r587 machine-derived facts (read from on-disk receipts):
r844 probe ADMIT A 406_404..408_403 staircase 38th E36 / B 408_404..408_603;
W177 finalize r844 dead-tail adopted (K 387,320 / head 795,305 / skill_line
1.1847); W177 sec7/sec8 backfill landed r845 window; W177 freeze c06cc230f;
W178 seat push 5b9284c79; seat self-ack processed/ on origin.

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess

SRC = r"results\\_r845bma_w178_prereg_src.txt"
OUT = r"research\\PERPETUAL_N1_W178_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r844bma_w178_probe_receipt.json", encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "406404_408403", "B": "408404_408603"}, probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], probe["legs"]["leg4"]
assert leg1["A"] == [406404, 408403] and leg1["B"] == [408404, 408603], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [406204, 408203], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [406404, 406603], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [406404, 406603], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 408404, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 175 and leg0["tail"] == "W177" and leg0["ordinal"] == 168 \\
    and leg0["bma_ordinal"] == 94 and leg0["owner_rows"] == 167 \\
    and leg0["bma_rows"] == 93 and leg0["w177_ledger_head"] == 795305, leg0
assert leg4["W179p_A"] == "408404..410403" and leg4["W179p_B"] == "408604..408803", leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W179p_B_lands_inside_W179p_A"] is True, leg4
assert "THIRTY-EIGHTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w177_results.json", encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 387320, "W177 merged K drift"
assert npc["pre_w177_cumulative"]["n_values"] == 385120, "pre-W177 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_387320"] == 1.1847 and kl["line_pre_w177"] == 1.1846 \\
    and kl["line_delta_k_lift"] == 0.0001 and kl["n_eff_held_equal"] == 793105, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k387320"] == 0.000394, "se_mu drift"
assert abs(npc["mu_delta_w177_vs_w176ext"] - (-0.004716)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3116, "p95 drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w177_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0927" and WONLY4 == "-0.0936" and SIG6 == "0.245080", (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w177_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "795,305" and KNEW == "387,320", (LEDG, KNEW)
KPROJ = "{:,}".format(387320 + 2200)
LEDGPROJ = "{:,}".format(795305 + 2200)
assert KPROJ == "389,520" and LEDGPROJ == "797,505", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W177 FREEZE", "-1"], capture_output=True, text=True)
W177_SHA = _r.stdout.strip()
assert W177_SHA == "c06cc230f", W177_SHA
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-07-2157-bma-w178-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "5b9284c79", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/MSG-2026-10-07-2157-bma-w178-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W178 seat MSG not on origin (r565 pre-freeze law)"
assert "406_404..408_403" in _r3.stdout.decode("utf-8", "replace"), "seat band face drift"
# W177 sec7/sec8 backfill landed r845 window -- the anchor face cites it
w177p = io.open(r"research\\PERPETUAL_N1_W177_PREREG.md", encoding="utf-8", newline="").read()
assert "mu_delta_w177_vs_w176ext" in w177p and "已回填 r845 窗" in w177p, \\
    "W177 sec7/sec8 backfill missing (anchor-face citation would be false)"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
'''

TAIL = '''
TOK178 = %s
BACK178 = %s

EXPECT = %s

out_t = src
for old, tok in TOK178:
    n = out_t.count(old)
    exp = EXPECT[tok]
    assert n == exp, f"TOK {tok}: count={n} expect={exp}: {old[:70]!r}"
    out_t = out_t.replace(old, tok)
for tok, new in BACK178:
    out_t = out_t.replace(tok, new)
resid = re.findall(r"@[A-Z0-9]+@", out_t)
assert not resid, f"unsubstituted tokens remain: {resid[:5]}"

# r773 leg-3 malformed-window scan (start>end dotted windows)
bad = [mm.group() for mm in re.finditer(r"(\\d{3})_(\\d{3})\\.\\.(\\d{3})_(\\d{3})", out_t)
       if int(mm.group(3)) < int(mm.group(1))]
assert not bad, f"malformed windows: {bad[:4]}"

# r754 two-form stale-face checklist (bare wave numbers + lowercase n1_w1xx)
stale_wave = sorted(set(re.findall(r"波号 17[0-9]", out_t)))
assert stale_wave == ["波号 178"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w177", "n1_w178"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W178") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W178 freeze" not in out_t.replace("；W177=bm-a r843 freeze", ""), \\
    "unexpected W178-freeze text"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W178 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, r754 two-form CLEAN)")
'''

tok_lit = repr(TOK178)
back_lit = repr([(t, BACK78[t]) for (t, _v) in BACK177])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results\_r845bma_w178_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r845bma_w178_prereg_build.py", len(out), "bytes")
