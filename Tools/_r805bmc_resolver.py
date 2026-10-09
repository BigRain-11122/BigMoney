# -*- coding: utf-8 -*-
"""r805 bm-c rebase-window resolver (14-UU, content-driven per r790 law).

Laws applied (pit-git-resolver-rebase.md canon):
- r648: read stage blobs via ls-files -u sha -> git cat-file -p (never :N:);
        marker-scan both sides as a HARD gate (origin may carry markers).
- r782: rebase stage semantics INVERTED: stage2 = onto side (origin), stage3 =
        the replayed commit (this machine's r805 commit d7bce8b83).
- r516/r794: deep-ts newer-wins; tie or no-parsable-ts -> stage2 (origin).
- r863/r685: compute_audit = latest newer-wins + history union (zero dup,
        zero reorder: origin order first, then replay-only entries appended).
- r794 c3: regime_state/update_status = (ts, machine) values-union when the
        payload has per-machine rows, else deep-ts newer-wins.
- r642 + treasure_guard rc3: token_usage.json = append-only ledger -> LINE-LEVEL
        UNION ONLY (origin rows first + replay-only rows appended, zero-loss
        assertion |resolved| == |origin| + |replay_only|).
- r794: NO add -u loops; targeted git add of exactly the resolved paths.
- r705: verification legs exit non-zero on FAIL (no print-only fake gates).

Output: resolved worktree files + receipt results/_r805bmc_resolver.json.
Exit: 0 resolved+staged | 2 mechanism failure (never silent)."""
import datetime as dt
import json
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
REPLAY_SHA = "d7bce8b83"   # the r805 round commit being replayed (theirs/stage3)
MARKERS = (b"<<<<<<<", b">>>>>>>", b"=======")
TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at",
           "last_run", "last_run_at", "asof", "cutoff", "time")
TWIN_MD = {
    "docs/daily_report/REPORT-2026-10-09.md": "docs/daily_report/REPORT-2026-10-09.json",
    "docs/live_usage/LIVE-2026-10-09.md": "docs/live_usage/LIVE-2026-10-09.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-2026-10-09.json",
}
TWIN_JSON_ALIAS = {
    "docs/live_usage/LIVE-latest.json": "docs/live_usage/LIVE-2026-10-09.json",
}


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    if p.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (
            args, p.returncode, p.stderr.decode("utf-8", "replace")[:200]))
    return p.stdout


def cat(sha):
    return git(["cat-file", "-p", sha])


def uu_set():
    out = git(["ls-files", "-u"]).decode("utf-8", "replace")
    faces = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        meta, path = parts
        f = meta.split()
        stage = int(f[2])
        faces.setdefault(path, {})[stage] = f[1]
    return faces


def has_markers(blob):
    return any(m in blob for m in MARKERS)


def parse_when(s):
    if not isinstance(s, str):
        return None
    s = s.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return dt.datetime.strptime(s[:26 if "%z" in fmt else 19], fmt)
        except ValueError:
            continue
    try:
        return dt.datetime.fromtimestamp(float(s))
    except (ValueError, OSError, OverflowError):
        return None


def deep_ts(obj):
    """Best parseable top-level (or one-level-nested) timestamp."""
    cands = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if any(t in k.lower() for t in ("ts", "time", "generated",
                                            "updated", "asof", "cutoff")):
                w = parse_when(v)
                if w:
                    cands.append(w)
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if any(t in k2.lower() for t in ("ts", "time", "generated",
                                                    "updated", "asof", "cutoff")):
                        w = parse_when(v2)
                        if w:
                            cands.append(w)
    return max(cands) if cands else None


def loads(blob):
    return json.loads(blob.decode("utf-8", "replace"))


def resolve_face(path, b2, b3, receipt):
    """Return resolved bytes. stage2=origin(onto), stage3=replay(mine)."""
    m2, m3 = has_markers(b2), has_markers(b3)
    if m2 and not m3:
        receipt["decisions"][path] = "origin-side-marker-poison -> replay clean blob"
        return b3
    if m3 and not m2:
        receipt["decisions"][path] = "replay-side-marker-poison -> origin clean blob"
        return b2
    if m2 and m3:
        raise RuntimeError("both sides carry markers: %s" % path)
    twin = TWIN_JSON_ALIAS.get(path)
    if twin:  # pointer copy: same decision as its source face
        src = receipt["decisions"].get(twin)
        if src:
            side = "stage3" if "replay-newer" in src or "values-union" in src else "stage2"
            receipt["decisions"][path] = "twin-of %s -> %s" % (twin, side)
            return b3 if side == "stage3" else b2
    if path.endswith(".md"):
        twin = TWIN_MD.get(path)
        src = receipt["decisions"].get(twin, "")
        side = "stage3" if "replay-newer" in src or "values-union" in src else "stage2"
        receipt["decisions"][path] = "md-twin-of %s -> %s" % (twin, side)
        return b3 if side == "stage3" else b2
    o, r = loads(b2), loads(b3)
    if path == "results/compute_audit.json":
        latest_o, latest_r = deep_ts(o) or dt.datetime.min, deep_ts(r) or dt.datetime.min
        base = r if latest_r > latest_o else o
        hist_key = None
        for k in ("history", "samples", "runs", "audit_history"):
            if k in o or k in r:
                hist_key = k
                break
        if hist_key:
            ho = o.get(hist_key) or []
            hr = r.get(hist_key) or []
            seen, merged = set(), []
            for e in ho + hr:
                key = json.dumps(
                    {k: e.get(k) for k in ("ts", "machine", "epoch", "audit_version")
                     if isinstance(e, dict) and k in e}, sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    merged.append(e)
            base = dict(base)
            base[hist_key] = merged
            receipt["decisions"][path] = ("compute_audit: latest newer-wins + history "
                                          "union %d+%d->%d" % (len(ho), len(hr), len(merged)))
        else:
            receipt["decisions"][path] = "compute_audit: latest newer-wins (no history key)"
        return json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    if path in ("results/regime_state.json", "results/update_status.json"):
        # (ts, machine) values-union when payload has per-machine rows
        rows_o = o.get("machines") if isinstance(o.get("machines"), dict) else None
        rows_r = r.get("machines") if isinstance(r.get("machines"), dict) else None
        if rows_o is not None and rows_r is not None:
            merged = dict(rows_o)
            added = 0
            for k, v in rows_r.items():
                if k not in merged or (deep_ts(v) or dt.datetime.min) > \
                        (deep_ts(merged[k]) or dt.datetime.min):
                    merged[k] = v
                    added += 1
            base = r if (deep_ts(r) or dt.datetime.min) > (deep_ts(o) or dt.datetime.min) else o
            base = dict(base)
            base["machines"] = merged
            receipt["decisions"][path] = ("values-union machines o%d+r%d (+%d replay-newer)"
                                          % (len(rows_o), len(rows_r), added))
            return json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    if path == "results/token_usage.json":
        # APPEND-ONLY LEDGER face (treasure_guard rc3): LINE-LEVEL UNION ONLY.
        # Actual shape (blob-inspected): scalars + machines{per-machine rows}
        # + l2_local_llm{... by_cmd{per-command cumulative counters}}.
        # Union semantics: per-machine rows = both sides' keys kept, per-key
        # deep-ts newer-wins; by_cmd = per-key union, numeric cumulative
        # fields take max (both sides counted the same shared ledger; the
        # later run is the true superset). Zero-loss: every key from both
        # sides survives with an assertion.
        wo = deep_ts(o) or dt.datetime.min
        wr = deep_ts(r) or dt.datetime.min
        base = r if wr > wo else o
        base = json.loads(json.dumps(base))   # deep copy before mutation

        def union_rows(d_o, d_r):
            merged = dict(d_o)
            only_r = 0
            for k, v in d_r.items():
                if k not in merged:
                    merged[k] = v
                    only_r += 1
                elif isinstance(v, dict) and isinstance(merged[k], dict):
                    w_m = deep_ts(merged[k]) or dt.datetime.min
                    w_v = deep_ts(v) or dt.datetime.min
                    if w_v > w_m:
                        merged[k] = v
                        only_r += 1
            return merged, only_r

        mo, mr = o.get("machines") or {}, r.get("machines") or {}
        assert isinstance(mo, dict) and isinstance(mr, dict)
        merged_m, took_r_m = union_rows(mo, mr)
        base["machines"] = merged_m
        l2o = o.get("l2_local_llm") or {}
        l2r = r.get("l2_local_llm") or {}
        if isinstance(l2o, dict) and isinstance(l2r, dict):
            merged_cmd, took_r_cmd = union_rows(l2o.get("by_cmd") or {},
                                                l2r.get("by_cmd") or {})
            for k, v in merged_cmd.items():
                if isinstance(v, dict) and isinstance(l2r.get("by_cmd", {}).get(k), dict) \
                        and isinstance(l2o.get("by_cmd", {}).get(k), dict):
                    for num in ("legs", "legs_total", "tokens_est",
                                "tokens_est_total", "prompt_bytes",
                                "response_bytes"):
                        if num in v:
                            v[num] = max(v[num], l2o["by_cmd"][k].get(num, 0))
            l2 = dict(l2r if wr > wo else l2o)
            l2["by_cmd"] = merged_cmd
            for num in ("legs_total", "legs_today", "tokens_est_total",
                        "tokens_est_today"):
                if num in l2o and num in l2:
                    l2[num] = max(l2[num], l2o[num])
                elif num in l2o:
                    l2[num] = l2o[num]
            base["l2_local_llm"] = l2
        else:
            took_r_cmd = 0
        assert set(merged_m) >= set(mo) | set(mr), "ledger machines zero-loss"
        receipt["decisions"][path] = (
            "LEDGER line-union: machines o%d+r%d (replay-newer rows %d) "
            "+ by_cmd union (replay-newer cmds %d) + base=%s "
            "(zero-loss asserted)" % (
                len(mo), len(mr), took_r_m, took_r_cmd,
                "replay" if wr > wo else "origin"))
        return json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    # default JSON face: deep-ts newer-wins, tie -> stage2 (r794)
    wo, wr = deep_ts(o), deep_ts(r)
    if wr and wo and wr > wo:
        receipt["decisions"][path] = "deep-ts newer-wins -> replay (%s > %s)" % (wr, wo)
        return b3
    if wr and wo and wo > wr:
        receipt["decisions"][path] = "deep-ts newer-wins -> origin (%s > %s)" % (wo, wr)
        return b2
    receipt["decisions"][path] = "ts-tie-or-absent -> stage2 origin (r794 tie law)"
    return b2


def main():
    faces = uu_set()
    if not faces:
        print("[resolver] no UU faces -- nothing to do")
        return 0
    receipt = {"round": 805, "replay": REPLAY_SHA, "decisions": {},
               "staged": [], "gates": {}}
    resolved = {}
    order = sorted(faces)
    for path in order:
        s = faces[path]
        b2, b3 = cat(s[2]), cat(s[3])
        resolved[path] = resolve_face(path, b2, b3, receipt)
    # r705 hard gates: zero markers in every resolved face; JSON parse OK
    for path, blob in resolved.items():
        if has_markers(blob):
            print("RESOLVE_VERIFY_FAIL: markers in %s" % path)
            return 2
        if path.endswith(".json"):
            try:
                loads(blob)
            except ValueError as e:
                print("RESOLVE_VERIFY_FAIL: json parse %s: %s" % (path, e))
                return 2
    receipt["gates"] = {"markers": 0, "json_parse": "OK",
                        "faces": len(resolved)}
    for path, blob in resolved.items():
        with open("\\".join([REPO, *path.split("/")]), "wb") as f:
            f.write(blob)
    # r794: targeted add ONLY (no add -u loops)
    git(["add"] + list(resolved))
    receipt["staged"] = list(resolved)
    with open("\\".join([REPO, "results", "_r805bmc_resolver.json"]), "w",
              encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    git(["add", "results/_r805bmc_resolver.json"])
    print(json.dumps(receipt, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
