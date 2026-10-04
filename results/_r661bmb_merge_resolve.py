# r661 merge resolver: 15 UU faces, bilateral originals via HEAD:/MERGE_HEAD: (r657 law 2)
# Face routing: CODELY.md=union+dedup (r453) | machines-keyed=per-key union w/ side-pick>0 assert (r456) | ts-snapshot=take-newer (r455) | history-bearing=hist union
import subprocess, json, sys

def side(path, which):
    r = subprocess.run(["git", "show", "%s:%s" % (which, path)], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def loadj(b):
    return json.loads(b.decode("utf-8"))

report = {}

def take_newer_json(path, ts_keys=("ts", "generated", "updated", "updated_at", "generated_at")):
    ours, theirs = side(path, "HEAD"), side(path, "MERGE_HEAD")
    if ours is None or theirs is None:
        report[path] = "MISSING SIDE"; return None
    try:
        o, t = loadj(ours), loadj(theirs)
    except Exception as e:
        report[path] = "PARSE FAIL %s" % e; return None
    def ts_of(x):
        for k in ts_keys:
            v = x.get(k) if isinstance(x, dict) else None
            if isinstance(v, str) and v: return v
        return ""
    to, tt = ts_of(o), ts_of(t)
    win = "ours" if to >= tt else "theirs"
    data = o if win == "ours" else t
    blob = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8")
    report[path] = "take-newer %s (ours_ts=%s theirs_ts=%s)" % (win, to, tt)
    return blob

def per_key_union_json(path, section, keyfields=("ts", "updated", "last_seen")):
    # machines-keyed (or named section) union: per-key take-newer by inner ts
    ours, theirs = side(path, "HEAD"), side(path, "MERGE_HEAD")
    if ours is None or theirs is None:
        report[path] = "MISSING SIDE"; return None
    o, t = loadj(ours), loadj(theirs)
    so, st = o.get(section, {}), t.get(section, {})
    if not isinstance(so, dict) or not isinstance(st, dict):
        report[path] = "section not dict"; return None
    out = dict(so); picks = 0
    for k, v in st.items():
        if k not in out:
            out[k] = v; picks += 1
        else:
            tv = str(out[k].get(keyfields[0], "") or "")
            nv = str(v.get(keyfields[0], "") or "")
            if nv > tv:
                out[k] = v; picks += 1
    if picks == 0:
        # r456 law: zero side-pick -> fall to whole-face freshness
        to = str(o.get("ts", "") or ""); tt = str(t.get("ts", "") or "")
        if tt > to:
            report[path] = "per-key 0-pick -> whole-face theirs (ts %s>%s)" % (tt, to)
            return theirs
        report[path] = "per-key 0-pick -> whole-face ours (ts %s<=%s)" % (to, tt)
        return ours
    o[section] = out
    blob = json.dumps(o, ensure_ascii=False, indent=1).encode("utf-8")
    report[path] = "per-key union picks=%d (section=%s keys=%d)" % (picks, section, len(out))
    return blob

def hist_union_json(path, hist_key, id_key, ts_key="ts"):
    ours, theirs = side(path, "HEAD"), side(path, "MERGE_HEAD")
    if ours is None or theirs is None:
        report[path] = "MISSING SIDE"; return None
    o, t = loadj(ours), loadj(theirs)
    ho = o.get(hist_key) or []; ht = t.get(hist_key) or []
    seen = {}
    for row in list(ho) + list(ht):
        rid = str(row.get(id_key, id(row)))
        ts = str(row.get(ts_key, ""))
        if rid not in seen or ts > str(seen[rid].get(ts_key, "")):
            seen[rid] = row
    merged = sorted(seen.values(), key=lambda r: str(r.get(ts_key, "")))
    o[hist_key] = merged
    # snapshot fields: take-newer top-level ts
    if str(t.get(ts_key, "")) > str(o.get(ts_key, "")):
        for k, v in t.items():
            if k != hist_key and not isinstance(v, (list, dict)):
                o[k] = v
    blob = json.dumps(o, ensure_ascii=False, indent=1).encode("utf-8")
    report[path] = "hist-union rows=%d" % len(merged)
    return blob

def codely_union():
    ours, theirs = side("CODELY.md", "HEAD"), side("CODELY.md", "MERGE_HEAD")
    ot = ours.decode("utf-8")
    # r439-family repair: my r661 append glued onto the r660 line tail (conditional-sep bug:
    # file did not end with \n -> sep=b"" -> entry concatenated mid-line). Insert "\n" before
    # the mid-line "- [2026-10-04 09:4x r661 bm-b]" occurrence (needle count==1 gate).
    needle = "- [2026-10-04 09:4x r661 bm-b]"
    lines0 = ot.split("\n")
    midline_hits = sum(1 for l in lines0 if needle in l and not l.startswith(needle))
    assert midline_hits == 1, "r661 midline glue occurrences=%d (expected 1)" % midline_hits
    ot = ot.replace(needle, "\n" + needle, 1)
    # post-repair: marker must now be at line start
    assert sum(1 for l in ot.split("\n") if l.startswith(needle)) == 1, "repair did not restore line start"
    ol = ot.split("\n")
    tl = theirs.decode("utf-8").split("\n")
    # r453: exact-line dedup keep-first, ours base + theirs additions
    seen = set(); out = []
    for l in ol + tl:
        key = l.strip()
        if key and key in seen and key.startswith("- "):
            continue
        if key: seen.add(key)
        out.append(l)
    text = "\n".join(out)
    # marker assertions (r453/r657: line-start markers, count==1 each)
    for marker in ("[2026-10-04 09:4x r661 bm-b]",):
        c = sum(1 for l in out if l.startswith("- " + marker) or l.startswith(marker))
        assert c == 1, "marker %s count=%d" % (marker, c)
    blob = text.encode("utf-8")
    report["CODELY.md"] = "union lines=%d (ours=%d theirs=%d, r439-glue repaired)" % (len(out), len(ol), len(tl))
    return blob

def twins(path_md):
    # md + json twin: resolve by json ts, write both sides consistently
    j = path_md.replace(".md", ".json")
    blob = take_newer_json(j)
    if blob is None: return
    win = report[j]
    # write the same winner for md
    which = "HEAD" if "ours" in win else "MERGE_HEAD"
    md = side(path_md, which)
    open(j, "wb").write(blob)
    open(path_md, "wb").write(md)
    report[path_md] = "twin follows json winner (%s)" % which

writes = []

# 1) CODELY.md union
b = codely_union()
open("CODELY.md", "wb").write(b); writes.append("CODELY.md")

# 2) twins (daily_report + live_usage): json decides, md follows
for md in ("docs/daily_report/REPORT-2026-10-04.md", "docs/live_usage/LIVE-2026-10-04.md"):
    twins(md)
for j in ("docs/live_usage/LIVE-latest.json",):
    b = take_newer_json(j)
    if b is not None: open(j, "wb").write(b); writes.append(j)
md = "docs/live_usage/LIVE-latest.md"
which = "HEAD" if "ours" in report.get("docs/live_usage/LIVE-latest.json", "ours") else "MERGE_HEAD"
open(md, "wb").write(side(md, which)); report[md] = "pointer-twin follows (%s)" % which

# 3) ts-snapshot regen faces: take-newer
for p in ("results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/regime_state.json", "results/update_status.json"):
    b = take_newer_json(p)
    if b is not None: open(p, "wb").write(b); writes.append(p)

# 4) compute_audit: hist union if history key present, else take-newer
ours = loadj(side("results/compute_audit.json", "HEAD"))
hist_keys = [k for k in ours.keys() if isinstance(ours[k], list) and ours[k] and isinstance(ours[k][0], dict)]
if hist_keys:
    b = hist_union_json("results/compute_audit.json", hist_keys[0], "ts", "ts")
else:
    b = take_newer_json("results/compute_audit.json")
if b is not None: open("results/compute_audit.json", "wb").write(b); writes.append("results/compute_audit.json")

# 5) token_usage: machines-keyed union (r456 precedent) with side-pick assert
b = per_key_union_json("results/token_usage.json", "machines", ("ts", "updated", "last_seen"))
if b is not None: open("results/token_usage.json", "wb").write(b); writes.append("results/token_usage.json")

# reparse gate on every written json
for p in writes:
    if p.endswith(".json"):
        json.load(open(p, encoding="utf-8"))
print(json.dumps(report, ensure_ascii=False, indent=1))
print("REPARSE ALL PASS | writes:", len(writes))
