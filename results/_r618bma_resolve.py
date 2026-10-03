# -*- coding: utf-8 -*-
"""r618 bm-a dynamic rebase resolver (per-pick-stop, re-runnable).

Reads `git ls-files -u` each run, routes each UU face by class:
  1. ALL_FACES registry -> scripts/merge_lane_views.py resolve <face>
     (reads rebase 3-stage directly, union recipe, parse-verified write)
  2. twin regen pairs (docs/daily_report/REPORT-*, docs/live_usage/LIVE-*):
     json hardened deep-ts diffpick + md byte-coupled from SAME side (r329)
  3. results/dashboard_status.js: whole-byte side coupled to the
     dashboard_status.json probe verdict (same producer run wrote both)
  4. CODELY.md: memory-union (merge-base prefix identity both sides ->
     base + origin-suffix + my-suffix byte concat; r327 entry-coverage
     fallback) -- never line-level dedupe (r311)
  5. other *.json: snapshot take-new via hardened deep-ts probe on STAGED
     blobs (:2: origin / :3: mine; key normalize strip _-, value must be
     ts-shaped AND carry time-of-day; no key-exclude lists, R350/r100)

Bytes read/written via subprocess git objects / binary mode (r209).
"""
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

ALL_FACES = {
    "compute_audit", "regime_state", "autofill_state", "runnable_pool",
    "gate_attrition", "post_review_criteria", "update_status",
    "heat_update_status", "lhb_update_status", "futures_update_status",
    "fundamental_status", "token_usage",
}

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")
TS_PREFIX = ("generated", "updated", "ts", "asof", "written",
             "scanned", "now", "time")


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
    """ALL_FACES route via merge_lane_views (in-repo single source)."""
    r = subprocess.run(
        ["python", "scripts/merge_lane_views.py", "resolve", path],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        errors="replace")
    print(f"[allface] {path}: rc={r.returncode} "
          f"{(r.stdout or r.stderr).strip()[:160]}")
    if r.returncode != 0:
        raise RuntimeError(f"merge_lane_views resolve {path} failed")


def probe_side(path):
    a = blob(":2:" + path)
    b = blob(":3:" + path)
    ta = deep_ts(a and __import__("json").loads(a.decode("utf-8")))
    tb = deep_ts(b and __import__("json").loads(b.decode("utf-8")))
    assert ta and tb, f"probe miss {path}: {ta} {tb}"
    return (":2:", ta[0], tb[0]) if ta[0] > tb[0] else (":3:", ta[0], tb[0])


def resolve_snapshot(path):
    side, ta, tb = probe_side(path)
    write(path, blob(side + path))
    __import__("json").loads(open(path, encoding="utf-8").read())
    tag = "origin" if side == ":2:" else "mine"
    print(f"[snap] {path}: {tag} ({ta} vs {tb})")


def resolve_twin(json_path, md_path):
    side, ta, tb = probe_side(json_path)
    write(json_path, blob(side + json_path))
    __import__("json").loads(open(json_path, encoding="utf-8").read())
    write(md_path, blob(side + md_path))
    tag = "origin" if side == ":2:" else "mine"
    print(f"[twin] {json_path}+{md_path}: {tag} ({ta} vs {tb}) coupled")


def resolve_codely():
    import json as _j
    mb = subprocess.run(
        ["git", "merge-base", "10530836c", "ad4d006f8"], cwd=ROOT,
        capture_output=True, text=True).stdout.strip()
    base = blob(mb + ":CODELY.md")
    o = blob(":2:CODELY.md")
    m = blob(":3:CODELY.md")
    if o.startswith(base) and m.startswith(base):
        new = m + o[len(base):]
        print(f"[codely] union prefix-OK: base {len(base)} + "
              f"my-suffix {len(m) - len(base)} + origin-suffix "
              f"{len(o) - len(base)} = {len(new)}")
    else:
        # r327 entry-level bidirectional coverage fallback
        base_l = [l for l in base.decode("utf-8").splitlines() if l.strip()]
        o_s = set(o.decode("utf-8").splitlines())
        m_s = set(m.decode("utf-8").splitlines())
        miss_o = [l for l in base_l if l not in o_s]
        miss_m = [l for l in base_l if l not in m_s]
        assert not miss_o and not miss_m, (
            f"coverage fail vs base: origin-missing {miss_o[:1]} "
            f"mine-missing {miss_m[:1]}")
        new = m + o[len(base):] if o.startswith(base) else (
            o + m[len(base):] if m.startswith(base) else None)
        assert new is not None, "neither side prefix-extends base"
        print(f"[codely] union fallback path: {len(new)}")
    write("CODELY.md", new)


def main():
    faces = uu_faces()
    if not faces:
        print("no UU faces -- nothing to do")
        return
    print(f"UU faces ({len(faces)}):")
    for f in faces:
        print("  " + f)
    done = []
    for path in faces:
        name = path.replace("\\", "/")
        face = name[len("results/"):-len(".json")] if (
            name.startswith("results/") and name.endswith(".json")) else None
        if face in ALL_FACES:
            resolve_face(name)
        elif name == "CODELY.md":
            resolve_codely()
        elif name == "results/dashboard_status.js":
            side, ta, tb = probe_side("results/dashboard_status.json")
            write(name, blob(side + "results/dashboard_status.js"))
            print(f"[js] dashboard_status.js: "
                  f"{'origin' if side == ':2:' else 'mine'} "
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
        elif name.endswith(".json"):
            resolve_snapshot(name)
        else:
            raise RuntimeError(f"unrouted face: {name} (fail-closed)")
        done.append(path)
    print(f"resolved {len(done)} faces; verify-parse + add next")


if __name__ == "__main__":
    main()
