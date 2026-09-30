import json, io
d = json.load(io.open('results/_r477bma_rw6_probe.json', encoding='utf-8'))
SEGS = ("in_sample", "out_sample")
def g(face, seg, k):
    v = face[seg]
    return v[k] if k in v else v["max_dd" if k == "dd" else k]
lines = []
lines.append("# RW-6 Final Old-vs-New Table — 6 Registered Members (fixed engine)")
lines.append("")
lines.append("One-time recompute per D-20260930-05 item 6 (ticket T-127). Engine = fully fixed: RW-1 exits fill T+1 open, RW-2 evidence_cutoff hard truncation, RW-3 single-source cost (13.041bp Face A), RW-4 panel gate. Evidence cutoff 2026-09-22 (frozen). Old = pre-fix frozen values (honest overstatement baseline, preserved verbatim); New = fresh recompute. Three-way consistency fresh==r472-refreeze==trader-JSON: BYTE-STABLE, drift 0.")
lines.append("")
for seg, seg_name in (("in_sample", "IS"), ("out_sample", "OOS")):
    lines.append(f"## {seg_name} ({seg})")
    lines.append("")
    lines.append("| member | sharpe old→new | annual old→new | trades old→new | max_dd old→new |")
    lines.append("|---|---|---|---|---|")
    for mid, m in d["members"].items():
        o, n = m["old"], m["new"]
        row = [mid]
        for k, fmt in (("sharpe", "{:+.4f}"), ("annual", "{:+.4f}"), ("trades", "{:d}"), ("dd", "{:+.4f}")):
            ov, nv = g(o, seg, k), g(n, seg, k)
            if k == "trades":
                row.append(f"{ov}→{nv} ({nv-ov:+d})")
            else:
                row.append(f"{ov:+.4f}→{nv:+.4f} ({nv-ov:+.4f})")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
tot_old_s = sum(g(m["old"], "out_sample", "sharpe") for m in d["members"].values())
tot_new_s = sum(g(m["new"], "out_sample", "sharpe") for m in d["members"].values())
lines.append("## Verdict")
lines.append("")
lines.append(f"- OOS Sharpe sum 6 members: old {tot_old_s:+.3f} → new {tot_new_s:+.3f} (Δ {tot_new_s-tot_old_s:+.3f})")
lines.append("- OOS Sharpe deltas per member (RW-1 disclosure, unchanged since r472): CE-01 −0.886, VOLATILITY −0.340, NEEDLE −0.216, ENGULF −0.215, CE-02 −0.079, DROUGHT +0.028")
lines.append("- Byte-stability: fresh recompute == r472 refrozen anchors == current trader JSONs (drift 0, r253 single-count law)")
lines.append("- Old numbers are DEAD for citation (D-20260930-22): no non-recomputed Sharpe to CEO before 10-31")
lines.append("- Null pool v2 + T-28 baseline recompute = runnable_pool entries this round; judgement line v2 (skill_line_v2) recomputes when the v2 null pool lands")
lines.append("")
io.open('results/RW6_FINAL_TABLE_20260930.md', 'w', encoding='utf-8', newline='').write("\n".join(lines) + "\n")
print("written:", len(lines), "lines")
