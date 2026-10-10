"""r831 bm-b rebase-resolver wave 2: preflight commit replay vs bm-a 12:0x
fresh S6 outputs. Recipes: compute_audit/regime_state = rolling-ledger union
(zero row loss); all others = snapshot take-new by doc ts with same-second
tie -> ours (origin side) per r140; .md docs take-ours (bm-a is today's
authoritative regenerator). Exit 0 ok / 2 fault.
"""
import json
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
LEDGERS = ("results/compute_audit.json", "results/regime_state.json")


def blob(stage, path):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show :%s:%s rc=%s" % (stage, path, r.returncode))
    return r.stdout


def doc_ts(d):
    for k in ("ts", "generated", "asof", "generated_at", "updated"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v:
            return v
    return ""


def union_ledgers(d_ours, d_theirs):
    out = {}
    for k in d_ours:
        ov, tv = d_ours.get(k), d_theirs.get(k)
        if isinstance(ov, list) and isinstance(tv, list):
            seen = {json.dumps(x, ensure_ascii=True, sort_keys=True) for x in ov}
            merged = list(ov)
            for x in tv:
                key = json.dumps(x, ensure_ascii=True, sort_keys=True)
                if key not in seen:
                    merged.append(x)
            out[k] = merged
        else:
            out[k] = ov if doc_ts(d_ours) >= doc_ts(d_theirs) else tv
    for k in d_theirs:
        if k not in out:
            out[k] = d_theirs[k]
    return out


def main():
    r = subprocess.run(["git", "-C", ROOT, "status", "--porcelain"],
                       capture_output=True, text=True)
    uus = [ln[3:].strip() for ln in r.stdout.splitlines()
           if ln[:2] in ("UU", "AA")]
    if not uus:
        print("no UU/AA entries")
        return 0
    log = []
    for p in uus:
        if p in LEDGERS:
            o = json.loads(blob(2, p).decode("utf-8"))
            t = json.loads(blob(3, p).decode("utf-8"))
            merged = union_ledgers(o, t)
            json.loads(json.dumps(merged))
            open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8",
                 newline="").write(json.dumps(merged, ensure_ascii=True,
                                              indent=1) + "\n")
            log.append("union-ledger: " + p)
        elif p.endswith(".md"):
            open(ROOT + "\\" + p.replace("/", "\\"), "wb").write(blob(2, p))
            log.append("take-ours(md): " + p)
        else:
            try:
                o = json.loads(blob(2, p).decode("utf-8"))
                t = json.loads(blob(3, p).decode("utf-8"))
                pick, side = (o, "ours") if doc_ts(o) >= doc_ts(t) else (t, "theirs")
                open(ROOT + "\\" + p.replace("/", "\\"), "w", encoding="utf-8",
                     newline="").write(json.dumps(pick, ensure_ascii=True,
                                                  indent=1) + "\n")
                log.append("take-new(%s): %s" % (side, p))
            except Exception:
                open(ROOT + "\\" + p.replace("/", "\\"), "wb").write(blob(2, p))
                log.append("take-ours(raw fallback): " + p)
    json.dump({"round": "r831-wave2", "files": log}, open(
        ROOT + r"\results\_r831bmb_resolve2_receipt.json", "w",
        encoding="utf-8"), ensure_ascii=True, indent=1)
    print("RESOLVED wave2: %d entries" % len(log))
    for l in log:
        print(" ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
