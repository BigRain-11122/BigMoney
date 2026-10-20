# -*- coding: utf-8 -*-
# r1152 bm-c: W286 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W285 prereg pre-run face (results/_w286bmc_w285_frozen_face.txt =
#       git show 3c12829cf9:research/PERPETUAL_N1_W285_PREREG.md, the r1149 freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law (r1149 lineage): measured values are rewritten FIRST with the pre-shift (this-wave)
# labels still in place, then wave/r labels shift in SINGLE regex passes (no cascade), then
# post-shift repairs (RAM freeze-anchor chain / se_mu chain / own-turn rotation) land last.
# Band tokens shift in a single-pass token map so an introduced range can never be re-mapped.
# Ordinal face: +2 shift (W286 self ordinals 37th A-hop / 38th above-own-A per the r1151 seat MSG);
# the prior prereg chain ran one behind the seat chain since W284 -- healed here, disclosed in receipt.
# DST = research/PERPETUAL_N1_W286_PREREG.md
import hashlib, io, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w286bmc_w285_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W286_PREREG.md")
FREEZE_COMMIT = "3c12829cf9"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W285_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W285 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1150bmc_w285_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w286bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W285 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W286 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [644501, 646500] and rc["bands"]["B"] == [646501, 646700], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (275, 275, 104, 276), "leg0 drift"
assert _l0["wprev_bands"] == {"A": [642301, 644300], "B": [644301, 644500]}, "W285 band drift"
assert _l0["wprev_minus1_bands"] == {"A": [640101, 642100], "B": [642101, 642300]}, "W284 band drift"
assert _l0["wprev_finalize_anchors"]["ledger_total"] == 1051341
assert _l0["wprev_finalize_anchors"]["merged_n"] == 624920
assert _l0["inflight_upstream"] is False and _l0["wprev_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [644501, 646500] and _l1["B"] == [646501, 646700], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert _l1["B_naive"] == [644501, 644700] and _l1["B_lands_above_own_A"] is True
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W287p_A_naive"] == "646_501..648_500" and _l4["W287p_A_first_clean"] == "646_501..648_500"
assert _l4["W287p_B_naive"] == "646_701..646_900" and _l4["W287p_B_first_clean"] == "646_701..646_900"
assert _l4["hops_A"] == 0 and _l4["hops_B"] == 0
assert _l4["W287p_B_lands_inside_W287p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w285_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w285"]; LINEM = hk["skill_line"]["line_merged_624920"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
SE = hk["merged"]["se_mu_k624920"]
assert (K, LEDGER, NEFF) == (624920, 1051341, 1049141)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09277606" and "%.8f" % ONLY_MU == "-0.08987918" and "%.8f" % SIG == "0.24506510"
assert P95 == 0.3188
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.1976, 1.1976)
assert SE == 0.00031
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 627120 and LEDGER_PROJ == 1053541 and NEFF_PROJ == 1051341

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
add("池第 283 枚", "池第 284 枚")
add("engine_owner 行 274 注册在册", "engine_owner 行 275 注册在册")
add("CLEAN-AT-BIRTH 16th gen", "CLEAN-AT-BIRTH 17th gen")
add("MSG-20261020-0758-bmc-w285-seat", "MSG-20261020-0855-bmc-w286-seat", 3)
add("597a614539", "ab76f5b0b3", 3)
add("28c5f465f2+a8e5ddfd65+c2e6d34ae0", "3c12829cf9+b097d23658+48df9ad768")
add("28c5f465f2", "3c12829cf9")
add("a8e5ddfd65", "b097d23658", 2)
add("0.24505609", "0.24506510")
# U+2212 minus (pre-register sign face)
add("\u22120.09278629", "\u22120.09277606")
add("\u22120.08587991", "\u22120.08987918")
add("共二百八十三面", "共二百八十四面")
add("实差 0.0069", "实差 0.0029")
add("0.3187", "0.3188")
add("1.1975", "1.1976", 2)
add("1,049,141", "1,051,341", 2)
add("1,046,941", "1,049,141")
add("=622,720+2,200（本波）=**624,920 投影**", "=624,920+2,200（本波）=**627,120 投影**")
add("622,720", "624,920", 5)
add("第 275 波", "第 276 波")
add("第一百零四枚自有波", "第一百零五枚自有波")
add("第 104 枚", "第 105 枚", 2)
add("engine_owner==bm-c 103 行注册", "engine_owner==bm-c 104 行注册")
add("bmc_rows=103", "bmc_rows=104")
add("bmc live rows 103", "bmc live rows 104")
add("bmc rows 103+候选", "bmc rows 104+候选", 2)
add("--wave 285/finalize --wave 285", "--wave 286/finalize --wave 286")
add("连续三十四波", "连续三十五波")
# stale chain faces healed this wave (r1149 derive missed the bare numbers; disclosed in receipt)
add("波号 284=注册表 W284 席后首个自由号", "波号 286=注册表 W285 席后首个自由号")
add("零 284 行", "零 286 行")
add("06:1x", "08:2x", 0)
add("07:1x", "08:2x", 2)
add("07:3x", "08:3x", 4)
add("08:0x", "09:0x")
add("本窗 free RAM 3.0GB", "本窗 free RAM %sGB" % RAM_FACE)
add("nvidia-smi 实读 2.0G VRAM", "nvidia-smi 实读 %s VRAM" % VRAM_G)

T1 = T0
COUNT = []
for old, new, n in RULES:
    c = T1.count(old)
    if c != n:
        raise SystemExit("RULE COUNT %d != %d: %r" % (c, n, old[:100]))
    if n:
        T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

# ---------- phase 1: wave labels, single simultaneous pass (no cascade) ----------
W_MAP = {"W283": "W284", "W284": "W285", "W285": "W286", "W286": "W287"}
W_HITS = {k: 0 for k in W_MAP}


def _w(m):
    W_HITS[m.group(0)] += 1
    return W_MAP[m.group(0)]


T2 = re.sub(r"W(?:283|284|285|286)", _w, T1)
w_MAP = {"w283": "w284", "w284": "w285", "w285": "w286"}
W_HITS_L = {k: 0 for k in w_MAP}


def _wl(m):
    W_HITS_L[m.group(0)] += 1
    return w_MAP[m.group(0)]


T2 = re.sub(r"w(?:283|284|285)", _wl, T2)
T2 = T2.replace("R286", "R287", 1)
# ---------- phase 2: r-label chain shift, single simultaneous pass ----------
R_MAP = {"r1145": "r1149", "r1146": "r1150", "r1147": "r1150",
         "r1148": "r1151", "r1149": "r1152"}
R_HITS = {k: 0 for k in R_MAP}


def _r(m):
    R_HITS[m.group(0)] += 1
    return R_MAP[m.group(0)]


T3 = re.sub(r"r114[5-9]", _r, T2)

# ---------- phase 3: band tokens, single-pass token map (no re-map of introduced ranges) ----------
B_MAP = {
    "642_100": "644_300",
    "642_101": "644_301",
    "642_300": "644_500",
    "642_301": "644_501",
    "642_500": "644_700",
    "644_100": "646_300",
    "644_300": "646_500",
    "644_301": "646_501",
    "644_500": "646_700",
    "644_501": "646_701",
    "644_700": "646_900",
    "646_300": "648_500",
}
B_HITS = {k: 0 for k in B_MAP}


def _b(m):
    B_HITS[m.group(0)] += 1
    return B_MAP[m.group(0)]


T4 = re.sub(r"\d{3}_\d{3}", _b, T3)

# ---------- phase 4: post-shift repairs ----------
_old_ram = "W285 冻结窗 ~3.5G bm-c 实锚·本窗冻结窗 ~3.0G bm-c 实锚"
_new_ram = "W285 冻结窗 ~3.0G bm-c 实锚·本窗冻结窗 ~%sG bm-c 实锚" % RAM_FACE
assert T4.count(_old_ram) == 1, "RAM anchor chain face drifted: %d" % T4.count(_old_ram)
T4 = T4.replace(_old_ram, _new_ram)
_old_se = "→W284 **0.000312**→W285 **0.000311**→W286 **0.000311**→W287 投影 0.000311"
_new_se = "→W284 **0.000311**→W285 **0.000311**→W286 **0.000310**→W287 投影 0.000310"
assert T4.count(_old_se) == 1, "se_mu chain face drifted: %d" % T4.count(_old_se)
T4 = T4.replace(_old_se, _new_se)
_old_rot = "（W279 bm-c→W284 bm-c→W285 bm-c→W286 bm-c own-turn rotation"
_new_rot = "（W283 bm-c→W284 bm-c→W285 bm-c→W286 bm-c own-turn rotation"
assert T4.count(_old_rot) == 1, "own-turn rotation chain drifted: %d" % T4.count(_old_rot)
T4 = T4.replace(_old_rot, _new_rot)
# r-label map cannot distinguish the W284-splice history label from the stale "freeze-window"
# label inherited since the W284 face (that one now resolves to r1149); pin it to THIS freeze window.
assert T4.count("heartbeat 新鲜 r1149 窗实读") == 1, "materialization anchor drifted"
T4 = T4.replace("heartbeat 新鲜 r1149 窗实读", "heartbeat 新鲜 r1152 窗实读")
# chain artifact: the parenthetical claimed THIS wave's finalize had landed; state the true upstream fact.
assert T4.count("（W286 finalize 已落地 08:3x）") == 1, "sec5 upstream face drifted"
T4 = T4.replace("（W286 finalize 已落地 08:3x）", "（W285 finalize 已落地 08:3x）")
T5 = T4

ORD_MAP = {"第三十五次": "第三十七次", "第三十六次": "第三十八次",
           "第三十四次": "第三十六次", "第三十三次": "第三十五次"}
O_HITS = {k: 0 for k in ORD_MAP}


def _o(m):
    O_HITS[m.group(0)] += 1
    return ORD_MAP[m.group(0)]

T5 = re.sub(r"第(?:三十五|三十六|三十四|三十三)次", _o, T5)

RESIDUAL = ["w283", "642_", "641_", "640_", "639_",
            "r1145", "r1146", "r1147", "r1148",
            "0.24505609", "0.3187", "1.1975", "07:1x", "07:3x", "08:0x", "16th gen", "@@",
            "第 283 枚", "第 275 波", "第 104 枚", "第 274", "共 283", "103 行注册",
            "622,720", "1,049,141 "]
left = {t: T5.count(t) for t in RESIDUAL if t in T5}
# W283 may re-appear ONLY in the own-turn rotation repair (history tail)
assert T5.count("W283") == 1, "unexpected W283 survivors: %d" % T5.count("W283")
# W287 (projection wave) must only appear in projection/carry-over clauses
assert T5.count("W287") >= 1

MUST = [
    "PERPETUAL-N1-W286", "research/PERPETUAL_N1_W286_PREREG.md",
    "644_501..646_500", "646_501..646_700",
    "624,920", "627,120", "1,051,341", "K=624,920",
    "n1_w285_results.json", "n1_w286_results.json",
    "第 284 枚", "第 276 波", "第一百零五枚自有波", "第 105 枚",
    "engine_owner 行 275 注册在册", "engine_owner==bm-c 104 行注册",
    "bmc_rows=104", "bmc live rows 104",
    "STAIRCASE-AFFECTS-A", "第三十七次连续 A-hop", "第三十八次连续 above-own-A",
    "_w286bmc_20261020", "--wave 286/finalize --wave 286",
    "results/_w286bmc_freeze_edits.py",
    "W285 finalize one-pass bm-c r1150", "n_eff_held_equal 1,049,141",
    "\u22120.09277606", "0.24506510", "\u22120.08987918", "0.3188", "1.1976",
    "W2..W285", "W1..W285", "W136..W285",
    "3c12829cf9", "b097d23658", "48df9ad768",
    "MSG-20261020-0855-bmc-w286-seat", "ab76f5b0b3", "17th gen",
    "W287p_B_lands_inside_W287p_A_naive",
    "R287：W286 带", "644_301..646_300", "644_501..644_700", "646_501..648_500", "646_701..646_900",
    "bm-c r1152 W286 §7 范式", "bm-c r1152 W286 §8 范式",
    "bm-c 循环班 r1152 席位窗 2026-10-20 09:0x",
    "W285 冻结窗 ~3.0G bm-c 实锚",
    "seed_admit_gate rc0 双带 FREE",
    "saturation_engine.py status live-read r1152",
    "heartbeat 新鲜实读 r1152 窗",
]
missing = [s for s in MUST if s not in T5]

MUST_NOT = [
    "PERPETUAL-N1-W284 预注册", "research/PERPETUAL_N1_W284_PREREG.md",
    "A-ext seed=642_301", "entry rng seed=**644_301+j**", "exit rng=**644_301+j**",
    "第三十五次连续 A-hop", "第三十六次连续 above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "0.24505609", "1.1975", "0.3187",
    "第 283 枚", "第 275 波", "第 104 枚", "16th gen",
    "W2..W284", "W1..W284",
    "engine_owner==bm-c 103 行注册", "engine_owner 行 274 注册在册",
    "bmc_rows=103", "bmc live rows 103",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "波号 284=注册表",
]
present_bad = [s for s in MUST_NOT if s in T5]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T5.encode("utf-8")), left))
print("W hits %r | w hits %r | r hits %r | band hits %r | ordinal hits %r"
      % (W_HITS, W_HITS_L, R_HITS, B_HITS, O_HITS))
print("band zero-hit tokens=%r" % [k for k, v in B_HITS.items() if v == 0])
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    io.open(os.path.join(REPO, "results", "_w286bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T5)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    assert not [k for k, v in B_HITS.items() if v == 0], "unused band token"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T5)
    print("W286 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T5.encode("utf-8")), T5.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu %s"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ, SE))
    print("bands A 644501..646500 / B 646501..646700 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T5.encode("utf-8")).hexdigest()[:16])