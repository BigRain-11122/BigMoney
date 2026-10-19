# -*- coding: utf-8 -*-
# r1145 bm-c: W284 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W283 prereg pre-run face (results/_w284bmc_w283_frozen_face.txt =
#       git show 83b394ce64:research/PERPETUAL_N1_W283_PREREG.md, the freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law: next-wave label tokens are parked in placeholders FIRST (W285->@@W286@@, W284->@@W285@@),
# then the wave-label shift runs (W283->W284, W282->W283, W281->W282) so shifted labels never
# re-shift, then placeholders are restored. Band arithmetic runs longest/projection-first so that
# introduced band strings are never re-replaced (r1141 pattern).
# DST = research/PERPETUAL_N1_W284_PREREG.md
import hashlib, io, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w284bmc_w283_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W284_PREREG.md")
FREEZE_COMMIT = "83b394ce64"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W283_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W283 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1143bmc_w283_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w284bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W283 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W284 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [640101, 642100] and rc["bands"]["B"] == [642101, 642300], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (273, 273, 102, 274), "leg0 drift"
assert _l0["w281_bands"] == {"A": [637901, 639900], "B": [639901, 640100]}, "W283 band drift"
assert _l0["inflight_upstream"] is False and _l0["w281_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [640101, 642100] and _l1["B"] == [642101, 642300], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W285p_A_naive"] == "642_101..644_100" and _l4["W285p_B_naive"] == "642_301..642_500"
assert _l4["W285p_B_lands_inside_W285p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w283_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w283"]; LINEM = hk["skill_line"]["line_merged_620520"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
SE = hk["merged"]["se_mu_k620520"]
assert (K, LEDGER, NEFF) == (620520, 1046941, 1044741)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09281078" and "%.8f" % ONLY_MU == "-0.09137100" and "%.8f" % SIG == "0.24505561"
assert P95 == 0.3185
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.1974, 1.1974)
assert SE == 0.000311
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 622720 and LEDGER_PROJ == 1049141 and NEFF_PROJ == 1046941

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


def add(old, new):
    RULES.append((old, new))


# ---------- phase 0: measured-value rules authored on PRE-shift labels ----------
add("MSG-20261020-0500-bmc-w283-seat", "MSG-20261020-0635-bmc-w284-seat")
add("8528d823fa", "52cca74151")
add("0.24506546**=W282 合并池实测", "0.24505561**=W283 合并池实测")
add("p95（**0.3075** 实测锚）", "p95（**0.3185** 实测锚）")
add("键 W282 实测 K-lift **+0.0000**·line_merged@K618,320 **1.1973**·line_pre_w282 1.1973·n_eff_held_equal 1,042,535；se_mu 收窄链 …→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000312**→W281 **0.000312**→W282 **0.000312**→W283 投影 0.000312】",
    "键 W283 实测 K-lift **+0.0000**·line_merged@K620,520 **1.1974**·line_pre_w283 1.1974·n_eff_held_equal 1,044,741；se_mu 收窄链 …→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000312**→W281 **0.000312**→W282 **0.000312**→W283 **0.000311**→W284 投影 0.000311】")
add("（W282 finalize 已落地 04:4x）", "（W283 finalize 已落地 06:1x）")
add("键·04:4x finalize one-pass】", "键·06:1x finalize one-pass】")
add("r1139 窗 04:4x", "r1143 窗 06:1x")
add("bm-c 循环班 r1141 席位窗 2026-10-20 05:0x", "bm-c 循环班 r1145 席位窗 2026-10-20 06:4x")

# ---------- phase 1: next-wave tokens to placeholder (they must not be re-shifted) ----------
add("W285", "@@W286@@")
add("W284", "@@W285@@")

# ---------- phase 2: wave-label shift (descending; no cascade) ----------
add("W283", "W284")
add("W282", "W283")
add("W281", "W282")
add("w283", "w284")
add("w282", "w283")
add("R284", "R285")
add("@@W285@@", "W285")
add("@@W286@@", "W286")

# ---------- phase 3: W283 chain / seat facts on the SHIFTED face ----------
add("7744416654+01fe28eec2+8b5730bec4", "83b394ce64+44a3abdff3+0cef7d9e38")
add("r1141", "r1145")
add("r1140", "r1144")
add("r1139", "r1143")
add("r1138", "r1142")
add("r1137", "r1141")
add("7744416654", "83b394ce64")
add("01fe28eec2", "44a3abdff3")
add("splice 44a3abdff3 落地 04:1x", "splice 44a3abdff3 落地 05:4x")
add("执行窗 04:1x", "执行窗 05:4x")
add("14th gen", "15th gen")
add("bmc_rows=101 attempt-continuity face（r1144 窗算法·bm-c own seat+bmc live rows 101 实读）——freeze 时 live derive bmc rows 101+候选=第 102 枚 EXACT",
    "bmc_rows=102 attempt-continuity face（r1144 窗算法·bm-c own seat+bmc live rows 102 实读）——freeze 时 live derive bmc rows 102+候选=第 103 枚 EXACT")


# ---------- phase 4: chain anchors / measured key numbers ----------
add("累计 null 池=618,320+2,200（本波）=**620,520 投影**",
    "累计 null 池=620,520+2,200（本波）=**622,720 投影**")
add("净账本锚头 **1,044,735**", "净账本锚头 **1,046,941**")
add("净账本锚头 1,044,735", "净账本锚头 1,046,941")
add("freeze 时 live derive bmc rows 101+候选=第 102 枚 EXACT",
    "freeze 时 live derive bmc rows 102+候选=第 103 枚 EXACT")
add("618,320", "620,520")
add("**−0.09281590**", "**−0.09281078**")
add("**−0.08849418**", "**−0.09137100**")

# ---------- phase 5: ordinal / count faces ----------
add("第三十四次连续 above-own-A", "第三十五次连续 above-own-A")
add("第三十三次连续 A-hop", "第三十四次连续 A-hop")
add("第三十二次连续", "第三十三次连续")
add("第三十一次连续", "第三十二次连续")
add("连续三十二波如实注记", "连续三十三波如实注记")
add("engine_owner 行 272 注册在册", "engine_owner 行 273 注册在册")
add("engine_owner==bm-c 101 行注册", "engine_owner==bm-c 102 行注册")
add("共二百八十一面实测", "共二百八十二面实测")
add("池第 281 枚", "池第 282 枚")
add("第 273 波", "第 274 波")
add("第一百零二枚自有波", "第一百零三枚自有波")
add("波号 283", "波号 284")
add("零 283 行", "零 284 行")
add("--wave 283/finalize --wave 283", "--wave 284/finalize --wave 284")

# ---------- phase 6: band / seed / base arithmetic ----------
add("637_901+j", "640_101+j")                 # A/B entry rng seed base
add("639_901+j", "642_101+j")                 # B exit rng seed base
add("639_901..641_900", "642_101..644_100")   # W285p A naive (projection-only instances)
add("640_101..640_300", "642_301..642_500")   # W285p B naive (projection-only instances)
add("637_701..639_700", "639_901..641_900")   # W284 A naive
add("637_901..638_100", "640_101..640_300")   # W284 B naive
add("639_901..640_100", "642_101..642_300")   # own B (W283) -> own B (W284)
add("637_701..637_900", "639_901..640_100")   # registered W282 B -> registered W283 B
add("637_901..639_900", "640_101..642_100")   # own A (W283) -> own A (W284)
add("637_900+1", "640_100+1")                 # registered prior-B tail + 1
add("639_900+1", "642_100+1")                 # own-A tail + 1
add("637_900", "640_100")                     # bare registered-W283-B tail
add("637_700", "639_900")                     # bare prior-wave A tail
add("→jump 637_901·", "→jump 640_101·")       # A hop-chain jump target

# ---------- phase 7: live faces (RAM / VRAM) ----------
add("本窗 free RAM 3.6GB", "本窗 free RAM %sGB" % RAM_FACE)
add("nvidia-smi 实读 2.0G VRAM 占用", "nvidia-smi 实读 %s VRAM 占用" % VRAM_G)
add("·W283 冻结窗 ~1.7G bm-c 实锚·本窗冻结窗 ~3.6G bm-c 实锚）",
    "·W282 冻结窗 ~1.7G bm-c 实锚·W283 冻结窗 ~3.6G bm-c 实锚·本窗冻结窗 ~%sG bm-c 实锚）" % RAM_FACE)

T1 = T0
COUNT = []
for old, new in RULES:
    c = T1.count(old)
    if c == 0:
        raise SystemExit("RULE MISS (zero hits): %r" % old[:100])
    T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

RESIDUAL = ["w281", "W281", "637_", "635_", "633_", "r1137", "r1138", "r1139", "r1140",
            "618,320", "1,044,735", "1,042,535", "0.24506546", "0.3075", "1.1973",
            "04:4x", "14th gen", "@@", "1.7GB", "第 102 枚", "第 273 波", "共二百八十一面实测",
            "wave 283", "2026-10-20 05:0", "8528d823fa", "7744416654", "01fe28eec2", "8b5730bec4"]
left = {t: T1.count(t) for t in RESIDUAL if t in T1}

MUST = [
    "PERPETUAL-N1-W284", "research/PERPETUAL_N1_W284_PREREG.md",
    "640_101..642_100", "642_101..642_300",
    "620,520", "1,046,941", "K=620,520", "622,720",
    "n1_w283_results.json", "n1_w284_results.json",
    "池第 282 枚", "第一百零三枚", "第 274 波", "第 103 枚",
    "STAIRCASE-AFFECTS-A", "第三十四次连续 A-hop", "第三十五次连续 above-own-A",
    "_w284bmc_20261020", "--wave 284/finalize --wave 284",
    "W283 finalize one-pass bm-c r1143", "n_eff_held_equal 1,044,741",
    "−0.09281078", "0.24505561", "−0.09137100", "0.3185",
    "共二百八十二面", "W2..W283", "W1..W283",
    "engine_owner==bm-c 102 行注册", "engine_owner 行 273 注册在册",
    "bmc_rows=102 attempt-continuity face", "bmc live rows 102",
    "bm-c 循环班 r1145 席位窗", "83b394ce64", "44a3abdff3", "0cef7d9e38",
    "W285+ 投影", "W285p_B_lands_inside_W285p_A_naive", "verify at W285 prereg",
    "results/_w284bmc_freeze_edits.py", "_w283bmc_freeze_edits.py 模板派生",
    "bm-c r1145 W284 §7 范式", "bm-c r1145 W284 §8 范式",
    "（上游 W283 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W282 冻结窗", "W283 冻结窗 ~3.6G bm-c 实锚",
    "席位时即解锁", "R285：W284 带",
    "640_100+1", "642_100+1",
    "A_staircase_hop_past_W283_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 284", "零 284 行", "零 skip-ahead W285/W286 席位声明",
    "06:1x", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "saturation_engine.py status live-read r1145",
    "heartbeat 新鲜实读 r1145 窗", "nvidia-smi 实读",
    "MSG-20261020-0635-bmc-w284-seat", "52cca74151",
    "15th gen",
]
missing = [s for s in MUST if s not in T1]

MUST_NOT = [
    "PERPETUAL-N1-W283 预注册", "research/PERPETUAL_N1_W283_PREREG.md",
    "A-ext seed=637_901", "entry rng seed=**637_901+j**", "exit rng=**639_901+j**",
    "第三十二次连续 A-hop", "第三十三次连续 above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "−0.09281590", "0.24506546", "−0.08849418", "0.3075",
    "共二百八十一面", "W2..W282", "W1..W282",
    "engine_owner==bm-c 101 行注册", "engine_owner 行 272 注册在册",
    "bmc_rows=101", "bmc live rows 101",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "第 102 枚", "第 273 波", "第一百零二枚", "池第 281 枚", "波号 283", "零 283 行",
]
present_bad = [s for s in MUST_NOT if s in T1]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T1.encode("utf-8")), left))
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    io.open(os.path.join(REPO, "results", "_w284bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T1)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T1)
    print("W284 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T1.encode("utf-8")), T1.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu %s"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ, SE))
    print("bands A 640101..642100 / B 642101..642300 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T1.encode("utf-8")).hexdigest()[:16])