# -*- coding: utf-8 -*-
# r1133 bm-c: W281 prereg derive (count-asserted substitution chain, same discipline as r1130 W280).
#
# SRC = frozen W280 prereg face (results/_w281bmc_w280_frozen_face.txt, pre-run face with §7/§8
#       placeholders; HEAD twin post-backfill is NOT used -- r1049/r1052 law).
# DST = research/PERPETUAL_N1_W281_PREREG.md
import hashlib, io, json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "results"))
from _r1133bmc_pairs_w281 import PAIRS  # noqa: E402

SRC = os.path.join(REPO, "results", "_w281bmc_w280_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W281_PREREG.md")
SRC_BYTES, SRC_SHA16 = 23767, "e34a383ea57a718b"
FREEZE_COMMIT = "5f279e44fc"


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
assert len(T0.encode("utf-8")) == SRC_BYTES, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == SRC_SHA16, "SRC sha mismatch"
_frozen_blob = git_out(["rev-parse", FREEZE_COMMIT + ":research/PERPETUAL_N1_W280_PREREG.md"])
assert git_out(["hash-object", SRC]) == _frozen_blob, "SRC blob mismatch vs freeze commit"

# ---------------- live chain values ----------------
hk = json.load(io.open(os.path.join(REPO, "results", "_r1132bmc_w280_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w281bmc_20261020_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W280 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W281 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [633501, 635500] and rc["bands"]["B"] == [635501, 635700], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (270, 270, 99, 271), "leg0 drift"
assert _l0["w280_bands"] == {"A": [631301, 633300], "B": [633301, 633500]}, "W280 band drift"
assert _l0["inflight_upstream"] is False and _l0["w280_finalize_landed"] is True
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [633501, 635500] and _l1["B"] == [635501, 635700], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
_ra = _l1["relation_asserts"]
assert _ra["A_staircase_hop_past_registered_W280_B"] is True
assert _ra["B_base_eq_own_A_tail_plus1"] is True and _ra["B_hop_lands_inside_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert rc["legs"]["leg2"]["AB_mutual_exclusion"] is True
assert rc["legs"]["leg3"]["bands_clear"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W282p_A_naive"] == "635_501..637_500" and _l4["W282p_B_naive"] == "635_701..635_900"
assert _l4["W282p_B_lands_inside_W282p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w280_only"]["mu"]; ONLY_SIG = hk["w280_only"]["sigma"]
P95 = hk["a_band"]["full_sharpe_p95"]; P99 = hk["a_band"]["full_sharpe_p99"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w280"]; LINEM = hk["skill_line"]["line_merged_613920"]
KLIFT = hk["skill_line"]["k_lift_delta"]
LEDGER = hk["ledger_identity"]["total"]
assert (K, LEDGER, NEFF) == (613920, 1040335, 1038135)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
_mu8 = "%.8f" % MU; _only8 = "%.8f" % ONLY_MU; _sig8 = "%.8f" % SIG
assert _mu8 == "-0.09284669" and _only8 == "-0.09925886" and _sig8 == "0.24507971", (_mu8, _only8, _sig8)
assert P95 == 0.3294 and P99 == 0.4598
assert (KLIFT, LINEPRE, LINEM) == (0.0001, 1.1971, 1.1972)

K_PROJ = K + 2200
LEDGER_PROJ = LEDGER + 2200
NEFF_PROJ = NEFF + 2200
assert K_PROJ == 616120 and LEDGER_PROJ == 1042535 and NEFF_PROJ == 1040335

# ---------------- live RAM / VRAM face ----------------
try:
    import psutil
    RAM_GB = psutil.virtual_memory().available / (1024 ** 3)
except Exception:
    RAM_GB = 0.0
RAM_FACE = "%.1f" % RAM_GB
VRAM_G = "2.0G"
try:
    _p = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                        capture_output=True)
    if _p.returncode == 0:
        _mib = int(_p.stdout.decode("utf-8", "replace").strip().splitlines()[0])
        VRAM_G = "%.1fG" % (_mib / 1024.0)
except Exception:
    pass

# ---------------- engine live face ----------------
ENG_OK = None
try:
    _p = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                        capture_output=True, cwd=REPO)
    ENG_OK = (_p.returncode == 0)
except Exception:
    ENG_OK = False

# ================= substitutes =================
T1 = T0
APPLIED = 0
for old, new, expect in PAIRS:
    c = T1.count(old)
    if c != expect:
        raise SystemExit("PAIR FAIL count=%d expect=%d old=%r" % (c, expect, old[:120]))
    T1 = T1.replace(old, new)
    APPLIED += 1

T2 = (T1.replace("@@RAM_FACE@@", RAM_FACE)
        .replace("@@VRAM_G@@", VRAM_G))

# ================= gates =================
MUST = [
    "PERPETUAL-N1-W281", "research/PERPETUAL_N1_W281_PREREG.md",
    "633_501..635_500", "635_501..635_700",
    "613,920", "1,040,335", "K=613,920", "616,120",
    "n1_w280_results.json", "n1_w281_results.json",
    "池第 279 枚", "第一百枚", "第 271 波", "第 100 枚",
    "STAIRCASE-AFFECTS-A", "第三十一次连续 A-hop", "第三十二次连续 above-own-A",
    "_w281bmc_20261020", "--wave 281/finalize --wave 281",
    "W280 finalize one-pass bm-c r1131", "n_eff_held_equal 1,038,135",
    "−0.09284669", "0.24507971", "−0.09925886", "0.3294",
    "实差 0.0064 在带内", "共二百七十九面", "W2..W280", "W1..W280",
    "engine_owner==bm-c 99 行注册", "engine_owner 行 270 注册在册",
    "bmc_rows=99 attempt-continuity face", "bmc live rows 99",
    "bm-c 循环班 r1133 席位窗", "W281=bm-c own-wave window per chain-order law",
    "5f279e44fc", "7a5b47ff94", "341a90637a",
    "W282+ 投影", "W282p_B_lands_inside_W282p_A_naive", "verify at W282 prereg",
    "results/_w281bmc_freeze_edits.py", "_w280bmc_freeze_edits.py 模板派生",
    "bm-c r1133 W281 §7 范式", "bm-c r1133 W281 §8 范式",
    "（上游 W280 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W279 冻结窗 ~2.2G bm-c 实锚", "W280 冻结窗 ~2.2G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R282：W281 带",
    "633_500+1", "635_500+1",
    "A_staircase_hop_past_W280_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 281", "零 281 行", "零 skip-ahead W282/W283 席位声明",
    "02:0x", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "saturation_engine.py status live-read r1133",
    "heartbeat 新鲜实读 r1133 窗", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1133 窗实读",
    "nvidia-smi 实读", "W281 带与 v1 在用带",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "PERPETUAL-N1-W280 预注册", "research/PERPETUAL_N1_W280_PREREG.md",
    "A-ext seed=631_301", "entry rng seed=**631_301+j**", "exit rng=**633_301+j**",
    "第二十九次连续 A-hop", "第三十次连续 above-own-A", "第三十次连续 A-hop",
    "连续二十九波",
    "GATED on", "finalize PENDING", "queue_depth",
    "−0.09282363", "0.24506025", "−0.10331555", "0.3104",
    "实差 0.0105 在带内", "共二百七十八面", "W2..W279", "W1..W279",
    "engine_owner==bm-c 98 行注册", "engine_owner 行 269 注册在册",
    "bmc_rows=98", "bmc live rows 98",
    "ba5c725b42", "3810f4a7ac", "6bdbdb9a07",
    "MSG-20261019-200x-bmc-w280-seat",
    "@@W281", "@@SPLICE", "@@RAM_FACE@", "@@VRAM", "@RAM_FACE@",
    "第 99 枚", "第 270 波", "第九十九枚", "池第 278 枚", "波号 280", "零 280 行",
    "finalize 已落地 20:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

assert T2.count("PERPETUAL-N1-W281") == 4, "batch count=%d" % T2.count("PERPETUAL-N1-W281")
assert T2.count("633_501..635_500") >= 8, "own-A count=%d" % T2.count("633_501..635_500")
assert T2.count("635_501..635_700") >= 6, "own-B count=%d" % T2.count("635_501..635_700")
assert T2.count("633_301..635_300") == 4, "A-naive count=%d" % T2.count("633_301..635_300")
assert T2.count("633_501..633_700") == 2, "B-naive count=%d" % T2.count("633_501..633_700")
assert T2.count("（占位·finalize one-pass 后回填") == 1 and T2.count("（占位·finalize 同窗回填") == 1
assert T2.count("（见 §5 item5）。") == 1
assert T2.count("W282+ 投影") >= 2
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W281 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("pairs applied: %d | src blob %s @ %s frozen pre-run face (HEAD twin disclosed, NOT used)"
      % (APPLIED, _frozen_blob[:12], FREEZE_COMMIT))
print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d -> %d | se_mu 0.000313"
      % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, NEFF_PROJ))
print("bands A %d..%d / B %d..%d | hops A=1 B=1 | live RAM %.2f GB | VRAM %s | engine rc-ok=%s"
      % (633501, 635500, 635501, 635700, RAM_GB, VRAM_G, ENG_OK))
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
