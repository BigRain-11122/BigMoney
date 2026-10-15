# r1029 bm-c rebase conflict resolver: shared regenerable faces
# law: single-object/ts faces -> theirs wholesale (bm-a r1018 chain ran after mine; host faces
# scorecard/dashboard/export are bm-a-owned single-writer anyway); compute_audit.json -> history
# union-by-ts + newer latest; append-only jsonl -> line union dedup.
import json
import subprocess
import sys

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

UNION_BY_TS = ["results/compute_audit.json"]
LINE_UNION = ["results/t24_prospect_paper_cells.jsonl",
              "results/x2_watch_log.jsonl"]


def git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a),
                          capture_output=True).stdout


def stage2(p):
    return git("show", ":2:" + p)


def stage3(p):
    return git("show", ":3:" + p)


def resolve_union_by_ts(path):
    ours = json.loads(stage2(path).decode("utf-8"))
    theirs = json.loads(stage3(path).decode("utf-8"))
    # history union by ts (audit history lives under 'history' key; entries carry 'ts')
    hist_o = ours.get("history", [])
    hist_t = theirs.get("history", [])
    merged = {}
    for e in hist_o + hist_t:
        k = e.get("ts")
        if k:
            merged[k] = e  # later write wins same ts
    hist = [merged[k] for k in sorted(merged)]
    latest = theirs if len(hist_t) >= len(hist_o) else ours
    if isinstance(latest, dict):
        out = dict(latest)
        out["history"] = hist
    else:
        out = latest
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return "union ts=%d (o=%d t=%d)" % (len(hist), len(hist_o), len(hist_t))


def resolve_line_union(path):
    o = stage2(path).decode("utf-8", "replace").splitlines()
    t = stage3(path).decode("utf-8", "replace").splitlines()
    seen, out = set(), []
    for ln in o + t:
        if ln and ln not in seen:
            seen.add(ln)
            out.append(ln)
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return "line-union o=%d t=%d -> %d" % (len(o), len(t), len(out))


def main():
    st = git("status", "--porcelain").decode("utf-8", "replace")
    conflicts = [ln[3:].strip().strip('"') for ln in st.splitlines()
                 if ln[:2] in ("UU", "AA", "DD")]
    for path in conflicts:
        if path in UNION_BY_TS:
            note = resolve_union_by_ts(path)
        elif path in LINE_UNION:
            note = resolve_line_union(path)
        else:
            blob = stage3(path) or stage2(path)
            if not blob:
                print("EMPTY-BOTH %s -> keep deleted" % path)
                subprocess.run(["git", "-C", ROOT, "rm", "-q", path], capture_output=True)
                continue
            with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
                f.write(blob)
            note = "theirs-wholesale"
        subprocess.run(["git", "-C", ROOT, "add", "--", path], capture_output=True)
        print("RESOLVED %s %s" % (path, note))
    left = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "--diff-filter=U"],
                          capture_output=True).stdout.decode("utf-8", "replace").strip()
    print("UNMERGED-LEFT:", left if left else "0")
    return 0 if not left else 2


if __name__ == "__main__":
    sys.exit(main())
