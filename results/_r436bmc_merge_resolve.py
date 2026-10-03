# -*- coding: utf-8 -*-
"""r436 bm-c merge resolver: origin r648 chain vs bm-c r436 same-day
idempotent regenerate faces (r638/r634/r634-supplement precedent).
Rules: CODELY.md = line-level memory-union; x2_watch_log.jsonl = line union
exact-dup removal (r463); compute_audit.json = history ts-key union (r120)
else take-new; everything else = embedded-ts newer-wins, fallback ours.
Validations: chosen JSON parses, zero conflict markers, receipt to disk."""
import datetime
import json
import os
import re
import subprocess

CREATE = 0x08000000
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFLICTED = [
    "CODELY.md",
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/x2_watch_log.jsonl",
]

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ][0-9]{2}:[0-9]{2}(?::[0-9]{2})?")


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True,
                       creationflags=CREATE, cwd=REPO)
    return p.returncode, (p.stdout or b""), (p.stderr or b"")


def blob(stage, path):
    rc, out, err = git("show", ":%s:%s" % (stage, path))
    if rc != 0:
        raise RuntimeError("stage %s %s fetch failed: %s" %
                           (stage, path, err.decode("utf-8", "replace")[:120]))
    return out


def max_ts(data):
    txt = data.decode("utf-8", "replace")
    ts = [m.group(0) for m in TS_RE.finditer(txt)]
    return max(ts) if ts else None


def resolve(path):
    ours = blob("2", path)
    theirs = blob("3", path)
    r = {"path": path}
    if path == "CODELY.md":
        # line-level memory-union: ours base + theirs lines not in ours
        o_lines = ours.decode("utf-8", "replace").splitlines()
        t_lines = theirs.decode("utf-8", "replace").splitlines()
        o_set = set(l.strip() for l in o_lines if l.strip())
        add = [l for l in t_lines if l.strip() and l.strip() not in o_set]
        chosen = "\n".join(o_lines + add).encode("utf-8")
        r.update(side="union", why="memory-union ours+%d-new-theirs-lines" % len(add))
    elif path.endswith("x2_watch_log.jsonl"):
        o_lines = [l for l in ours.decode("utf-8", "replace").splitlines() if l.strip()]
        t_lines = [l for l in theirs.decode("utf-8", "replace").splitlines() if l.strip()]
        seen = set(o_lines)
        add = [l for l in t_lines if l not in seen]
        chosen = ("\n".join(o_lines + add) + "\n").encode("utf-8")
        r.update(side="union", why="append-only line union +%d" % len(add))
    elif path.endswith(".json"):
        try:
            jo = json.loads(ours.decode("utf-8", "replace"))
            jt = json.loads(theirs.decode("utf-8", "replace"))
        except Exception:
            jo = jt = None
        if isinstance(jo, dict) and isinstance(jt, dict) and \
                isinstance(jo.get("history"), list) and isinstance(jt.get("history"), list):
            key_ts = lambda d: str(d.get("ts") or d.get("time") or d.get("generated") or "")
            by = {key_ts(d): d for d in jo["history"]}
            add = [d for d in jt["history"] if key_ts(d) not in by]
            jo["history"] = jo["history"] + add
            jo_ts_keys = [k for k in ("ts", "generated", "updated_at", "generated_at")
                          if k in jo and k in jt]
            if jo_ts_keys:
                k = jo_ts_keys[0]
                if str(jt.get(k, "")) > str(jo.get(k, "")):
                    jo[k] = jt[k]
            chosen = json.dumps(jo, ensure_ascii=False, indent=1).encode("utf-8")
            r.update(side="union", why="history ts-key union +%d envelope-newer=%s" %
                     (len(add), any(add)))
        else:
            to, tt = max_ts(ours), max_ts(theirs)
            if to and tt and tt > to:
                chosen = theirs
                r.update(side="theirs", why="ts %s > %s" % (tt, to))
            else:
                chosen = ours
                r.update(side="ours", why="ts ours=%s theirs=%s" % (to, tt))
    else:
        to, tt = max_ts(ours), max_ts(theirs)
        if to and tt and tt > to:
            chosen = theirs
            r.update(side="theirs", why="ts %s > %s" % (tt, to))
        else:
            chosen = ours
            r.update(side="ours", why="ts ours=%s theirs=%s" % (to, tt))
    # validate before write
    if path.endswith(".json"):
        json.loads(chosen.decode("utf-8", "replace"))
    for ln in chosen.split(b"\n"):
        s = ln.strip()
        assert not (s.startswith(b"<<<<<<<") or s.startswith(b">>>>>>>") or
                    s.startswith(b"|||||||")), \
            "marker line %r in %s" % (ln[:30], path)
    with open(os.path.join(REPO, path), "wb") as f:
        f.write(chosen)
    rc, _, err = git("add", "--", path)
    assert rc == 0, "add %s failed: %s" % (path, err.decode("utf-8", "replace")[:120])
    r["ok"] = True
    return r


def main():
    receipt = {"ts": datetime.datetime.now().isoformat(), "faces": []}
    for p in CONFLICTED:
        receipt["faces"].append(resolve(p))
    rc, out, _ = git("diff", "--name-only", "--diff-filter=U")
    left = [l for l in out.decode("utf-8", "replace").splitlines() if l.strip()]
    assert not left, "unresolved faces remain: %r" % left
    sides = {}
    for f in receipt["faces"]:
        sides[f["side"]] = sides.get(f["side"], 0) + 1
    receipt["sides"] = sides
    rp = os.path.join(REPO, "results", "_r436bmc_merge_resolve.json")
    with open(rp, "w", encoding="utf-8", newline="") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    print("RESOLVED %d faces sides=%s receipt=%s" %
          (len(receipt["faces"]), sides, rp))
    for f in receipt["faces"]:
        print("  %-55s %-7s %s" % (f["path"], f["side"], f["why"][:70]))


if __name__ == "__main__":
    main()
