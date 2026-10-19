"""r1052 bm-b: render FUND-STAGESTYLE-COMBO-P1 CEO matrix face from the readout JSON.

Deterministic (no clock): reads results/stagestyle_combo_p1/SSCOMBO-P1-<cutoff>.json,
writes docs/stagestyle/REPORT-STAGESTYLE-v1.md + .json twin.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "results", "stagestyle_combo_p1", "SSCOMBO-P1-2026-10-19.json")
OUT_DIR = os.path.join(ROOT, "docs", "stagestyle")
MD = os.path.join(OUT_DIR, "REPORT-STAGESTYLE-v1.md")
JS = os.path.join(OUT_DIR, "REPORT-STAGESTYLE-v1.json")

d = json.load(open(SRC, encoding="utf-8"))
res = d["results"]
win = d["window"]
order = ["C1", "C2", "C3", "U-divlowvol", "U-EW", "U-value", "U-quality"]
labels = {
    "C1": "C1 阶段组合（BEAR/GRIND->现金；其余 DIVLOWVOL-YIELDVOL）",
    "C2": "C2 阶段组合（BULL->VALUE-PE；BEAR/GRIND->现金；其余 DIVLOWVOL-YIELDVOL）",
    "C3": "C3 阶段组合（BEAR/GRIND->现金；BULL/CHOP/SUPPORT 三格分映射）",
    "U-divlowvol": "无条件 divlowvol 袖面",
    "U-EW": "无条件等权（U-EW）",
    "U-value": "无条件 value 袖面",
    "U-quality": "无条件 quality 袖面",
}

best_uncond = max((k for k in res if k.startswith("U-")), key=lambda k: res[k]["x1"]["sharpe"])
thr = 0.894 + 0.10  # prereg §5 P4 baseline + 0.10

rows = []
for k in order:
    r = res[k]
    rows.append(
        {
            "id": k,
            "label": labels.get(k, k),
            "x1": r["x1"],
            "x2": r["x2"],
        }
    )

p4 = {}
for k in ("C1", "C2", "C3"):
    s1 = res[k]["x1"]["sharpe"]
    p4[k] = {
        "sharpe_x1": s1,
        "threshold": round(thr, 4),
        "clears_threshold": s1 >= thr,
        "beats_best_uncond_same_run": s1 > res[best_uncond]["x1"]["sharpe"],
    }

payload = {
    "batch": d["batch"],
    "face": "REPORT-STAGESTYLE-v1",
    "machine": d["machine"],
    "generated_by_round": "r1052",
    "prereg": d["prereg"],
    "prereg_state": d["prereg_state"],
    "status": d["status"],
    "evidence_cutoff": d["evidence_cutoff"],
    "cutoff_meta": d.get("cutoff_meta"),
    "window": win,
    "table": rows,
    "mapping_v1": d.get("mapping_v1"),
    "d6_disclosure": d.get("d6_disclosure"),
    "sleeve_notes": d.get("sleeve_notes"),
    "p4_check": p4,
    "best_unconditional_same_run": best_uncond,
    "gates": "UNJUDGED -- G1'/G2/DSR/M1 belong to finalize; this face is a readout matrix only",
    "nulls": d.get("nulls"),
    "data_gaps": d.get("data_gaps"),
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(JS, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, ensure_ascii=False, indent=1)


def fmt(v):
    return f"{v:,.3f}"


lines = []
lines.append("# STAGE-STYLE 组合矩阵 v1 — 阶段×风格条件化组合读数")
lines.append("")
lines.append(f"- 批次：`{d['batch']}`｜机：{d['machine']}｜证据截止：{d['evidence_cutoff']}")
lines.append(f"- 窗口：{win['lo']}..{win['hi']}（{win['bars']} bars）")
lines.append(f"- 面板：{d['panel']['source']} shape {d['panel']['shape']} cutoff {d['panel']['cutoff']}")
lines.append(f"- 预注册：`{d['prereg']}`（状态 **{d['prereg_state']}**）")
lines.append("- 本页=读数矩阵（READOUT_ONLY），**不是判决**：G1'/G2/DSR/M1 属 finalize 面，未跑。")
lines.append("")
lines.append("## 1. 主表（年化夏普 / 全窗累计收益 / 最大回撤 / 年化波动）")
lines.append("")
lines.append("| 组合 | 成本 x1 夏普 | x1 累计收益 | x1 最大回撤 | x2 夏普 | x2 累计收益 | x2 最大回撤 |")
lines.append("|---|---|---|---|---|---|---|")
for r in rows:
    a, b = r["x1"], r["x2"]
    lines.append(
        f"| {r['label']} | {fmt(a['sharpe'])} | {a['ret']*100:,.1f}% | {a['max_dd']*100:,.1f}% "
        f"| {fmt(b['sharpe'])} | {b['ret']*100:,.1f}% | {b['max_dd']*100:,.1f}% |"
    )
lines.append("")
lines.append("成本口径：x1=13.041bp/边；x2=双倍成本压力面。日收益序列在 JSON 孪生 `results` 原样件。")
lines.append("")
lines.append("## 2. 一句话结论")
lines.append("")
best_c = max(("C1", "C2", "C3"), key=lambda k: res[k]["x1"]["sharpe"])
lines.append(
    f"**三个阶段组合全部跑不赢「什么都不做，只拿 divlowvol 袖面」**：最好的 {best_c} x1 夏普 "
    f"{res[best_c]['x1']['sharpe']:.3f}／累计 {res[best_c]['x1']['ret']*100:.1f}%／最大回撤 "
    f"{res[best_c]['x1']['max_dd']*100:.1f}%，而无条件 divlowvol 读 "
    f"{res['U-divlowvol']['x1']['sharpe']:.3f}／{res['U-divlowvol']['x1']['ret']*100:.1f}%／"
    f"{res['U-divlowvol']['x1']['max_dd']*100:.1f}%。阶段择时付了换手税，收益和回撤两头都更差。"
)
lines.append("")
lines.append("## 3. 预注册 §5 预测对照（跑前写死，禁改）")
lines.append("")
lines.append(f"- **P4（组合主张门，阈值 {thr:.3f}＝divlowvol 0.894＋0.10）**：")
for k in ("C1", "C2", "C3"):
    v = p4[k]
    verdict = "过阈值" if v["clears_threshold"] else "未过阈值"
    rel = "赢" if v["beats_best_uncond_same_run"] else "输"
    lines.append(
        f"  - {k} x1 夏普 {v['sharpe_x1']:.3f} → {verdict}；同轮无条件最强袖面（{best_uncond} "
        f"{res[best_uncond]['x1']['sharpe']:.3f}）比它{rel}。"
    )
lines.append("- **P1（BULL 格为主收益源）／P2（BEAR 格回避可回收损失）／P3（SUPPORT 不设专格）**：三格分解读数落在")
lines.append("  JSON 孪生逐格面，本条只记「组合整体不及无条件」这一层；格级归因待 finalize 批。")
lines.append("")
lines.append("## 4. 诚实边界")
lines.append("")
lines.append(f"- null 面：{d.get('nulls')}")
lines.append(f"- 数据缺口：{json.dumps(d.get('data_gaps'), ensure_ascii=False)}")
lines.append(f"- 单源声明：{d.get('single_source')}")
sn = d.get("sleeve_notes", {})
if sn:
    lines.append("- 袖面注记：divlowvol 本地起算 2003-11-03，冻结 t0 2006-02-06，前 27 个月被 clamp；"
                 "侧录面 qfq 反演 5,123 件（分红现金流倒推，`Money02` factor 面本机缺席）。")
lines.append(f"- D6 披露（与 divlowvol 相关）：{json.dumps(d.get('d6_disclosure'), ensure_ascii=False)}")
lines.append("")
lines.append(f"- 生成器：`scripts/stagestyle_combo_p1_report.py`（确定性·零墙钟）｜原件：`results/stagestyle_combo_p1/SSCOMBO-P1-{d['evidence_cutoff']}.json`")

with open(MD, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines) + "\n")

print("wrote", MD)
print("wrote", JS)
print("best_combo", best_c, round(res[best_c]["x1"]["sharpe"], 4))
print("best_uncond", best_uncond, round(res[best_uncond]["x1"]["sharpe"], 4))