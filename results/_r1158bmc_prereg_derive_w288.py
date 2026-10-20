# -*- coding: utf-8 -*-
# r1158 bm-c: W288 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W287 prereg pre-run face (results/_w288bmc_w287_frozen_face.txt =
#       git show f138546d08:research/PERPETUAL_N1_W287_PREREG.md, the r1155 freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law (r1149/r1152/r1155 lineage): numeric placeholders first (no cascade), measured values on
# pre-shift labels, single-pass wave/w/r/band token maps, ordinal map, then post-shift repairs.
import hashlib, io, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w288bmc_w287_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W288_PREREG.md")
FREEZE_COMMIT = "f138546d08"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W287_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W287 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1156bmc_w287_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w288bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W287 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W288 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [648901, 650900] and rc["bands"]["B"] == [650901, 651100], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (277, 277, 106, 278), "leg0 drift"
assert _l0["wprev_bands"] == {"A": [646701, 648700], "B": [648701, 648900]}, "W287 band drift"
assert _l0["wprev_minus1_bands"] == {"A": [644501, 646500], "B": [646501, 646700]}, "W286 band drift"
assert _l0["wprev_finalize_anchors"]["ledger_total"] == 1055741
assert _l0["wprev_finalize_anchors"]["merged_n"] == 629320
assert _l0["inflight_upstream"] is False and _l0["wprev_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [648901, 650900] and _l1["B"] == [650901, 651100], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert _l1["B_naive"] == [648901, 649100] and _l1["B_lands_above_own_A"] is True
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W289p_A_naive"] == "650_901..652_900" and _l4["W289p_A_first_clean"] == "650_901..652_900"
assert _l4["W289p_B_naive"] == "651_101..651_300" and _l4["W289p_B_first_clean"] == "651_101..651_300"
assert _l4["hops_A"] == 0 and _l4["hops_B"] == 0
assert _l4["W289p_B_lands_inside_W289p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w287_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEM = hk["skill_line"]["line_merged_629320"]; LINEPRE = hk["skill_line"]["line_pre_w287"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
SE = hk["merged"]["se_mu_k629320"]
assert (K, LEDGER, NEFF) == (629320, 1055741, 1053541)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09278516" and "%.8f" % ONLY_MU == "-0.09961141" and "%.8f" % SIG == "0.24509732"
assert P95 == 0.3126
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.198, 1.198)
assert SE == 0.000309
GAP = abs(ONLY_MU - MU)
assert "%.4f" % GAP == "0.0068"
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 631520 and LEDGER_PROJ == 1057941 and NEFF_PROJ == 1055741

try:
    import psutil
    RAM_GB = psutil.virtual_memory().available / (1024 ** 3)
except Exception:
    RAM_GB = 0.0
RAM_FACE = "%.1f" % RAM_GB
VRAM_G = "2.0G"
try:
    _p = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True)
    if _p.returncode == 0:
        VRAM_G = "%.1fG" % (int(_p.stdout.decode("utf-8", "replace").strip().splitlines()[0]) / 1024.0)
except Exception:
    pass
_p = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                    capture_output=True, cwd=REPO)
assert _p.returncode == 0, "engine status rc=%d" % _p.returncode
_st = json.loads(_p.stdout.decode("utf-8", "replace"))
assert _st.get("alive_flag") is True and _st.get("burns_active") == [] and _st.get("queue_next") == [], \
    "engine not idle: %r" % _st

# ---------- phase -1: numeric placeholders (single pass, no cascade) ----------
NUM = {"627,120": "629,320", "629,320": "631,520",
       "1,053,541": "1,055,741", "1,051,341": "1,053,541"}
NUM_HITS = {k: 0 for k in NUM}


def _n(m):
    s = m.group(0)
    if s not in NUM:
        return s
    NUM_HITS[s] += 1
    return "\u00a7%s\u00a7" % list(NUM).index(s)


T = re.sub(r"\d{1,3},\d{3}(?:,\d{3})?", _n, T0)

RULES = []


def add(old, new, n=None):
    RULES.append((old, new, 1 if n is None else n))


# ---------- phase 0: measured-value rules authored on PRE-shift labels ----------
add("池第 285 枚", "池第 286 枚")
add("engine_owner 行 276 注册在册", "engine_owner 行 277 注册在册")
add("engine_owner==bm-c 105 行注册", "engine_owner==bm-c 106 行注册")
add("bmc_rows=105", "bmc_rows=106")
add("bmc live rows 105", "bmc live rows 106")
add("bmc rows 104+候选=第 106 枚", "bmc rows 106+候选=第 107 枚", 2)
add("CLEAN-AT-BIRTH 18th gen", "CLEAN-AT-BIRTH 19th gen")
add("MSG-20261020-1027-bmc-w287-seat", "MSG-20261020-1335-bmc-w288-seat", 3)
add("63236cf485", "a2f3e3ce27", 3)
add("beb10feab8+96cfcf7125+fecd144e37", "f138546d08+0b5adf2a6b+6414b3a685")
add("beb10feab8", "f138546d08", 1)
add("96cfcf7125", "0b5adf2a6b", 2)
add("0.24508362", "0.24509732")
add("\u22120.09276121", "\u22120.09278516")
add("\u22120.08854400", "\u22120.09961141")
add("共二百八十五面", "共二百八十六面")
add("实差 0.0042", "实差 0.0068")
add("0.3197", "0.3126")
add("**+0.0002**", "**+0.0000**")
add("1.1977", "1.198")
add("1.1979", "1.198")
add("第 277 波", "第 278 波")
add("W211..W279", "W211..W280")
add("第一百零六枚自有波", "第一百零七枚自有波")
add("--wave 287/finalize --wave 287", "--wave 288/finalize --wave 288")
add("波号 287=注册表 W288 席后首个自由号", "波号 288=注册表 W289 席后首个自由号")
add("零 287 行", "零 288 行")
add("09:2x", "12:2x", 2)
add("09:3x", "12:4x", 4)
add("11:1x", "13:1x", 1)
add("本窗 free RAM 2.5GB", "本窗 free RAM %sGB" % RAM_FACE)
add("~2.5G", "\u00a7R1\u00a7", 1)
add("~4.2G", "~2.5G", 1)
add("\u00a7R1\u00a7", "~%sG" % RAM_FACE, 1)

T1 = T
COUNT = []
for old, new, n in RULES:
    c = T1.count(old)
    if c != n:
        raise SystemExit("RULE COUNT %d != %d: %r" % (c, n, old[:100]))
    if n:
        T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

# ---------- phase 1: wave labels, single simultaneous pass (no cascade) ----------
W_MAP = {"W283": "W284", "W284": "W285", "W285": "W286", "W286": "W287", "W287": "W288", "W288": "W289"}
W_HITS = {k: 0 for k in W_MAP}


def _w(m):
    W_HITS[m.group(0)] += 1
    return W_MAP[m.group(0)]


T2 = re.sub(r"W(?:283|284|285|286|287|288)", _w, T1)
w_MAP = {"w286": "w287", "w287": "w288"}
W_HITS_L = {k: 0 for k in w_MAP}


def _wl(m):
    W_HITS_L[m.group(0)] += 1
    return w_MAP[m.group(0)]

T2 = re.sub(r"w(?:286|287)", _wl, T2)
T2 = T2.replace("R288", "R289", 1)

# ---------- phase 2: r-label chain shift, single simultaneous pass (+3) ----------
R_MAP = {"r1152": "r1155", "r1153": "r1156", "r1154": "r1157", "r1155": "r1158"}
R_HITS = {k: 0 for k in R_MAP}


def _r(m):
    R_HITS[m.group(0)] += 1
    return R_MAP[m.group(0)]

T3 = re.sub(r"r11(?:52|53|54|55)", _r, T2)

# ---------- phase 3: band tokens, single-pass token map (+2,200 uniform) ----------
B_MAP = {
    "646_500": "648_700", "646_501": "648_701", "646_700": "648_900", "646_701": "648_901",
    "646_900": "649_100", "648_500": "650_700", "648_700": "650_900", "648_701": "650_901",
    "648_900": "651_100", "648_901": "651_101", "649_100": "651_300", "650_700": "652_900",
}
B_HITS = {k: 0 for k in B_MAP}


def _b(m):
    B_HITS[m.group(0)] += 1
    return B_MAP[m.group(0)]

T4 = re.sub(r"\d{3}_\d{3}", _b, T3)

# ---------- phase 4: ordinal map (single pass) ----------
ORD_MAP = {"第三十七次": "第三十九次", "第三十八次": "第四十次",
           "第三十九次": "第四十一次", "第四十次": "第四十二次"}
O_HITS = {k: 0 for k in ORD_MAP}


def _o(m):
    O_HITS[m.group(0)] += 1
    return ORD_MAP[m.group(0)]

T5 = re.sub(r"第(?:三十七|三十八|三十九|四十)次", _o, T4)
T5 = T5.replace("连续三十六波", "连续三十七波", 1)

# ---------- phase 5: post-shift repairs ----------
# se_mu narrowing chain carries ACTUALS up to W287 + one projection: relabelling it by +1 would
# falsely claim a W288 actual, so the source span is restored verbatim (zero numeric change).
SE_CHAIN_SRC = ("\u2192W277 **0.000314**\u2192W278 **0.000314**\u2192W279 **0.000313**"
                "\u2192W280 **0.000312**\u2192W282 **0.000312**\u2192W286 **0.000311**"
                "\u2192W287 **0.000309**\u2192W288 投影 0.000309")
SE_CHAIN_SHIFTED = ("\u2192W277 **0.000314**\u2192W278 **0.000314**\u2192W279 **0.000313**"
                    "\u2192W280 **0.000312**\u2192W282 **0.000312**\u2192W287 **0.000311**"
                    "\u2192W288 **0.000309**\u2192W289 投影 0.000309")
if T5.count(SE_CHAIN_SHIFTED) != 1:
    raise SystemExit("se_mu chain shifted-span not unique: %d" % T5.count(SE_CHAIN_SHIFTED))
T5 = T5.replace(SE_CHAIN_SHIFTED, SE_CHAIN_SRC)

# sec.5 keys carry W287 ACTUALS (fivekeys receipt); the +1 label shift would mislabel them as
# W288 actuals -- relabel back to the wave the numbers were measured on (truth-first).
POST = [
    ("0.24509732**=W288 合并池实测", "0.24509732**=W287 合并池实测", 1),
    ("键 W288 实测 K-lift **+0.0000**", "键 W287 实测 K-lift **+0.0000**", 1),
    ("line_pre_w288 1.198", "line_pre_w287 1.198", 1),
    # ordinals describing the CURRENT wave's own legs are known exactly (seat receipt)
    ("W288 B 650_901..651_100 落本波 A 窗之上〔第四十次连续〕",
     "W288 B 650_901..651_100 落本波 A 窗之上〔第四十二次连续〕", 1),
    ("W288 A 面 1-hop=staircase affects A〔第三十九次连续〕",
     "W288 A 面 1-hop=staircase affects A〔第四十一次连续〕", 1),
    # forward-projection ordinals are NOT knowable at prereg time -> reference live derivation
    ("staircase affects A 承袭·第四十一次连续 A-hop 预期",
     "staircase affects A 承袭预期\u00b7ordinal 以 W289 seat live trace 为准 r587", 1),
    ("staircase affects A 第四十一次连续 A-hop 预期",
     "staircase affects A 承袭预期（ordinal 以 W289 seat live trace 为准 r587）", 1),
    ("staircase-affects-A 第四十一次连续 A-hop 预期",
     "staircase-affects-A 承袭预期\u00b7ordinal 以 W289 seat live trace 为准 r587", 1),
]
for old, new, n in POST:
    c = T5.count(old)
    if c != n:
        raise SystemExit("POST COUNT %d != %d: %r" % (c, n, old[:80]))
    T5 = T5.replace(old, new)

# ---------- phase 6: numeric placeholder restore ----------
for i, k in enumerate(NUM):
    T5 = T5.replace("\u00a7%d\u00a7" % i, NUM[k])

RESIDUAL = ["w286", "646_", "644_", "642_", "r1152", "r1153", "r1154",
            "0.24508362", "1.1977", "1.1979", "0.3197", "12:2x0",
            "第 285 枚", "第 277 波", "第 106 枚", "18th gen", "共二百八十五",
            "105 行注册", "104+候选"]

assert not re.search(r"\u00a7\d+\u00a7", T5), "unrestored numeric placeholder"

left = {t: T5.count(t) for t in RESIDUAL if t in T5}
assert T5.count("W285") == 1, "unexpected W285 survivors: %d" % T5.count("W285")
assert T5.count("W288") >= 1 and T5.count("W289") >= 1

MUST = [
    "PERPETUAL-N1-W288", "research/PERPETUAL_N1_W288_PREREG.md",
    "648_901..650_900", "650_901..651_100",
    "629,320", "631,520", "1,055,741", "K=629,320",
    "n1_w287_results.json", "n1_w288_results.json",
    "第 286 枚", "第 278 波", "第一百零七枚自有波", "第 107 枚",
    "engine_owner 行 277 注册在册", "engine_owner==bm-c 106 行注册",
    "bmc_rows=106", "bmc live rows 106", "bmc rows 106+候选=第 107 枚",
    "STAIRCASE-AFFECTS-A", "第四十一次连续 A-hop", "第四十二次连续 above-own-A",
    "_w288bmc_20261020", "--wave 288/finalize --wave 288",
    "results/_w288bmc_freeze_edits.py", "_w287bmc_freeze_edits.py",
    "W287 finalize one-pass bm-c r1156", "n_eff_held_equal 1,053,541",
    "\u22120.09278516", "0.24509732", "\u22120.09961141", "0.3126", "1.198",
    "W2..W287", "W1..W287", "W136..W287",
    "f138546d08", "0b5adf2a6b", "6414b3a685",
    "MSG-20261020-1335-bmc-w288-seat", "a2f3e3ce27", "19th gen",
    "W289p_B_lands_inside_W289p_A_naive",
    "R289：W288 带", "648_701..650_700", "648_901..649_100",
    "650_901..652_900", "651_101..651_300",
    "bm-c r1158 W288 §7 范式", "bm-c r1158 W288 §8 范式",
    "bm-c 循环班 r1158 席位窗 2026-10-20 13:1x",
    "W287 冻结窗 ~2.5G bm-c 实锚",
    "seed_admit_gate rc0 双带 FREE",
    "saturation_engine.py status live-read r1158",
    "heartbeat 新鲜实读 r1158 窗",
    "\u2192W287 **0.000309**\u2192W288 投影 0.000309",
    "0.24509732**=W287 合并池实测",
    "键 W287 实测 K-lift **+0.0000**",
    "line_pre_w287 1.198",
    "〔第四十二次连续〕", "〔第四十一次连续〕",
    "ordinal 以 W289 seat live trace 为准 r587",
]
missing = [s for s in MUST if s not in T5]

MUST_NOT = [
    "PERPETUAL-N1-W287 预注册", "research/PERPETUAL_N1_W287_PREREG.md",
    "A-ext seed=646_701", "entry rng seed=**646_701+j**", "exit rng=**648_701+j**",
    "第三十九次连续 A-hop", "第四十次连续 above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "0.24508362", "1.1977", "1.1979", "0.3197",
    "第 285 枚", "第 277 波", "第 106 枚", "18th gen",
    "W2..W286", "W1..W286",
    "engine_owner==bm-c 105 行注册", "engine_owner 行 276 注册在册",
    "bmc_rows=105", "bmc live rows 105",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "波号 287=注册表",
    "W288 **0.000309**\u2192W289 投影",
]
present_bad = [s for s in MUST_NOT if s in T5]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T5.encode("utf-8")), left))
print("W hits %r | w hits %r | r hits %r | band hits %r | ordinal hits %r"
      % (W_HITS, W_HITS_L, R_HITS, B_HITS, O_HITS))
print("num hits %r" % NUM_HITS)
print("band zero-hit tokens=%r" % [k for k, v in B_HITS.items() if v == 0])
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    io.open(os.path.join(REPO, "results", "_w288bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T5)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    assert not [k for k, v in B_HITS.items() if v == 0], "unused band token"
    assert not [k for k, v in R_HITS.items() if v == 0], "unused r token"
    assert not [k for k, v in O_HITS.items() if v == 0], "unused ordinal token"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T5)
    print("W288 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T5.encode("utf-8")), T5.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu %s"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ, SE))
    print("bands A 648901..650900 / B 650901..651100 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T5.encode("utf-8")).hexdigest()[:16])