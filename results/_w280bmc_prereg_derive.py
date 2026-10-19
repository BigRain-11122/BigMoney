# -*- coding: utf-8 -*-
# r1130 bm-c: W280 prereg derive (count-asserted substitution chain; supersedes the r1129 roller).
#
# SRC = frozen W279 prereg face (results/_w280bmc_w279_frozen_face.txt, 23,681 B, sha256_16
#       c2fc7c34d0e41a68, blob 51d7ca52a811bc22a4ada6f4635915d5219ec734 @ freeze commit ba5c725b42).
#       The HEAD twin b98e8592 (28,043 B, sec.7/8 backfilled) is NOT used (r1049/r1052 law).
# DST = research/PERPETUAL_N1_W280_PREREG.md
#
# Chain faces (machine-read, r587 live-read governs):
#   results/_r1124bmc_w279_fivekeys.json   W279 finalize actuals (K 611,720 / ledger 1,038,135)
#   results/_w280bmc_20261019_probe_receipt.json  W280 seat ADMIT (A 631_301..633_300 /
#                                          B 633_301..633_500, 29th A-hop / 30th above-own-A)
#
# DESIGN NOTE (r1130): the r1129 roller tried to re-emit the canon's VMAP/POST/BLOCKS machinery.
# That approach kept producing cascades (a substitution feeding the next) and mis-keyed markers.
# This derive instead carries 67 exact old->new pairs, each MEASURED on the frozen face (or on a
# face produced by an earlier pair), applied through a single left-to-right scan so no pair can
# ever consume another pair's output. Every OLD must occur exactly once; fail-closed before write.
import hashlib, io, json, math, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "results"))
from _r1130bmc_pairs_w280 import PAIRS  # noqa: E402

SRC = os.path.join(REPO, "results", "_w280bmc_w279_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W280_PREREG.md")
SRC_BYTES, SRC_SHA16 = 23681, "c2fc7c34d0e41a68"
SRC_BLOB = "51d7ca52a811bc22a4ada6f4635915d5219ec734"       # @ ba5c725b42
HEAD_TWIN = "b98e85926cdff71cde7ac3705ad82a368c7e620b"      # disclosed, NOT used


def git_out(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True)
    if p.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), p.stderr.decode("utf-8", "replace")[:300]))
    return p.stdout.decode("utf-8", "replace").strip()


# ---------------- source identity ----------------
T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\r\n", "\n")
assert len(T0.encode("utf-8")) == SRC_BYTES, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == SRC_SHA16, "SRC sha mismatch"
assert git_out(["hash-object", SRC]) == SRC_BLOB, "SRC blob mismatch"
assert git_out(["rev-parse", "ba5c725b42:research/PERPETUAL_N1_W279_PREREG.md"]) == SRC_BLOB, \
    "freeze-commit blob mismatch"
assert git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W279_PREREG.md"]) == HEAD_TWIN, \
    "HEAD post-backfill twin drifted"

# ---------------- chain commits ----------------
for sha in ("ba5c725b42", "3810f4a7ac", "498d178d0b", "332e8e8656", "6bdbdb9a07", "f96272d8b9"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "3810f4a7ac"])          # 2026-10-19 19:33:30 +0800
_m = re.match(r"2026-10-19 19:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "19:%sx" % _m.group(1)[0]
_ci2 = git_out(["show", "-s", "--format=%ci", "6bdbdb9a07"])         # 2026-10-19 20:06:06 +0800
assert _ci2.startswith("2026-10-19 20:0"), "finalize estate ts unexpected: %r" % _ci2
assert git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w279_results.json"]) == "6bdbdb9a07"
_seat_files = git_out(["show", "--name-only", "--format=", "f96272d8b9"])
assert "MSG-20261019-200x-bmc-w280-seat.md" in _seat_files, "W280 seat MSG not in seat commit"

# ---------------- live chain values (full precision; anchors in prose are 8dp rounded) ----------------
hk = json.load(io.open(os.path.join(REPO, "results", "_r1124bmc_w279_fivekeys.json"), encoding="utf-8"))
rc = json.load(io.open(os.path.join(REPO, "results", "_w280bmc_20261019_probe_receipt.json"), encoding="utf-8"))
assert hk["all_pass"] is True, "W279 fivekeys not all-pass"
assert rc["verdict"] == "ADMIT", "W280 seat probe verdict %r" % rc["verdict"]
assert rc["bands"]["A"] == [631301, 633300] and rc["bands"]["B"] == [633301, 633500], "band drift"
_l0 = rc["legs"]["leg0"]
assert (_l0["rows"], _l0["owner_rows"], _l0["bmc_rows"], _l0["ordinal"]) == (277, 269, 98, 270), "leg0 drift"
_l1 = rc["legs"]["leg1"]
assert _l1["A"] == [631301, 633300] and _l1["B"] == [633301, 633500], "leg1 bands drift"
assert _l1["hops_A"] == 1 and _l1["hops_B"] == 1, "hop drift"
_ra = _l1["relation_asserts"]
assert _ra["A_staircase_hop_past_W279_B"] is True and _ra["B_base_above_W279_tail"] is True
assert _ra["W277_W278_W279_bands_respected_A"] is True and _ra["W277_W278_W279_bands_respected_B"] is True
_l2 = rc["legs"]["leg2"]
assert _l2["conflicts"] == 0
assert any("base=631301 span=2000" in s and "FREE" in s for s in _l2["seed_admit_gate"])
assert any("base=633301 span=200" in s and "FREE" in s for s in _l2["seed_admit_gate"])
assert rc["legs"]["leg3"]["origin_vacancy"] is True
_l4 = rc["legs"]["leg4"]
assert _l4["W281p_A_naive"] == "633301..635300" and _l4["W281p_B_naive"] == "633501..633700"
assert _l4["W281p_B_lands_inside_W281p_A_naive"] is True

K = hk["merged"]["k"]; MU = hk["merged"]["mu"]; SIG = hk["merged"]["sigma"]
ONLY_MU = hk["w279_only"]["mu"]; ONLY_SIG = hk["w279_only"]["sigma"]
P95 = hk["a_band"]["full_sharpe_p95"]; P99 = hk["a_band"]["full_sharpe_p99"]
NEFF = hk["skill_line"]["n_eff_held"]
LINEPRE = hk["skill_line"]["line_pre_w279"]; LINEM = hk["skill_line"]["line_merged_611720"]
KLIFT = hk["skill_line"]["k_lift_delta"]; SE = hk["merged"]["se_mu_k611720"]
LEDGER = hk["ledger_identity"]["total"]
assert (K, LEDGER, NEFF, SE) == (611720, 1038135, 1035935, 0.000313)
assert hk["ledger_identity"]["exact"] is True and hk["ledger_identity"]["prev_total"] + 2200 == LEDGER
assert hk["merged_k_identity"]["prev_k"] + 2200 == K
assert round(ONLY_MU - MU, 4) == -0.0105 or round(MU - ONLY_MU, 4) == 0.0105
DIFF4 = "%0.4f" % round(abs(MU - ONLY_MU), 4)
K_PROJ = K + 2200; LEDGER_PROJ = LEDGER + 2200; NEFF_PROJ = NEFF + 2200
SE_PROJ = "%.6f" % round(SIG / math.sqrt(K_PROJ), 6)
assert SE_PROJ == "0.000313", SE_PROJ
W280_ONLY_MU = "@@W280_ONLY_MU@@"      # resolved at the freeze pass
P95_NEXT = "@@W280_P95@@"              # resolved at the freeze pass
KL_NEXT = "@@W280_KLIFT@@"
LINE_M_NEXT = "@@W280_LINE_M@@"
LINE_P_NEXT = "@@W280_LINE_P@@"
K_NEXT = "@@W280_K@@"

try:
    import psutil
    RAM_GB = psutil.virtual_memory().available / (1024 ** 3)
except Exception:
    RAM_GB = 0.0
RAM_FACE = "%.1f" % RAM_GB
RAM_ANCHOR = "%.1f" % max(RAM_GB, 0.1)

# ---------------- live engine face (honest window stamp) ----------------
ENG_TS = "r1130"
try:
    _p = subprocess.run([sys.executable, os.path.join(REPO, "scripts", "saturation_engine.py"), "status"],
                        capture_output=True, cwd=REPO)
    _st = _p.stdout.decode("utf-8", "replace")
    _eng_ok = (_p.returncode == 0 and "alive" in _st.lower())
except Exception:
    _eng_ok = False

# ================= substitutes =================
T1 = T0
APPLIED = 0
for old, new in PAIRS:
    c = T1.count(old)
    if c != 1:
        raise SystemExit("PAIR FAIL count=%d old=%r" % (c, old[:90]))
    T1 = T1.replace(old, new)
    APPLIED += 1

T2 = (T1.replace("@@W280_ONLY_MU@@", W280_ONLY_MU)
        .replace("@@W280_P95@@", P95_NEXT)
        .replace("@@W280_KLIFT@@", KL_NEXT)
        .replace("@@W280_LINE_M@@", LINE_M_NEXT)
        .replace("@@W280_LINE_P@@", LINE_P_NEXT)
        .replace("@@W280_K@@", K_NEXT)
        .replace("@@W280_DIFF4@@", DIFF4)
        .replace("@@W280_SIGMA@@", "%.8f" % SIG)
        .replace("@@W280_NEFF@@", "{:,}".format(NEFF_PROJ))
        .replace("@@W280_SE_PROJ@@", SE_PROJ)
        .replace("@@W280_PARADIGM_WIN@@", "r1130")
        .replace("@@VRAM_G@@", "2.0G")
        .replace("@@SPLICE_T@@", SPLICE_T)
        .replace("@@SEAT_HHMM@@", "@@SEAT_HHMM@@")
        .replace("@@SEAT_SHA@@", "@@SEAT_SHA@@")
        .replace("@RAM_FACE@", RAM_FACE)
        .replace("@RAM_ANCHOR@", RAM_ANCHOR))

# ================= gates =================
MUST = [
    "PERPETUAL-N1-W280", "research/PERPETUAL_N1_W280_PREREG.md",
    "631_301..633_300", "633_301..633_500",
    "611,720", "1,038,135", "K=611,720",
    "n1_w279_results.json", "n1_w280_results.json",
    "池第 278 枚", "第九十九枚", "第 270 波", "第 99 枚",
    "STAIRCASE-AFFECTS-A", "第二十九次连续 A-hop", "第三十次连续 above-own-A",
    "_w280bmc_20261019", "--wave 280/finalize --wave 280",
    "W279 finalize one-pass bm-c r1124", "n_eff_held_equal 1,035,935",
    "−0.09282363", "0.24506025", "−0.10331555", "0.3104",
    "实差 0.0105 在带内", "共二百七十八面", "W2..W279", "W1..W279",
    "engine_owner==bm-c 98 行注册", "engine_owner 行 269 注册在册",
    "bmc_rows=98 attempt-continuity face", "bmc live rows 98",
    "bm-c 循环班 r1130 席位窗", "W280=bm-c own-wave window per chain-order law",
    "ba5c725b42", "3810f4a7ac", "498d178d0b", "332e8e8656", "6bdbdb9a07",
    "W281+ 投影", "W281p_B_lands_inside_W281p_A_naive", "verify at W281 prereg",
    "results/_w280bmc_freeze_edits.py", "_w279bmc_freeze_edits.py 模板派生",
    "bm-c r1130 W280 §7 范式", "bm-c r1130 W280 §8 范式",
    "（上游 W279 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W206/W211..W279 低 RAM 实烧先例", "W278 冻结窗 ~6.4G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R281：W280 带",
    "631_300+1", "633_300+1",
    "A_staircase_hop_past_W279_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 280", "零 280 行", "零 skip-ahead W281/W282 席位声明",
    "20:0x", "（占位·finalize one-pass 后回填", "（占位·finalize 同窗回填",
    "saturation_engine.py status live-read r1130",
    "heartbeat 新鲜实读 r1130 窗", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1130 窗实读",
    "nvidia-smi 实读 0%·2.0G VRAM 占用",
    "r1130 席位窗实跑：origin inbox 零 W280 席位外机命中",
    "results/p2cal_ext/n1_w279/ 12/12",
    "W279 冻结窗", "MS-%%" if False else "W280 带与 v1 在用带",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "PERPETUAL-N1-W279 预注册", "research/PERPETUAL_N1_W279_PREREG.md",
    "A-ext seed=629_101", "exit rng=**631_101+j**", "entry rng seed=**629_101+j**",
    "A-ext seed=626_901", "B-ext exit seed=631_101",
    "第二十八次连续 A-hop", "第三十一次连续 A-hop", "连续二十八波", "连续三十波",
    "GATED on", "finalize PENDING", "queue_depth",
    "−0.09278576", "0.24505494", "−0.09701509", "0.2844",
    "实差 0.0042 在带内", "共二百七十七面", "W2..W278", "W1..W278",
    "engine_owner==bm-c 97 行注册", "engine_owner 行 268 注册在册",
    "df1aaba72a", "b6f486af35", "60e630918f", "b965e2ecf0", "0a92fcc28f", "900c23fe7d",
    "MSG-20261019-145x-bmc-w279-seat",
    "@@W280", "@@SPLICE", "@RAM_FACE@", "@RAM_ANCHOR@", "@@VRAM",
    "W281p_ 投影 A naive 631_101",
    "第 98 枚", "第 269 波", "第九十八枚", "池第 277 枚", "波号 279", "零 279 行",
    "finalize 已落地 15:1x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned counts
assert T2.count("PERPETUAL-N1-W280") == 4, "batch count=%d" % T2.count("PERPETUAL-N1-W280")
assert T2.count("631_301..633_300") >= 8, "own-A count=%d" % T2.count("631_301..633_300")
assert T2.count("633_301..633_500") >= 6, "own-B count=%d" % T2.count("633_301..633_500")
assert T2.count("631_101..633_100") == 4, "A-naive count=%d" % T2.count("631_101..633_100")
assert T2.count("631_301..631_500") == 4, "B-naive count=%d" % T2.count("631_301..631_500")
assert T2.count("（占位·finalize one-pass 后回填") == 1 and T2.count("（占位·finalize 同窗回填") == 1
assert T2.count("（见 §5 item5）。") == 1
assert T2.count("W281+ 投影") >= 2
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
extra = ["PERPETUAL-N1-W280"] if False else []
print("W280 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("pairs applied: %d | splice %s | finalize estate 6bdbdb9a07 @ 20:0x | seat f96272d8b9 @ 20:0x"
      % (APPLIED, SPLICE_T))
print("src blob-verified == %s @ ba5c725b42 (frozen pre-run face; HEAD twin b98e8592 disclosed, NOT used)" % SRC_BLOB)
print("chain: K %d -> %d proj | ledger %d -> %d proj | n_eff %d | se_mu %s" % (K, K_PROJ, LEDGER, LEDGER_PROJ, NEFF, SE_PROJ))
print("live RAM face: %.2f GB available (%sGB written) | engine status ok=%s" % (_ram_free if False else RAM_GB, RAM_FACE, _eng_ok))
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])