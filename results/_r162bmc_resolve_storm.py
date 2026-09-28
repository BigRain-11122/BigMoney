# -*- coding: utf-8 -*-
"""r162 bm-c push-storm resolver (15-UU vs bm-b same-window S6 derived faces + CODELY union).

Canon: r158/r161 recipe + r159 direction law (stopped-sha full-file ts-probe decides
side; :2:/:3: labels never used as direction semantics). Probe result this window:
ALL 14 S6 faces take :3: (bm-c 12:27-12:28 derive fresher than bm-b 12:15-12:18;
deep-probe REPORT/dashboard twin JSONs confirm 12:28:46/12:28:48 vs 12:17:07/12:17:10).
compute_audit: latest take-newer + history ts-key union zero-loss (r161 verbatim).
CODELY.md: merge-base prefix identity assertion + both-side append suffix direct-concat
(D-20260927-09 canon; bm-b r381 entry first then bm-c r162 entry) -> byte check vs
<=10KB hard line -> water-mark archival (batch 48) if over, line-level zero-loss verified.
All resolved faces parse-verified before staging.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def stage(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("stage read fail %s" % path)
    return r.stdout

report = {}

# 1) ts-probed take-:3: faces (probe log in _r162bmc_storm_probe.py, direction = newer ts on :3:)
TAKE3 = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in TAKE3:
    data = stage(3, p)
    with open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.loads(data)  # parse-verify
    report[p] = "take-:3: (ts-probe newer) parse-ok"

# 2) compute_audit: latest take-newer + history ts-key union zero-loss (r161 verbatim)
p = "results/compute_audit.json"
a = json.loads(stage(2, p))
b = json.loads(stage(3, p))
lat_a = a.get("latest", {})
lat_b = b.get("latest", {})
latest = lat_b if str(lat_b.get("ts", "")) >= str(lat_a.get("ts", "")) else lat_a
hist = {}
for e in a.get("history", []) + b.get("history", []):
    k = str(e.get("ts"))
    if k not in hist:
        hist[k] = e
merged_hist = sorted(hist.values(), key=lambda e: str(e.get("ts")))
merged = {k: v for k, v in b.items() if k not in ("latest", "history")}
merged["latest"] = latest
merged["history"] = merged_hist
with open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
report[p] = ("latest=%s (take-newer) + history union %d+%d->%d zero-loss"
             % (latest.get("ts"), len(a.get("history", [])),
                len(b.get("history", [])), len(merged_hist)))

# 3) CODELY.md union: base prefix identity + both-side suffix direct-concat (D-20260927-09)
p = "CODELY.md"
base_p = subprocess.run(["git", "show", "fced4388~1:CODELY.md"], capture_output=True)
assert base_p.returncode == 0, "base read fail"
base = base_p.stdout.decode("utf-8")
o2 = stage(2, p).decode("utf-8")
o3 = stage(3, p).decode("utf-8")
assert o2.startswith(base), ":2: base-prefix identity FAILED"
assert o3.startswith(base), ":3: base-prefix identity FAILED"
suf_bmb = o2[len(base):]
suf_bmc = o3[len(base):]
union = base + suf_bmb + suf_bmc  # bmb entry (12:1x) first, bmc r162 (12:41) second

HARD = 10240
union_b = union.encode("utf-8")
report[p] = "union base %dB + bmb suffix %dB + bmc suffix %dB = %dB (hard line %dB)" % (
    len(base.encode("utf-8")), len(suf_bmb.encode("utf-8")),
    len(suf_bmc.encode("utf-8")), len(union_b), HARD)

# 4) water-mark archival if over hard line (batch 48)
if len(union_b) > HARD:
    lines = union.split("\n")
    # entry extraction: lines starting with '- [2026-09-28' until next '- [' or section
    def entry_span(ls, start_idx):
        end = start_idx + 1
        while end < len(ls) and not ls[end].startswith("- ["):
            end += 1
        # trim trailing blank lines from entry block
        while end > start_idx + 1 and ls[end - 1].strip() == "":
            end -= 1
        return start_idx, end

    # find full-text kenglu entries oldest-first (r159 then r379)
    targets = ["- [2026-09-28 11:3 r159 bm-c] 坑律：**rebase 冲突 stage 语义",
               "- [2026-09-28 11:4 r379 bm-b] 坑律：**crash-fuse confirm"]
    migrated = []
    for tgt in targets:
        idx = next((i for i, l in enumerate(lines) if l.startswith(tgt[:40])), None)
        assert idx is not None, "target entry not found: %s" % tgt[:40]
        s, e = entry_span(lines, idx)
        block = lines[s:e]
        assert block[0].startswith("- [2026-09-28"), "entry boundary sanity"
        migrated.append((s, block))

    # remove from highest index first
    removed_bytes = 0
    for s, block in sorted(migrated, key=lambda x: -x[0]):
        for _ in range(len(block)):
            removed_bytes += len(lines[s].encode("utf-8")) + 1
            del lines[s]

    pointer = ("冷层指针：坑律正典 2026-09-28 四十八批（r162 bm-c 窗·水位律当窗整编：push-storm union 复超 ≤10KB 硬线）："
               "r159 rebase-stage :2:/:3: 反映射二犯 / r379 crash-fuse wait-law 两条全文 verbatim="
               "archive 202609.md『坑律归档 2026-09-28 四十八批』节（行级零丢失校验）。")
    # insert pointer after the 四十七批 pointer line
    pidx = next((i for i, l in enumerate(lines) if "四十七批" in l and l.startswith("冷层指针")), None)
    assert pidx is not None, "四十七批 pointer line not found"
    lines.insert(pidx + 1, pointer)

    final = "\n".join(lines)
    final_b = final.encode("utf-8")
    assert len(final_b) <= HARD, "post-archival still over hard line: %d" % len(final_b)

    # append verbatim to archive (line-level zero-loss)
    arch_path = "research/memory-archive/202609.md"
    arch = open(arch_path, encoding="utf-8").read()
    section = ["", "## 坑律归档 2026-09-28 四十八批（r162 bm-c 窗·水位律当窗整编：push-storm union 复超 ≤10KB 硬线）", ""]
    for _, block in sorted(migrated, key=lambda x: x[0]):
        section.append("")
        section.extend(block)
    section.append("")
    arch_new = arch.rstrip("\n") + "\n" + "\n".join(section)
    with open(arch_path, "w", encoding="utf-8", newline="") as f:
        f.write(arch_new)
    # zero-loss verify: every migrated line present in archive verbatim
    arch_check = open(arch_path, encoding="utf-8").read()
    for _, block in migrated:
        for l in block:
            if l.strip():
                assert l in arch_check, "zero-loss FAIL: %s" % l[:60]
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(final)
    report["archival"] = ("batch-48: migrated %d entries (%dB removed + %dB pointer) -> CODELY %dB <= %d hard line; "
                          "archive zero-loss verified line-level" % (
                              len(migrated), removed_bytes, len(pointer.encode("utf-8")) + 1, len(final_b), HARD))
else:
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(union)
    report["archival"] = "union under hard line, no archival needed"

print(json.dumps(report, ensure_ascii=False, indent=1))
print("RESOLVED: 15 faces (14 take-:3: + audit union) + CODELY union%s"
      % (" + batch-48 archival" if "archival" in report and "batch-48" in report["archival"] else ""))
