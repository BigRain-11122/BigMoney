"""Finance-material inventory: one tool, run on both machines, diffable.

Why
---
"Send me the finance files" is unverifiable without a list. This produces the
list: what exists on *this* machine, with sizes, date ranges and git state, in a
form another machine can produce identically and a third party can diff.

Design rules
------------
* Two tiers. `repo` = files git tracks (portable, cheap to move). `lane` = data
  the repo ignores on purpose (astock_daily, moneyflow, ...) -- these cannot be
  moved by git and must either be rebuilt by a script or packed in <=95MB parts.
* No secrets. Only paths of config/token files, never their contents.
* Hashing is opt-in (`--hash`): 1.2GB of A-share bars makes a full sha256 pass
  slow, and a size+mtime+bar-range triple already catches "same file, older".
* Exit 0 always: an inventory is a statement, not a gate.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "research", "INGEST")
TZ = timezone(timedelta(hours=8))

LANES = {
    "astock_daily": "data/astock_daily/per",
    "moneyflow": "data/moneyflow",
    "lhb_inst": "data/lhb_inst",
    "options": "data/options",
    "futures_contracts": "data/futures_contracts",
    "futures_daily": "data/futures_daily",
    "index_daily": "data/index_daily",
    "daily": "data/daily",
    "cb_daily": "data/cb_daily",
    "repo_daily": "data/repo_daily",
    "zt_pool": "data/zt_pool",
    "fundamental": "data/fundamental",
    "heat": "data/heat",
    "ext_slots": "data/ext_slots",
    "minute_feed": "data/minute_feed",
}
SECRET_HINTS = ("token", "credential", "secret", ".env", "cookie", ".key")


def now():
    return datetime.now(TZ)


def git(*args):
    try:
        r = subprocess.run(["git"] + list(args), cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def last_bar(path, limit=3):
    """Newest date-looking token in the tail of a csv (3 files, cheap)."""
    try:
        files = [f for f in os.listdir(path) if f.endswith(".csv")]
    except OSError:
        return None
    if not files:
        return None
    files.sort(key=lambda f: os.path.getmtime(os.path.join(path, f)), reverse=True)
    best = None
    for f in files[:limit]:
        try:
            with open(os.path.join(path, f), "rb") as fh:
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - 400))
                for line in reversed(fh.read().decode("utf-8", "ignore").splitlines()):
                    head = line.split(",")[0].strip()
                    if len(head) >= 8 and head[:4].isdigit():
                        best = head[:10] if best is None else max(best, head[:10])
                        break
        except OSError:
            continue
    return best


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def repo_inventory(do_hash=False):
    tracked = (git("ls-files") or "").splitlines()
    rows = []
    for rel in tracked:
        full = os.path.join(ROOT, rel)
        if not os.path.exists(full):
            rows.append({"path": rel, "state": "missing-in-worktree"})
            continue
        st = os.stat(full)
        row = {"path": rel, "bytes": st.st_size,
               "mtime": datetime.fromtimestamp(st.st_mtime, TZ).isoformat(timespec="seconds")}
        if do_hash and st.st_size <= 20 * 1024 * 1024:
            row["sha256"] = sha256(full)
        rows.append(row)
    status = (git("status", "--porcelain") or "").splitlines()
    return {
        "files": rows,
        "count": len(rows),
        "bytes": sum(r.get("bytes", 0) for r in rows),
        "dirty": {"total": len(status),
                  "untracked": [s[3:] for s in status if s.startswith("??")][:200],
                  "modified": [s[3:] for s in status if s[:2].strip() in ("M", "MM", "A")][:200]},
        "git": {"branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "head": git("rev-parse", "HEAD"),
                "ahead_of_origin": git("rev-list", "--count", "origin/main..HEAD"),
                "behind_origin": git("rev-list", "--count", "HEAD..origin/main"),
                "stash": (git("stash", "list") or "").splitlines()[:20]},
    }


def lane_inventory(do_hash=False):
    out = {}
    for name, rel in LANES.items():
        path = os.path.join(ROOT, rel)
        if not os.path.isdir(path):
            out[name] = {"state": "absent", "path": rel}
            continue
        files, total = 0, 0
        newest = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                files += 1
                total += st.st_size
                newest = max(newest, st.st_mtime)
        out[name] = {
            "state": "present",
            "path": rel,
            "files": files,
            "bytes": total,
            "modified": (datetime.fromtimestamp(newest, TZ).isoformat(timespec="seconds")
                         if newest else None),
            "last_bar": last_bar(path),
            "movable_by_git": False,
        }
    return out


def config_pointers():
    """Paths only -- never contents. A reader learns where to look, not the secret."""
    found = []
    for base in (ROOT, os.path.dirname(os.path.dirname(ROOT))):
        if not os.path.isdir(base):
            continue
        try:
            entries = os.listdir(base)
        except OSError:
            continue
        for name in entries:
            low = name.lower()
            if any(h in low for h in SECRET_HINTS):
                found.append(os.path.relpath(os.path.join(base, name), ROOT))
    return sorted(set(found))[:50]


def build(do_hash=False):
    inv = {
        "generated": now().isoformat(timespec="seconds"),
        "machine": os.environ.get("COMPUTERNAME"),
        "root": ROOT,
        "note": "repo tier = portable via git; lane tier = gitignored data, needs rebuild script or <=95MB packs",
        "repo": repo_inventory(do_hash),
        "lanes": lane_inventory(do_hash),
        "config_pointers": config_pointers(),
        "research_surfaces": {
            "research_md": len([f for f in os.listdir(os.path.join(ROOT, "research"))
                                if f.endswith(".md")]) if os.path.isdir(os.path.join(ROOT, "research")) else 0,
            "results_json": len([f for f in os.listdir(os.path.join(ROOT, "results"))
                                 if f.endswith(".json")]) if os.path.isdir(os.path.join(ROOT, "results")) else 0,
            "bench_cells": len([f for f in os.listdir(os.path.join(ROOT, "results"))
                                if f.startswith("bench_") and f.endswith(".json")])
            if os.path.isdir(os.path.join(ROOT, "results")) else 0,
        },
    }
    return inv


def render_md(inv):
    r = inv["repo"]
    lines = [f"# 金融资料清单 · {inv['machine']}", "",
             f"generated {inv['generated']}", "",
             f"- 入库件 {r['count']} 个 / {r['bytes']/1048576:.1f}MB · "
             f"分支 {r['git']['branch']} · 领先 {r['git']['ahead_of_origin']} / 落后 {r['git']['behind_origin']}",
             f"- 未提交 {r['dirty']['total']} 件（未跟踪 {len(r['dirty']['untracked'])} / 修改 {len(r['dirty']['modified'])}）",
             f"- 研究面 {inv['research_surfaces']['research_md']} 页 · 结果面 "
             f"{inv['research_surfaces']['results_json']} 个（试验格 {inv['research_surfaces']['bench_cells']}）",
             "", "## 数据车道", "",
             "| 车道 | 文件 | 体量MB | 最新 bar | 修改时间 | git 可搬? |",
             "|---|---|---|---|---|---|"]
    for name, v in inv["lanes"].items():
        if v.get("state") != "present":
            lines.append(f"| {name} | 缺席 | — | — | — | 否 |")
            continue
        lines.append(f"| {name} | {v['files']} | {v['bytes']/1048576:.1f} | {v.get('last_bar','—')} | "
                     f"{v.get('modified','—')} | 否（需重建脚本或分包） |")
    if inv["config_pointers"]:
        lines += ["", "## 配置指针（只列路径，不含内容）", ""] + \
                 [f"- `{p}`" for p in inv["config_pointers"]]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hash", action="store_true", help="also sha256 repo files <=20MB")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    inv = build(a.hash)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = a.out or os.path.join(OUT_DIR, f"INVENTORY-{inv['machine']}-{now().strftime('%Y%m%d')}.json")
    if not os.path.isabs(out):
        out = os.path.join(ROOT, out)
    with open(out + ".tmp", "w", encoding="utf-8") as f:
        json.dump(inv, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(out + ".tmp", out)
    md = out.replace(".json", ".md")
    with open(md, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(inv))
    print(json.dumps({"ok": True, "out": os.path.relpath(out, ROOT),
                      "repo_files": inv["repo"]["count"],
                      "lanes": {k: v.get("files", 0) for k, v in inv["lanes"].items() if v.get("state") == "present"}},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
