# -*- coding: utf-8 -*-
"""r264 bm-c rebase-conflict resolver (r446 union blob recipe + r449 dedupe law).

Conflicts: CODELY.md + archive (both-side hot-cold reorgs, overlapping) and
docs/results shared regenerated faces (take-newer = mine 10:39 > bm-b 10:34).
Union: origin base + my delta only (r261x2 + r254 already archived by bm-b
r455 section verbatim -- dedupe, no revival).
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print("git fail:", args, r.stderr[:300])
        sys.exit(1)
    return r.stdout


def blob(stage, path):
    return git("show", ":%d:%s" % (stage, path))


# ---------- 1) docs/* + results/* shared regenerated faces: take mine (newer) ----------
take_theirs = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
for p in take_theirs:
    git("checkout", "--theirs", "--", p)
    git("add", "--", p)
    print("take-mine:", p)

# ---------- 2) archive: origin base + deduped r264 section ----------
AP = "research/memory-archive/202609.md"
ours_arch = blob(2, AP)
# my six verbatim entries, delta-filtered: drop r261x2 + r254 (already in r455)
keep_probes = ["web_fetch 伪成坑", "过继手术锚律收割器范式", "reconfigure 律漏网面"]
mine_arch_lines = [
    "",
    "## 热冷整编 2026-09-30 r264 bm-c 窗批（CODELY ≤10KB 硬线当窗整编·迁移零丢失·r449 去重律：r261×2+r254 三条已由 bm-b r455 窗批节 verbatim 归档·本节只载增量三条不复活）",
    "",
]
theirs_arch = blob(3, AP)
sec_idx = theirs_arch.find("## 热冷整编 2026-09-30 r264 bm-c 窗批")
sec = theirs_arch[sec_idx:]
kept = 0
for line in sec.splitlines():
    if line.strip().startswith("- [") :
        if any(p in line for p in keep_probes):
            mine_arch_lines.append(line)
            kept += 1
        # else: r261x2/r254 -> dedupe-drop (already in r455 section)
mine_arch_lines.append("")
mine_arch_lines.append("（热冷整编零丢失校验：本节三条与迁移前 CODELY.md 热层逐字节恒等；r261×2/r254 三条与 bm-b r455 节逐字节恒等=双窗批同录去重不复活；整编者=bm-c r264 S4 水位律当窗动作·rebase 冲突窗 union 收口。）")
mine_arch_lines.append("")
assert kept == 3, "expected 3 delta entries, got %d" % kept
if not ours_arch.endswith("\n"):
    ours_arch += "\n"
open(os.path.join(ROOT, AP), "w", encoding="utf-8", newline="\n").write(
    ours_arch + "\n".join(mine_arch_lines))
git("add", "--", AP)
print("archive union rebuilt: 3 delta entries")

# ---------- 3) CODELY.md: origin base + my delta (pit + pointer, remove 3 hot) ----------
CP = "CODELY.md"
ours_c = blob(2, CP)
lines = ours_c.splitlines()
out = []
removed = {"web_fetch 伪成坑": 0, "过继手术锚律收割器范式": 0, "reconfigure 律漏网面": 0}
for l in lines:
    if l.strip().startswith("- [") and any(p in l for p in removed):
        for p in removed:
            if p in l:
                removed[p] += 1
        continue  # drop hot entry (archived by my r264 section)
    out.append(l)
assert all(v == 1 for v in removed.values()), "remove counts wrong: %s" % removed
new_pit = ("- [2026-09-30 r264 bm-c] 截面 z 均值恒零坑（泊位探针实证·P0 级）：逐日截面 z（ddof=0）的截面均值数学恒=0"
           "——浮点残差（~1e-16）喂滚动分位门=纯噪声分类（占用恰为 q90/q10 机械占用）且随机子集 fwd 差可伪装成「信号」"
           "（r263 #97 面「2.6pp 热冷差」伪影撤回实证）。Why：面板列语义必须逐字核"
           "（premium_z=逐日截面 z 非「逐员滚动 z」——digest 凭印象描述列语义=伪证之源）。How：凡「截面聚合门」构造前必跑退化审计"
           "（聚合序列 max|值| 与业务量级比对+列语义 verbatim 核）；判例面=INNOVATION_QUOTA_W10_PREREG 泊位史节+r264 泊位探针 degeneracy_audit。")
new_ptr = ("- 冷层指针（r264 合并·指针合并归档 r444 范式）：r263 bm-c web_fetch 伪成坑+r465 bm-a 过继手术锚律收割器范式"
           "+r454 bm-b S6 分离链驱动 reconfigure 漏网面，三条全文 verbatim=archive 202609.md『热冷整编 2026-09-30 r264 bm-c 窗批』节"
           "（r261×2+r254 已由 bm-b r455 合并指针行归档·r449 去重律不复活）。")
# insert pit+pointer right after the last r261-merged pointer line (position parity with mine)
for i, l in enumerate(out):
    if l.startswith("- 冷层指针（r261 合并"):
        out.insert(i + 1, new_pit)
        out.insert(i + 2, new_ptr)
        break
else:
    out.append(new_pit)
    out.append(new_ptr)
if not out[-1] == "":
    out.append("")
open(os.path.join(ROOT, CP), "w", encoding="utf-8", newline="\n").write("\n".join(out))
git("add", "--", CP)
print("CODELY union rebuilt: 3 hot removed, pit+pointer added")

# ---------- 4) stage own runtime state files (r290 carry law) ----------
git("add", "--", "results/autofill_state.bm-c.json", "results/dispatcher_state.bm-c.json")
print("runtime state staged")
print("resolver done")
