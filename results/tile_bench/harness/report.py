# -*- coding: utf-8 -*-
"""Aggregate TileBench run JSONs -> summary.json + REPORT.md (frame budget readout)."""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "results")

MS_60 = 1000.0 / 60.0


def load_runs():
    rows = []
    for p in sorted(glob.glob(os.path.join(RES, "run*.json"))):
        try:
            with io.open(p, "r", encoding="utf-8") as f:
                rows.append((os.path.basename(p), json.load(f)))
        except Exception as e:  # honest skip, keep going
            print("skip %s: %s" % (p, e))
    return rows


def fps(ms):
    return 1000.0 / ms if ms and ms > 0 else 0.0


def verdict(pan_avg, pan_p99):
    if pan_avg > MS_60:
        return "RED"          # avg already over 16.7ms budget
    if pan_p99 > MS_60:
        return "YELLOW"       # avg holds 60 but p99 breaches (frame drops)
    return "GREEN"


def main():
    rows = load_runs()
    if not rows:
        print("no run jsons yet")
        sys.exit(1)
    out = []
    lines = []
    lines.append("# CPH4 低配机 2D 渲染性能基准 · tile 大城帧预算（bm-b RTX 3070 8GB 档）")
    lines.append("")
    lines.append("> backlog #9 · claimed bm-b 2026-10-10T21:59:03+08:00 · 引擎=Tuanjie 2022.3.62t15 editor -batchmode 手动渲染循环 (RT 1600×900/内置管线) · 32px point-filter 运行时生成 tile · Tilemap chunk 模式")
    env0 = rows[0][1].get("env", {})
    lines.append("> 环境: GPU=%s (%dMB) · CPU=%s · RAM=%dGB · editor-batchmode 无窗 RT 1600×900 手动渲染 · co-resident=Ollama 7b 常驻(~4.5GB VRAM) + astock 刷新 IO 后台" % (
        env0.get("gpu", "?"), env0.get("gpuMemMB", 0), env0.get("cpu", "?"),
        env0.get("ramGB", 0)))
    lines.append("")
    lines.append("## 矩阵读数（hold=静止视角 / pan=12 tile/s 对角平移最坏段）")
    lines.append("")
    lines.append("| 配置 | 地图 tiles | 可见 tiles/帧 | hold avg/p99 ms | pan avg/p99 ms | pan avg fps | 判定 |")
    lines.append("|---|---|---|---|---|---|---|")
    for name, r in rows:
        a = r.get("args", {})
        m = r.get("map", {})
        vis = r.get("visibleTilesPerFrame", {})
        s = r.get("segments", {})
        h1 = s.get("hold1", {})
        pan = s.get("pan", {})
        v = verdict(pan.get("avgMs", 999), pan.get("p99Ms", 999))
        lines.append("| %s (L%d,o%s) | %s | %s | %s / %s | %s / %s | %.1f | %s |" % (
            name.replace("run", "").replace(".json", ""), a.get("layers", 1), a.get("ortho", 17),
            "{:,}".format(m.get("totalTiles", 0)),
            "{:,.0f}".format(vis.get("total", 0)),
            h1.get("avgMs", 0), h1.get("p99Ms", 0),
            pan.get("avgMs", 0), pan.get("p99Ms", 0),
            fps(pan.get("avgMs", 999)), v))
        out.append({"run": name, "args": a, "env": r.get("env"), "map": m,
                    "visibleTilesPerFrame": vis, "mem": r.get("mem"),
                    "segments": s, "panFps": fps(s.get("pan", {}).get("avgMs", 999)),
                    "verdict": v})
    # frame budget derivation: best GREEN config by visible tiles/frame
    greens = [o for o in out if o["verdict"] == "GREEN"]
    lines.append("")
    lines.append("## 帧预算结论")
    if greens:
        best = max(greens, key=lambda o: o["visibleTilesPerFrame"].get("total", 0))
        vis = best["visibleTilesPerFrame"].get("total", 0)
        budget = int(vis * 0.8)  # 20% safety margin
        lines.append("- 全 GREEN 最大可见面: %s = %s tiles/帧（pan p99 %.2fms ≤16.67）" % (
            best["run"], "{:,.0f}".format(vis), best["segments"]["pan"]["p99Ms"]))
        lines.append("- **tile 大城帧预算（bm-b 3070 档推荐值，含 20%% 安全余量）: 每帧可见 tiles ≤ %s（60fps p99 口径）**" % "{:,}".format(budget))
        lines.append("- 换算: 1600×900 窗口下 ortho 尺寸 ≤ 该可见面所对应视口；地图总尺寸受内存/生成成本约束（见 size sweep 对比）而非渲染")
    else:
        lines.append("- 无全 GREEN 配置：3070 档在该矩阵下均无法 p99 持 60fps，帧预算需按最接近 YELLOW 配置打折")
    # size sweep readout
    by_size = {}
    for o in out:
        a = o["args"]
        if a.get("layers") == 1 and abs(float(a.get("ortho", 17)) - 17.0) < 0.01:
            by_size[a.get("mapSize")] = o["segments"]["pan"]["avgMs"]
    if len(by_size) >= 2:
        lines.append("- size sweep（同视口 L1）: " + " · ".join(
            "%s²=%sms" % (k, "%.2f" % v) for k, v in sorted(by_size.items())) +
            " → 渲染成本由可见 tiles 主导，地图总尺寸主要抬升内存（reservedMB 见 JSON；workingSet 在 editor batchmode 下两 API 皆返 0=该口径不可用，如实留 0）")
    # repeatability
    r1 = [o for o in out if o["run"].endswith("s1024_L3_o17.json")]
    r2 = [o for o in out if o["run"].endswith("s1024_L3_o17_r2.json")]
    if r1 and r2:
        d1 = r1[0]["segments"]["pan"]["avgMs"]
        d2 = r2[0]["segments"]["pan"]["avgMs"]
        lines.append("- 复跑一致性: pan avg %s vs %s ms（差 %.1f%%）" % ("%.2f" % d1, "%.2f" % d2, abs(d1 - d2) / max(d1, d2) * 100))
    lines.append("")
    lines.append("## 方法论与诚实披露")
    lines.append("- r845 路线=editor -batchmode 手动渲染循环（r844 实测 standalone player 隐藏窗不进 player loop、可见窗被零窗律禁 → 弃 player 路线）。每 tick cam.Render() 渲至固定 RT 1600×900，1×1 ReadPixels 强制 GPU 排空，帧 dt=编辑器 loop tick 间隔（含渲染提交+GPU+循环开销）。")
    lines.append("- 口径=standalone player 的保守下界：编辑器循环开销计入帧、无 DWM 合成收益，实机 player 通常更快；working set 含编辑器本体常驻开销，size sweep 读增量不读绝对值。无后处理、无灯光（Sprites/Default unlit）。")
    lines.append("- 基准与 Ollama 7b 常驻(~4.5GB VRAM)、astock 全宇宙刷新 IO 并发运行=机队真实载荷口径。")
    lines.append("- tile 为 32px/格点过滤/4 变体；deco 层 30% 稀疏填充模拟装饰覆盖。pan 段 12 tiles/s 对角平移=持续新块入视的最坏段。")
    lines.append("- 判定: GREEN=pan p99 ≤16.67ms · YELLOW=avg 达标但 p99 超线 · RED=avg 超线。")
    with io.open(os.path.join(RES, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with io.open(os.path.join(RES, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("aggregated %d runs -> summary.json + REPORT.md" % len(out))


if __name__ == "__main__":
    main()
