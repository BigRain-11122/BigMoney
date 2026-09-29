#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r253 bm-c round2 conflict triage: CODELY lines + x2_watch_log + compute_audit."""
import json, subprocess, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True, cwd=ROOT)
    return r.stdout

def unresolved(path):
    r = subprocess.run(["git", "ls-files", "-u", "--", path], capture_output=True, cwd=ROOT)
    return bool(r.stdout.strip())

# CODELY.md both-side unique lines
if unresolved("CODELY.md"):
    co = blob(2, "CODELY.md").decode("utf-8", "replace")
    ct = blob(3, "CODELY.md").decode("utf-8", "replace")
    lo, lt = co.splitlines(), ct.splitlines()
    so, st = set(lo), set(lt)
    print("CODELY ours=%dB theirs=%dB" % (len(co.encode("utf-8")), len(ct.encode("utf-8"))))
    print("-- only-in-theirs(mine) --")
    for l in lt:
        if l not in so and l.strip(): print("T| " + l[:150])
    print("-- only-in-ours(origin r458) --")
    for l in lo:
        if l not in st and l.strip(): print("O| " + l[:150])

# x2_watch_log.jsonl both sides
if unresolved("results/x2_watch_log.jsonl"):
    xo = blob(2, "results/x2_watch_log.jsonl").decode("utf-8", "replace").strip().splitlines()
    xt = blob(3, "results/x2_watch_log.jsonl").decode("utf-8", "replace").strip().splitlines()
    print("\nx2_watch_log ours=%d lines theirs=%d lines" % (len(xo), len(xt)))
    so, st = set(xo), set(xt)
    print("only-in-theirs=%d only-in-ours=%d" % (sum(1 for l in xt if l not in so), sum(1 for l in xo if l not in st)))
    for l in xt:
        if l not in so: print("T| " + l[:160])
    for l in xo:
        if l not in st: print("O| " + l[:160])

# compute_audit
if unresolved("results/compute_audit.json"):
    o = json.loads(blob(2, "results/compute_audit.json").decode("utf-8"))
    t = json.loads(blob(3, "results/compute_audit.json").decode("utf-8"))
    ok = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in o.get("history", [])}
    tk = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in t.get("history", [])}
    print("\ncompute_audit ours-h=%d theirs-h=%d onlyT=%d onlyO=%d latest ours=%s theirs=%s" % (
        len(o.get("history", [])), len(t.get("history", [])),
        len(tk - ok), len(ok - tk),
        o.get("latest", {}).get("ts"), t.get("latest", {}).get("ts")))
