# -*- coding: utf-8 -*-
"""r456 bm-c merge resolve: 14 UU faces per r450/r452/r453/r655/r657 recipes.
Auto honest-ts side-pick: survey both stage blobs, decide per face, apply via
checkout --ours/--theirs, union the union-faces, then guards (line-start
marker scan r453/r657 + JSON reparse + union containment) + git add + zero-UU
assert. compute_audit history-union recipe per r455 verbatim (latest by ts);
token_usage per-machine-key union with whole-file-newer fallback. Tie -> ours
(r452 deterministic-tie precedent). Probe-miss -> ours + dual-head disclosure
(r655 law). Merge commit itself staged separately."""
import json
import re
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

REGEN = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
AUDIT = "results/compute_audit.json"
TOKEN = "results/token_usage.json"
ALL_FACES = REGEN + [AUDIT, TOKEN]


def run(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                          text=True, encoding="utf-8", errors="replace",
                          creationflags=CNW)


def run_raw(args):
    return subprocess.run(["git"] + args, capture_output=True, cwd=ROOT,
                          creationflags=CNW)


def blob(side, path):
    return run_raw(["show", ":%s:%s" % (side, path)]).stdout


TS_RE = re.compile(r"2026-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?")
TS_KEYS = ("ts", "generated_at", "generated", "updated_at", "updated",
           "last_fetch_attempt", "probe_time", "asof", "time")


def _walk_ts(obj, depth=0):
    if depth > 6:
        return None
    if isinstance(obj, dict):
        for k in TS_KEYS:
            v = obj.get(k)
            if isinstance(v, str) and TS_RE.search(v):
                return TS_RE.search(v).group(0)
        for v in obj.values():
            r = _walk_ts(v, depth + 1)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = _walk_ts(v, depth + 1)
            if r:
                return r
    return None


def face_ts(raw, is_json):
    if is_json:
        try:
            return _walk_ts(json.loads(raw.decode("utf-8", "replace")))
        except Exception:
            pass
    m = TS_RE.search(raw.decode("utf-8", "replace"))
    return m.group(0) if m else None


def main():
    # 1) regen faces: honest-ts side-pick
    decisions = []
    for f in REGEN:
        o, t = blob("2", f), blob("3", f)
        isj = f.endswith(".json")
        to, tt = face_ts(o, isj), face_ts(t, isj)
        if to and tt:
            side = "ours" if to >= tt else "theirs"
            note = "ts ours=%s theirs=%s" % (to, tt)
        else:
            side = "ours"
            note = ("PROBE-MISS ours_ts=%s theirs_ts=%s | OURS[:100]=%r | "
                    "THEIRS[:100]=%r" % (to, tt,
                                         o[:100].decode("utf-8", "replace"),
                                         t[:100].decode("utf-8", "replace")))
        r = run(["checkout", "--" + side, f])
        assert r.returncode == 0, "checkout %s failed: %s" % (side, f)
        decisions.append((f, side, note))
    for f, side, note in decisions:
        print("%-46s -> %s  (%s)" % (f, side.upper(), note))

    # 2) compute_audit union (r455 recipe, latest by honest ts)
    ours = json.loads(blob("2", AUDIT).decode("utf-8", "replace"))
    theirs = json.loads(blob("3", AUDIT).decode("utf-8", "replace"))
    h_o = ours.get("history", [])
    h_t = theirs.get("history", [])
    seen = {}
    order = []
    for e in h_t + h_o:
        k = e.get("ts")
        if k in seen:
            seen[k] = e          # same ts: ours wins (iterated last)
        else:
            seen[k] = e
            order.append(k)
    union = [seen[k] for k in sorted(order)]
    assert len(union) >= max(len(h_o), len(h_t)), "audit union shrank"
    assert set(e.get("ts") for e in h_o) <= set(seen), "ours audit not contained"
    assert set(e.get("ts") for e in h_t) <= set(seen), "theirs audit not contained"
    merged = dict(theirs)          # superset top keys (machines, ts)
    merged["history"] = union
    lo_ts = (ours.get("latest") or {}).get("ts", "")
    lt_ts = (theirs.get("latest") or {}).get("ts", "")
    merged["latest"] = ours["latest"] if lo_ts >= lt_ts else theirs["latest"]
    if "ts" in merged:
        merged["ts"] = merged["latest"].get("ts", theirs.get("ts"))
    out = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
    with open(ROOT + "\\results\\compute_audit.json", "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(out)
    print("COMPUTE_AUDIT union: hist %d+%d -> %d, latest=%s (ours %s vs theirs %s)"
          % (len(h_o), len(h_t), len(union), merged["latest"].get("ts"), lo_ts, lt_ts))

    # 3) token_usage: per-machine-key union, whole-file-newer fallback
    ok = False
    try:
        o = json.loads(blob("2", TOKEN).decode("utf-8", "replace"))
        t = json.loads(blob("3", TOKEN).decode("utf-8", "replace"))
        if isinstance(o, dict) and isinstance(t, dict):
            m = dict(t)
            per = 0
            for k, v in o.items():
                tv = t.get(k)
                if isinstance(v, dict) and isinstance(tv, dict) and \
                        isinstance(v.get("ts"), str) and isinstance(tv.get("ts"), str):
                    m[k] = v if v["ts"] >= tv["ts"] else tv
                    per += 1
                elif k not in t:
                    m[k] = v
            out = json.dumps(m, ensure_ascii=False, indent=1) + "\n"
            with open(ROOT + "\\results\\token_usage.json", "w",
                      encoding="utf-8", newline="\n") as fh:
                fh.write(out)
            print("TOKEN_USAGE per-key union: %d keys side-picked by ts "
                  "(top keys: %s)" % (per, sorted(set(o) | set(t))[:8]))
            ok = True
    except Exception as e:
        print("TOKEN_USAGE per-key union failed: %s -> fallback" % str(e)[:80])
    if not ok:
        o = blob("2", TOKEN)
        t = blob("3", TOKEN)
        to, tt = face_ts(o, True), face_ts(t, True)
        side = "ours" if (to or "") >= (tt or "") else "theirs"
        r = run(["checkout", "--" + side, TOKEN])
        assert r.returncode == 0
        print("TOKEN_USAGE fallback whole-file %s (ours %s vs theirs %s)"
              % (side.upper(), to, tt))

    # 4) guards: line-start marker scan + JSON reparse (all 14 faces)
    bad = []
    for f in ALL_FACES:
        p = ROOT + "\\" + f.replace("/", "\\")
        with open(p, "rb") as fh:
            raw = fh.read()
        for ln in raw.split(b"\n"):
            if ln.startswith(b"<<<<<<<") or ln.startswith(b">>>>>>>") or \
               (ln.strip() == b"======="):
                bad.append(f + " MARKER")
                break
        if f.endswith(".json"):
            try:
                json.loads(raw.decode("utf-8", "replace"))
            except Exception as e:
                bad.append(f + " JSON-FAIL:" + str(e)[:60])
    assert not bad, "guards failed: %s" % bad
    print("MARKER+JSON guards PASS (14 faces)")

    # 5) stage + zero-UU assert
    r = run(["add"] + ALL_FACES)
    assert r.returncode == 0, "add failed: " + (r.stdout + r.stderr)[:200]
    r = run(["diff", "--name-only", "--diff-filter=U"])
    assert not r.stdout.strip(), "UU still present: " + r.stdout
    print("STAGED 14 faces, zero UU remaining")
    print("RESOLVE_DONE")


if __name__ == "__main__":
    main()
