# -*- coding: utf-8 -*-
# r1161 bm-c: W289 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W288 prereg pre-run face (results/_w289bmc_w288_frozen_face.txt =
#       git show 22ffa74b01:research/PERPETUAL_N1_W288_PREREG.md, the r1158 freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law (r1149/r1152/r1155/r1158 lineage): numeric placeholders first (no cascade), measured
# values on pre-shift labels, single-pass wave/w/r/band token maps, ordinal map, then post-shift repairs.
import hashlib, io, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w289bmc_w288_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W289_PREREG.md")
FREEZE_COMMIT = "22ffa74b01"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W288_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W288 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1159bmc_w288_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w289bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W288 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W289 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [651101, 653100] and rc["bands"]["B"] == [653101, 653300], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (278, 107, 279), "leg0 drift"
assert _l0["wprev_bands"] == {"A": [648901, 650900], "B": [650901, 651100]}, "W288 band drift"
assert _l0["wprev_minus1_bands"] == {"A": [646701, 648700], "B": [648701, 648900]}, "W287 band drift"
assert _l0["wprev_finalize_anchors"]["ledger_total"] == 1057941
assert _l0["wprev_finalize_anchors"]["merged_n"] == 631520
assert _l0["inflight_upstream"] is False and _l0["wprev_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [651101, 653100] and _l1["B"] == [653101, 653300], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert _l1["B_naive"] == [651101, 651300] and _l1["B_lands_above_own_A"] is True
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W290p_A_naive"] == "653_101..655_100" and _l4["W290p_A_first_clean"] == "653_101..655_100"
assert _l4["W290p_B_naive"] == "653_301..653_500" and _l4["W290p_B_first_clean"] == "653_301..653_500"
assert _l4["hops_A"] == 0 and _l4["hops_B"] == 0
assert _l4["W290p_B_lands_inside_W290p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w288_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEM = hk["skill_line"]["line_merged_631520"]; LINEPRE = hk["skill_line"]["line_pre_w288"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
SE = hk["merged"]["se_mu_k631520"]
assert (K, LEDGER, NEFF) == (631520, 1057941, 1055741)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09277584" and "%.8f" % ONLY_MU == "-0.09011132" and "%.8f" % SIG == "0.24510025"
assert P95 == 0.3222
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.1981, 1.1981)
assert SE == 0.000308
GAP = abs(ONLY_MU - MU)
assert "%.4f" % GAP == "0.0027"
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 633720 and LEDGER_PROJ == 1060141 and NEFF_PROJ == 1057941

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
assert _st.get("alive_flag") is True, "engine dead: %r" % _st
ENGINE_BURNS = len(_st.get("burns_active") or [])
ENGINE_QUEUE = _st.get("queue_next") or []
ENGINE_FACE = "idle" if (ENGINE_BURNS == 0 and not ENGINE_QUEUE) else \
    "busy burns=%d queue=%d" % (ENGINE_BURNS, len(ENGINE_QUEUE))

# ---------- phase -1: numeric placeholders (single pass, no cascade) ----------
NUM = {"629,320": "631,520", "631,520": "633,720",
       "1,055,741": "1,057,941", "1,053,541": "1,055,741"}
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
add("池第 286 枚", "池第 287 枚")
add("engine_owner 行 277 注册在册", "engine_owner 行 278 注册在册")
add("engine_owner==bm-c 106 行注册", "engine_owner==bm-c 107 行注册")
add("bmc_rows=106", "bmc_rows=107")
add("bmc live rows 106", "bmc live rows 107")
add("bmc rows 106+候选=第 107 枚", "bmc rows 107+候选=第 108 枚", 2)
add("CLEAN-AT-BIRTH 19th gen", "CLEAN-AT-BIRTH 20th gen")
add("MSG-20261020-1335-bmc-w288-seat", "MSG-20261020-1535-bmc-w289-seat", 3)
add("f138546d08+0b5adf2a6b+6414b3a685", "22ffa74b01+f59b40c6c1+f0570e0459")
add("f138546d08", "22ffa74b01", 1)
add("0b5adf2a6b", "f59b40c6c1", 2)
add("a2f3e3ce27", "677d49d3c0", 3)
add("0.24509732", "0.24510025")
add("\u22120.09278516", "\u22120.09277584")
add("\u22120.09961141", "\u22120.09011132")
add("共二百八十六面", "共二百八十七面")
add("实差 0.0068", "实差 0.0027")
add("0.3126", "0.3222")
add("1.198", "1.1981", 2)
add("第 278 波", "第 279 波")
add("W211..W280", "W211..W281")
add("第一百零七枚自有波", "第一百零八枚自有波")
add("--wave 288/finalize --wave 288", "--wave 289/finalize --wave 289")
add("波号 288=注册表 W289 席后首个自由号", "波号 289=注册表 W290 席后首个自由号")
add("零 288 行", "零 289 行")
add("连续三十七波", "连续三十八波")
add("12:2x", "13:5x", 2)
add("12:4x", "14:0x", 4)
add("13:1x", "14:4x", 1)
add("本窗 free RAM 3.5GB", "本窗 free RAM %sGB" % RAM_FACE)
# GPU face is a live claim, not inherited: this window's nvidia-smi shows a ComfyUI job on the card,
# so the W288 "GPU idle 回释" caption would be false -- restate it from the live read instead.
add("nvidia-smi 实读 2.0G VRAM 占用\u00b7MV 车道已收官 GPU idle 回释",
    "nvidia-smi 实读 %s VRAM 占用\u00b7ComfyUI 工件在烧\u3014非本波占用\u00b7CPU 车道独立\u3015" % VRAM_G)
add("~3.5G", "\u00a7R1\u00a7", 1)
add("~2.5G", "~3.5G", 1)
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
W_MAP = {"W284": "W285", "W285": "W286", "W286": "W287", "W287": "W288", "W288": "W289", "W289": "W290"}
W_HITS = {k: 0 for k in W_MAP}


def _w(m):
    W_HITS[m.group(0)] += 1
    return W_MAP[m.group(0)]


T2 = re.sub(r"W(?:284|285|286|287|288|289)", _w, T1)
w_MAP = {"w287": "w288", "w288": "w289"}
W_HITS_L = {k: 0 for k in w_MAP}


def _wl(m):
    W_HITS_L[m.group(0)] += 1
    return w_MAP[m.group(0)]


T2 = re.sub(r"w(?:287|288)", _wl, T2)
T2 = T2.replace("R289", "R290", 1)

# ---------- phase 2: r-label chain shift, single simultaneous pass (+3) ----------
R_MAP = {"r1155": "r1158", "r1156": "r1159", "r1157": "r1160", "r1158": "r1161"}
R_HITS = {k: 0 for k in R_MAP}


def _r(m):
    R_HITS[m.group(0)] += 1
    return R_MAP[m.group(0)]


T3 = re.sub(r"r11(?:55|56|57|58)", _r, T2)

# ---------- phase 3: band tokens, single-pass token map (+2,200 uniform) ----------
B_TOKENS = ["648_700", "648_701", "648_900", "648_901", "649_100", "650_700",
            "650_900", "650_901", "651_100", "651_101", "651_300", "652_900"]
B_HITS = {k: 0 for k in B_TOKENS}


def _b(m):
    s = m.group(0)
    if s not in B_HITS:
        raise SystemExit("unregistered band token %r" % s)
    B_HITS[s] += 1
    hi, lo = s.split("_")
    return "%d_%03d" % ((int(hi) * 1000 + int(lo) + 2200) // 1000, (int(hi) * 1000 + int(lo) + 2200) % 1000)


T4 = re.sub(r"\d{3}_\d{3}", _b, T3)

# ---------- phase 4: ordinal map (single pass) ----------
ORD_MAP = {"第四十一次": "第四十二次", "第四十二次": "第四十三次"}
O_HITS = {k: 0 for k in ORD_MAP}


def _o(m):
    O_HITS[m.group(0)] += 1
    return ORD_MAP[m.group(0)]


T5 = re.sub(r"第(?:四十一|四十二)次", _o, T4)

# ---------- phase 5: post-shift repairs ----------
# se_mu narrowing chain carries ACTUALS up to W288 + one projection: relabelling it by +1 would
# falsely claim a W289 actual, so the chain is restored verbatim with the true W288 actual.
SE_CHAIN_SRC = ("\u2192W277 **0.000314**\u2192W278 **0.000314**\u2192W279 **0.000313**"
                "\u2192W280 **0.000312**\u2192W282 **0.000312**\u2192W286 **0.000311**"
                "\u2192W288 **0.000309**\u2192W289 \u6295\u5f71 0.000309")
SE_CHAIN_SHIFTED = ("\u2192W277 **0.000314**\u2192W278 **0.000314**\u2192W279 **0.000313**"
                    "\u2192W280 **0.000312**\u2192W282 **0.000312**\u2192W287 **0.000311**"
                    "\u2192W288 **0.000309**\u2192W289 \u6295\u5f71 0.000309")
SE_CHAIN_TARGET = ("\u2192W277 **0.000314**\u2192W278 **0.000314**\u2192W279 **0.000313**"
                   "\u2192W280 **0.000312**\u2192W282 **0.000312**\u2192W287 **0.000311**"
                   "\u2192W288 **0.000308**\u2192W289 \u6295\u5f71 0.000308")
if T5.count(SE_CHAIN_SHIFTED) != 1:
    raise SystemExit("se_mu chain shifted-span not unique: %d" % T5.count(SE_CHAIN_SHIFTED))
T5 = T5.replace(SE_CHAIN_SHIFTED, SE_CHAIN_TARGET)

# sec.5 keys carry W288 ACTUALS (fivekeys receipt read this window) and the +1 label shift lands
# them on W288 exactly -- measured-value rules were authored on PRE-shift labels, so no relabel
# repair is needed this wave (contrast W288 where the same shift overshot by one). All §5 caption
# spans were checked by hand against the receipt before this list was left empty.
POST = []
for old, new, n in POST:
    c = T5.count(old)
    if c != n:
        if old == new:
            continue
        raise SystemExit("POST COUNT %d != %d: %r" % (c, n, old[:80]))
    T5 = T5.replace(old, new)

# ---------- phase 6: numeric placeholder restore ----------
for i, k in enumerate(NUM):
    T5 = T5.replace("\u00a7%d\u00a7" % i, NUM[k])

RESIDUAL = ["w287", "648_", "646_", "644_", "r1155", "r1156", "r1157",
            "0.24509732", "0.3126", "12:2x0",
            "\u7b2c 286 \u679a", "\u7b2c 278 \u6ce2", "\u7b2c 107 \u679a", "19th gen",
            "\u5171\u4e8c\u767e\u516b\u5341\u516d", "106 \u884c\u6ce8\u518c", "106+\u5019\u9009"]

assert not re.search(r"\u00a7\d+\u00a7", T5), "unrestored numeric placeholder"

left = {t: T5.count(t) for t in RESIDUAL if t in T5}
assert T5.count("W288") >= 1 and T5.count("W289") >= 1 and T5.count("W290") >= 1

MUST = [
    "PERPETUAL-N1-W289", "research/PERPETUAL_N1_W289_PREREG.md",
    "651_101..653_100", "653_101..653_300",
    "631,520", "633,720", "1,057,941", "K=631,520",
    "n1_w288_results.json", "n1_w289_results.json",
    "\u7b2c 287 \u679a", "\u7b2c 279 \u6ce2", "\u7b2c\u4e00\u767e\u96f6\u516b\u679a\u81ea\u6709\u6ce2", "\u7b2c 108 \u679a",
    "engine_owner \u884c 278 \u6ce8\u518c\u5728\u518c", "engine_owner==bm-c 107 \u884c\u6ce8\u518c",
    "bmc_rows=107", "bmc live rows 107", "bmc rows 107+\u5019\u9009=\u7b2c 108 \u679a",
    "STAIRCASE-AFFECTS-A", "\u7b2c\u56db\u5341\u4e8c\u6b21\u8fde\u7eed A-hop", "\u7b2c\u56db\u5341\u4e09\u6b21\u8fde\u7eed above-own-A",
    "_w289bmc_20261020", "--wave 289/finalize --wave 289",
    "results/_w289bmc_freeze_edits.py", "_w288bmc_freeze_edits.py",
    "W288 finalize one-pass bm-c r1159", "n_eff_held_equal 1,055,741",
    "\u22120.09277584", "0.24510025", "\u22120.09011132", "0.3222", "1.1981",
    "W2..W288", "W1..W288", "W136..W288",
    "22ffa74b01", "f59b40c6c1", "f0570e0459",
    "MSG-20261020-1535-bmc-w289-seat", "677d49d3c0", "20th gen",
    "W290p_B_lands_inside_W290p_A_naive",
    "R290\uff1aW289 \u5e26", "650_901..652_900", "651_101..651_300",
    "653_101..655_100", "653_301..653_500",
    "bm-c r1161 W289 \u00a77 \u8303\u5f0f", "bm-c r1161 W289 \u00a78 \u8303\u5f0f",
    "bm-c \u5faa\u73af\u73ed r1161 \u5e2d\u4f4d\u7a97 2026-10-20 14:4x",
    "W288 \u51bb\u7ed3\u7a97 ~3.5G bm-c \u5b9e\u951a",
    "seed_admit_gate rc0 \u53cc\u5e26 FREE",
    "saturation_engine.py status live-read r1161",
    "heartbeat \u65b0\u9c9c\u5b9e\u8bfb r1161 \u7a97",
    "\u2192W288 **0.000308**\u2192W289 \u6295\u5f71 0.000308",
    "0.24510025**=W288 \u5408\u5e76\u6c60\u5b9e\u6d4b",
    "\u952e W288 \u5b9e\u6d4b K-lift **+0.0000**",
    "line_pre_w288 1.1981",
    "ordinal \u4ee5 W290 seat live trace \u4e3a\u51c6 r587",
]
missing = [s for s in MUST if s not in T5]

MUST_NOT = [
    "PERPETUAL-N1-W288 \u9884\u6ce8\u518c", "research/PERPETUAL_N1_W288_PREREG.md",
    "A-ext seed=650_901", "entry rng seed=**650_901+j**",
    "\u7b2c\u56db\u5341\u4e00\u6b21\u8fde\u7eed A-hop", "\u7b2c\u56db\u5341\u4e8c\u6b21\u8fde\u7eed above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "0.24509732", "0.3126",
    "\u7b2c 286 \u679a", "\u7b2c 278 \u6ce2", "\u7b2c 107 \u679a", "19th gen",
    "W2..W287", "W1..W287",
    "engine_owner==bm-c 106 \u884c\u6ce8\u518c", "engine_owner \u884c 277 \u6ce8\u518c\u5728\u518c",
    "bmc_rows=106", "bmc live rows 106",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "\u6ce2\u53f7 288=\u6ce8\u518c\u8868",
    "W289 **0.000309**\u2192W290 \u6295\u5f71",
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
    io.open(os.path.join(REPO, "results", "_w289bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T5)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    assert not [k for k, v in B_HITS.items() if v == 0], "unused band token"
    assert not [k for k, v in R_HITS.items() if v == 0], "unused r token"
    assert not [k for k, v in O_HITS.items() if v == 0], "unused ordinal token"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T5)
    print("W289 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T5.encode("utf-8")), T5.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu %s"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ, SE))
    print("bands A 651101..653100 / B 653101..653300 | hops A=1 B=1 | RAM %s GB | VRAM %s | engine %s"
          % (RAM_FACE, VRAM_G, ENGINE_FACE))
    print("out sha256_16: %s" % hashlib.sha256(T5.encode("utf-8")).hexdigest()[:16])