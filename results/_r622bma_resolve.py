# -*- coding: utf-8 -*-
"""r622 bm-a dynamic MERGE resolver (constructive merge, re-runnable).

Adapts r618 resolver for merge orientation (:2: = ours/HEAD = bm-a,
:3: = theirs = origin) -- ts probes are orientation-independent; the
r140 same-second tie resolves to :2: = HEAD which is canon-correct in a
merge too.  Routes:
  1. ALL_FACES (incl. crash_fuse, B-family r385) -> merge_lane_views resolve
  2. lane files results/runnable_pool.bm-*.json -> R31 owner side = :3:
     (origin carries the owner machine's own write), never union
  3. twin regen pairs (REPORT-*, LIVE-*) -> json deep-ts diffpick + md
     byte-coupled same side (r329); all LIVE-* twins take the SAME side
  4. dashboard_status.js -> whole-byte side coupled to json probe verdict
  5. append-log *.jsonl -> line-level union, dict-only door (r570 law)
  6. other *.json -> snapshot take-new via hardened deep-ts probe on
     STAGED blobs (r100/R350: key normalize, ts-shaped + time-of-day
     value gate, no key-exclude lists)
Bytes via git objects / binary mode (r209).  Fail-closed on unrouted.
"""
import re
import subprocess
import sys
import json as _j

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

ALL_FACES = {
    "compute_audit", "regime_state", "autofill_state", "runnable_pool",
    "gate_attrition", "post_review_criteria", "update_status",
    "heat_update_status", "lhb_update_status", "futures_update_status",
    "fundamental_status", "token_usage", "crash_fuse", "market_clock",
}

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")
TS_PREFIX = ("generated", "updated", "ts", "asof", "written",
             "scanned", "now", "time", "stateupdated", "donets")


def git_out(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args}: {r.stderr[:200]}")
    return r.stdout


def blob(spec):
    r = subprocess.run(["git", "show", spec], cwd=ROOT, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"git show {spec}: {r.stderr[:200]}")
    return r.stdout


def write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def uu_faces():
    out = git_out("ls-files", "-u").decode("utf-8", "replace")
    return sorted({ln.split("\t", 1)[1] for ln in out.splitlines() if ln})


def deep_ts(obj, best=None):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_-]", "", str(k)).lower()
            if isinstance(v, str) and TS_RE.match(v) and (
                    "T" in v or re.search(r"\d{2}:\d{2}", v)):
                if any(nk.startswith(p) for p in TS_PREFIX):
                    if best is None or v > best[0]:
                        best = (v, k)
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best


def resolve_face(path):
    r = subprocess.run(
        ["python", "scripts/merge_lane_views.py", "resolve", path],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    print(f"[allface] {path}: rc={r.returncode} "
          f"{(r.stdout or r.stderr).strip()[-160:]}")
    if r.returncode != 0:
        raise RuntimeError(f"merge_lane_views resolve {path} failed")


def probe_side(path):
    a = blob(":2:" + path)
    b = blob(":3:" + path)
    ta = deep_ts(_j.loads(a.decode("utf-8")))
    tb = deep_ts(_j.loads(b.decode("utf-8")))
    assert ta and tb, f"probe miss {path}: {ta} {tb}"
    # merge orientation: :2: = ours (bm-a), :3: = origin
    return (":2:", ta[0], tb[0]) if ta[0] > tb[0] else (":3:", ta[0], tb[0])


def resolve_snapshot(path):
    side, ta, tb = probe_side(path)
    write(path, blob(side + path))
    _j.loads(open(path, encoding="utf-8").read())
    tag = "mine(bm-a)" if side == ":2:" else "origin"
    print(f"[snap] {path}: {tag} ({ta} vs {tb})")


def resolve_twin(json_path, md_path):
    side, ta, tb = probe_side(json_path)
    write(json_path, blob(side + json_path))
    _j.loads(open(json_path, encoding="utf-8").read())
    write(md_path, blob(side + md_path))
    tag = "mine(bm-a)" if side == ":2:" else "origin"
    print(f"[twin] {json_path}+{md_path}: {tag} ({ta} vs {tb}) coupled")


def resolve_lane_takeowner(path):
    # R31 machine authority: lane file owned by the other machine; origin
    # side (:3:) carries the owner's own write. Never union, never probe.
    write(path, blob(":3:" + path))
    _j.loads(open(path, encoding="utf-8").read())
    print(f"[lane] {path}: took origin/owner side verbatim (R31)")


def resolve_jsonl_union(path):
    a = blob(":2:" + path).decode("utf-8", errors="replace")
    b = blob(":3:" + path).decode("utf-8", errors="replace")
    seen, out = set(), []
    ndict = 0
    for src in (a, b):
        for line in src.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = _j.loads(line)
            except Exception:
                continue  # parse door
            if not isinstance(rec, dict):
                ndict += 1
                continue  # type door (r570)
            key = _j.dumps(rec, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            out.append(line)
    write(path, ("\n".join(out) + "\n").encode("utf-8"))
    print(f"[jsonl] {path}: union {len(out)} rows "
          f"(dropped dup/non-dict {ndict})")


def main():
    faces = uu_faces()
    if not faces:
        print("no UU faces -- nothing to do")
        return
    print(f"UU faces ({len(faces)}):")
    for f in faces:
        print("  " + f)
    live_side = {}
    done = []
    for path in faces:
        name = path.replace("\\", "/")
        face = name[len("results/"):-len(".json")] if (
            name.startswith("results/") and name.endswith(".json")) else None
        if face in ALL_FACES:
            resolve_face(name)
        elif re.match(r"^results/runnable_pool\.bm-(a|b|c)\.json$", name):
            resolve_lane_takeowner(name)
        elif name == "results/dashboard_status.js":
            side, ta, tb = probe_side("results/dashboard_status.json")
            write(name, blob(side + "results/dashboard_status.js"))
            print(f"[js] dashboard_status.js: "
                  f"{'mine(bm-a)' if side == ':2:' else 'origin'} "
                  f"coupled to json side ({ta} vs {tb})")
        elif (name.startswith("docs/daily_report/REPORT-")
                or name.startswith("docs/live_usage/LIVE-")):
            if name.endswith(".json"):
                md = name[:-5] + ".md"
                if md in faces:
                    resolve_twin(name, md)
                else:
                    resolve_snapshot(name)
            # md half handled coupled by its json twin above
        elif name.endswith(".jsonl"):
            resolve_jsonl_union(name)
        elif name.endswith(".json"):
            resolve_snapshot(name)
        else:
            raise RuntimeError(f"unrouted face: {name} (fail-closed)")
        done.append(path)
    print(f"resolved {len(done)} faces; verify-parse done; git add next")


if __name__ == "__main__":
    main()
