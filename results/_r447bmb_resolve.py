# -*- coding: utf-8 -*-
# r447 bm-b stash-pop conflict resolver (bigmoney-conflict-resolve skill recipes)
# Classes: 12x snapshot(take-new via ts probe) / 2x rolling-ledger(union) /
#          1x js-wrapper-snapshot(take-side with json twin) / 1x UD(identical, keep ours)
# Idempotent: if no unmerged paths exist, no-op exit 0 (r457 law).
import subprocess, json, os, sys, re

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

def git(args, check=True):
    r = subprocess.run(["git"] + args, capture_output=True, cwd=REPO)
    if check and r.returncode != 0:
        raise RuntimeError("git %s: %s" % (args[:3], r.stderr.decode(errors="replace")[:300]))
    return r

def unmerged():
    r = git(["ls-files", "-u"])
    out = []
    for line in r.stdout.decode("utf-8", errors="replace").strip().splitlines():
        meta, path = line.split("\t", 1)
        parts = meta.split()
        out.append((int(parts[2]), parts[1], path))
    return out

def blob_bytes(sha):
    return git(["cat-file", "blob", sha]).stdout

PROBE_PREFIXES = ("generated", "ts", "updated", "cutoff", "asof", "date", "now",
                  "generatedat", "reportdate", "day", "lastseen", "clockread")

def norm_key(k):
    return k.replace("_", "").replace("-", "").lower()

def probe_ts(obj, best=None):
    # r100/R350: deep-scan nested layers; key normalized prefix match; value ^20\d{2}-
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = norm_key(k)
            if any(nk.startswith(p) for p in PROBE_PREFIXES) and isinstance(v, str) \
               and v[:2] == "20" and len(v) >= 10 and v[4] == "-":
                if best is None or v > best:
                    best = v
            best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    return best

def resolve_snapshot(p, entries):
    b = {}
    for stage, sha, _ in entries:
        b[stage] = blob_bytes(sha)
    t2 = probe_ts(json.loads(b[2]))
    t3 = probe_ts(json.loads(b[3]))
    win = b[3] if (t3 or "") >= (t2 or "") else b[2]
    side = "theirs(stash)" if win is b[3] else "ours(HEAD)"
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(win)
    git(["add", "--", p])
    return side, t2, t3

def resolve_union(p, entries):
    b = {s: blob_bytes(sha) for s, sha, _ in entries}
    d2, d3 = json.loads(b[2]), json.loads(b[3])
    merged = dict(d3) if (probe_ts(d3) or "") >= (probe_ts(d2) or "") else dict(d2)
    # scalar/dict state fields take-new already via base choice; union every list-of-dict face
    for k, v in list(merged.items()):
        if isinstance(v, list) and v and isinstance(v[0], dict):
            seen = set()
            union = []
            for src in (d2.get(k), d3.get(k)):
                for e in (src or []):
                    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
                    if key not in seen:
                        seen.add(key)
                        union.append(e)
            # keep chronological order if entries carry a ts-ish field
            if union and any(norm_key(x) in ("ts", "updated", "generated", "time", "date") for x in union[0]):
                tk = next(x for x in union[0] if norm_key(x) in ("ts", "updated", "generated", "time", "date"))
                union.sort(key=lambda e: str(e.get(tk, "")))
            n2, n3 = len(d2.get(k, [])), len(d3.get(k, []))
            assert len(union) >= max(n2, n3), "union loss on %s:%s" % (p, k)
            merged[k] = union
            print("    union %s: |s2|=%d |s3|=%d -> |union|=%d" % (k, n2, n3, len(union)))
    out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
    with open(os.path.join(REPO, p), "wb") as f:
        f.write(out)
    json.loads(open(os.path.join(REPO, p), "rb").read().decode("utf-8"))  # parse-verify
    git(["add", "--", p])
    return "union+take-new"

def main():
    um = unmerged()
    if not um:
        print("no unmerged entries; idempotent no-op")
        return 0
    by_path = {}
    for stage, sha, path in um:
        by_path.setdefault(path, []).append((stage, sha, path))
    results = {}
    md_follow = {}
    for p, entries in sorted(by_path.items()):
        st = sorted(e[0] for e in entries)
        if p == "fleet/inbox/processed/MSG-20260930-0356-bma-ALL-W13-berth.md":
            # UD: ours kept; stash^3 copy verified byte-identical earlier (sha 973309eb)
            git(["add", "--", p])
            results[p] = "UD-identical keep-ours"
        elif p == "results/compute_audit.json" or p == "results/regime_state.json":
            results[p] = resolve_union(p, entries)
        elif p == "results/dashboard_status.js":
            results[p] = "PENDING-js-twin"
        elif p.endswith(".md") and p.startswith(("docs/daily_report/", "docs/live_usage/")):
            # md twin: independent ISO-timestamp regex scan of both blobs, take-new
            ent = entries
            b = {e[0]: blob_bytes(e[1]) for e in ent}
            ts_re = re.compile(rb"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2})?")
            t2 = ts_re.findall(b[2]) or [b""]
            t3 = ts_re.findall(b[3]) or [b""]
            win = b[3] if max(t3) >= max(t2) else b[2]
            with open(os.path.join(REPO, p), "wb") as f:
                f.write(win)
            git(["add", "--", p])
            results[p] = "take-new md-regex %s (t2=%s t3=%s)" % (
                "theirs(stash)" if win is b[3] else "ours(HEAD)", max(t2).decode(), max(t3).decode())
        else:
            side, t2, t3 = resolve_snapshot(p, entries)
            results[p] = "take-new %s (t2=%s t3=%s)" % (side, t2, t3)
            twin = p[:-5] + ".md" if p.endswith(".json") else None
            if twin and twin in md_follow:
                # resolve md twin with the same winning side
                ent = by_path[twin]
                b = {e[0]: blob_bytes(e[1]) for e in ent}
                win = b[3] if side.startswith("take-new theirs") else b[2]
                with open(os.path.join(REPO, twin), "wb") as f:
                    f.write(win)
                git(["add", "--", twin])
                md_follow[twin] = "resolved-with-json-twin %s" % ("theirs" if win is b[3] else "ours")
    # js twin follows dashboard_status.json winner
    dsp = "results/dashboard_status.json"
    if dsp in results and results[dsp].startswith("take-new"):
        ent = by_path["results/dashboard_status.js"]
        b = {e[0]: blob_bytes(e[1]) for e in ent}
        win = b[3] if "theirs" in results[dsp] else b[2]
        with open(os.path.join(REPO, "results/dashboard_status.js"), "wb") as f:
            f.write(win)
        git(["add", "--", "results/dashboard_status.js"])
        results["results/dashboard_status.js"] = "take-side with json twin %s" % ("theirs" if win is b[3] else "ours")
    for p in list(md_follow):
        if md_follow[p].startswith("PENDING"):
            results[p] = "UNRESOLVED-twin-missing"
    for p, v in sorted(results.items()):
        print("%-55s %s" % (p, v))
    rem = unmerged()
    if rem:
        print("FAIL: %d unmerged remain" % len(rem))
        return 2
    print("all resolved")
    return 0

if __name__ == "__main__":
    sys.exit(main())
