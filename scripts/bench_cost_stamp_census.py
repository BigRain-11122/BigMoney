"""Cost-stamp census: which finished cells can say what their cost was, and what it takes to fix the rest.

The point
---------
The block board already answers "is the C2 cost-model cell red?" with one string.
That string is not a work order: it names the cell, not the file, the key, or the
number. This census walks every finished strategy cell in research/BENCH-QUEUE.json,
asks the *same* predicate the board uses (scripts/block_board.py::cost_stamp_problem,
imported -- never re-typed), and for each miss reads the cell's own script to find
the cost constant it already runs with, so the repair is a copy-paste diff instead
of a judgement call.

Two rules keep this honest:

  * the predicate is imported, not re-implemented, and a cross-check leg asserts the
    census agrees with block_board.probe_cells_cost on the same queue -- if the board
    changes its skip rules tomorrow, this face goes red instead of drifting quietly;
  * a face that is not in git is reported as such, because a green verdict reached
    through an unpublished file is not evidence a fresh clone can read (r1783 family).

Usage:
  python scripts/bench_cost_stamp_census.py run     # write results + page
  python scripts/bench_cost_stamp_census.py check    # re-derive and compare (rc3 on drift)
  python scripts/bench_cost_stamp_census.py selftest # offline behaviour legs

Exit: 0 = clean, 1 = stamps missing (report written), 3 = drift/selftest failure.
"""
import argparse
import ast
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import silent_run  # noqa: E402
import block_board  # noqa: E402  (predicate source of truth)

ROOT = block_board.ROOT
QUEUE = os.path.join(ROOT, "research", "BENCH-QUEUE.json")
OUT_JSON = os.path.join(ROOT, "results", "bench_cost_stamp_census.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH_COST_STAMP_CENSUS.md")
TZ = timezone(timedelta(hours=8))
C2_SPEC = {"path": "research/BENCH-QUEUE.json"}


def now():
    return datetime.now(TZ)


def p(rel):
    return os.path.join(ROOT, rel.replace("/", os.sep))


def _tracked(rels):
    return block_board._git_tracked(rels)


def _cost_constants(script_rel):
    """Module-level numeric assignments whose name mentions cost, from the cell's own script.

    Statics only: the census never imports a cell script (some of them hit the network
    or write faces on import), it reads the source and takes the literals.
    """
    path = p(script_rel)
    if not os.path.exists(path):
        return []
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except SyntaxError:
        return []
    found = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        val = node.value
        if not isinstance(val, ast.Constant) or isinstance(val.value, bool):
            continue
        if not isinstance(val.value, (int, float)):
            continue
        for t in node.targets:
            if isinstance(t, ast.Name) and "COST" in t.id.upper():
                found.append({"name": t.id, "value": val.value})
    return found


def _eligible_cells(queue):
    """The same population the board judges: done, has a result face, not monitoring/reuse."""
    out = []
    for c in queue.get("cells", []):
        if c.get("status") != "done" or not c.get("result"):
            continue
        if c.get("revalidate") is False or c.get("monitor"):
            continue
        if str(c.get("id", "")).startswith(("revalidate", "idx_fut_basis_reuse",
                                            "cb_dual_low_reuse", "astock_resid_industry_reuse")):
            continue
        out.append(c)
    return out


def census():
    queue = json.load(open(QUEUE, encoding="utf-8"))
    cells = _eligible_cells(queue)
    tracked = _tracked([c["result"] for c in cells])
    rows = []
    missing = []
    for c in cells:
        rel = c["result"]
        path = p(rel)
        row = {"cell": c["id"], "face": rel, "script": c.get("script")}
        if not os.path.exists(path):
            row["state"] = "FACE_MISSING"
            row["why"] = "result face absent on disk"
            missing.append(row)
            rows.append(row)
            continue
        row["in_git"] = (tracked is None) or (rel in tracked)
        if not row["in_git"]:
            row["state"] = "UNPUBLISHED"
            row["why"] = "face exists in this worktree only; a fresh clone reads nothing"
            missing.append(row)
            rows.append(row)
            continue
        try:
            d = json.load(open(path, encoding="utf-8"))
        except Exception as e:
            row["state"] = "UNREADABLE"
            row["why"] = "json load failed: %s" % e
            missing.append(row)
            rows.append(row)
            continue
        why = block_board.cost_stamp_problem(d)
        if why is None:
            row["state"] = "STAMPED"
            rows.append(row)
            continue
        row["state"] = "NO_STAMP"
        row["why"] = why
        consts = _cost_constants(c.get("script") or "")
        row["cost_constants_in_script"] = consts
        if consts:
            v = consts[0]["value"]
            row["patch_hint"] = (
                'in the dict written to %s add: "cost": {"basis": "per_side_bp", '
                '"side_bp": %s}   # from %s = %s' % (rel, v, consts[0]["name"], v))
        else:
            row["patch_hint"] = "no numeric cost constant found in the cell script; name the unit by hand"
        top = list(d)[:20]
        row["face_top_keys"] = top
        if "evidence_cutoff" not in d:
            row["also_missing_evidence_cutoff"] = True
        missing.append(row)
        rows.append(row)

    # Cross-check: the board's own whole-population verdict must agree with this walk.
    try:
        board_ok, board_msg = block_board.probe_cells_cost(C2_SPEC)
    except Exception as e:
        board_ok, board_msg = None, "board probe failed: %s" % e
    agree = None
    if board_ok is not None:
        agree = (board_ok == (not missing))
    cutoffs = sorted({r.get("cell") for r in rows if r.get("also_missing_evidence_cutoff")})
    out = {
        "artifact": "bench_cost_stamp_census",
        "generated": now().isoformat(timespec="seconds"),
        "evidence_cutoff": _queue_cutoff(queue),
        "question": "every finished strategy cell must print the cost rate it used; which ones cannot, and what is the exact repair?",
        "predicate_source": "scripts/block_board.py::cost_stamp_problem (imported)",
        "population": {"eligible": len(cells), "stamped": len(cells) - len(missing),
                       "missing": len(missing)},
        "board_cross_check": {"board_ok": board_ok, "board_msg": board_msg,
                              "census_agrees": agree},
        "cells": rows,
        "missing": missing,
        "missing_evidence_cutoff_cells": cutoffs,
        "verdict": "CLEAN" if not missing else "MISSING_STAMPS",
    }
    return out


def _queue_cutoff(queue):
    """Newest last_run among finished cells is the honest as-of for this census."""
    ts = [c.get("last_run") or c.get("finished") for c in queue.get("cells", [])
          if c.get("status") == "done" and (c.get("last_run") or c.get("finished"))]
    return max(ts) if ts else None


def write(out):
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    lines = [
        "# 成本戳普查 · 每格能不能说出自己的成本",
        "",
        "generated %s | 队列口径 cutoff %s | 谓词同源 `block_board.cost_stamp_problem`"
        % (out["generated"], out["evidence_cutoff"]),
        "",
        "**结论**：合格格 %d / 共 %d，缺戳 %d —— board 交叉核对 %s。"
        % (out["population"]["stamped"], out["population"]["eligible"],
           out["population"]["missing"],
           "一致" if out["board_cross_check"]["census_agrees"] else "**不一致（面本身有问题）**"),
        "",
        "| 格 | 结果面 | 状态 | 说明 |",
        "|---|---|---|---|",
    ]
    for r in out["cells"]:
        lines.append("| %s | %s | %s | %s |" % (r["cell"], r["face"], r["state"],
                                                (r.get("why") or "").replace("|", "/")))
    if out["missing"]:
        lines += ["", "## 修复处方（逐格照抄）", ""]
        for r in out["missing"]:
            lines.append("- **%s** → `%s`" % (r["cell"], r.get("patch_hint", "")))
            if r.get("also_missing_evidence_cutoff"):
                lines.append("  - 同批还缺顶层 `evidence_cutoff`（science_gates C2 合法键）；写入最新 bar 日")
    else:
        lines += ["", "无需修复：每个已跑格都带着成本率。"]
    lines += ["", "本面只读普查，不改任何格的结果面；修复按处方落到各格脚本后重跑该格。", ""]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def cmd_check():
    if not os.path.exists(OUT_JSON):
        print("no face to check", file=sys.stderr)
        return 3
    prev = json.load(open(OUT_JSON, encoding="utf-8"))
    cur = census()
    drift = []
    if prev.get("population") != cur.get("population"):
        drift.append("population %s -> %s" % (prev.get("population"), cur.get("population")))
    a = {r["cell"]: r["state"] for r in prev.get("cells", [])}
    b = {r["cell"]: r["state"] for r in cur.get("cells", [])}
    for k in sorted(set(a) | set(b)):
        if a.get(k) != b.get(k):
            drift.append("%s: %s -> %s" % (k, a.get(k), b.get(k)))
    if drift:
        print("STALE census face drifted: " + "; ".join(drift), file=sys.stderr)
        return 3
    print(json.dumps({"ok": True, "verdict": cur["verdict"],
                      "eligible": cur["population"]["eligible"],
                      "missing": cur["population"]["missing"]}, ensure_ascii=False))
    return 0


def cmd_selftest():
    fails = []
    ok_face = {"cost": {"basis": "per_side_bp", "side_bp": 1.5}}
    legacy_face = {"criteria": {"cost_bp_side": 10.0}}
    empty_face = {"rule": {"cost_bp_side": 1.5}, "verdict": "TRACKING"}
    if block_board.cost_stamp_problem(ok_face) is not None:
        fails.append("selftest: a structured stamp judged missing")
    if block_board.cost_stamp_problem(legacy_face) is not None:
        fails.append("selftest: a legacy flat stamp judged missing")
    if block_board.cost_stamp_problem(empty_face) is None:
        fails.append("selftest: a face with no top-level cost judged stamped")
    # the extractor must see a literal, and must not invent one where there is none
    got = _cost_constants("scripts/paper_basis_timing.py")
    if not any(abs(float(c["value"]) - 1.5) < 1e-9 for c in got):
        fails.append("selftest: cost constant 1.5 not extracted from paper_basis_timing.py")
    if _cost_constants("no/such/script.py"):
        fails.append("selftest: extractor returned constants for a missing file")
    cur = census()
    if cur["board_cross_check"]["census_agrees"] is not True:
        fails.append("selftest: census disagrees with block_board on the live queue: %s"
                     % cur["board_cross_check"])
    if fails:
        for f in fails:
            print("FAIL " + f, file=sys.stderr)
        return 3
    print(json.dumps({"ok": True, "legs": 6, "verdict": cur["verdict"],
                      "eligible": cur["population"]["eligible"],
                      "missing": cur["population"]["missing"]}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "check", "selftest"])
    a = ap.parse_args()
    if a.cmd == "selftest":
        return cmd_selftest()
    if a.cmd == "check":
        return cmd_check()
    out = census()
    write(out)
    print(json.dumps({"ok": True, "verdict": out["verdict"],
                      "eligible": out["population"]["eligible"],
                      "missing": out["population"]["missing"],
                      "board_agrees": out["board_cross_check"]["census_agrees"]},
                     ensure_ascii=False))
    return 0 if out["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(main())
