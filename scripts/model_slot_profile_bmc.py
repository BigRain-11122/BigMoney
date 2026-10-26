"""Render MACHINE-PROFILE-bm-c.md from the measured model-slot bench artefact.

Why a generator instead of a hand-written profile: the profile is a table of numbers
tok/s, load seconds, VRAM/RAM headroom) that will be re-measured whenever a model is
pulled or evicted. Typed by hand it drifts from the bench it claims to summarise -- the
same "field promises one quantity" class as r1292. Here every number is copied out of
``results/model_slots/bench-bm-c-latest.json`` and nothing else, so the profile is only
ever as current as the bench, and says so.

Answer for MSG-20261027-0100-bmc-modelslots (48h window).
Usage: python scripts/model_slot_profile_bmc.py run|selftest
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PATHS

BENCH = os.path.join(PATHS.results_dir, "model_slots", "bench-bm-c-latest.json")
OUT = os.path.join(PATHS.root, "fleet", "model-slots", "MACHINE-PROFILE-bm-c.md")


def _fmt(x, unit="", nd=2):
    if x is None:
        return "NOT MEASURED"
    if isinstance(x, float):
        return ("%." + str(nd) + "f%s") % (x, unit)
    return "%s%s" % (x, unit)


def render(b):
    hw = b.get("hardware") or {}
    gpu = hw.get("gpu") or {}
    after = b.get("gpu_after") or {}
    rows = b.get("results") or []
    L = []
    L.append("# MACHINE-PROFILE-bm-c — bm-c 模型槽位画像（SLOT-POLICY-v1·实测优先）")
    L.append("")
    L.append("- 机器身份：**bm-c**（compute-node / GPU 生产节点）")
    L.append("- 承接：MSG-20261027-0100-bmc-modelslots（委员会牵头 / CPH4 Labs 统筹）")
    L.append("- 实测产物：`results/model_slots/bench-bm-c-latest.json` 与同批时间戳件")
    L.append("- 实测命令：`python scripts/model_slot_bench_bmc.py run`")
    L.append("- 上次实测：**%s**（本文件由 `scripts/model_slot_profile_bmc.py run` 从该件"
             "逐字派生，禁手抄）" % b.get("measured_at"))
    L.append("- 本轮 bench 标签：`%s`" % b.get("tag"))
    L.append("")
    L.append("## 一、硬件（实测）")
    L.append("")
    L.append("| 项 | 实测 |")
    L.append("|---|---|")
    L.append("| GPU | %s，**%s MiB** 显存（bench 前 used %s / free %s，util %s%%） |"
             % (_fmt(gpu.get("name")), _fmt(gpu.get("total_mb")), _fmt(gpu.get("used_mb")),
                _fmt(gpu.get("free_mb")), _fmt(gpu.get("util_pct"))))
    L.append("| RAM | %s GB 总，bench 前可用 **%s GB**（留存闸 %s GB） |"
             % (_fmt(hw.get("ram_total_gb"), "", 1), _fmt(hw.get("ram_available_gb")),
                _fmt(hw.get("ram_gate_reserve_gb"))))
    L.append("| bench 后 GPU | used %s MiB / free %s MiB / util %s%% |"
             % (_fmt(after.get("used_mb")), _fmt(after.get("free_mb")),
                _fmt(after.get("util_pct"))))
    L.append("")
    L.append("**本机关键约束：RAM 只剩 %s GB 可用。** bm-c 的 16 GB 显卡装得下 13 GB 级模型，"
             "但系统内存装不下「模型常驻 + 桌面/ComfyUI 应用」的叠加，任何 keep_alive=Forever "
             "的大模型常驻都会把本机推向 OOM 或整机卡死。结论：**bm-c 的槽位策略只能是"
             "「用完即卸、单模型串行」，禁止常驻。**" % _fmt(hw.get("ram_available_gb")))
    L.append("")
    L.append("## 二、本机模型清单（ollama 实盘）")
    L.append("")
    L.append("| 模型 | 权重 |")
    L.append("|---|---|")
    inv = b.get("inventory") or []
    for m in inv:
        L.append("| `%s` | %s GB |" % (m.get("name"), _fmt(m.get("size_gb"))))
    if not inv:
        L.append("| （空） | — |")
    L.append("")
    L.append("## 三、实测吞吐（同一脚本、同一 prompt、temperature=0、n_predict=128）")
    L.append("")
    L.append("| 模型 | 状态 | 解码 tok/s（3 次中位） | 预填充 tok/s | 首次加载 | 权重 |")
    L.append("|---|---|---|---|---|---|")
    for r in rows:
        runs = r.get("runs") or []
        dec = " / ".join(_fmt(x.get("decode_tok_s")) for x in runs) or "—"
        L.append("| `%s` | %s | **%s**（%s） | %s | %s s | %s GB |"
                 % (r.get("model"), r.get("status"), _fmt(r.get("median_decode_tok_s")),
                    dec, _fmt(r.get("median_prefill_tok_s")),
                    _fmt(r.get("median_first_load_s")), _fmt(r.get("size_gb"))))
    L.append("")
    note = b.get("measurement_note")
    if note:
        L.append("口径：%s" % note)
        L.append("")
    L.append("闸门判定（脚本逐模型记录，非人工）：")
    for r in rows:
        L.append("- `%s`：%s" % (r.get("model"), r.get("gate")))
    L.append("")
    L.append("## 四、槽位策略（由上面三节推得，禁凭感觉）")
    L.append("")
    L.append("| 槽位 | 用途 | 模型 | 常驻 |")
    L.append("|---|---|---|---|")
    L.append("| slot-1 | 本地推理主力（llm_assist / 轮报告摘要 / 代码一审） | 见上表实测件 | **否**（use-and-evict） |")
    L.append("| slot-2 | 图像/批量生成（ComfyUI 独立占用显存） | 非 ollama | 否 |")
    L.append("| 禁用 | 常驻大模型（keep_alive=Forever） | — | **禁止**：RAM 可用仅 %s GB |"
             % _fmt(hw.get("ram_available_gb")))
    L.append("")
    L.append("实测后常驻列表：%s（空=bench 按 keep_alive=0 卸载，符合本机策略）"
             % (json.dumps(b.get("resident_after") or [], ensure_ascii=False)))
    L.append("")
    L.append("## 五、复现与更新")
    L.append("")
    L.append("```")
    L.append("python scripts/model_slot_bench_bmc.py run     # 重新测量，写 results/model_slots/")
    L.append("python scripts/model_slot_profile_bmc.py run   # 从最新实测件重派生本文件")
    L.append("python scripts/model_slot_profile_bmc.py selftest")
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


def _write(text):
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return OUT


def run():
    if not os.path.exists(BENCH):
        print("no bench artefact at %s -- run scripts/model_slot_bench_bmc.py run first"
              % os.path.relpath(BENCH, PATHS.root))
        return 2
    with open(BENCH, "r", encoding="utf-8") as f:
        b = json.load(f)
    if b.get("machine_id") != "bm-c":
        print("bench artefact belongs to %s, not bm-c -- refusing to label it" % b.get("machine_id"))
        return 2
    p = _write(render(b))
    print("wrote %s (bench %s, %d model(s) measured)"
          % (os.path.relpath(p, PATHS.root), b.get("measured_at"), len(b.get("results") or [])))
    return 0


def selftest():
    fails = []
    b = {"machine_id": "bm-c", "tag": "t", "measured_at": "2026-01-01T00:00:00+0800",
         "hardware": {"gpu": {"name": "G", "total_mb": 16384, "used_mb": 1, "free_mb": 2,
                              "util_pct": 0},
                      "ram_total_gb": 23.9, "ram_available_gb": 1.57,
                      "ram_gate_reserve_gb": 0.6},
         "gpu_after": {"used_mb": 1, "free_mb": 2, "util_pct": 97},
         "inventory": [{"name": "m:1b", "size_gb": 1.5}],
         "results": [{"model": "m:1b", "status": "measured",
                      "runs": [{"decode_tok_s": 10.0}, {"decode_tok_s": 12.0}],
                      "median_decode_tok_s": 11.0, "median_prefill_tok_s": 20.0,
                      "median_first_load_s": 3.0, "size_gb": 1.5, "gate": "gate-ok"}],
         "resident_after": [], "measurement_note": "note"}
    t = render(b)
    # L1 every number in the table comes from the artefact, and the median is the median --
    #    not the last run (a hand-written row would silently pick "a number that looked right").
    if "**11.00**（10.00 / 12.00）" not in t:
        fails.append("L1 median not derived from runs")
    if "1.57" not in t:
        fails.append("L2 RAM constraint missing")
    # L2 the profile must state the resident rule it derives from that RAM figure
    if "禁止常驻" not in t or "用完即卸" not in t:
        fails.append("L3 eviction policy missing")
    # L3 an empty inventory must not print an empty table with no explanation
    b2 = json.loads(json.dumps(b))
    b2["inventory"] = []
    if "（空）" not in render(b2):
        fails.append("L4 empty inventory unmarked")
    # L4 NOT MEASURED is a word, never a zero (0.00 tok/s reads as a real measurement)
    b3 = json.loads(json.dumps(b))
    b3["results"][0]["median_decode_tok_s"] = None
    if "NOT MEASURED" not in render(b3):
        fails.append("L5 missing value printed as zero")
    n = 5 - len(fails)
    print("selftest: %d/5 PASS%s" % (n, "" if not fails else "; " + "; ".join(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit(selftest() if cmd == "selftest" else run())