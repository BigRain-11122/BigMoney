"""Diff two finance-material inventories: what the other machine has that we lack.

Usage:
  python scripts/ingest_diff.py research/INGEST/INVENTORY-DASHENG-20261124.json

Reports three things and nothing else:
  1. repo files present there and absent here (the only ones that can simply be
     pulled), plus files whose mtime is newer there;
  2. data lanes: file-count and byte deltas, and which side has the newer bar --
     lanes are gitignored, so a delta here means "rebuild or pack", not "pull";
  3. git state on the other side (ahead/behind, stash, dirty) so a reader knows
     whether the delivery is actually complete.

Exit 0 always: a diff is a statement, not a gate.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TZ = timezone(timedelta(hours=8))
LOCAL_DEFAULT = os.path.join(ROOT, "research", "INGEST")


def latest_local():
    if not os.path.isdir(LOCAL_DEFAULT):
        return None
    files = [f for f in os.listdir(LOCAL_DEFAULT)
             if f.startswith("INVENTORY-") and f.endswith(".json")]
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(LOCAL_DEFAULT, f)), reverse=True)
    return os.path.join(LOCAL_DEFAULT, files[0])


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def diff(theirs, mine):
    thr = {r["path"]: r for r in theirs.get("repo", {}).get("files", []) if "path" in r}
    loc = {r["path"]: r for r in mine.get("repo", {}).get("files", []) if "path" in r}
    missing = sorted(set(thr) - set(loc))
    extra = sorted(set(loc) - set(thr))
    newer = []
    for p in sorted(set(thr) & set(loc)):
        a, b = thr[p].get("mtime"), loc[p].get("mtime")
        if a and b and a > b:
            newer.append(p)

    lanes = {}
    for name, t in (theirs.get("lanes") or {}).items():
        m = (mine.get("lanes") or {}).get(name, {})
        lanes[name] = {
            "theirs": {k: t.get(k) for k in ("state", "files", "bytes", "last_bar", "modified")},
            "ours": {k: m.get(k) for k in ("state", "files", "bytes", "last_bar", "modified")},
            "file_delta": (t.get("files") or 0) - (m.get("files") or 0),
            "byte_delta": (t.get("bytes") or 0) - (m.get("bytes") or 0),
            "newer_bar_side": ("theirs" if (t.get("last_bar") or "") > (m.get("last_bar") or "")
                               else ("ours" if (m.get("last_bar") or "") > (t.get("last_bar") or "")
                                     else "same")),
        }

    return {
        "theirs": {"machine": theirs.get("machine"), "generated": theirs.get("generated")},
        "ours": {"machine": mine.get("machine"), "generated": mine.get("generated")},
        "repo": {
            "missing_here": missing[:500],
            "missing_here_count": len(missing),
            "newer_there": newer[:500],
            "newer_there_count": len(newer),
            "only_here_count": len(extra),
            "only_here_sample": extra[:100],
        },
        "lanes": lanes,
        "their_git": theirs.get("repo", {}).get("git"),
        "their_dirty": theirs.get("repo", {}).get("dirty", {}).get("total"),
        "verdict": ("COMPLETE" if not missing and not newer else "GAPS_FOUND"),
    }


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src:
        print("usage: ingest_diff.py <their INVENTORY.json> [our INVENTORY.json]")
        return 2
    theirs = load(src if os.path.isabs(src) else os.path.join(ROOT, src))
    mine_path = sys.argv[2] if len(sys.argv) > 2 else latest_local()
    mine = load(mine_path)
    d = diff(theirs, mine)

    out_json = os.path.join(LOCAL_DEFAULT, "DIFF-latest.json")
    with open(out_json + ".tmp", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(out_json + ".tmp", out_json)

    lines = [f"# 金融资料交接差异 · {d['theirs']['machine']} ↔ {d['ours']['machine']}", "",
             f"their inventory {d['theirs']['generated']} | ours {d['ours']['generated']}", "",
             f"**{d['verdict']}**", "",
             f"- 他们有而我们没有的入库件：**{d['repo']['missing_here_count']}** 个"
             + (f"（例：{', '.join(d['repo']['missing_here'][:5])}）" if d['repo']['missing_here'] else ""),
             f"- 他们更新而我们落后的：**{d['repo']['newer_there_count']}** 个",
             f"- 我们独有的：{d['repo']['only_here_count']} 个（正常，本机写出了新结果）",
             f"- 他们未提交：{d['their_dirty']} 件 · git 状态：{json.dumps(d['their_git'], ensure_ascii=False)}",
             "", "## 数据车道（git 搬不动）", "",
             "| 车道 | 他们 | 我们 | 文件差 | bar 更新方 |", "|---|---|---|---|---|"]
    for name, v in d["lanes"].items():
        lines.append(f"| {name} | {v['theirs'].get('files')} 文件 / {v['theirs'].get('last_bar')} | "
                     f"{v['ours'].get('files')} 文件 / {v['ours'].get('last_bar')} | "
                     f"{v['file_delta']:+d} | {v['newer_bar_side']} |")
    lines += ["", "车道差异不能靠 git 解决：要么他们给重建脚本，要么按 ≤95MB 分包。"]
    with open(os.path.join(LOCAL_DEFAULT, "DIFF-latest.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": d["verdict"],
                      "missing_here": d["repo"]["missing_here_count"],
                      "newer_there": d["repo"]["newer_there_count"],
                      "lanes_newer_there": [k for k, v in d["lanes"].items()
                                            if v["newer_bar_side"] == "theirs"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
