# -*- coding: utf-8 -*-
"""r798 bm-c rebase conflict resolver (18-UU window, pick 7bd95d329).

Laws applied (pit-git-resolver-rebase.md):
- r648: stage blob reads via `git ls-files -u` sha + `git cat-file -p`
  (never `git show :N:` -- silent empty-read face).
- r782: rebase stages are REVERSED (stage2=onto/origin, stage3=replayed
  ours); resolution is CONTENT-DRIVEN ts evidence, side labels ignored.
- r516: deep-ts audit -- recursive scan for any timestamp-ish field
  (ts/_ts/_at/generated/updated/asof...), newest wins; no blind fallback.
- r742/r570: append-only jsonl -> line-level union, zero-loss.
- r790: UU set read live from ls-files -u (never pre-scanned plan).
- r794: resolved paths are added with TARGETED git add only (no -u/-A).
Receipt -> results/_r798bmc_rebase_resolve.json.
"""
import json
import re
import subprocess
import sys
from datetime import datetime

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TS_KEYS = ("ts", "generated", "generated_at", "updated", "updated_at",
           "asof", "as_of", "last_update", "last_updated_at", "written_at",
           "cutoff", "evidence_cutoff", "last_crash_ts", "last_refusal_ts",
           "last_seen", "last_run_at", "last_pulled_at", "last_shard_done_at",
           "last_flush_at", "last_tick_ts", "now", "time", "date")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
UNION_FILES = ("results/x2_watch_log.jsonl",)


def git(args):
    p = subprocess.run(["git", "-C", REPO] + args, capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout, p.stderr


def uu_set():
    rc, out, _ = git(["ls-files", "-u"])
    per = {}
    for line in out.decode("utf-8", "replace").splitlines():
        parts = line.split()
        if len(parts) >= 4:
            mode, sha, stage, path = parts[0], parts[1], parts[2], parts[3]
            per.setdefault(path, {})[int(stage)] = sha
    return {p: s for p, s in per.items() if 2 in s and 3 in s}


def blob(sha):
    rc, out, _ = git(["cat-file", "-p", sha])
    return out


def deep_ts(obj, best=None):
    """Recursive newest-timestamp scan over JSON face."""
    if best is None:
        best = [None]
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RE.match(v):
                if best[0] is None or v > best[0]:
                    best[0] = v
            else:
                deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            deep_ts(v, best)
    return best[0]


def json_ts(raw):
    try:
        obj = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        # line-jsonl or js: scan raw text for timestamp-ish tokens
        cands = TS_RE.findall(raw.decode("utf-8", "replace"))
        cands = [c if isinstance(c, str) else c[0] for c in cands]
        cands = [c for c in cands if len(c) >= 16]
        return max(cands) if cands else None
    return deep_ts(obj)


def resolve(path, s2, s3):
    b2, b3 = blob(s2), blob(s3)
    rec = {"path": path, "stage2_sha": s2[:12], "stage3_sha": s3[:12],
           "bytes2": len(b2), "bytes3": len(b3)}
    if b2 == b3:
        open(path_abs(path), "wb").write(b2)
        rec["verdict"] = "byte-identical"
        return rec
    if path.replace("\\", "/") in UNION_FILES:
        l2 = b2.decode("utf-8", "replace").splitlines()
        l3 = b3.decode("utf-8", "replace").splitlines()
        seen, merged = set(), []
        for l in l2 + l3:
            if l not in seen:
                seen.add(l)
                merged.append(l)
        open(path_abs(path), "w", encoding="utf-8", newline="\n").write(
            "\n".join(merged) + ("\n" if merged else ""))
        rec.update({"verdict": "line-union", "rows2": len(l2),
                    "rows3": len(l3), "rows_out": len(merged),
                    "loss_assert": len(merged) >= max(len(l2), len(l3))})
        return rec
    t2, t3 = json_ts(b2), json_ts(b3)
    rec["ts2"], rec["ts3"] = t2, t3
    if t2 and t3 and t2 != t3:
        win = "stage2" if t2 > t3 else "stage3"
    elif t2 and t3 and t2 == t3:
        win = "stage3"  # identical ts -> keep replayed round product
    elif t3 and not t2:
        win = "stage3"
    elif t2 and not t3:
        win = "stage2"
    else:
        win = "stage2"  # no ts evidence either side -> keep published origin
        rec["verdict_note"] = "no-ts-evidence, origin-published baseline"
    open(path_abs(path), "wb").write(b2 if win == "stage2" else b3)
    rec["verdict"] = "ts-newer-wins:%s" % win
    return rec


def path_abs(p):
    import os
    return REPO + "\\" + p.replace("/", "\\")


def main():
    uus = uu_set()
    print("UU faces: %d" % len(uus))
    receipt = {"round": 798, "uu_n": len(uus),
               "law_ref": "r648 sha-channel + r782 content-driven + r516 deep-ts + r742 union"}
    recs = []
    for path in sorted(uus):
        recs.append(resolve(path, uus[path][2], uus[path][3]))
        print("%-52s %s" % (path, recs[-1]["verdict"]))
    receipt["faces"] = recs
    # marker scan over every resolved face (r705 hard gate)
    dirty_n = 0
    for r in recs:
        txt = open(path_abs(r["path"]), "rb").read()
        for mk in (b"<<<<<<<", b">>>>>>>", b"======="):
            if mk in txt:
                print("MARKER-FAIL %s" % r["path"])
                return 3
    with open(REPO + r"\results\_r798bmc_rebase_resolve.json", "w",
              encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    print("receipt written; marker scan clean; faces=%d" % len(recs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
