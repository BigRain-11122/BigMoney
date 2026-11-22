"""Block board: does every block of the quant line have a fresh, checkable artefact?

The point
---------
A line "running" is not the same as its blocks working. This board reads
research/QUANT-BLOCKS.json (one row per block: seat, skills, input, artefact,
cadence, probe, what to do when red) and answers, per block, three questions
with machine evidence:

  1. does the artefact exist?
  2. is it fresher than the block's cadence?
  3. where the block declares a predicate (a verdict field, a set of keys), does
     the content actually satisfy it?

A block that fails any of the three is RED, and every RED row already carries
the seat that owns it and the action that closes it -- so the board is a work
queue, not a status wall. `--fix-safe` executes only the fixes marked in the
registry as deterministic and local (re-running a face, regenerating a lane
board); anything that needs a decision is left for a person.

Exit code: 0 = no red, 1 = at least one red (so a scheduled tick can act on it).
"""
import argparse
import fnmatch
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, "research", "QUANT-BLOCKS.json")
OUT_JSON = os.path.join(ROOT, "results", "quant_block_board.json")
OUT_MD = os.path.join(ROOT, "research", "QUANT-BLOCK-BOARD.md")
TZ = timezone(timedelta(hours=8))


def now():
    return datetime.now(TZ)


def age_h(path):
    if not os.path.exists(path):
        return None
    return (time.time() - os.path.getmtime(path)) / 3600.0


def p(path):
    return path if os.path.isabs(path) else os.path.join(ROOT, path)


def probe_dir_fresh(spec):
    d = p(spec["dir"])
    pat = spec.get("pattern", "*")
    min_count = int(spec.get("min_count", 1))
    max_age = float(spec["max_age_h"])
    if not os.path.isdir(d):
        return False, f"dir missing: {spec['dir']}"
    files = [f for f in os.listdir(d) if fnmatch.fnmatch(f, pat)]
    if len(files) < min_count:
        return False, f"only {len(files)} files matching {pat} < {min_count} in {spec['dir']}"
    newest = max(os.path.getmtime(os.path.join(d, f)) for f in files)
    age = (time.time() - newest) / 3600.0
    if age > max_age:
        return False, f"newest write {age:.1f}h ago > {max_age}h"
    return True, f"{len(files)} files, newest {age:.1f}h"


def last_bar_date(path):
    """First column of the last non-empty line, if it looks like a date."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 600))
            lines = f.read().decode("utf-8", "ignore").strip().splitlines()
    except OSError:
        return None
    for line in reversed(lines):
        head = line.split(",")[0].strip()
        if len(head) >= 8 and head[:4].isdigit() and "-" in head:
            return head[:10]
    return None


def expected_last_weekday():
    d = now().date()
    while d.weekday() >= 5:          # Sat/Sun -> Friday
        d -= timedelta(days=1)
    return d


def probe_dir_bar_fresh(spec):
    """Freshness measured on the BAR DATE, not the file write time.

    A daily lane written on Saturday for Friday's bar is healthy on Sunday; a
    file-write probe calls it 40h stale and cries wolf. The bar date is taken as
    the MODE over a sample of files: one quarantined symbol with an old tail must
    not turn a 99.8%-covered lane red (that happened on the first run).
    """
    d = p(spec["dir"])
    pat = spec.get("pattern", "*.csv")
    min_count = int(spec.get("min_count", 1))
    if not os.path.isdir(d):
        return False, f"dir missing: {spec['dir']}"
    files = sorted(f for f in os.listdir(d) if fnmatch.fnmatch(f, pat))
    if len(files) < min_count:
        return False, f"only {len(files)} files < {min_count}"
    files.sort(key=lambda f: os.path.getmtime(os.path.join(d, f)), reverse=True)
    sample = files[:3]                       # newest writes always sampled
    step = max(1, len(files) // 300)
    sample += files[::step][:300]
    counts = {}
    for f in sample:
        b = last_bar_date(os.path.join(d, f))
        if b:
            counts[b] = counts.get(b, 0) + 1
    if not counts:
        return False, "cannot read a bar date"
    newest_mode = max(counts, key=lambda k: (counts[k], k))
    exp = expected_last_weekday()
    bar_day = datetime.strptime(newest_mode, "%Y-%m-%d").date()
    lag = (exp - bar_day).days
    allow = int(spec.get("holiday_allow_days", 4))
    share = counts[newest_mode] / max(sum(counts.values()), 1)
    if lag > allow:
        return False, f"modal bar {newest_mode} is {lag}d behind last weekday {exp} ({share:.0%} of sample)"
    return True, f"modal bar {newest_mode} ({share:.0%} of {len(counts)} sampled dates)"


def probe_file_fresh(spec):
    f = p(spec["path"])
    a = age_h(f)
    if a is None:
        return False, f"missing: {spec['path']}"
    if a > float(spec["max_age_h"]):
        return False, f"{a:.1f}h old > {spec['max_age_h']}h"
    return True, f"{a:.1f}h old"


def probe_json_keys(spec):
    f = p(spec["path"])
    a = age_h(f)
    if a is None:
        return False, f"missing: {spec['path']}"
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        return False, f"unreadable: {e}"
    missing = [k for k in spec["keys"] if k not in d]
    if missing:
        return False, f"missing keys {missing}"
    if "max_age_h" in spec and a > float(spec["max_age_h"]):
        return False, f"{a:.1f}h old > {spec['max_age_h']}h"
    return True, f"keys ok, {a:.1f}h old"


def probe_json_predicate(spec):
    f = p(spec["path"])
    a = age_h(f)
    if a is None:
        return False, f"missing: {spec['path']}"
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception as e:
        return False, f"unreadable: {e}"
    got = d.get(spec["field"])
    if got != spec["expect"]:
        return False, f"{spec['field']}={got} != {spec['expect']}"
    if "max_age_h" in spec and a > float(spec["max_age_h"]):
        return False, f"{a:.1f}h old > {spec['max_age_h']}h"
    return True, f"{spec['field']}={got}, {a:.1f}h old"


def probe_cells_cost(spec):
    """Every finished strategy cell's result must print the cost rate it used.

    Monitoring cells (revalidation) and reuse pointers are not strategy runs and
    are skipped; a leg-based cell may print cost_bp_side_leg instead.
    """
    q = json.load(open(p(spec["path"]), encoding="utf-8"))
    missing = []
    for c in q.get("cells", []):
        if c.get("status") != "done" or not c.get("result"):
            continue
        if c.get("revalidate") is False or c.get("monitor"):
            continue
        if str(c.get("id", "")).startswith(("revalidate", "idx_fut_basis_reuse",
                                            "cb_dual_low_reuse", "astock_resid_industry_reuse")):
            continue
        rp = p(c["result"])
        if not os.path.exists(rp):
            continue
        try:
            d = json.load(open(rp, encoding="utf-8"))
        except Exception:
            missing.append(c["id"] + ":unreadable")
            continue
        crit = d.get("criteria") or {}
        if not any(k in crit or k in d for k in
                   ("cost_bp_side", "cost_bp_side_leg", "cost_bp")):
            missing.append(c["id"])
    if missing:
        return False, "no cost rate printed: " + ", ".join(missing)
    return True, "every finished strategy cell prints its cost rate"


def probe_self_board(spec):
    f = p(spec["path"])
    a = age_h(f)
    if a is None:
        return False, "board has never been written"
    if a > float(spec["max_age_h"]):
        return False, f"board {a:.1f}h old"
    return True, f"board {a:.1f}h old"


PROBES = {
    "dir_fresh": probe_dir_fresh,
    "dir_bar_fresh": probe_dir_bar_fresh,
    "file_fresh": probe_file_fresh,
    "json_exists_keys": probe_json_keys,
    "json_predicate": probe_json_predicate,
    "cells_have_field": probe_cells_cost,
    "self_board": probe_self_board,
}


def run_block(b):
    kind = b["probe"]["type"]
    fn = PROBES.get(kind)
    if fn is None:
        return False, f"unknown probe type {kind}"
    try:
        return fn(b["probe"])
    except Exception as e:
        return False, f"probe error: {e}"


def build():
    reg = json.load(open(REG, encoding="utf-8"))
    rows = []
    for b in reg["blocks"]:
        ok, detail = run_block(b)
        rows.append({
            "id": b["id"], "group": b["group"], "name": b["name"],
            "granularity": b.get("granularity"),
            "seat": b["seat"], "skills": b.get("skills", []),
            "status": "GREEN" if ok else "RED",
            "detail": detail,
            "cadence_h": b.get("cadence_h"),
            "on_red": b.get("on_red"),
            "auto_fix": b.get("auto_fix"),
        })

    groups = {}
    for r in rows:
        g = groups.setdefault(r["group"], {"total": 0, "green": 0, "red": 0})
        g["total"] += 1
        g["green" if r["status"] == "GREEN" else "red"] += 1

    # idle vs starving: an empty research queue is legitimate idle only if every
    # block is green. If blocks are red while the queue is empty, that is a
    # starving line wearing an idle label.
    qpath = p("research/BENCH-QUEUE.json")
    pending = 0
    if os.path.exists(qpath):
        q = json.load(open(qpath, encoding="utf-8"))
        pending = sum(1 for c in q.get("cells", []) if c.get("status") == "pending")
    red = [r for r in rows if r["status"] == "RED"]
    if pending > 0:
        state = "BUSY"
    elif red:
        state = "STARVING"
    else:
        state = "LEGIT_IDLE"

    return {
        "generated": now().isoformat(timespec="seconds"),
        "version": reg.get("version"),
        "target_edge_pp": reg.get("target_edge_pp"),
        "blocks": len(rows),
        "green": len(rows) - len(red),
        "red": len(red),
        "groups": groups,
        "queue_pending": pending,
        "line_state": state,
        "rows": rows,
    }


def render_md(payload):
    lines = ["# 量化线块面看板", "",
             f"generated {payload['generated']} | 块面 {payload['blocks']} · "
             f"绿 {payload['green']} · 红 {payload['red']} | 队列待跑 {payload['queue_pending']} | "
             f"线态 **{payload['line_state']}**", "",
             "线态读法：BUSY=队列有活；LEGIT_IDLE=全绿且无 pending（合法的空转）；"
             "STARVING=有红块却没活可干（等于断供）。", ""]
    for g, s in payload["groups"].items():
        lines.append(f"- {g}：{s['green']}/{s['total']} 绿")
    lines += ["", "| 块面 | 粒度 | 席位 | 技能 | 状态 | 证据 | 红了怎么办 |",
              "|---|---|---|---|---|---|---|"]
    for r in payload["rows"]:
        mark = "🟢" if r["status"] == "GREEN" else "🔴"
        lines.append(f"| {r['name']}（{r['id']}） | {r['granularity']} | {r['seat']} | "
                     f"{', '.join(r['skills']) or '—'} | {mark} {r['status']} | {r['detail']} | "
                     f"{r['on_red'] if r['status'] == 'RED' else '—'} |")
    reds = [r for r in payload["rows"] if r["status"] == "RED"]
    if reds:
        lines += ["", "## 红块清单（带认领与动作）", ""]
        for r in reds:
            fix = r.get("auto_fix") or "需人工/需决策"
            lines.append(f"- **{r['name']}**（{r['seat']}）：{r['detail']} → {r['on_red']} "
                         f"｜可自动修复：{fix}")
    return "\n".join(lines) + "\n"


def fix_safe(payload):
    """Run only the deterministic local fixes declared in the registry."""
    done = []
    for r in payload["rows"]:
        if r["status"] != "RED" or not r.get("auto_fix"):
            continue
        cmd = r["auto_fix"]
        t0 = time.time()
        try:
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            res = subprocess.run(cmd, cwd=ROOT, shell=True, env=env,
                                 capture_output=True, text=True, timeout=1500)
            done.append({"block": r["id"], "cmd": cmd, "rc": res.returncode,
                         "seconds": round(time.time() - t0, 1)})
        except Exception as e:
            done.append({"block": r["id"], "cmd": cmd, "error": str(e)})
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-safe", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    payload = build()
    fixes = []
    if a.fix_safe:
        fixes = fix_safe(payload)
        payload = build()
        payload["fixes_applied"] = fixes

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON + ".tmp", "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
        f.write("\n")
    os.replace(OUT_JSON + ".tmp", OUT_JSON)
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_md(payload))

    print(json.dumps({"generated": payload["generated"], "line_state": payload["line_state"],
                      "green": payload["green"], "red": payload["red"],
                      "red_blocks": [r["id"] for r in payload["rows"] if r["status"] == "RED"],
                      "fixes": fixes}, ensure_ascii=False, indent=1))
    return 0 if payload["red"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
