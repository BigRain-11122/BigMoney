# -*- coding: utf-8 -*-
# r1137 bm-c: W282 prereg derive (ordered substitution chain, count-measured, fail-closed).
# SRC = frozen W281 prereg face (results/_w282bmc_w281_frozen_face.txt = git show
#       f51afd09ad:research/PERPETUAL_N1_W281_PREREG.md, pre-run face with sec.7/sec.8
#       placeholders; HEAD twin is post-backfill and is NOT used -- r1049/r1052 law).
# Order law: wave-label shift FIRST (W282->W283, W281->W282, W280->W281), then the
# W281 chain-fact rules operate on the SHIFTED face, so inserted W281 facts are not
# shifted a second time.
# DST = research/PERPETUAL_N1_W282_PREREG.md
import hashlib, io, json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w282bmc_w281_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W282_PREREG.md")
FREEZE_COMMIT = "f51afd09ad"
DRY = "--apply" not in sys.argv


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W281_PREREG.md"])
assert git_out(["hash-object", SRC]) == _blob, "SRC blob mismatch vs W281 freeze commit"

hk = json.load(io.open(os.path.join(REPO, "results", "_r1135bmc_w281_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w282bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W281 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W282 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [635701, 637700] and rc["bands"]["B"] == [637701, 637900], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (271, 271, 100, 272), "leg0 drift"
assert _l0["w281_bands"] == {"A": [633501, 635500], "B": [635501, 635700]}, "W281 band drift"
assert _l0["inflight_upstream"] is False and _l0["w281_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [635701, 637700] and _l1["B"] == [637701, 637900], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
assert all((_l1["relation_asserts"] or {}).values()), "relation assert false: %r" % _l1["relation_asserts"]
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W283p_A_naive"] == "637_701..639_700" and _l4["W283p_B_naive"] == "637_901..638_100"
assert _l4["W283p_B_lands_inside_W283p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w281_only"]["mu"]
P95 = hk["a_band"]["full_sharpe_p95"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w281"]; LINEM = hk["skill_line"]["line_merged_616120"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
assert (K, LEDGER, NEFF) == (616120, 1042535, 1040335)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert "%.8f" % MU == "-0.09283133" and "%.8f" % ONLY_MU == "-0.08854614" and "%.8f" % SIG == "0.24507389"
assert P95 == 0.3228
assert (KLIFT, LINEPRE, LINEM) == (-0.0001, 1.1973, 1.1972)
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
assert K_PROJ == 618320 and LEDGER_PROJ == 1044735 and NEFF_PROJ == 1042535

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

RULES = []


def add(old, new):
    RULES.append((old, new))


# ---------- phase 0: measured-value rules authored on PRE-Shift labels ----------
add("键 **0.24507971**=W280 合并池实测", "键 **0.24507389**=W280 合并池实测")
add("W280 A 档 p95（**0.3294** 实测锚）", "W280 A 档 p95（**0.3228** 实测锚）")
add("键 W280 实测 K-lift **+0.0001**·line_merged@K613,920 **1.1972**·line_pre_w280 1.1971·n_eff_held_equal 1,038,135；se_mu 收窄链 …→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000313**→W281 投影 0.000313】",
    "键 W280 实测 K-lift **−0.0001**·line_merged@K616,120 **1.1972**·line_pre_w280 1.1973·n_eff_held_equal 1,040,335；se_mu 收窄链 …→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 **0.000313**→W280 **0.000312**→W281 投影 0.000312】")
add("（W280 finalize 已落地 02:0x）", "（W280 finalize 已落地 03:2x）")
add("n1_w280_results.json·N1 面最新已 finalize 键·02:0x finalize one-pass】",
    "n1_w280_results.json·N1 面最新已 finalize 键·03:2x finalize one-pass】")
add("bm-c 循环班 r1133 席位窗 2026-10-20 02:3x", "bm-c 循环班 r1137 席位窗 2026-10-20 03:4x")
add("零 skip-ahead W282/W283 席位声明", "零 skip-ahead W283/W284 席位声明")

# ---------- phase 1: wave-label shift (descending; no cascade) ----------
add("W282", "W283")
add("W281", "W282")
add("W280", "W281")
add("w282", "w283")
add("w281", "w282")
add("w280", "w281")

# ---------- phase 2: W281 chain / seat facts on the SHIFTED face ----------
add("r1133", "r1137")   # seat-window round label (runs before the fact rules insert chain rounds)
add("bm-c r1131 五面冻结 splice 7a5b47ff94 落地 01:5x·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 12th gen）",
    "bm-c r1134 五面冻结 splice aa376549cd 落地 03:0x·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 13th gen）")
add("W281 finalize one-pass bm-c r1131 窗 02:0x·estate chain r1129/r1130/r1131 W281 全周期 5f279e44fc+7a5b47ff94+341a90637a",
    "W281 finalize one-pass bm-c r1135 窗 03:2x·estate chain r1133/r1134/r1135 W281 全周期 f51afd09ad+aa376549cd+fbd1511689")
add("W281 finalize one-pass bm-c r1131 窗 02:0x】】", "W281 finalize one-pass bm-c r1135 窗 03:2x】】")
add("（r1129/r1130/r1131 W281 全周期先例实时间线：prereg 5f279e44fc 落于 r1130 窗·splice 7a5b47ff94 落于 r1131 执行窗 01:5x——**W282 freeze 面：W281 own-wave finalize 已落地=席位时即解锁——席位 r1132 窗+prereg r1137 窗落地",
    "（r1133/r1134/r1135 W281 全周期先例实时间线：prereg f51afd09ad 落于 r1133 窗·splice aa376549cd 落于 r1134 执行窗 03:0x——**W282 freeze 面：W281 own-wave finalize 已落地=席位时即解锁——席位 r1136 窗+prereg r1137 窗落地")
add("results/p2cal_ext/n1_w281/ 12/12·ledger append a4cf451113+982058016c",
    "results/p2cal_ext/n1_w281/ 12/12·ledger append 806aefddd1+8c9247edbe")

# ---------- phase 3: live faces (RAM / VRAM / freeze-window chain) ----------
add("本窗 free RAM 2.4GB", "本窗 free RAM %sGB" % RAM_FACE)
add("nvidia-smi 实读 1.8G VRAM 占用", "nvidia-smi 实读 %s VRAM 占用" % VRAM_G)
add("·W281 冻结窗 ~2.2G bm-c 实锚）",
    "·W280 冻结窗 ~2.2G bm-c 实锚·W281 冻结窗 ~2.4G bm-c 实锚·本窗冻结窗 ~%sG bm-c 实锚）" % RAM_FACE)

# ---------- phase 4: chain anchors / measured key numbers ----------
add("净账本锚头 1,040,335", "净账本锚头 1,042,535")
add("净账本锚头 **1,040,335**", "净账本锚头 **1,042,535**")
add("K=613,920 合并池", "K=616,120 合并池")
add("累计 null 池=613,920+2,200（本波）=**616,120 投影**",
    "累计 null 池=616,120+2,200（本波）=**618,320 投影**")
add("已落账 613,920 实测", "已落账 616,120 实测")
add("**−0.09284669**", "**−0.09283133**")
add("**−0.09925886**", "**−0.08854614**")
add("实差 0.0064 在带内", "实差 0.0043 在带内")

# ---------- phase 5: ordinal / count faces ----------
add("第三十二次连续 above-own-A", "第三十三次连续 above-own-A")
add("第三十一次连续 A-hop", "第三十二次连续 A-hop")
add("连续三十波如实注记", "连续三十一波如实注记")
add("engine_owner 行 270 注册在册", "engine_owner 行 271 注册在册")
add("bmc rows 99+候选=第 100 枚 EXACT", "bmc rows 100+候选=第 101 枚 EXACT")
add("bmc_rows=99 attempt-continuity face（r1132 窗算法·bm-c own seat+bmc live rows 99 实读）",
    "bmc_rows=100 attempt-continuity face（r1136 窗算法·bm-c own seat+bmc live rows 100 实读）")
add("引擎线第 271 波【bm-c 第一百枚自有波", "引擎线第 272 波【bm-c 第一百零一枚自有波")
add("共二百七十九面实测", "共二百八十面实测")
add("池第 279 枚", "池第 280 枚")
add("engine_owner==bm-c 99 行注册", "engine_owner==bm-c 100 行注册")
add("--wave 281/finalize --wave 281", "--wave 282/finalize --wave 282")
add("§5.5 W281+ 投影承接机证", "§5.5 W283+ 投影承接机证")

# ---------- phase 6: band / seed / base arithmetic ----------
add("635_501..637_500", "637_701..639_700")   # W283p A naive (projection-only instances)
add("635_701..635_900", "637_901..638_100")   # W283p B naive (projection-only instances)
add("635_501..635_700", "637_701..637_900")   # own B (W281) -> own B (W282)
add("633_501..635_500", "635_701..637_700")   # own A (W281) -> own A (W282)
add("633_301..633_500", "635_501..635_700")   # registered W280 B -> registered W281 B
add("633_301..635_300", "635_501..637_500")   # A naive -> W282 A naive
add("633_501..633_700", "635_701..635_900")   # B naive -> W282 B naive
add("635_501+j", "637_701+j")                 # exit rng
add("633_501+j", "635_701+j")                 # entry rng (A and B entry)
add("635_500+1", "637_700+1")                 # own-A tail + 1
add("633_500+1", "635_700+1")                 # registered W281 B tail + 1
add("jump 633_501", "jump 635_701")           # hop-chain jump target
add("633_500", "635_700")                     # bare registered-W281-B tail (post-band-face)
add("波号 281", "波号 282")
add("零 281 行", "零 282 行")
add("R282", "R283")
add("自注册 W281 A 尾 633_300 续", "自注册 W281 A 尾 635_500 续")

T1 = T0
COUNT = []
for old, new in RULES:
    c = T1.count(old)
    if c == 0:
        raise SystemExit("RULE MISS (zero hits): %r" % old[:100])
    T1 = T1.replace(old, new)
    COUNT.append((c, old[:64]))

RESIDUAL = ["w280", "633_", "r1129", "r1130", "r1131", "613,920",
            "1,038,135", "0.24507971", "0.3294", "1.1971", "02:0x", "02:3x", "01:5x",
            "2.4GB", "1.8G", "12th gen", "第 100 枚", "第 271 波", "二百七十九", "wave 281"]
left = {t: T1.count(t) for t in RESIDUAL if t in T1}

MUST = [
    "PERPETUAL-N1-W282", "research/PERPETUAL_N1_W282_PREREG.md",
    "635_701..637_700", "637_701..637_900",
    "616,120", "1,042,535", "K=616,120", "618,320",
    "n1_w281_results.json", "n1_w282_results.json",
    "池第 280 枚", "第一百零一枚", "第 272 波", "第 101 枚",
    "STAIRCASE-AFFECTS-A", "第三十二次连续 A-hop", "第三十三次连续 above-own-A",
    "_w282bmc_20261020", "--wave 282/finalize --wave 282",
    "W281 finalize one-pass bm-c r1135", "n_eff_held_equal 1,040,335",
    "−0.09283133", "0.24507389", "−0.08854614", "0.3228",
    "实差 0.0043 在带内", "共二百八十面", "W2..W281", "W1..W281",
    "engine_owner==bm-c 100 行注册", "engine_owner 行 271 注册在册",
    "bmc_rows=100 attempt-continuity face", "bmc live rows 100",
    "bm-c 循环班 r1137 席位窗", "W282=bm-c own-wave window per chain-order law",
    "f51afd09ad", "aa376549cd", "fbd1511689",
    "W283+ 投影", "W283p_B_lands_inside_W283p_A_naive", "verify at W283 prereg",
    "results/_w282bmc_freeze_edits.py", "_w281bmc_freeze_edits.py 模板派生",
    "bm-c r1137 W282 §7 范式", "bm-c r1137 W282 §8 范式",
    "（上游 W281 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W280 冻结窗 ~2.2G bm-c 实锚", "W281 冻结窗 ~2.4G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R283：W282 带",
    "635_700+1", "637_700+1",
    "A_staircase_hop_past_W281_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 282", "零 282 行", "零 skip-ahead W283/W284 席位声明",
    "03:0x", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "saturation_engine.py status live-read r1137",
    "heartbeat 新鲜实读 r1137 窗", "nvidia-smi 实读",
]
missing = [s for s in MUST if s not in T1]

MUST_NOT = [
    "PERPETUAL-N1-W281 预注册", "research/PERPETUAL_N1_W281_PREREG.md",
    "A-ext seed=633_501", "entry rng seed=**633_501+j**", "exit rng=**635_501+j**",
    "第二十九次连续 A-hop", "第三十次连续 above-own-A", "第三十次连续 A-hop",
    "GATED on", "finalize PENDING", "queue_depth",
    "−0.09284669", "0.24507971", "−0.09925886", "0.3294",
    "实差 0.0064 在带内", "共二百七十九面", "W2..W280", "W1..W280",
    "engine_owner==bm-c 99 行注册", "engine_owner 行 270 注册在册",
    "bmc_rows=99", "bmc live rows 99",
    "ba5c725b42", "3810f4a7ac", "6bdbdb9a07", "5f279e44fc", "7a5b47ff94", "341a90637a",
    "@@W281", "@@SPLICE", "@@VRAM", "@RAM_FACE@",
    "第 99 枚", "第 270 波", "第九十九枚", "池第 279 枚", "波号 281", "零 281 行",
]
present_bad = [s for s in MUST_NOT if s in T1]

print("rules=%d | out_bytes=%d | residual=%r" % (len(RULES), len(T1.encode("utf-8")), left))
print("missing MUST=%r" % missing)
print("present MUST_NOT=%r" % present_bad)
if DRY:
    for c, o in COUNT:
        print("  [%2d] %s" % (c, o))
    print("DRY-RUN only (pass --apply to write)")
else:
    assert not missing and not present_bad and not left, "gate failure -- abort"
    io.open(OUT, "w", encoding="utf-8", newline="").write(T1)
    print("W282 PREREG DERIVE OK -> %s (%d bytes, %d lines)"
          % (OUT, len(T1.encode("utf-8")), T1.count("\n") + 1))
    print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu 0.000312"
          % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ))
    print("bands A 635701..637700 / B 637701..637900 | hops A=1 B=1 | RAM %s GB | VRAM %s"
          % (RAM_FACE, VRAM_G))
    print("out sha256_16: %s" % hashlib.sha256(T1.encode("utf-8")).hexdigest()[:16])