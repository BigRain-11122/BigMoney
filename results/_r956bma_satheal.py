"""r956 bm-a saturation-face heal (autostash pop conflict + r808 marker purge).

Faces:
  1. results/saturation_engine/face_bm-a.json   : pop conflict -> take ours (stage2=HEAD clean, fresher than stash)
  2. results/saturation_engine/state_bm-a.json   : same
  3. results/saturation_engine/history_bm-a.jsonl: pop conflict -> line-union stage2+stage3+WT-clean minus markers
  4. results/saturation_engine/history_bm-b.jsonl: pre-existing origin pollution (r833/834) -> purge 3 marker lines
     from WT (single-writer law: data lines preserved verbatim, ONLY marker lines removed)
Laws: r808 (tree tip zero markers), r917 (daemon live faces), r185 (parse-verify before write),
union zero-loss (line count = |A u B| minus markers).
"""
import json
import subprocess
import sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
MARKERS = ("<<<<<<<", "=======", ">>>>>>>")


def stage_lines(stage, path):
    b = subprocess.run([GIT, "show", f":{stage}:{path}"], capture_output=True, check=False)
    if b.returncode != 0:
        return None
    return b.stdout.decode("utf-8", "replace").splitlines()


def main():
    report = []

    # --- face/state: take ours (stage2) ---
    for p in ["results/saturation_engine/face_bm-a.json", "results/saturation_engine/state_bm-a.json"]:
        b = subprocess.run([GIT, "show", f":2:{p}"], capture_output=True, check=False)
        if b.returncode != 0:
            print(f"FAIL: no stage2 for {p}")
            return 2
        json.loads(b.stdout.decode("utf-8"))  # parse-verify
        open(p, "wb").write(b.stdout)
        report.append(f"face/state ours: {p} ({len(b.stdout)}B, parse-verified)")

    # --- history bm-a: union of stage2 + stage3 + WT-clean, dedup, minus markers ---
    p = "results/saturation_engine/history_bm-a.jsonl"
    s2, s3 = stage_lines(2, p), stage_lines(3, p)
    wt = [l for l in open(p, encoding="utf-8", errors="replace").read().splitlines()
          if not l.startswith(MARKERS)]
    out, seen = [], set()
    for src in (wt, s2, s3):  # WT first: daemon post-pop writes live-wins
        for l in src:
            if l.startswith(MARKERS) or l in seen or not l.strip():
                continue
            seen.add(l)
            out.append(l)
    # parse-verify every kept line is JSON
    bad = [l for l in out if not _isjson(l)]
    if bad:
        print(f"FAIL: {len(bad)} non-JSON lines in union, abort write")
        for l in bad[:3]:
            print(" bad:", l[:120])
        return 2
    data = ("\n".join(out) + "\n").encode("utf-8")
    open(p, "wb").write(data)
    report.append(f"history bm-a union: wt_clean={len(wt)} s2={len(s2)} s3={len(s3)} -> {len(out)} lines, all JSON-verified")

    # --- history bm-b: purge marker lines only (data lines preserved verbatim) ---
    p = "results/saturation_engine/history_bm-b.jsonl"
    lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
    keep = [l for l in lines if not l.startswith(MARKERS)]
    removed = len(lines) - len(keep)
    bad = [l for l in keep if l.strip() and not _isjson(l)]
    if bad:
        print(f"FAIL: bm-b face has {len(bad)} non-JSON data lines, abort")
        return 2
    open(p, "wb").write(("\n".join(keep) + "\n").encode("utf-8"))
    report.append(f"history bm-b marker purge: {len(lines)} -> {len(keep)} lines (removed {removed} markers), data verbatim")

    for r in report:
        print(r)
    return 0


def _isjson(l):
    try:
        json.loads(l)
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
