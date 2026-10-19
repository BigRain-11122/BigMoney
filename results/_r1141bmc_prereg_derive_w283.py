# -*- coding: utf-8 -*-
# r1141 bm-c: W283 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W282 prereg pre-run face (results/_w283bmc_w282_frozen_face.txt =
#       git show 7744416654:research/PERPETUAL_N1_W282_PREREG.md, the freeze-commit face
#       with sec.7/sec.8 placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law: wave-label shift FIRST (W283->W284, W282->W283, W281->W282), then the
# W282 chain-fact rules operate on the SHIFTED face, so inserted W282 facts are not
# shifted a second time.
# DST = research/PERPETUAL_N1_W283_PREREG.md
import hashlib, io, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w283bmc_w282_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W283_PREREG.md")
FREEZE_COMMIT = "7744416654"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W282_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W282 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1139bmc_w282_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w283bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W282 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W283 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [637901, 639900] and rc["bands"]["B"] == [639901, 640100], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (272, 272, 101, 273), "leg0 drift"
assert _l0["w281_bands"] == {"A": [635701, 637700], "B": [637701, 637900]}, "W282 band drift"
assert _l0["inflight_upstream"] is False and _l0["w281_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [637901, 639900] and _l1["B"] == [639901, 640100], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W284p_A_naive"] == "639_901..641_900" and _l4["W284p_B_naive"] == "640_101..640_300"
assert _l4["W284p_B_lands_inside_W284p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w282_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w282"]; LINEM = hk["skill_line"]["line_merged_618320"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
assert (K, LEDGER, NEFF) == (618320, 1044735, 1042535)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09281590" and "%.8f" % ONLY_MU == "-0.08849418" and "%.8f" % SIG == "0.24506546"
assert P95 == 0.3075
assert (KLIFT, LINEPRE, LINEM) == (0.0, 1.1973, 1.1973)
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 620520 and LEDGER_PROJ == 1046935 and NEFF_PROJ == 1044735

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
add("0.24507389**=W281 合并池实测", "0.24506546**=W281 合并池实测")
add("p95（**0.3228** 实测锚）", "p95（**0.3075** 实测锚）")
add("键 W281 实测 K-lift **−0.0001**·line_merged@K616,120 **1.1972**·line_pre_w281 1.1973·n_eff_held_equal 1,040,335；se_mu 收窄链 …→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W281 **0.000312**→W282 投影 0.000312】",
    "键 W281 实测 K-lift **+0.0000**·line_merged@K618,320 **1.1973**·line_pre_w281 1.1973·n_eff_held_equal 1,042,535；se_mu 收窄链 …→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000312**→W281 **0.000312**→W282 投影 0.000312】")
add("（W281 finalize 已落地 03:2x）", "（W281 finalize 已落地 04:4x）")
add("·03:2x finalize one-pass】", "·04:4x finalize one-pass】")
add("bm-c 循环班 r1137 席位窗 2026-10-20 03:4x", "bm-c 循环班 r1137 席位窗 2026-10-20 05:0x")
add("零 skip-ahead W283/W284 席位声明", "零 skip-ahead W284/W285 席位声明")

# ---------- phase 1: wave-label shift (descending; no cascade) ----------
add("W283", "W284")
add("W282", "W283")
add("W281", "W282")
add("w283", "w284")
add("w282", "w283")
add("w281", "w282")

# ---------- phase 2: W282 chain / seat facts on the SHIFTED face ----------
add("bm-c r1134 五面冻结 splice aa376549cd 落地 03:0x·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 13th gen）",
    "bm-c r1138 五面冻结 splice 01fe28eec2 落地 04:1x·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 14th gen）")
add("W282 finalize one-pass bm-c r1135 窗 03:2x·estate chain r1133/r1134/r1135 W282 全周期 f51afd09ad+aa376549cd+fbd1511689",
    "W282 finalize one-pass bm-c r1139 窗 04:4x·estate chain r1137/r1138/r1139 W282 全周期 7744416654+01fe28eec2+8b5730bec4")
add("W282 finalize one-pass bm-c r1135 窗 03:2x】】", "W282 finalize one-pass bm-c r1139 窗 04:4x】】")
add("（r1133/r1134/r1135 W282 全周期先例实时间线：prereg f51afd09ad 落于 r1133 窗·splice aa376549cd 落于 r1134 执行窗 03:0x——**W283 freeze 面：W282 own-wave finalize 已落地=席位时即解锁——席位 r1136 窗+prereg r1137 窗落地",
    "（r1137/r1138/r1139 W282 全周期先例实时间线：prereg 7744416654 落于 r1137 窗·splice 01fe28eec2 落于 r1138 执行窗 04:1x——**W283 freeze 面：W282 own-wave finalize 已落地=席位时即解锁——席位 r1140 窗+prereg r1141 窗落地")
add("·ledger append 806aefddd1+8c9247edbe", "·ledger append 记录见 n1_w282_results.json science_gates 段（禁手抄 r583）")
add("bm-c 循环班 r1137 席位窗", "bm-c 循环班 r1141 席位窗")
add("bmc_rows=100 attempt-continuity face（r1136 窗算法·bm-c own seat+bmc live rows 100 实读）——freeze 时 live derive bmc rows 100+候选=第 101 枚 EXACT",
    "bmc_rows=101 attempt-continuity face（r1140 窗算法·bm-c own seat+bmc live rows 101 实读）——freeze 时 live derive bmc rows 101+候选=第 102 枚 EXACT")
add("bmc rows 100+候选=第 101 枚 EXACT", "bmc rows 101+候选=第 102 枚 EXACT")
add("MSG-20261020-@@SEAT_HHMM@@-bmc-w284-seat 已推 origin @@SEAT_SHA@@",
    "MSG-20261020-0500-bmc-w283-seat 已推 origin 8528d823fa")
add("MSG-20261020-@@SEAT_HHMM@@-bmc-w283-seat 先推 origin @@SEAT_SHA@@",
    "MSG-20261020-0500-bmc-w283-seat 先推 origin 8528d823fa")
add("（bm-c r1137 席位 MSG-20261020-0500-bmc-w283-seat", "（bm-c r1140 席位 MSG-20261020-0500-bmc-w283-seat")
add("r1137 席位窗实跑", "r1140 席位窗实跑")
add("（bm-c r1137 席·queue-head", "（bm-c r1140 席·queue-head")
add("live-read r1137", "live-read r1141")
add("heartbeat 新鲜实读 r1137 窗", "heartbeat 新鲜实读 r1141 窗")
add("bm-c r1137 W283 §7 范式", "bm-c r1141 W283 §7 范式")
add("bm-c r1137 W283 §8 范式", "bm-c r1141 W283 §8 范式")

# ---------- phase 3: live faces (RAM / VRAM / freeze-window chain) ----------
add("本窗 free RAM 1.7GB", "本窗 free RAM %sGB" % RAM_FACE)
add("nvidia-smi 实读 2.0G VRAM 占用", "nvidia-smi 实读 %s VRAM 占用" % VRAM_G)
add("·W282 冻结窗 ~2.4G bm-c 实锚·本窗冻结窗 ~1.7G bm-c 实锚）",
    "·W281 冻结窗 ~2.4G bm-c 实锚·W282 冻结窗 ~1.7G bm-c 实锚·本窗冻结窗 ~%sG bm-c 实锚）" % RAM_FACE)

# ---------- phase 4: chain anchors / measured key numbers ----------
add("净账本锚头 **1,042,535**", "净账本锚头 **1,044,735**")
add("净账本锚头 1,042,535", "净账本锚头 1,044,735")

add("累计 null 池=616,120+2,200（本波）=**618,320 投影**",
    "累计 null 池=618,320+2,200（本波）=**620,520 投影**")
add("已落账 616,120 实测", "已落账 618,320 实测")
add("K=616,120 合并池", "K=618,320 合并池")
add("**−0.09283133**", "**−0.09281590**")
add("**−0.08854614**", "**−0.08849418**")

# ---------- phase 5: ordinal / count faces ----------
add("第三十三次连续 above-own-A", "第三十四次连续 above-own-A")
add("第三十二次连续 A-hop", "第三十三次连续 A-hop")
add("连续三十一波如实注记", "连续三十二波如实注记")
add("engine_owner 行 271 注册在册", "engine_owner 行 272 注册在册")
add("engine_owner==bm-c 100 行注册", "engine_owner==bm-c 101 行注册")
add("共二百八十面实测", "共二百八十一面实测")
add("池第 280 枚", "池第 281 枚")
add("第 272 波", "第 273 波")
add("第一百零一枚自有波", "第一百零二枚自有波")
add("波号 282", "波号 283")
add("零 282 行", "零 283 行")
add("R283", "R284")
add("→W280 **0.000312**→W282 **0.000312**", "→W280 **0.000312**→W281 **0.000312**→W282 **0.000312**")
add("--wave 282/finalize --wave 282", "--wave 283/finalize --wave 283")

# ---------- phase 6: band / seed / base arithmetic ----------
add("637_701..639_700", "639_901..641_900")   # W284p A naive (projection-only instances)
add("637_901..638_100", "640_101..640_300")   # W284p B naive (projection-only instances)
add("637_701..637_900", "639_901..640_100")   # own B (W282) -> own B (W283)
add("635_701..637_700", "637_901..639_900")   # own A (W282) -> own A (W283)
add("635_501..635_700", "637_701..637_900")   # registered W281 B -> registered W282 B
add("635_501..637_500", "637_701..639_700")   # W283 A naive -> W284 A naive (pre-shift numbers)
add("635_701..635_900", "637_901..638_100")   # W283 B naive
add("637_701+j", "639_901+j")                 # exit rng
add("635_701+j", "637_901+j")                 # entry rng (A and B entry)
add("637_700+1", "639_900+1")                 # own-A tail + 1
add("635_700+1", "637_900+1")                 # registered prior B tail + 1
add("jump 635_701", "jump 637_901")           # hop-chain jump target
add("635_700", "637_900")                     # bare registered-W282-B tail (post-band-face)
add("635_500", "637_700")                     # bare prior-wave A tail

T1 = T0
COUNT = []
for old, new in RULES:
    c = T1.count(old)
    if c == 0:
        raise SystemExit("RULE MISS (zero hits): %r" % old[:100])
    T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

RESIDUAL = ["w281", "635_", "633_", "r1133", "r1134", "r1135", "r1136", "616,120",
            "1,040,335", "0.24507389", "0.3228", "1.1972", "03:2x", "03:4x", "01:5x",
            "1.7GB", "13th gen", "第 101 枚", "第 272 波", "共二百八十面实测", "wave 282",
            "@@SEAT", "805aefddd1", "806aefddd1"]
left = {t: T1.count(t) for t in RESIDUAL if t in T1}

MUST = [
    "PERPETUAL-N1-W283", "research/PERPETUAL_N1_W283_PREREG.md",
    "637_901..639_900", "639_901..640_100",
    "618,320", "1,044,735", "K=618,320", "620,520",
    "n1_w282_results.json", "n1_w283_results.json",
    "池第 281 枚", "第一百零二枚", "第 273 波", "第 102 枚",
    "STAIRCASE-AFFECTS-A", "第三十三次连续 A-hop", "第三十四次连续 above-own-A",
    "_w283bmc_20261020", "--wave 283/finalize --wave 283",
    "W282 finalize one-pass bm-c r1139", "n_eff_held_equal 1,042,535",
    "−0.09281590", "0.24506546", "−0.08849418", "0.3075",
    "共二百八十一面", "W2..W282", "W1..W282",
    "engine_owner==bm-c 101 行注册", "engine_owner 行 272 注册在册",
    "bmc_rows=101 attempt-continuity face", "bmc live rows 101",
    "bm-c 循环班 r1141 席位窗", "7744416654", "01fe28eec2", "8b5730bec4",
    "W284+ 投影", "W284p_B_lands_inside_W284p_A_naive", "verify at W284 prereg",
    "results/_w283bmc_freeze_edits.py", "_w282bmc_freeze_edits.py 模板派生",
    "bm-c r1141 W283 §7 范式", "bm-c r1141 W283 §8 范式",
    "（上游 W282 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W281 冻结窗", "W282 冻结窗 ~1.7G bm-c 实锚",
    "席位时即解锁", "R284：W283 带",
    "637_900+1", "639_900+1",
    "A_staircase_hop_past_W282_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 283", "零 283 行", "零 skip-ahead W284/W285 席位声明",
    "04:4x", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "saturation_engine.py status live-read r1141",
    "heartbeat 新鲜实读 r1141 窗", "nvidia-smi 实读",
    "MSG-20261020-0500-bmc-w283-seat", "8528d823fa",
]
missing = [s for s in MUST if s not in T1]

MUST_NOT = [
    "PERPETUAL-N1-W282 预注册", "research/PERPETUAL_N1_W282_PREREG.md",
    "A-ext seed=635_701", "entry rng seed=**635_701+j**", "exit rng=**637_701+j**",
    "第三十一次连续 A-hop", "第三十二次连续 above-own-A",
    "GATED on", "finalize PENDING", "queue_depth",
    "−0.09283133", "0.24507389", "−0.08854614", "0.3228",
    "共二百八十面", "W2..W281", "W1..W281",
    "engine_owner==bm-c 100 行注册", "engine_owner 行 271 注册在册",
    "bmc_rows=100", "bmc live rows 100",
    "f51afd09ad", "aa376549cd", "fbd1511689",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@", "@@SEAT",
    "第 101 枚", "第 272 波", "第一百零一枚", "池第 280 枚", "波号 282", "零 282 行",
]
present_bad = [s for s in MUST_NOT if s in T1]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T1.encode("utf-8")), left))
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    io.open(os.path.join(REPO, "results", "_w283bmc_dry.txt"), "w", encoding="utf-8", newline="").write(T1)
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T1)
    print("W283 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T1.encode("utf-8")), T1.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu 0.000312"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ))
    print("bands A 637901..639900 / B 639901..640100 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T1.encode("utf-8")).hexdigest()[:16])