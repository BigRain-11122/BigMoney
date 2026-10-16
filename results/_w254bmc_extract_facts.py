# -*- coding: utf-8 -*-
# r1054 bm-c: W254 prereg derive PREP v2 -- frozen-template byte-exact extraction (idempotent) + machine-facts + needle counts -> file.
import io, os, sys, json, subprocess, hashlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_FACE = os.path.join(REPO, "results", "_w254bmc_w253_frozen_face.txt")
OUT_FACTS = os.path.join(REPO, "results", "_w254bmc_facts.txt")
TPL = "research/PERPETUAL_N1_W253_PREREG.md"
FREEZE_SHA = "741371846"

lines = []
def P(*a):
    lines.append(" ".join(str(x) for x in a))

# 1) byte-extract the frozen pre-run face at the freeze commit (idempotent)
blob_freeze = subprocess.run(["git", "rev-parse", FREEZE_SHA + ":" + TPL], capture_output=True, text=True, cwd=REPO).stdout.strip()
blob_head = subprocess.run(["git", "rev-parse", "HEAD:" + TPL], capture_output=True, text=True, cwd=REPO).stdout.strip()
raw = subprocess.run(["git", "show", FREEZE_SHA + ":" + TPL], capture_output=True, cwd=REPO).stdout
io.open(OUT_FACE, "wb").write(raw)
ho = subprocess.run(["git", "hash-object", OUT_FACE], capture_output=True, text=True, cwd=REPO).stdout.strip()
P("freeze-commit blob:", blob_freeze)
P("HEAD post-backfill twin (disclosed, NOT used):", blob_head)
P("extracted bytes:", len(raw), "hash-object:", ho, "identical:", ho == blob_freeze)
T0 = raw.decode("utf-8")
P("T0 sha256[:16]:", hashlib.sha256(raw).hexdigest()[:16], "lines:", T0.count("\n") + 1)

# 2) W253 finalize machine faces (direct key reads -- never transcribed)
r = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w253_results.json"), encoding="utf-8"))
npc = r["null_pool_cumulative"]
P("RES merged.mu", repr(npc["merged"]["mu"]))
P("RES merged.sigma", repr(npc["merged"]["sigma"]))
P("RES merged.n_values", npc["merged"]["n_values"])
P("RES se_mu_at_k554520", repr(npc["se_mu_at_k554520"]))
P("RES w253_only.mu", repr(npc["w253_only"]["mu"]))
sl = r["skill_line_v2_k_lift"]
P("RES line_pre_w253", repr(sl["line_pre_w253"]), "line_merged_554520", repr(sl["line_merged_554520"]), "line_delta_k_lift", repr(sl["line_delta_k_lift"]))
# A-band p95 + ledger total hunt (key-path search)
def hunt(obj, pred, path=""):
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + "." + str(k)
            if isinstance(v, (int, float)) and pred(k, v):
                out.append((p, v))
            elif isinstance(v, (dict, list)):
                out.extend(hunt(v, pred, p))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(hunt(v, pred, path + "[%d]" % i))
    return out
for p, v in hunt(r, lambda k, v: ("p95" in str(k).lower() or "ledger" in str(k).lower() or "cum" in str(k).lower()) and not isinstance(v, bool))[:40]:
    P("RES-HUNT", p, repr(v))

# 3) needle counts on the frozen template (floor authoring input)
NEEDLES = [
    "W253", "W252", "W251", "W250", "n1_w253", "n1_w252", "_w253bmc", "_w252bmc", "_w251bmc",
    "--wave 253", "波号 253", "第 251 枚", "第 243 波", "第七十三枚",
    "554,520 投影", "line_merged@K552,320 **1.1943**", "552,320", "550,120",
    "978,735", "976,535", "980,935",
    "−0.09273968", "−0.09018", "0.2450479", "实差 0.0026 在带内", "（**0.3199** 实测锚）",
    "键 W252 实测 K-lift", "键 W252 实测 K-lift **+0.0001**",
    "line_pre_w252 1.1942", "n_eff_held_equal 978,735", "n_eff_held_equal 976,535",
    "A-ext seed=571_901..573_900", "entry rng seed=**571_901+j**", "entry rng=**571_901+j**",
    "exit rng=**573_901+j**", "A base=571901 span=2000 checked=2000 verdict=FREE",
    "B base=573901 span=200 checked=200 verdict=FREE", "R254：W253",
    "MSG-20261016-12xx-bmc-w253-seat", "f6433ee61",
    "（bm-c r1050 席·queue-head FREEZE-UNBLOCKED 发布）", "（bm-c r1050 席位", "（r1050 席位窗实跑",
    "bm-c r1050 窗 11:5x", "已落账键·11:5x",
    "saturation_engine.py status live-read r1052", "本窗 free RAM ~1.8GB（",
    "bm-c 循环班 r1052 freeze 窗 2026-10-16", "§5.5 W254+ 投影承接机证",
    "（**A 面=STAIRCASE-AFFECTS-A", "已如实披露非分叉）",
    "法典 §4 W253 行 A=571_901..573_900", "法典 §4 W253 行 B=573_901..574_100",
    "披露收敛·ADMIT 回执在场）", "非转录 r587·ADMIT 回执在场）",
    "5. **W254+ 投影（probe 机证 leg4", "verify at W254 prereg，hop 链逐跳在 probe 回执。",
    "·probe W254+ 投影 A naive 573_901..575_900 CLEAN hops=0", "never transcribe r587**）",
    "·W252 冻结窗 7.0G bm-c 实锚", "·W250 冻结窗 RAM 未记录（r1046 死窗", "W240 冻结窗 33.2G bm-a 实锚）",
    "selftest W253 face（", "零假设零风险。",
    "+W246=bm-a r1016 prereg derive", "——本波上游链=", "W254 freezer 承接面）】。",
    "queue-head FREEZE-UNBLOCKED lane", "本候选=bm-c 自有席自有波",
    "表尾 W252 行", "pre-W253 全二百五十行注册 N1 带表", "全二百五十行注册 N1 带表",
    "freeze 窗 live derive 250 行单态 owner rows 242",
    "probe leg0 机证 250 行〔", "席位窗 probe leg0 实测 250 行〔",
    "perpetual_faces.py 零 251 行", "共二百五十面实测",
    "bmc rows 72+候选=第 73 枚 EXACT", "第 72 枚", "第 73 枚",
    "probe leg0 bmc_rows=72 attempt-continuity face（r1050 窗算法·bm-c own seat+bmc live rows 72 实读）",
    "engine_owner==bm-c 72 行注册", "engine_owner 行 242 注册在册",
    "W243/W246/W248/W249/W250/W251/W252 低 RAM 实烧先例",
    "W239..W252 leg（14 行）构成 W253 块 parity 111 行",
    "W252 块的自有 W239..W251 legs（13 行）",
    "r1049/W252 先例 freeze-prep 同式",
    "→W249 **0.000332**→W250 **0.000331**→W251 **0.000330**→W252 **0.000330**】",
    "bm-c r1050 W252 §7 范式", "bm-c r1050 W252 §8 范式",
    "hops=1", "hops=2", "第二次连续 A-hop", "第三次连续 above-own-A",
    "571_901..573_900", "573_901..574_100", "574_101..576_100", "576_101..576_300",
    "573_901..575_900", "574_101..574_300", "576_101..578_100", "576_301..576_500",
    "waits-upstream ARMED", "（**B 面=CLEAN", "W254p_", "W255p_",
    "本波上游链=W1..W252 finalize 全落地", "W252 own-wave finalize 已落",
    "first-clean", "e63561df3", "472cc8386", "cbf6411bf", "b3d563f4f",
    "b3caaedc1", "bec86607a", "c9b4fd855", "fa70f3765", "741371846",
]
P("--- needle counts on frozen W253 template ---")
for n in NEEDLES:
    P("CNT %r = %d" % (n, T0.count(n)))

# 4) W254 probe receipt anchors (machine re-read)
pr = json.load(io.open(os.path.join(REPO, "results", "_w254bmc_20261016_probe_receipt.json"), encoding="utf-8"))
P("--- probe receipt anchors ---")
P("verdict", pr["verdict"], "bands", json.dumps(pr["bands"]))
l0 = pr["legs"]["leg0"]
P("leg0 rows", l0["rows"], "owner_rows", l0["owner_rows"], "bmc_rows", l0["bmc_rows"], "ordinal", l0["ordinal"])
P("finalize anchors", json.dumps(l0["w253_finalize_anchors"]))
P("chain_relation", json.dumps(l0["chain_relation"]))
P("A_hop_chain", json.dumps(pr["legs"]["leg1"]["A_hop_chain"]))
P("B_hop_chain", json.dumps(pr["legs"]["leg1"]["B_hop_chain"]))
P("rel", json.dumps(pr["legs"]["leg1"]["relation_asserts"]))
P("seed gates", json.dumps(pr["legs"]["leg2"]["seed_admit_gate"], ensure_ascii=False))
P("leg4", json.dumps(pr["legs"]["leg4"], ensure_ascii=False))

# 5) live free RAM now (mb -> GB honest face for header)
import ctypes
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
m = MEMORYSTATUSEX(); m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
P("live free RAM GB:", round(m.ullAvailPhys / 1e9, 1), "total:", round(m.ullTotalPhys / 1e9, 1))

io.open(OUT_FACTS, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
print("facts written:", OUT_FACTS, len(lines), "lines")
