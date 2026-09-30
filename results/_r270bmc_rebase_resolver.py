"""_r270bmc_rebase_resolver.py — r270 bm-c push 撞车 rebase 15-UU 正典解。

法则（r446 union/blob 族+D-20260928-03① take-new）：
  - 快照/状态再生产物（REPORT/LIVE/status 族 JSON）= 内嵌 ts 取新一侧（origin 13:18:56 > mine 13:17:39）；
  - research/HANDOVER.md = append-only 台账 union（双方 5x 条目并存·我的 r270 条目为最新置顶）；
  - 解后 ls-files -u 必零（r261 坑律：全 staged 后 rebase --continue）。
用法：python results/_r270bmc_rebase_resolver.py [--check]
"""
import re
import subprocess
import sys

ROOT = "."

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


def newest_ts(text: str):
    hits = TS_RE.findall(text)
    return max(hits) if hits else ""


def side_blob(rev: str, path: str):
    return git("show", f"{rev}:{path}")


SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
HANDOVER = "research/HANDOVER.md"
MY_COMMIT = "57f535933"  # rebase 中 = theirs 侧


def resolve(check_only: bool) -> int:
    uus = sorted(set(l.split("\t")[-1] for l in git("ls-files", "-u").splitlines() if l.strip()))
    print("UU files:", len(uus))
    decisions = []
    for path in uus:
        if path == HANDOVER:
            decisions.append((path, "union"))
            continue
        origin_txt = side_blob("origin/main", path)
        mine_txt = side_blob(MY_COMMIT, path)
        o_ts, m_ts = newest_ts(origin_txt), newest_ts(mine_txt)
        take = "origin" if o_ts >= m_ts else "mine"
        decisions.append((path, f"take-{take} (origin={o_ts} mine={m_ts})"))
    for path, d in decisions:
        print(f"  {d}  <-  {path}")
    if check_only:
        return 0
    for path, d in decisions:
        if path == HANDOVER:
            origin_txt = side_blob("origin/main", path)
            mine_txt = side_blob(MY_COMMIT, path)
            # union: my r270 entry line (unique to mine) + full origin body
            my_lines = [l for l in mine_txt.splitlines() if l.startswith("> bm-c round 270")]
            assert len(my_lines) == 1, f"HANDOVER my entry count {len(my_lines)}"
            marker = "> bm-a round 450"
            idx = origin_txt.index(marker)
            merged = origin_txt[:idx] + my_lines[0] + "\n" + origin_txt[idx:]
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(merged if merged.endswith("\n") else merged + "\n")
        elif d.startswith("take-origin"):
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(side_blob("origin/main", path))
        else:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(side_blob(MY_COMMIT, path))
        subprocess.run(["git", "add", "--", path], check=True, capture_output=True)
    left = [l for l in git("ls-files", "-u").splitlines() if l.strip()]
    assert not left, f"unmerged remain: {left}"
    print("all staged, zero unmerged")
    return 0


if __name__ == "__main__":
    sys.exit(resolve("--check" in sys.argv))
