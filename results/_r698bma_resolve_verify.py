# -*- coding: utf-8 -*-
"""r698 bm-a: verify resolver suspicions before trusting (r641 reproduce-first).
(a) pool_red_flags / pool_core_samples HEAD-side internal dupes;
(b) token_usage.json real structure both sides (default key?);
(c) which machine entries differ (side_picks=2)."""
import json, subprocess, io, collections


def side(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout

out = io.StringIO()

for path in ("results/pool_red_flags.jsonl", "results/pool_core_samples.jsonl"):
    for ref in ("HEAD", "MERGE_HEAD"):
        raw = side(ref, path).decode("utf-8-sig")
        lines = [ln for ln in raw.split("\n") if ln.strip()]
        c = collections.Counter(lines)
        dupes = {k: v for k, v in c.items() if v > 1}
        print("%s @%s: rows=%d distinct=%d internal_dupes=%d" % (
            path, ref, len(lines), len(c), sum(v - 1 for v in dupes.values())), file=out)
        for k, v in list(dupes.items())[:3]:
            print("   dupx%d: %s" % (v, k[:160]), file=out)

print(file=out)
print("=== token_usage structure ===", file=out)
ja = json.loads(side("HEAD", "results/token_usage.json").decode("utf-8-sig"))
jb = json.loads(side("MERGE_HEAD", "results/token_usage.json").decode("utf-8-sig"))
print("ours top keys:", sorted(ja.keys()), file=out)
print("theirs top keys:", sorted(jb.keys()), file=out)
ma, mb = ja.get("machines", {}), jb.get("machines", {})
for k in sorted(set(ma) | set(mb)):
    same = ma.get(k) == mb.get(k)
    print("  machine %s same=%s" % (k, same), file=out)
    if not same:
        va, vb = ma.get(k), mb.get(k)
        sa = json.dumps(va, sort_keys=True)[:200] if va is not None else "None"
        sb = json.dumps(vb, sort_keys=True)[:200] if vb is not None else "None"
        print("    ours  : %s" % sa, file=out)
        print("    theirs: %s" % sb, file=out)
for key in sorted(set(ja) | set(jb)):
    if key != "machines":
        va, vb = ja.get(key), jb.get(key)
        if va != vb:
            print("  TOP-DIFF %s: ours=%r theirs=%r" % (key, str(va)[:100], str(vb)[:100]), file=out)

with open("results/_r698bma_resolve_verify.txt", "w", encoding="utf-8", newline="") as fh:
    fh.write(out.getvalue())
print(out.getvalue())
