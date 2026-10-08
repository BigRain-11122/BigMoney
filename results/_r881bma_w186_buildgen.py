# -*- coding: utf-8 -*-
"""r881 bm-a generator: builds results/_r881bma_w186_prereg_build.py by
AST-extracting the r877 build script's BACK185/EXPECT pairs (all values
machine-read, zero exec of its live asserts), then deriving the BACK186
pairs as (token, rolled W186 value).  Old side = the W185-era value
(freeze-time blob d431b448a5 at prereg-freeze commit ad4eded99,
byte-identical to registry-freeze commit beb4b5abd; extracted
byte-verbatim to results/_r881bma_w186_prereg_src.txt this window),
new side = the S83' W186 fact map applied to that W185 text.
r773/r775/r781/r830/r833 compliance inherited: token-first two-phase
vmap, whole-string composites, numerals LAST; r735 substring-order
law = BACK list order preserved (projections consumed before the naive
rolls re-create them; own-B before prior-B; LEDG head before NEFF
re-creates it; pool projection composite before the bare K roll);
pre-TOK sequential DRY below (r833 law 2, zero writes until all green).

TWO-FACE src disclosure (this window's finding, supersedes the r880
facts extract face):
  * results/_r880bma_w186_prereg_src.txt (24,653B, sha256 548a91ab...)
    = the POST-§7/§8-backfill FINAL face (origin blob cae3cdcc, r879
    backfill landed) -- NOT usable as build src: the §7/§8 regions are
    un-tokenized and would ride verbatim, leaking W185's finalize
    actuals into the W186 pre-registration.
  * results/_r881bma_w186_prereg_src.txt (21,459B, this extract) = the
    freeze-time PRE-backfill face (blob d431b448a5 at ad4eded99 ==
    beb4b5abd), §7/§8 as placeholders -- the r876/r877 bloodline src
    law (W184 build consumed freeze-time blob a9925eac6a at f908433c4
    the same way).

Structural notes vs the r877 bloodline (disclosed):
  * @S55@/@SEATPUB@/@SEATSENT@ are s83-ROLLED this wave (all their
    constituents map-covered: proj bands, own-B, cascade, MSG/sha,
    session composites);
  * @N171@/@N170@/@N169@ vestigial tokens (EXPECT=0 both generations):
    phase 1 skips them with a stray-check (legal bare-183 strays = the
    two fixed historical "MSG-183x" references, riding verbatim);
  * self-ack archive face re-derived this wave: the W186 seat MSG
    self-ack inbox->processed move landed the bm-a r880 window ITSELF
    (4c0cfabc3 closeout, same-window as the seat push dd362c690 --
    unlike W185's r875 push / r876 self-move two-window pattern) --
    dedicated pair "bm-a r876 窗自移" -> "bm-a r880 窗自移", disclosed;
  * r841 stale-stamp honesty fix (disclosed): @SEATSENT@'s
    "本机 r841 席位" + "（r841 seat push·r565 律）" were W176-era ridden
    stamps (9 generations; the r877 bloodline rode them undisclosed) --
    this wave fixed to r880 via dedicated pairs (the W186 seat WAS
    pushed r880);
  * the anchor procrastination-precedent list "W159/W168/W169/W181"
    rides FIXED (no new procrastination case in W185 -- sec7/sec8
    landed r879 same-window-as-finalize, adopted-window disclosed in
    the stamp itself);
  * cascade span extended to 7 pairs (W186->W187 down to W180->W181):
    the low end is anchored by the W-list compensation pair (r877
    mechanism: long-form new side writes W180, cascade W180->W181
    restores W181);
  * @KLT@ K-lift chain and @SEMT@ se_mu chain ride via dedicated r1
    appends (W185: K-lift −0.0001 first negative after the W181..W184
    four-flat / se_mu 0.000385); historical labels W161..W184 stay
    fixed;
  * merged-mu 4dp ROLLS this wave (−0.0928 -> −0.0929, first display
    roll since W181; r833 law 3 U+2212 display form held).

r587 machine-derived facts (every displayed value read from on-disk
receipts / git history this window):
  - pre-seat probe results/_r880bma_w186_probe_receipt.json rc0 ADMIT
    (leg0 registry 183 rows tail W185 ordinal 176 / bma_ordinal 102 /
    owner_rows 175 / bma_rows 101 / w185_ledger_head 814,328; leg1
    naive A 423_804..425_803 REFUSED at its own start by the registered
    W185 B band 423_804..424_003 -> honest forward walk 1 hop lands
    A 424_004..426_003 (staircase FORTY-SIXTH instance E36 per receipt
    A_semantics; the W185 seat leg4 + r875 probe leg4 + W185 prereg
    succession notes anticipated and MANDATED this re-derive --
    projection and receipt ordinals MATCH, no divergence face); naive B
    424_004..424_203 lands inside own-wave A 424_004..426_003 ->
    same-freeze mutual exclusion (W141 precedent leg2 law) -> reserved
    walk 1 hop lands B 426_004..426_203; leg2 conflicts 0; leg3 origin
    vacancy True at probe time (seat MSG published same window, r565
    law held); leg4 W187+ projection A 426_004..428_003 hops=0 /
    B 426_204..426_403 hops=0, B inside A);
  - W185 finalize landed r879 adopted-window (b387a9938, dead-session
    adoption r844-law family; ledger head 812,128 + 2,200 = 814,328
    EXACT zero-delta vs frozen projection; merged K=404,920 EXACT;
    merged mu -0.09285237 4dp -0.0929 (display ROLLS this wave);
    w185-only mu -0.09921359 4dp -0.0992; sigma 0.24509000 6dp
    0.245090; se_mu_at_k404920 = 0.000385; skill_line line_pre_w185
    1.1858 -> line_merged@404,920 1.1857 (K-lift -0.0001, n_eff held
    812,128); A p95 = 0.3066); W185 sec7/sec8 settle backfill landed
    the r879 SAME window as the finalize (adopted-window note in the
    §7 header itself; on-disk W185 prereg text "814,328" + "K=404,920"
    live-asserted below);
  - W185 freeze registered sha machine-derived = beb4b5abd (git log
    origin/main --grep "W185 FREEZE"); W185 prereg freeze ad4eded99
    (r877 window, blob d431b448a5 at both freeze commits, asserted
    live below); W186 seat push sha machine-derived = dd362c690 (git
    log --diff-filter=A on the seat MSG inbox path, r880 window);
    W186 seat self-ack archive move landed the bm-a r880 window
    (4c0cfabc3 closeout, self-move; processed/ path on origin
    live-verified below).
"""
import ast
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- 0. verify the freeze-time W185 prereg blob (LF, byte-verbatim) ----------
_r = subprocess.run(
    ["git", "rev-parse", "ad4eded99:research/PERPETUAL_N1_W185_PREREG.md"],
    capture_output=True, text=True)
BLOB_SHA = _r.stdout.strip()
assert BLOB_SHA == "d431b448a5b1879429f5569a5e92df94858476c5", BLOB_SHA
_r2 = subprocess.run(
    ["git", "rev-parse", "beb4b5abd:research/PERPETUAL_N1_W185_PREREG.md"],
    capture_output=True, text=True)
assert _r2.stdout.strip() == BLOB_SHA, "prereg-freeze != registry-freeze blob"
blob = subprocess.run(
    ["git", "show", "ad4eded99:research/PERPETUAL_N1_W185_PREREG.md"],
    capture_output=True).stdout
assert b"\r\n" not in blob, "blob expected LF (git convention)"
assert len(blob) == 21459, len(blob)
open(r"results/_r881bma_w186_prereg_src.txt", "wb").write(blob)
ondisk = open(r"results/_r881bma_w186_prereg_src.txt", "rb").read()
assert ondisk == blob, "on-disk src re-write drift"
# two-face disclosure: the r880 facts extract = post-backfill FINAL face
import hashlib
_r880face = open(r"results/_r880bma_w186_prereg_src.txt", "rb").read()
assert hashlib.sha256(_r880face).hexdigest() == \
    "548a91ab9a3e32d52deba23e2437404e8431bf5ac89bdf6d8ae681b8e3241e32"
assert len(_r880face) == 24653 and _r880face != blob
_w185_final = subprocess.run(
    ["git", "show", "origin/main:research/PERPETUAL_N1_W185_PREREG.md"],
    capture_output=True).stdout
assert _r880face == _w185_final, "r880 face != current origin blob"
print("W186 src verified (freeze face):", len(blob), "bytes (blob",
      BLOB_SHA[:10] + "); r880 facts face = post-backfill FINAL (",
      len(_r880face), "bytes), disclosed two-face, build consumes freeze face")

# --- 1. AST-extract the r877 build script's BACK185 + EXPECT ---------------
src877 = io.open(r"results/_r877bma_w185_prereg_build.py",
                 encoding="utf-8").read()
tree = ast.parse(src877)


def ev(n):
    if isinstance(n, ast.Constant):
        return n.value
    raise AssertionError("unsupported node %r" % (ast.dump(n)[:80],))


BACK185 = None
EXPECT = None
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        tg = node.targets[0]
        if isinstance(tg, ast.Name) and tg.id == "BACK185" and \
           isinstance(node.value, ast.List):
            BACK185 = []
            for p in node.value.elts:
                assert isinstance(p, ast.Tuple) and len(p.elts) == 2, "pair shape"
                BACK185.append((ev(p.elts[0]), ev(p.elts[1])))
        if isinstance(tg, ast.Name) and tg.id == "EXPECT" and \
           isinstance(node.value, ast.Dict):
            EXPECT = {}
            for k, v in zip(node.value.keys, node.value.values):
                EXPECT[ev(k)] = ev(v)
assert BACK185 is not None and EXPECT is not None, "BACK185/EXPECT not extracted"
assert len(BACK185) == 50 and len(EXPECT) == 50, (len(BACK185), len(EXPECT))
back185_map = dict(BACK185)
assert len(back185_map) == len(BACK185)
print("r877 BACK185 entries:", len(BACK185), "EXPECT entries:", len(EXPECT))

# --- 2. W186 facts (machine-read this window) -------------------------------
probe = json.load(open(r"results/_r880bma_w186_probe_receipt.json",
                       encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "424004_426003", "B": "426004_426203"}, \
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \
    probe["legs"]["leg4"]
assert leg1["A"] == [424004, 426003] and leg1["B"] == [426004, 426203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [423804, 425803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [424004, 424203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [424004, 424203], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 426004, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 183 and leg0["tail"] == "W185" and \
    leg0["ordinal"] == 176 and leg0["bma_ordinal"] == 102 and \
    leg0["owner_rows"] == 175 and leg0["bma_rows"] == 101 and \
    leg0["w185_ledger_head"] == 814328, leg0
assert leg4["W187p_A"] in ("426004..428003", "426_004..428_003") and \
    leg4["W187p_B"] in ("426204..426403", "426_204..426_403"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W187p_B_lands_inside_W187p_A"] is True, leg4
assert "FORTY-SIXTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w185_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 404920, "W185 merged K drift"
assert npc["pre_w185_cumulative"]["n_values"] == 402720, "pre-W185 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_404920"] == 1.1857 and kl["line_pre_w185"] == 1.1858 \
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 812128, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k404920"] == 0.000385, "se_mu drift"
assert abs(npc["mu_delta_w185_vs_w184ext"] - (-0.005922)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3066, \
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 814328 and \
    res["science_gates"]["ledger"]["prev_total"] == 812128, \
    res["science_gates"]["ledger"]
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w185_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
LINE4 = "%.4f" % kl["line_merged_404920"]
PRE4 = "%.4f" % kl["line_pre_w185"]
SEM4 = "%.6f" % npc["se_mu_at_k404920"]
P954 = "%.4f" % res["families"]["A_random_engine_exit"]["full_sharpe_p95"]
DELTA4 = "%.4f" % abs(kl["line_delta_k_lift"])
DSIGN = "+" if kl["line_delta_k_lift"] >= 0 else "\u2212"
assert MU4 == "-0.0929" and WONLY4 == "-0.0992" and SIG6 == "0.245090", \
    (MU4, WONLY4, SIG6)
assert LINE4 == "1.1857" and PRE4 == "1.1858" and SEM4 == "0.000385" \
    and P954 == "0.3066" and DELTA4 == "0.0001" and DSIGN == "\u2212", \
    (LINE4, PRE4, SEM4, P954, DELTA4, DSIGN)
MU_U = MU4.replace("-", "\u2212")      # display form U+2212 (r833 law 3)
WONLY_U = WONLY4.replace("-", "\u2212")
assert MU_U == "\u22120.0929" and WONLY_U == "\u22120.0992", (MU_U, WONLY_U)
LEDG = "{:,}".format(leg0["w185_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
NEFF = "{:,}".format(kl["n_eff_held_equal"])
assert LEDG == "814,328" and KNEW == "404,920" and NEFF == "812,128", \
    (LEDG, KNEW, NEFF)
KPROJ = "{:,}".format(404920 + 2200)
LEDGPROJ = "{:,}".format(814328 + 2200)
assert KPROJ == "407,120" and LEDGPROJ == "816,528", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r_ = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W185 FREEZE", "-1"], capture_output=True,
                     text=True)
W185_SHA = _r_.stdout.strip()
assert W185_SHA == "beb4b5abd", W185_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                      "--grep=W186 FREEZE", "-1"], capture_output=True,
                     text=True)
assert _r0.stdout.strip() == "", "origin already carries a W186 FREEZE (r511)"
_r2s = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                       "--diff-filter=A",
                       "--", "fleet/inbox/MSG-2026-10-08-1354-bma-w186-seat.md"],
                      capture_output=True, text=True)
SEAT_SHA = _r2s.stdout.strip()
assert SEAT_SHA == "dd362c690", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                      "origin/main:fleet/inbox/processed/"
                      "MSG-2026-10-08-1354-bma-w186-seat.md"],
                     capture_output=True)
assert _r3.returncode == 0, "W186 seat MSG not on origin processed/ (r565 law)"
_seat_txt = _r3.stdout.decode("utf-8", "replace")
assert "424_004..426_003" in _seat_txt and "426_004..426_203" in _seat_txt, \
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                      "ad4eded99:research/PERPETUAL_N1_W185_PREREG.md"],
                     capture_output=True, text=True)
assert _r4.stdout.strip() == "d431b448a5b1879429f5569a5e92df94858476c5", \
    "src blob drift: %s" % _r4.stdout.strip()
# W185 sec7/sec8 settle backfill landed the r879 adopted-window (same
# window as the finalize) -- the anchor face cites it (adopted-window
# disclosure lives in the W185 prereg's own sec7 header)
w185p = io.open(r"research/PERPETUAL_N1_W185_PREREG.md", encoding="utf-8",
                newline="").read()
assert "814,328" in w185p and "K=404,920" in w185p, \
    "W185 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r879 收养窗" in w185p, "W185 sec7 adopted-window note missing"

A_BAND = "424_004..426_003"
B_BAND = "426_004..426_203"
NAIVE_A = "423_804..425_803"
NAIVE_B = "424_004..424_203"
PRIOR_B = "423_804..424_003"     # registered W185 B band (refusal band)
A_SEED, B_SEED = "424_004", "426_004"
SEAT_MSG = "MSG-2026-10-08-1354-bma-w186-seat"
W187p_A = "426_004..428_003"
W187p_B = "426_204..426_403"

# --- 3. S83' = W185->W186 ordered fact map -----------------------------------
# (r735 substring-order law preserved from the r877 bloodline: projections
#  consumed before the naive rolls re-create them; own-B before prior-B;
#  pool projection composite before the bare K roll; LEDG head before NEFF;
#  high ordinals before low; cascade high first; bare numerals LAST.)
S83 = [
    # -- window/session composites (longest first) --
    ("已回填（r875 同窗·无漏补·r864 教训兑现·W159/W168/W169/W181 拖延窗先例对照·如实注记）",
     "已回填（r879 收养窗·无漏补·r864 教训兑现·W159/W168/W169/W180 拖延窗先例对照·如实注记）"),
    ("已回填（r875 同窗）", "已回填（r879 同窗）"),
    ("r875 bm-a 带闸窗（pre-seat probe r875 单窗", "r880 bm-a 带闸窗（pre-seat probe r880 单窗"),
    ("（r875 承袭", "（r880 承袭"),
    ("r875 probe 单跑兑现注记", "r880 probe 单跑兑现注记"),
    ("（r875 probe leg2/leg3 实跑）", "（r880 probe leg2/leg3 实跑）"),
    ("r875 probe 回执 A_semantics 机读序数=FORTY-FIFTH",
     "r880 probe 回执 A_semantics 机读序数=FORTY-SIXTH"),
    ("FORTY-FIFTH（第四十五例）", "FORTY-SIXTH（第四十六例）"),
    ("r870 probe leg4", "r875 probe leg4"),
    ("（r872 冻结件）", "（r877 冻结件）"),
    ("_r875bma_w185_probe_receipt.json", "_r880bma_w186_probe_receipt.json"),
    ("MSG-2026-10-08-1032-bma-w185-seat", "MSG-2026-10-08-1354-bma-w186-seat"),
    ("304909e0e", "dd362c690"),
    ("【r875】", "【r880】"),
    ("r875 seat push", "r880 seat push"),
    ("自 r875 收口", "自 r880 收口"),
    ("bm-a r876 窗自移·如实注记", "bm-a r880 窗自移·如实注记"),
    ("本机 r841 席位", "本机 r880 席位"),
    ("（r841 seat push·r565 律）", "（r880 seat push·r565 律）"),
    # -- band geometry (r735 order law: proj-A/proj-B consumed before the
    #    naive rolls re-create them; own-B consumed before prior-B) --
    ("423_804..425_803", "426_004..428_003"),      # proj-A (W187+)
    ("424_004..424_203", "426_204..426_403"),      # proj-B (W187+)
    ("423_804..424_003", "426_004..426_203"),      # own-B (W186 B)
    ("421_804..423_803", "424_004..426_003"),      # own-A (W186 A)
    ("421_604..421_803", "423_804..424_003"),      # prior-B (W185 B)
    ("421_604..423_603", "423_804..425_803"),      # naive-A window (W186)
    ("421_804..422_003", "424_004..424_203"),      # naive-B window (W186)
    ("421_803+1", "424_003+1"),
    ("423_803+1", "426_003+1"),
    ("421_804+j", "424_004+j"),
    ("423_804+j", "426_004+j"),
    # -- ordinals (high first: projection pair before own pair) --
    ("第四十七例", "第四十八例"),
    ("第四十六例", "第四十七例"),
    ("第四十五例", "第四十六例"),
    ("第 183 枚", "第 184 枚"),
    ("行 174+本候选", "行 175+本候选"),
    ("第一百零一枚", "第一百零二枚"),
    ("第 175 波", "第 176 波"),
    ("行 100+本候选", "行 101+本候选"),
    ("bm-a 100 行注册", "bm-a 101 行注册"),
    ("一百八十二行注册", "一百八十三行注册"),
    ("机证 182 行", "机证 183 行"),
    ("一百八十三面实测", "一百八十四面实测"),
    # -- n1_w forms (high first) --
    ("n1_w185", "n1_w186"),
    ("n1_w184", "n1_w185"),
    # -- wave-word cascade (high first; 7 pairs this wave -- the low end
    #    W180->W181 is anchored by the W-list compensation pair above) --
    ("W186", "W187"),
    ("W185", "W186"),
    ("W184", "W185"),
    ("W183", "W184"),
    ("W182", "W183"),
    ("W181", "W182"),
    ("W180", "W181"),
    # -- bare-number leftovers --
    ("波号 185=", "波号 186="),
    ("--wave 185", "--wave 186"),
    # -- numbers (pool projection composite first; head LEDG consumed
    #    before NEFF re-creates it; merged-mu 4dp ROLLS this wave
    #    -0.0928 -> -0.0929; w-only mu rolls -0.0933 -> -0.0992) --
    ("**404,920 投影**", "**" + KPROJ + " 投影**"),
    ("**1.1857**", "**" + LINE4 + "**"),
    ("·line_pre 1.1857·", "·line_pre " + PRE4 + "·"),
    ("**0.3194**", "**" + P954 + "**"),
    ("**\u22120.0928**", "**" + MU_U + "**"),
    ("**\u22120.0933**", "**" + WONLY_U + "**"),
    ("**+0.0000**", "**" + DSIGN + DELTA4 + "**"),
    ("0.245094", SIG6),
    ("812,128", LEDG),
    ("809,928", NEFF),
    ("402,720", KNEW),
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
BACK186 = {
    "@CHAIN@": back185_map["@CHAIN@"] + "；W185=bm-a r878 freeze（" + W185_SHA + "）",
    "@KLT@": r1(back185_map["@KLT@"], " 如实披露",
                "/W185 **" + DSIGN + DELTA4 + "** 如实披露"),
    "@SEMT@": r1(back185_map["@SEMT@"], "**0.000386**】）",
                 "**0.000386**→W185 **" + SEM4 + "**】）"),
    "@S55@": s83(back185_map["@S55@"]),
    "@SEATPUB@": s83(back185_map["@SEATPUB@"]),
    "@ORDINALS@": (
        r1(r1(r1(r1(r1(r1(r1(back185_map["@ORDINALS@"],
            "第 175 波", "第 176 波"),
            "第一百零一枚", "第一百零二枚"),
            "行 100+本候选", "行 101+本候选"),
            "/W183/W184 最近自有波", "/W184/W185 最近自有波"),
            "注册表 W184 行后", "注册表 W185 行后"),
            "MSG-2026-10-08-1032-bma-w185-seat", SEAT_MSG),
            "304909e0e", SEAT_SHA)
    ),
    "@OWNCHAIN@": r1(back185_map["@OWNCHAIN@"],
                     "/W183/W184 最近自有波", "/W184/W185 最近自有波"),
    "@N171@": "186",
    "@N170@": "185",
    "@N169@": "184",
}
for tok in ("@TITLE@", "@WAVEFREE@", "@VAC@", "@MERGE@", "@AFACE@", "@BFACE@",
            "@R250@", "@SCANFACE@", "@ANCHOR@", "@POOL@", "@SEATSENT@",
            "@CLAIMLAW@", "@V2W@", "@ASEED@", "@ASEEDPROSE@", "@BENTRY@",
            "@BSEEDPROSE@", "@GATEW@", "@FN@", "@RFN@", "@ODOLD@",
            "@S5ANCH@", "@S51@", "@S51B@", "@S52@", "@S53@", "@KLKEY@",
            "@WAVECLI@", "@EOB@", "@W136TO@", "@W2TO@", "@W1TO@", "@PRC@",
            "@PF@", "@B@", "@WPN2@", "@WN@", "@W@", "@SD@", "@KOLD@"):
    BACK186[tok] = s83(back185_map[tok])
missing = [t for (t, _v) in BACK185 if t not in BACK186]
assert not missing, missing
extra = [t for t in BACK186 if t not in back185_map]
assert not extra, extra

# spot-check the rolled faces before the DRY (fail loud, zero writes)
chk = BACK186["@AFACE@"]
assert "A-ext seed=" + A_BAND in chk and PRIOR_B + " **拒**" in chk \
    and "（424_003+1）" in chk and "FORTY-SIXTH（第四十六例）" in chk, chk[:250]
chk = BACK186["@BFACE@"]
assert "B-ext exit seed=" + B_BAND in chk and NAIVE_B in chk \
    and "A 窗 " + A_BAND in chk and "（426_003+1）" in chk, chk[:250]
chk = BACK186["@ANCHOR@"]
assert "W1..W185 N1 finalize 已全部落地" in chk and "**814,328**" in chk \
    and "K=404,920 合并池" in chk and "r844 dead-tail 收养窗" in chk \
    and "已回填（r879 收养窗·无漏补·r864 教训兑现" in chk, chk[:250]
assert BACK186["@POOL@"] == "累计 null 池=" + KNEW + "+2,200（本波）=**" + KPROJ + \
    " 投影**", BACK186["@POOL@"]
assert "**" + LINE4 + "**" in BACK186["@KLKEY@"] and "n_eff " + NEFF in \
    BACK186["@KLKEY@"], BACK186["@KLKEY@"]
assert "line_pre " + PRE4 in BACK186["@KLKEY@"], BACK186["@KLKEY@"]
assert "**" + DSIGN + DELTA4 + "**" in BACK186["@KLKEY@"], BACK186["@KLKEY@"]
assert BACK186["@WAVEFREE@"] == "波号 186=注册表 W185 行后首个自由号", \
    BACK186["@WAVEFREE@"]
assert "n1_w186_results.json" in BACK186["@FN@"] and \
    "n1_w185_results.json" in BACK186["@ODOLD@"]
assert BACK186["@WAVECLI@"] == "--wave 186/finalize --wave 186", \
    BACK186["@WAVECLI@"]
assert "W187+ 投影" in BACK186["@S55@"] and W187p_A in BACK186["@S55@"] \
    and W187p_B in BACK186["@S55@"] and "继承第四十七例" in BACK186["@S55@"] \
    and "W186 B 带 " + B_BAND in BACK186["@S55@"], BACK186["@S55@"][:200]
assert "verify at W187 prereg" in BACK186["@S55@"], BACK186["@S55@"][-120:]
assert SEAT_SHA in BACK186["@SEATPUB@"] and "r880 seat push" in \
    BACK186["@SEATPUB@"] and "自 r880 收口" in BACK186["@SEATPUB@"] \
    and "bm-a r880 窗自移" in BACK186["@SEATPUB@"], BACK186["@SEATPUB@"][:200]
assert "第 176 波" in BACK186["@ORDINALS@"] and "第一百零二枚" in \
    BACK186["@ORDINALS@"] and "/W184/W185 最近自有波" in BACK186["@ORDINALS@"] \
    and "注册表 W185 行后" in BACK186["@ORDINALS@"], BACK186["@ORDINALS@"][:200]
assert "W187+ 投影" in BACK186["@SEATSENT@"] and SEAT_MSG in \
    BACK186["@SEATSENT@"] and "继承第四十七例" in BACK186["@SEATSENT@"], \
    BACK186["@SEATSENT@"][:200]
assert "本机 r880 席位" in BACK186["@SEATSENT@"] and \
    "（r880 seat push·r565 律）" in BACK186["@SEATSENT@"], \
    BACK186["@SEATSENT@"][:200]
assert "法典 §4 W186 行 A=" + A_BAND in BACK186["@ASEEDPROSE@"], \
    BACK186["@ASEEDPROSE@"][:250]
assert "法典 §4 W186 行 B=" + B_BAND in BACK186["@BSEEDPROSE@"], \
    BACK186["@BSEEDPROSE@"][:250]
assert "净账本锚头 " + LEDG in BACK186["@S5ANCH@"] and "r839 承袭收口窗" in \
    BACK186["@S5ANCH@"] and "已回填（r879 同窗）" in BACK186["@S5ANCH@"], \
    BACK186["@S5ANCH@"]
assert "K=" + KNEW + " 合并池" in BACK186["@S51@"] and \
    "**" + WONLY_U + "**" in BACK186["@S51@"], BACK186["@S51@"]
assert "**" + MU_U + "**" in BACK186["@S51@"], BACK186["@S51@"]
assert "**" + SIG6 + "**" in BACK186["@S52@"], BACK186["@S52@"]
assert "**" + P954 + "**" in BACK186["@S53@"], BACK186["@S53@"]
assert "一百八十三行注册" in BACK186["@SCANFACE@"] and "表尾 W185 行" in \
    BACK186["@SCANFACE@"] and "机证 183 行" in BACK186["@SCANFACE@"], \
    BACK186["@SCANFACE@"]
assert BACK186["@EOB@"] == "engine_owner==bm-a 101 行注册", BACK186["@EOB@"]
assert "PERPETUAL-N1-W186" in BACK186["@TITLE@"] and "第 184 枚" in \
    BACK186["@TITLE@"] and "【r880】" in BACK186["@TITLE@"], BACK186["@TITLE@"]
assert "r880 bm-a 带闸窗（pre-seat probe r880 单窗" in BACK186["@GATEW@"], \
    BACK186["@GATEW@"]
assert BACK186["@VAC@"] == "（r880 probe leg2/leg3 实跑）", BACK186["@VAC@"]
assert "（r880 承袭" in BACK186["@MERGE@"], BACK186["@MERGE@"]
assert "r880 probe 单跑兑现注记" in BACK186["@CLAIMLAW@"], \
    BACK186["@CLAIMLAW@"]
assert BACK186["@PRC@"] == "results/_r880bma_w186_probe_receipt.json", \
    BACK186["@PRC@"]
assert "W185=bm-a r878 freeze（" + W185_SHA + "）" in BACK186["@CHAIN@"]
assert BACK186["@SEMT@"].endswith("→W185 **" + SEM4 + "**】）"), \
    BACK186["@SEMT@"][-60:]
assert BACK186["@KLT@"].endswith("/W185 **" + DSIGN + DELTA4 + "** 如实披露"), \
    BACK186["@KLT@"][-60:]
assert BACK186["@OWNCHAIN@"].endswith("/W184/W185 最近自有波"), \
    BACK186["@OWNCHAIN@"][-40:]
assert BACK186["@WPN2@"] == "W187+ 投影", BACK186["@WPN2@"]
assert BACK186["@W136TO@"] == "W136..W185", BACK186["@W136TO@"]
assert BACK186["@W2TO@"] == "W2..W185" and BACK186["@W1TO@"] == "W1..W185" \
    and BACK186["@V2W@"] == "v2..W185 落地", (BACK186["@W2TO@"],
                                              BACK186["@W1TO@"],
                                              BACK186["@V2W@"])
assert BACK186["@WN@"] == "W186" and BACK186["@W@"] == "W185" and \
    BACK186["@SD@"] == "n1_w186" and BACK186["@KOLD@"] == KNEW, \
    (BACK186["@WN@"], BACK186["@W@"], BACK186["@SD@"], BACK186["@KOLD@"])
assert BACK186["@ASEED@"] == "entry rng seed=**424_004+j**", BACK186["@ASEED@"]
assert "entry rng=**424_004+j**" in BACK186["@BENTRY@"], BACK186["@BENTRY@"]
assert BACK186["@PF@"] == "PERPETUAL_N1_W186_PREREG.md", BACK186["@PF@"]
assert BACK186["@R250@"] == "R250：W186 带从未指派·测量面零结果可锁", \
    BACK186["@R250@"]
assert BACK186["@S51B@"] == "（W2..W185 共一百八十四面实测 mu 稳定先例·单波跨键微）", \
    BACK186["@S51B@"]
print("S83' spot-checks: PASS (composite faces)")

# --- 4. DRY full-file transform gate (E41: zero writes until all green) ----
TOK186 = [(val, tok) for (tok, val) in BACK185]
src = blob.decode("utf-8")
out_t = src
for old, tok in TOK186:
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
for tok, new in [(t, BACK186[t]) for (t, _v) in BACK185]:
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
assert stale_wave == ["波号 186"], "DRY stale bare wave numbers: %r" % (stale_wave,)
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w185", "n1_w186"], \
    "DRY unexpected n1_w1xx forms: %r" % (low_forms,)
assert out_t.count("PERPETUAL-N1-W186") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W186 freeze" not in out_t.replace("；W185=bm-a r878 freeze", ""), \
    "unexpected W186-freeze text"
# stale-session sweep: no W185-era session stamps may survive ("r875 probe
# leg4" is the LEGAL new citation -- the W185 probe leg4 that anticipated
# the W186 staircase; only its 回执/leg2 faces must have rolled)
for stale in ("r875 probe 回执", "（r875 probe leg2", "r870 probe", "r872 冻结件",
              "已回填（r875", "304909e0e", "【r875】", "FORTY-FIFTH",
              "第四十五例", "0.3194", "0.245094", "\u22120.0933", "\u22120.0928",
              "402,720", "净账本锚头 812,128", "809,928", "MSG-2026-10-08-1032",
              "r875 seat push", "bm-a r876 窗自移", "本机 r841 席位",
              "（r841 seat push", "d431b448a5"):
    assert stale not in out_t, "DRY stale token survives: %r" % stale
assert "r875 probe leg4" in out_t, "new W185-probe-leg4 citation missing"
assert out_t.count("r875") == 3, "r875 residual count=%d (expect 3 = leg4 x3)" % \
    out_t.count("r875")
assert out_t.count("r870") == 0, "r870 residual count=%d (expect 0)" % \
    out_t.count("r870")
assert out_t.count("r841") == 0, "r841 residual count=%d (expect 0)" % \
    out_t.count("r841")
assert out_t.count("W186 finalize 窗") == 2 and \
    "W185 finalize 窗" not in out_t, "sec7/8 placeholder wave faces missing"
print("DRY GATE PASS: %d live TOK counts + 3 vestigial stray-checks, "
      "residue-zero, malformed-window CLEAN, two-form CLEAN, "
      "stale-session sweep CLEAN" % len(TOK186))

# --- 5. emit the W186 build script -------------------------------------------
HDR = '''# -*- coding: utf-8 -*-
"""r881 bm-a W186 per-wave prereg build: transforms the freeze-time W185
prereg (git blob d431b448a5 -- file research/PERPETUAL_N1_W185_PREREG.md
at prereg-freeze commit ad4eded99, byte-identical to registry-freeze
commit beb4b5abd; extracted byte-verbatim to
results/_r881bma_w186_prereg_src.txt, re-verified this window) into
research/PERPETUAL_N1_W186_PREREG.md.  The post-§7/§8-backfill FINAL
face (24,653B, origin blob cae3cdcc, r880 facts extract) is NOT the
build src -- §7/§8 regions are un-tokenized and would leak W185
actuals; disclosed two-face in the buildgen docstring.

Generated by results/_r881bma_w186_buildgen.py (TOK/BACK pairs
AST-extracted from the r877 build script -- no exec of its live
asserts; r773/r775/r781/r830/r833 compliance inherited: token-first
two-phase vmap, whole-string composites, numerals LAST; r735
substring-order law = BACK list order preserved; pre-TOK sequential
DRY 50/50).  r587 machine-derived facts (read from on-disk receipts):
r880 probe ADMIT naive A 423_804..425_803 refused by W185 B
423_804..424_003 -> A 424_004..426_003 staircase 46th E36 / B
426_004..426_203 own-A reservation W141 leg2; W185 finalize r879
adopted-window one-pass (K 404,920 EXACT / head 814,328 EXACT delta
zero vs frozen projection / merged mu -0.0929 display ROLLS this
wave / w-only -0.0992 / sigma 0.245090 / skill_line 1.1858 -> 1.1857
K-lift -0.0001 first negative after the W181..W184 four-flat / n_eff
812,128 / A p95 0.3066); W185 sec7/sec8 settle backfill landed r879
SAME window as the finalize (adopted-window); W185 freeze beb4b5abd
(prereg freeze ad4eded99 r877); W186 seat push dd362c690 r880; seat
self-ack archive move landed the bm-a r880 window itself (4c0cfabc3
closeout, self-move, same-window pattern disclosed); @SEATSENT@
r841 stale stamps fixed to r880 this wave (disclosed).

Output written CRLF (on-disk convention, r370 law)."""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "results/_r881bma_w186_prereg_src.txt"
OUT = "research/PERPETUAL_N1_W186_PREREG.md"


# --- machine-derived facts (r587: read from on-disk receipts) ----------
probe = json.load(open(r"results/_r880bma_w186_probe_receipt.json",
                      encoding="utf-8"))
assert probe["verdict"] == "ADMIT", probe["verdict"]
assert probe["bands"] == {"A": "424004_426003", "B": "426004_426203"}, \\
    probe["bands"]
leg0, leg1 = probe["legs"]["leg0"], probe["legs"]["leg1"]
leg2, leg3, leg4 = probe["legs"]["leg2"], probe["legs"]["leg3"], \\
    probe["legs"]["leg4"]
assert leg1["A"] == [424004, 426003] and leg1["B"] == [426004, 426203], leg1
assert leg1["hops_A"] == 1 and leg1["hops_B"] == 1, leg1
assert leg1["ARITH_A"] == [423804, 425803], leg1["ARITH_A"]
assert leg1["ARITH_B"] == [424004, 424203], leg1["ARITH_B"]
assert leg1["B_naive_first_clean"] == [424004, 424203], leg1
assert leg1["B_hop_chain"][0]["jump_to"] == 426004, leg1["B_hop_chain"]
assert leg2["conflicts"] == 0 and leg3["origin_vacancy"] is True, (leg2, leg3)
assert leg0["rows"] == 183 and leg0["tail"] == "W185" and \\
    leg0["ordinal"] == 176 and leg0["bma_ordinal"] == 102 and \\
    leg0["owner_rows"] == 175 and leg0["bma_rows"] == 101 and \\
    leg0["w185_ledger_head"] == 814328, leg0
assert leg4["W187p_A"] in ("426004..428003", "426_004..428_003") and \\
    leg4["W187p_B"] in ("426204..426403", "426_204..426_403"), leg4
assert leg4["hops_A"] == 0 and leg4["hops_B"] == 0, leg4
assert leg4["W187p_B_lands_inside_W187p_A"] is True, leg4
assert "FORTY-SIXTH" in leg1["A_semantics"], leg1["A_semantics"]

res = json.load(open(r"results/perpetual_faces/n1_w185_results.json",
                     encoding="utf-8"))
npc = res["null_pool_cumulative"]
assert npc["merged"]["n_values"] == 404920, "W185 merged K drift"
assert npc["pre_w185_cumulative"]["n_values"] == 402720, "pre-W185 K drift"
kl = res["skill_line_v2_k_lift"]
assert kl["line_merged_404920"] == 1.1857 and kl["line_pre_w185"] == 1.1858 \\
    and kl["line_delta_k_lift"] == -0.0001 and kl["n_eff_held_equal"] == 812128, kl
assert kl["canon_flip"].startswith("NOT performed"), kl
assert npc["se_mu_at_k404920"] == 0.000385, "se_mu drift"
assert abs(npc["mu_delta_w185_vs_w184ext"] - (-0.005922)) < 1e-9, "mu_delta drift"
assert res["families"]["A_random_engine_exit"]["full_sharpe_p95"] == 0.3066, \\
    "p95 drift"
assert res["science_gates"]["ledger"]["total"] == 814328, "ledger head drift"
MU4 = "%.4f" % npc["merged"]["mu"]
WONLY4 = "%.4f" % npc["w185_only"]["mu"]
SIG6 = "%.6f" % npc["merged"]["sigma"]
assert MU4 == "-0.0929" and WONLY4 == "-0.0992" and SIG6 == "0.245090", \\
    (MU4, WONLY4, SIG6)
LEDG = "{:,}".format(leg0["w185_ledger_head"])
KNEW = "{:,}".format(npc["merged"]["n_values"])
assert LEDG == "814,328" and KNEW == "404,920", (LEDG, KNEW)
KPROJ = "{:,}".format(404920 + 2200)
LEDGPROJ = "{:,}".format(814328 + 2200)
assert KPROJ == "407,120" and LEDGPROJ == "816,528", (KPROJ, LEDGPROJ)

# shas (live machine-derive, r587) + r511 rolling re-check
subprocess.run(["git", "fetch", "origin"], capture_output=True)
_r = subprocess.run(["git", "log", "origin/main", "--format=%h",
                    "--grep=W185 FREEZE", "-1"], capture_output=True, text=True)
W185_SHA = _r.stdout.strip()
assert W185_SHA == "beb4b5abd", W185_SHA
_r0 = subprocess.run(["git", "log", "origin/main", "--format=%h",
                     "--grep=W186 FREEZE", "-1"], capture_output=True, text=True)
assert _r0.stdout.strip() == "", "origin already carries a W186 FREEZE"
_r2 = subprocess.run(["git", "log", "origin/main", "--format=%h", "-1",
                     "--diff-filter=A",
                     "--", "fleet/inbox/MSG-2026-10-08-1354-bma-w186-seat.md"],
                    capture_output=True, text=True)
SEAT_SHA = _r2.stdout.strip()
assert SEAT_SHA == "dd362c690", SEAT_SHA
_r3 = subprocess.run(["git", "show",
                     "origin/main:fleet/inbox/processed/"
                     "MSG-2026-10-08-1354-bma-w186-seat.md"],
                    capture_output=True)
assert _r3.returncode == 0, "W186 seat MSG not on origin processed/ (r565 law)"
assert "424_004..426_003" in _r3.stdout.decode("utf-8", "replace"), \\
    "seat band face drift"
_r4 = subprocess.run(["git", "rev-parse",
                     "ad4eded99:research/PERPETUAL_N1_W185_PREREG.md"],
                    capture_output=True, text=True)
assert _r4.stdout.strip() == "d431b448a5b1879429f5569a5e92df94858476c5", \\
    "src blob drift: %s" % _r4.stdout.strip()
# W185 sec7/sec8 settle backfill landed the r879 adopted-window (same
# window as the finalize) -- the anchor face cites it (the adopted-window
# disclosure lives in the W185 prereg's own sec7 header)
w185p = io.open(r"research/PERPETUAL_N1_W185_PREREG.md", encoding="utf-8",
                newline="").read()
assert "814,328" in w185p and "K=404,920" in w185p, \\
    "W185 sec7/sec8 backfill missing (anchor-face citation would be false)"
assert "r879 收养窗" in w185p, "W185 sec7 adopted-window note missing"

src = io.open(SRC, encoding="utf-8").read()
assert src.count("\\r\\n") == 0, "source blob expected LF (git blob convention)"
assert "PERPETUAL-N1-W185" in src and "423_804..425_803" in src, "src face drift"
'''

TAIL = '''
TOK186 = %s
BACK186 = %s

EXPECT = %s

out_t = src
for old, tok in TOK186:
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
for tok, new in BACK186:
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
assert stale_wave == ["波号 186"], f"stale bare wave numbers: {stale_wave}"
low_forms = sorted(set(re.findall(r"n1_w1[0-9][0-9]", out_t)))
assert low_forms == ["n1_w185", "n1_w186"], f"unexpected n1_w1xx forms: {low_forms}"
assert out_t.count("PERPETUAL-N1-W186") == EXPECT["@B@"] + 1, "batch id count drift"
assert "W186 freeze" not in out_t.replace("；W185=bm-a r878 freeze", ""), \\
    "unexpected W186-freeze text"

# stale-session sweep ("r875 probe leg4" = LEGAL new citation -- the W185
# probe leg4 that anticipated the W186 staircase; bare "402,720" consumed
# by the K roll -- head-face stale probe uses the whole-string form)
for stale in ("r875 probe 回执", "（r875 probe leg2", "r870 probe", "r872 冻结件",
              "已回填（r875", "304909e0e", "【r875】", "FORTY-FIFTH",
              "第四十五例", "0.3194", "0.245094", "−0.0933", "−0.0928",
              "402,720", "净账本锚头 812,128", "809,928", "MSG-2026-10-08-1032",
              "r875 seat push", "bm-a r876 窗自移", "本机 r841 席位",
              "（r841 seat push", "d431b448a5"):
    assert stale not in out_t, f"stale token survives: {stale!r}"
assert "r875 probe leg4" in out_t, "new W185-probe-leg4 citation missing"
assert out_t.count("r875") == 3, "r875 residual count=%%d (expect 3 = leg4 x3)"
assert out_t.count("r870") == 0, "r870 residual count=%%d (expect 0)"
assert out_t.count("r841") == 0, "r841 residual count=%%d (expect 0)"
assert out_t.count("W186 finalize 窗") == 2, "sec7/8 placeholder wave face missing"
assert "W185 finalize 窗" not in out_t, "stale sec7/8 placeholder wave face"

open(OUT, "wb").write(out_t.replace("\\n", "\\r\\n").encode("utf-8"))
chk = io.open(OUT, encoding="utf-8", newline="").read()
assert chk == out_t.replace("\\n", "\\r\\n"), "CRLF write roundtrip drift"
assert chk.count("\\r\\n") >= 60, chk.count("\\r\\n")
print(f"W186 prereg built: {OUT} bytes={len(chk.encode('utf-8'))} crlf={chk.count(chr(13)+chr(10))}")
print("post-transform asserts PASS (token counts, residue-zero, malformed-window CLEAN, two-form CLEAN, stale-session sweep CLEAN)")
'''

tok_lit = repr(TOK186)
back_lit = repr([(t, BACK186[t]) for (t, _v) in BACK185])
exp_lit = repr(EXPECT)
assert TAIL.count("%s") == 3, TAIL.count("%s")
out = HDR + "\n" + (TAIL % (tok_lit, back_lit, exp_lit))
io.open(r"results/_r881bma_w186_prereg_build.py", "w", encoding="utf-8",
        newline="\n").write(out)
ast.parse(out)
print("emitted: results/_r881bma_w186_prereg_build.py", len(out), "bytes")
