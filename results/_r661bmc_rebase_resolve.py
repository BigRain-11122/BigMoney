# -*- coding: utf-8 -*-
"""r661 bm-c rebase resolver: 28 UU shared faces from push race vs bm-a r811
(+bm-b r799/r800 tails). Policy per r648/r799 law (judge by CONTENT ts, never
by side label; receipts mandatory):
  - compute_audit.json   : history = union by row ts (zero-row-loss, r799
                           1-row-restore precedent), latest = newer side,
                           indent=2 per scripts/compute_audit.py L589.
  - x2_watch_log.jsonl  : append-only union, dedup by full line, ts-stable
                           order (r190 union law).
  - all other faces      : whole-file newer-wins by max ISO stamp in blob
                           (deterministic regeneration class, r799 law).
Side semantics for receipt only: stage2 = onto-side (origin), stage3 =
replayed commit (bm-c r661). All git child calls CREATE_NO_WINDOW (U060)."""
import json
import re
import subprocess
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CNW = 0x08000000
ISO = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")
RECEIPT = r"results\_r661bmc_rebase_resolve.json"


def git(args):
    return subprocess.run(["git"] + args, capture_output=True,
                           creationflags=CNW)


def stage_blob(stage, path):
    r = git(["cat-file", "-p", ":%d:%s" % (stage, path)])
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout


def unmerged_paths():
    r = git(["ls-files", "-u"])
    out = []
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        if "\t" in line:
            out.append(line.split("\t", 1)[1])
    return sorted(set(out))


def norm_ts(s):
    s = s.replace("T", " ")
    s = re.sub(r"[+-]\d{2}:?\d{2}$", "", s.strip()).replace("Z", "")
    return s[:19]


def blob_ts(blob_bytes):
    stamps = [norm_ts(m.group(0)) for m in ISO.finditer(
        blob_bytes.decode("utf-8", "replace"))]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def union_compute_audit(b2, b3):
    d2, d3 = json.loads(b2), json.loads(b3)
    rows = {}
    for row in d2["history"] + d3["history"]:
        rows[norm_ts(row["ts"])] = row          # dedup by row ts
    hist = [rows[k] for k in sorted(rows)]
    lat2, lat3 = d2["latest"], d3["latest"]
    newer = lat3 if norm_ts(lat3["ts"]) >= norm_ts(lat2["ts"]) else lat2
    merged = {"history": hist, "latest": newer}
    assert len(hist) >= max(len(d2["history"]), len(d3["history"]))
    data = json.dumps(merged, indent=2, ensure_ascii=False)
    rec = {"policy": "history-union-by-ts + latest-newer",
           "hist2": len(d2["history"]), "hist3": len(d3["history"]),
           "hist_union": len(hist),
           "latest2": lat2["ts"], "latest3": lat3["ts"],
           "latest_kept": newer["ts"]}
    return data.encode("utf-8"), rec


def union_x2_log(b2, b3):
    def lines(bb):
        return [l for l in bb.decode("utf-8", "replace").splitlines() if l.strip()]
    l2, l3 = lines(b2), lines(b3)
    seen, union = set(), []
    for l in l2 + l3:
        if l not in seen:
            seen.add(l)
            union.append(l)

    def ts_of(l):
        m = ISO.search(l)
        return norm_ts(m.group(0)) if m else ""
    union.sort(key=lambda l: ts_of(l))
    data = ("\n".join(union) + "\n").encode("utf-8")
    rec = {"policy": "append-only union dedup-by-line ts-stable",
           "n2": len(l2), "n3": len(l3), "n_union": len(union)}
    assert len(union) >= max(len(l2), len(l3))
    return data, rec


def main():
    faces = unmerged_paths()
    print("UU faces:", len(faces))
    receipt = {"probe": "r661 bm-c rebase resolve",
               "side_semantics": "stage2=onto(origin)/stage3=replayed(bm-c r661)",
               "judged_by": "content ts per r648/r799 law", "faces": {}}
    assert faces, "no unmerged faces -- nothing to resolve"
    for path in faces:
        b2, b3 = stage_blob(2, path), stage_blob(3, path)
        if path == "results/compute_audit.json":
            data, rec = union_compute_audit(b2, b3)
        elif path == "results/x2_watch_log.jsonl":
            data, rec = union_x2_log(b2, b3)
        else:
            t2, t3 = blob_ts(b2), blob_ts(b3)
            assert t2 and t3, "no parsable ISO stamp: %s (%r/%r)" % (path, t2, t3)
            if t3 >= t2:
                data, rec = b3, {"policy": "whole-file newer-wins",
                                 "ts_stage2": t2, "ts_stage3": t3,
                                 "winner": "stage3(bm-c)"}
            else:
                data, rec = b2, {"policy": "whole-file newer-wins",
                                 "ts_stage2": t2, "ts_stage3": t3,
                                 "winner": "stage2(origin)"}
            assert rec["winner"].endswith(
                "bm-c)") or rec["winner"].endswith("origin)")
        with open(path, "wb") as fh:
            fh.write(data)
        r = git(["add", "--", path])
        assert r.returncode == 0, (path, r.stderr[:200])
        receipt["faces"][path] = rec
        print("resolved %s -> %s" % (path, rec.get("policy")))
    left = unmerged_paths()
    assert left == [], "still unmerged: %r" % left
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("RECEIPT ->", RECEIPT, "faces:", len(receipt["faces"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
