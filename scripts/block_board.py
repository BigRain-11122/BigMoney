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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import silent_run  # noqa: E402  (no console window from any child process)

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


def _git_tracked(paths):
    """Repo-relative paths git knows about, or None when git cannot answer.

    A face that exists on this disk because this machine wrote it is not published:
    a fresh clone reads nothing there, so a cell's evidence can look green here and
    be absent everywhere else (r1783 family). None means "do not judge", not "clean".
    """
    if not paths:
        return set()
    try:
        r = silent_run.run(["git", "ls-files", "--"] + list(paths), cwd=ROOT, timeout=60)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return set(x for x in r.stdout.split("\n") if x.strip())


def _selftest_git_reach():
    """The git leg must answer true for a tracked file and false for a missing one."""
    got = _git_tracked(["scripts/block_board.py", "no/such/face-for-selftest.json"])
    if got is None:
        return [], "SKIP (git not reachable here)"
    fails = []
    if "scripts/block_board.py" not in got:
        fails.append("git reach: scripts/block_board.py reported untracked")
    if "no/such/face-for-selftest.json" in got:
        fails.append("git reach: a nonexistent path reported as tracked")
    return fails, "git reach 2/2"


def cost_stamp_problem(d):
    """Return a reason string when a result face cannot say what its cost was, else None.

    Two shapes count as a printed cost rate:

      * legacy flat keys -- cost_bp_side / cost_bp_side_leg / cost_bp (per-side bp), or
      * a structured `cost` block whose `basis` names the unit and whose quantity for that
        unit is present.

    The structured form exists because a repo leg pays commission per lend on notional,
    which has no honest per-side bp: before it was allowed, the only options were to
    invent a bp number or to stay red. Either way the face must carry a quantity, so a
    block that names a basis but prints no number is still a miss.
    """
    crit = d.get("criteria") or {}
    legacy = [k for k in ("cost_bp_side", "cost_bp_side_leg", "cost_bp")
              if k in crit or k in d]
    blk = d.get("cost")
    if not isinstance(blk, dict):
        if legacy:
            return None
        return "no cost rate printed"
    basis = str(blk.get("basis") or "").strip()
    if not basis:
        return "cost block without a basis"
    if basis == "per_side_bp":
        qty = blk.get("side_bp")
        if isinstance(qty, (int, float)) and not isinstance(qty, bool):
            return None
        return "cost basis per_side_bp without a numeric side_bp"
    if basis == "per_trade_fee_of_notional":
        qty = blk.get("per_trade_bps_by_tenor") or blk.get("per_trade_bps")
        if isinstance(qty, dict) and any(isinstance(v, (int, float)) for v in qty.values()):
            return None
        if isinstance(qty, (int, float)) and not isinstance(qty, bool):
            return None
        return "cost basis per_trade_fee_of_notional without a numeric per-trade bps"
    # an unknown basis is only acceptable when the legacy flat keys are there too
    return None if legacy else "unknown cost basis %r" % basis


def probe_cells_cost(spec):
    """Every finished strategy cell's result must print the cost rate it used.

    Monitoring cells (revalidation) and reuse pointers are not strategy runs and
    are skipped.
    """
    q = json.load(open(p(spec["path"]), encoding="utf-8"))
    missing = []
    faces = []
    for c in q.get("cells", []):
        if c.get("status") != "done" or not c.get("result"):
            continue
        if c.get("revalidate") is False or c.get("monitor"):
            continue
        if str(c.get("id", "")).startswith(("revalidate", "idx_fut_basis_reuse",
                                            "cb_dual_low_reuse", "astock_resid_industry_reuse")):
            continue
        rp = p(c["result"])
        faces.append((c["id"], c["result"], rp))
    tracked = _git_tracked([rel for _, rel, _ in faces])
    for cid, rel, rp in faces:
        if not os.path.exists(rp):
            # a done cell whose face is gone is not "nothing to check" -- it is the hole
            # that lets a fresh clone read green (r1783 family).
            missing.append(cid + ": face missing")
            continue
        if tracked is not None and rel.replace(os.sep, "/") not in tracked:
            # the face is readable here only because this machine wrote it; git would
            # hand a fresh clone nothing, so the cell's evidence is not published.
            missing.append(cid + ": face in worktree but not in git")
            continue
        try:
            d = json.load(open(rp, encoding="utf-8"))
        except Exception:
            missing.append(cid + ":unreadable")
            continue
        why = cost_stamp_problem(d)
        if why:
            missing.append(cid + " (" + why + ")" if why != "no cost rate printed" else cid)
    if missing:
        return False, "no cost rate printed: " + ", ".join(missing)
    return True, "every finished strategy cell prints its cost rate"


def _selftest_cost_stamp():
    """Behaviour legs: the guard must go green on a real stamp and red on an empty one."""
    ok = [
        {"criteria": {"cost_bp_side": 10.0}},
        {"cost": {"basis": "per_side_bp", "side_bp": 10.0}},
        {"cost": {"basis": "per_trade_fee_of_notional",
                  "per_trade_bps_by_tenor": {"1": 0.1}}},
        {"cost": {"basis": "per_trade_fee_of_notional", "per_trade_bps": 0.1}},
    ]
    bad = [
        {},
        {"cost": {}},
        {"cost": {"basis": "per_side_bp"}},
        {"cost": {"basis": "per_side_bp", "side_bp": None}},
        {"cost": {"basis": "per_trade_fee_of_notional"}},
        {"cost": {"basis": "per_trade_fee_of_notional", "per_trade_bps_by_tenor": {}}},
        {"cost": {"basis": "made_up_unit"}},
    ]
    fails = []
    for i, d in enumerate(ok):
        if cost_stamp_problem(d) is not None:
            fails.append("ok[%d] judged %r" % (i, cost_stamp_problem(d)))
    for i, d in enumerate(bad):
        if cost_stamp_problem(d) is None:
            fails.append("bad[%d] passed" % i)
    return fails


def probe_self_board(spec):
    f = p(spec["path"])
    a = age_h(f)
    if a is None:
        return False, "board has never been written"
    if a > float(spec["max_age_h"]):
        return False, f"board {a:.1f}h old"
    return True, f"board {a:.1f}h old"


def probe_no_raw_subprocess(spec):
    """Any automation that calls subprocess directly can flash a console window.

    Measured on this box: pythonw plus a plain subprocess call to a console
    program shows one visible console window; the same call through silent_run
    shows zero. A future script that forgets the flag is what this catches.
    """
    import re
    pat = re.compile(r"(?<!silent_run\.)subprocess\.(run|Popen)\s*\(")
    offenders = []
    for f in spec.get("files", []):
        path = p(f)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh, 1):
                if pat.search(line) and not line.lstrip().startswith("#"):
                    offenders.append(f"{f}:{i}")
    if offenders:
        return False, "raw subprocess call(s): " + ", ".join(offenders[:8])
    return True, f"{len(spec.get('files', []))} automation script(s) clean"


def probe_supply(spec):
    """The line must never run out of *pre-registered* questions.

    Green: at least one pending cell in the queue, or at least one open item in
    the work bank. Red: both empty -- that is not "idle", it is a supply
    failure, because the machine has nothing to do only when nobody wrote down
    the next question. Refill cannot invent questions, so this is the one red a
    person must clear (add to research/WORK-BANK.json).
    """
    q = read_json_any(p(spec["queue"])) or {}
    b = read_json_any(p(spec["bank"])) or {}
    pending = sum(1 for c in q.get("cells", []) if c.get("status") in ("pending", "failed"))
    open_items = sum(1 for i in b.get("items", []) if i.get("status") == "open")
    if pending or open_items:
        return True, f"pending={pending} · bank_open={open_items}"
    blocked = [i.get("id") for i in b.get("items", []) if i.get("status") == "blocked"]
    return False, ("no open question left; blocked on data: "
                   + (", ".join(blocked) if blocked else "none documented"))


def read_json_any(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


PROBES = {
    "dir_fresh": probe_dir_fresh,
    "dir_bar_fresh": probe_dir_bar_fresh,
    "file_fresh": probe_file_fresh,
    "json_exists_keys": probe_json_keys,
    "json_predicate": probe_json_predicate,
    "cells_have_field": probe_cells_cost,
    "self_board": probe_self_board,
    "no_raw_subprocess": probe_no_raw_subprocess,
    "supply": probe_supply,
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
            res = silent_run.run(cmd, cwd=ROOT, shell=True, env=env, timeout=1500)
            done.append({"block": r["id"], "cmd": cmd, "rc": res.returncode,
                         "seconds": round(time.time() - t0, 1)})
        except Exception as e:
            done.append({"block": r["id"], "cmd": cmd, "error": str(e)})
    return done


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix-safe", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        fails = _selftest_cost_stamp()
        git_fails, git_note = _selftest_git_reach()
        fails += git_fails
        if fails:
            print("SELFTEST FAILED (%d):" % len(fails))
            for x in fails:
                print("  -", x)
            return 3
        print("SELFTEST 11/11 PASS (cost stamp guard: 4 green shapes, 7 red shapes) + %s" % git_note)
        return 0

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
