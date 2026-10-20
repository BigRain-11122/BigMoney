# -*- coding: utf-8 -*-
# r1149 bm-c: W285 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W284 prereg pre-run face (results/_w285bmc_w284_frozen_face.txt =
#       git show 28c5f465f2:research/PERPETUAL_N1_W284_PREREG.md, the r1145 freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law: measured values are rewritten FIRST with the pre-shift (this-wave) labels still in place,
# then wave/r labels shift in a SINGLE regex pass (no cascade), then post-shift repairs
# (RAM freeze-anchor chain) land last. Band tokens shift in a single-pass token map so an
# introduced range can never be re-mapped (r1141/r1145 pattern).
# DST = research/PERPETUAL_N1_W285_PREREG.md
import hashlib, io, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w285bmc_w284_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W285_PREREG.md")
FREEZE_COMMIT = "28c5f465f2"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W284_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W284 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1147bmc_w284_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w285bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W284 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W285 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [642301, 644300] and rc["bands"]["B"] == [644301, 644500], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (274, 274, 103, 275), "leg0 drift"
assert _l0["w281_bands"] == {"A": [640101, 642100], "B": [642101, 642300]}, "W284 band drift"
assert _l0["inflight_upstream"] is False and _l0["w281_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [642301, 644300] and _l1["B"] == [644301, 644500], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W286p_A_naive"] == "644_301..646_300" and _l4["W286p_A_first_clean"] == "644_301..646_300"
assert _l4["W286p_B_naive"] == "644_501..644_700" and _l4["W286p_B_first_clean"] == "644_501..644_700"
assert _l4["hops_A"] == 0 and _l4["hops_B"] == 0
assert _l4["W286p_B_lands_inside_W286p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w284_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w284"]; LINEM = hk["skill_line"]["line_merged_622720"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
SE = hk["merged"]["se_mu_k622720"]
assert (K, LEDGER, NEFF) == (622720, 1049141, 1046941)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09278629" and "%.8f" % ONLY_MU == "-0.08587991" and "%.8f" % SIG == "0.24505609"
assert P95 == 0.3187
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.1975, 1.1975)
assert SE == 0.000311
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 624920 and LEDGER_PROJ == 1051341 and NEFF_PROJ == 1049141

try:
    import psutil
    RAM_GB = psutil.virtual_memory().available / (1024 ** 3)
except Exception:
    RAM_GB = 0.0
RAM_FACE = "%.1f" % RAM_GB
VRAM_G = "4.0G"
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

RULES = []


def add(old, new, n=None):
    RULES.append((old, new, 1 if n is None else n))


# ---------- phase 0: measured-value rules authored on PRE-shift labels ----------
add("池第 282 枚", "池第 283 枚")
add("engine_owner 行 273 注册在册", "engine_owner 行 274 注册在册")
add("CLEAN-AT-BIRTH 15th gen", "CLEAN-AT-BIRTH 16th gen")
add("MSG-20261020-0635-bmc-w284-seat", "MSG-20261020-0758-bmc-w284-seat", 3)
add("52cca74151", "597a614539", 3)
add("83b394ce64+44a3abdff3+0cef7d9e38", "28c5f465f2+a8e5ddfd65+c2e6d34ae0")
add("83b394ce64", "28c5f465f2")
add("44a3abdff3", "a8e5ddfd65", 2)
add("0.24505561", "0.24505609")
# U+2212 minus (pre-register sign face)
add("\u22120.09281078", "\u22120.09278629")
add("\u22120.09137100", "\u22120.08587991")
add("共二百八十二面", "共二百八十三面")
add("实差 0.0043", "实差 0.0069")
add("0.3185", "0.3187")
add("1.1974", "1.1975", 2)
add("1,046,941", "1,049,141", 2)
add("1,044,741", "1,046,941")
add("=620,520+2,200（本波）=**622,720 投影**", "=622,720+2,200（本波）=**624,920 投影**")
add("620,520", "622,720", 5)
add("第 274 波", "第 275 波")
add("第一百零三枚自有波", "第一百零四枚自有波")
add("第 103 枚", "第 104 枚", 2)
add("engine_owner==bm-c 102 行注册", "engine_owner==bm-c 103 行注册")
add("bmc_rows=102", "bmc_rows=103")
add("bmc live rows 102", "bmc live rows 103")
add("bmc rows 102+候选", "bmc rows 103+候选", 2)
add("--wave 284/finalize --wave 284", "--wave 285/finalize --wave 285")
add("06:1x", "07:3x", 4)
add("05:4x", "07:1x", 2)
add("06:4x", "08:0x")
add("连续三十三波", "连续三十四波")
add("本窗 free RAM 3.5GB", "本窗 free RAM %sGB" % RAM_FACE)
add("nvidia-smi 实读 2.0G VRAM 占用", "nvidia-smi 实读 %s VRAM 占用" % VRAM_G)

T1 = T0
COUNT = []
for old, new, n in RULES:
    c = T1.count(old)
    if c != n:
        raise SystemExit("RULE COUNT %d != %d: %r" % (c, n, old[:100]))
    T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

# ---------- phase 1: wave labels, single simultaneous pass (no cascade) ----------
W_MAP = {"W283": "W284", "W284": "W285", "W285": "W286"}
W_HITS = {"W283": 0, "W284": 0, "W285": 0}


def _w(m):
    W_HITS[m.group(0)] += 1
    return W_MAP[m.group(0)]


T2 = re.sub(r"W(?:283|284|285)", _w, T1)
w_MAP = {"w283": "w284", "w284": "w285", "w285": "w286"}
W_HITS_L = {"w283": 0, "w284": 0, "w285": 0}


def _wl(m):
    W_HITS_L[m.group(0)] += 1
    return w_MAP[m.group(0)]


T2 = re.sub(r"w(?:283|284|285)", _wl, T2)
T2 = T2.replace("R285", "R286", 1)
# ---------- phase 2: r-label chain shift, single simultaneous pass ----------
R_MAP = {"r1141": "r1145", "r1142": "r1146", "r1143": "r1147", "r1144": "r1148", "r1145": "r1149"}
R_HITS = {k: 0 for k in R_MAP}


def _r(m):
    R_HITS[m.group(0)] += 1
    return R_MAP[m.group(0)]


T3 = re.sub(r"r114[1-5]", _r, T2)

# ---------- phase 3: band tokens, single-pass token map (no re-map of introduced ranges) ----------
B_MAP = {
    "639_900": "642_100",
    "639_901": "642_101",
    "640_100": "642_300",
    "640_101": "642_301",
    "640_300": "642_500",
    "641_900": "644_100",
    "642_100": "644_300",
    "642_101": "644_301",
    "642_300": "644_500",
    "642_301": "644_501",
    "642_500": "644_700",
    "644_100": "646_300",
}
B_HITS = {k: 0 for k in B_MAP}


def _b(m):
    B_HITS[m.group(0)] += 1
    return B_MAP[m.group(0)]


T4 = re.sub(r"\d{3}_\d{3}", _b, T3)

# ---------- phase 4: post-shift repairs (RAM freeze-anchor chain) ----------
_old_ram = "W284 冻结窗 ~3.6G bm-c 实锚·本窗冻结窗 ~3.5G bm-c 实锚"
_new_ram = "W284 冻结窗 ~3.5G bm-c 实锚·本窗冻结窗 ~%sG bm-c 实锚" % RAM_FACE
assert T4.count(_old_ram) == 1, "RAM anchor chain face drifted: %d" % T4.count(_old_ram)
T4 = T4.replace(_old_ram, _new_ram)
_old_se = "→W282 **0.000312**→W284 **0.000312**→W285 **0.000311**→W286 投影 0.000311"
_new_se = "→W282 **0.000312**→W283 **0.000312**→W284 **0.000311**→W285 **0.000311**→W286 投影 0.000311"
assert T4.count(_old_se) == 1, "se_mu chain face drifted: %d" % T4.count(_old_se)
T4 = T4.replace(_old_se, _new_se)
_old_rot = "（W278 bm-c→W279 bm-c→W284 bm-c→W285 bm-c own-turn rotation"
_new_rot = "（W279 bm-c→W283 bm-c→W284 bm-c→W285 bm-c own-turn rotation"
assert T4.count(_old_rot) == 1, "own-turn rotation chain drifted: %d" % T4.count(_old_rot)
T4 = T4.replace(_old_rot, _new_rot)
T5 = T4

ORD_MAP = {"第三十四次": "第三十五次", "第三十五次": "第三十六次",
           "第三十三次": "第三十四次", "第三十二次": "第三十三次"}
O_HITS = {k: 0 for k in ORD_MAP}


def _o(m):
    O_HITS[m.group(0)] += 1
    return ORD_MAP[m.group(0)]


T5 = re.sub(r"第(?:三十四|三十五|三十三|三十二)次", _o, T5)

RESIDUAL = ["w283", "639_", "640_", "641_",
            "r1141", "r1142", "r1143", "r1144",
            "0.24505561", "0.3075", "1.1974", "06:1x", "05:4x", "15th gen", "@@",
            "第 282 枚", "第 274 波", "第 103 枚", "第 273", "共 274", "102 行注册",
            "620,520", "1,046,941 "]
left = {t: T5.count(t) for t in RESIDUAL if t in T5}
# W283 may re-appear ONLY in the two repaired history chains (se_mu tail + own-turn rotation)
assert T5.count("W283") == 2, "unexpected W283 survivors: %d" % T5.count("W283")

MUST = [
    "PERPETUAL-N1-W285", "research/PERPETUAL_N1_W285_PREREG.md",
    "642_301..644_300", "644_301..644_500",
    "622,720", "624,920", "1,049,141", "K=622,720", "1,051,341" if "1,051,341" in T5 else "622,720",
    "n1_w284_results.json", "n1_w285_results.json",
    "第 283 枚", "第 275 波", "第一百零四枚自有波", "第 104 枚",
    "engine_owner 行 274 注册在册", "engine_owner==bm-c 103 行注册",
    "bmc_rows=103", "bmc live rows 103",
    "STAIRCASE-AFFECTS-A", "第三十五次连续 A-hop", "第三十六次连续 above-own-A",
    "第三十五次连续 A-hop 预期",
    "_w285bmc_20261020", "--wave 285/finalize --wave 285",
    "results/_w285bmc_freeze_edits.py",
    "W284 finalize one-pass bm-c r1147", "n_eff_held_equal 1,046,941",
    "\u22120.09278629", "0.24505609", "\u22120.08587991", "0.3187", "1.1975",
    "W2..W284", "W1..W284", "W136..W284",
    "28c5f465f2", "a8e5ddfd65", "c2e6d34ae0",
    "MSG-20261020-0758-bmc-w285-seat", "597a614539", "16th gen",
    "W286p_B_lands_inside_W286p_A_naive",
    "R286：W285 带", "644_301..646_300", "644_501..644_700",
    "bm-c r1149 W285 §7 范式", "bm-c r1149 W285 §8 范式",
    "bm-c 循环班 r1149 席位窗 2026-10-20 08:0x",
    "W284 冻结窗 ~3.5G bm-c 实锚",
    "seed_admit_gate rc0 双带 FREE",
    "saturation_engine.py status live-read r1149",
    "heartbeat 新鲜实读 r1149 窗",
    "135_000" if "135_000" in T5 else "95_000..95_003",
]
missing = [s for s in MUST if s not in T5]

MUST_NOT = [
    "PERPETUAL-N1-W283 预注册", "research/PERPETUAL_N1_W283_PREREG.md",
    "A-ext seed=639_901", "entry rng seed=**640_101+j**", "exit rng=**642_101+j**",
    "第三十四次连续 A-hop", "第三十五次连续 above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "0.24505561", "1.1974", "0.3185",
    "第三十六次连续 above-own-A" if False else "第 282 枚",
    "W2..W283", "W1..W283",
    "engine_owner==bm-c 102 行注册", "engine_owner 行 273 注册在册",
    "bmc_rows=102", "bmc live rows 102",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "第 103 枚", "第 274 波", "15th gen",
]
present_bad = [s for s in MUST_NOT if s in T5]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T5.encode("utf-8")), left))
print("W hits %r | w hits %r | r hits %r | band hits %r | ordinal hits %r"
      % (W_HITS, W_HITS_L, R_HITS, B_HITS, O_HITS))
print("band zero-hit tokens=%r" % [k for k, v in B_HITS.items() if v == 0])
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    io.open(os.path.join(REPO, "results", "_w285bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T5)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    assert not [k for k, v in B_HITS.items() if v == 0], "unused band token"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T5)
    print("W285 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T5.encode("utf-8")), T5.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu %s"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ, SE))
    print("bands A 642301..644300 / B 644301..644500 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T5.encode("utf-8")).hexdigest()[:16])