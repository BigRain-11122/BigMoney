# -*- coding: utf-8 -*-
"""r802 bm-c rebase conflict resolver (13-UU window vs bm-a r914 closeout).

Cloned 1-gen from _r801bmc_rebase_resolver.py (r802 law).
Laws applied (pit-git-resolver-rebase.md):
- r648: stage blob reads via `git ls-files -u` sha + `git cat-file -p`
  (never `git show :N:` -- silent empty-read face).
- r782: rebase stages are REVERSED (stage2=onto/origin, stage3=replayed
  ours); resolution is CONTENT-DRIVEN ts evidence, side labels ignored.
- r516: deep-ts audit -- recursive scan for any timestamp-ish field,
  newest wins; no blind fallback.
- r742/r570: append-only jsonl -> line-level union, zero-loss.
- r790: UU set read live from ls-files -u (never pre-scanned plan).
- r794: resolved paths are added with TARGETED git add only (no -u/-A).
r802 addition: compute_audit.json = rolling {latest,history} face ->
history UNION by ts (dedupe on ts, sort by ts, zero-loss both tails per
bm-a r914 same-window precedent "compute_audit history-union zero-loss")
+ latest newer-wins.
Receipt -> results/_r802bmc_rebase_resolve.json.
"""
import json
import re
import subprocess
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")
UNION_FILES = ("results/x2_watch_log.jsonl", "results/pool_core_samples.jsonl",
               "results/pool_red_flags.jsonl")
HISTORY_UNION_FILES = ("results/compute_audit.json",)


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
        cands = TS_RE.findall(raw.decode("utf-8", "replace"))
        cands = [c if isinstance(c, str) else c[0] for c in cands]
        cands = [c for c in cands if len(c) >= 16]
        return max(cands) if cands else None
    return deep_ts(obj)


def path_abs(p):
    return REPO + "\\" + p.replace("/", "\\")


def resolve_history_union(path, b2, b3, rec):
    d2 = json.loads(b2.decode("utf-8", "replace"))
    d3 = json.loads(b3.decode("utf-8", "replace"))
    h2 = d2.get("history", [])
    h3 = d3.get("history", [])
    by_ts = {}
    for row in h2 + h3:
        t = row.get("ts")
        if t not in by_ts:
            by_ts[t] = row
    merged = [by_ts[t] for t in sorted(by_ts)]
    latest = d2.get("latest", {}) if (deep_ts(d2.get("latest", {})) or "") > \
        (deep_ts(d3.get("latest", {})) or "") else d3.get("latest", {})
    out = {"latest": latest, "history": merged}
    data = json.dumps(out, ensure_ascii=False, indent=1)
    open(path_abs(path), "w", encoding="utf-8", newline="\n").write(data + "\n")
    rec.update({"verdict": "history-union",
                "rows2": len(h2), "rows3": len(h3), "rows_out": len(merged),
                "loss_assert": len(merged) >= max(len(h2), len(h3)),
                "latest_ts": latest.get("ts")})
    return rec


def resolve(path, s2, s3):
    b2, b3 = blob(s2), blob(s3)
    rec = {"path": path, "stage2_sha": s2[:12], "stage3_sha": s3[:12],
           "bytes2": len(b2), "bytes3": len(b3)}
    if b2 == b3:
        open(path_abs(path), "wb").write(b2)
        rec["verdict"] = "byte-identical"
        return rec
    if path.replace("\\", "/") in HISTORY_UNION_FILES:
        return resolve_history_union(path, b2, b3, rec)
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


def main():
    uus = uu_set()
    print("UU faces: %d" % len(uus))
    receipt = {"round": 802, "uu_n": len(uus),
               "law_ref": "r648 sha-channel + r782 content-driven + r516 deep-ts + r742 union + r794 targeted-add; compute_audit history-union per bm-a r914 same-window precedent"}
    recs = []
    for path in sorted(uus):
        recs.append(resolve(path, uus[path][2], uus[path][3]))
        print("%-52s %s" % (path, recs[-1]["verdict"]))
    receipt["faces"] = recs
    for r in recs:
        txt = open(path_abs(r["path"]), "rb").read()
        for mk in (b"<<<<<<<", b">>>>>>>", b"======="):
            if mk in txt:
                print("MARKER-FAIL %s" % r["path"])
                return 3
    with open(REPO + r"\results\_r802bmc_rebase_resolve.json", "w",
              encoding="utf-8") as fh:
        json.dump(receipt, fh, ensure_ascii=False, indent=1)
    # r794: targeted add of resolved faces only
    rc, out, err = git(["add"] + sorted(uus))
    if rc != 0:
        print("targeted add failed:", err.decode("utf-8", "replace")[:200])
        return 2
    print("receipt written; marker scan clean; faces=%d; targeted-add done" % len(recs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
