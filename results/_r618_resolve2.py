"""r618 bm-b resolver leg 2: saturation engine live faces (pick #2 conflict).
state/face json = take-new by embedded ts among stage2/stage3/disk (engine
keeps writing; disk is live truth). history jsonl = union of stage2+stage3+
disk lines (append-log zero-loss)."""
import json
import subprocess
import sys

FILES_STATE = ["results/saturation_engine/face_bm-b.json",
               "results/saturation_engine/state_bm-b.json"]
FILES_JSONL = ["results/saturation_engine/history_bm-b.jsonl"]
TS_KEYS = ["updated", "ts", "now", "generated", "asof", "tick_ts"]


def stage(n, p):
    r = subprocess.run(["git", "show", ":%s:%s" % (n, p)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def find_ts(b):
    try:
        d = json.loads(b)
    except Exception:
        return None
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
        if isinstance(v, (int, float)):
            return str(v)
    return None


def main():
    for p in FILES_STATE:
        cands = [(find_ts(b), b, tag) for tag, b in
                 [("stage2", stage(2, p)), ("stage3", stage(3, p))]
                 if b is not None]
        disk = open(p, "rb").read()
        cands.append((find_ts(disk), disk, "disk"))
        cands = [(t or "", b, tag) for t, b, tag in cands]
        best = max(cands, key=lambda x: x[0])
        json.loads(best[1])  # r185 parse gate
        open(p, "wb").write(best[1])
        print(p, "take-new:", best[2], "ts:", best[0])
    for p in FILES_JSONL:
        seen, out = set(), []
        for tag in ("stage2", "stage3"):
            b = stage(2 if tag == "stage2" else 3, p)
            if b:
                for raw in b.splitlines(keepends=True):
                    ln = raw.rstrip(b"\r\n")
                    if ln not in seen:
                        seen.add(ln)
                        out.append(raw)
        for raw in open(p, "rb").read().splitlines(keepends=True):
            ln = raw.rstrip(b"\r\n")
            if ln not in seen:
                seen.add(ln)
                out.append(raw)
        merged = b"".join(out)
        open(p, "wb").write(merged)
        print(p, "union lines:", len(merged.splitlines()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
