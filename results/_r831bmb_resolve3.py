"""r831 bm-b rebase-resolver wave 3: closeout commit replay. bm-b single-writer
satengine faces appear on origin side only because bm-a's absorb-everything
commit swallowed stale copies -> take THEIRS (my commit = real bm-b daemon
fresh state). history_bm-b.jsonl = append-log line union (r188). attrition/
token_usage shared faces = take-new by ts, tie->ours (r140). Exit 0 / 2.
"""
import json
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
THEIRS = ("results/saturation_engine/face_bm-b.json",
          "results/saturation_engine/state_bm-b.json")
JSONL = "results/saturation_engine/history_bm-b.jsonl"


def blob(stage, path):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show :%s:%s rc=%s" % (stage, path, r.returncode))
    return r.stdout


def doc_ts(d):
    for k in ("ts", "generated", "asof", "generated_at", "updated", "time"):
        v = d.get(k) if isinstance(d, dict) else None
        if isinstance(v, str) and v:
            return v
    return ""


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
        dst = ROOT + "\\" + p.replace("/", "\\")
        if p in THEIRS:
            open(dst, "wb").write(blob(3, p))
            log.append("take-theirs(bm-b single-writer): " + p)
        elif p == JSONL:
            a = blob(2, p).decode("utf-8", "replace").splitlines()
            b = blob(3, p).decode("utf-8", "replace").splitlines()
            seen = set(a)
            merged = a + [x for x in b if x not in seen]
            open(dst, "w", encoding="utf-8", newline="").write(
                "\n".join(merged) + ("\n" if merged else ""))
            log.append("jsonl-union: %s |ours|=%d +theirs_new=%d"
                       % (p, len(a), len(merged) - len(a)))
        else:
            try:
                o = json.loads(blob(2, p).decode("utf-8"))
                t = json.loads(blob(3, p).decode("utf-8"))
                pick, side = (o, "ours") if doc_ts(o) >= doc_ts(t) else (t, "theirs")
                open(dst, "w", encoding="utf-8", newline="").write(
                    json.dumps(pick, ensure_ascii=True, indent=1) + "\n")
                log.append("take-new(%s): %s" % (side, p))
            except Exception:
                open(dst, "wb").write(blob(3, p))
                log.append("take-theirs(raw fallback): " + p)
    json.dump({"round": "r831-wave3", "files": log}, open(
        ROOT + r"\results\_r831bmb_resolve3_receipt.json", "w",
        encoding="utf-8"), ensure_ascii=True, indent=1)
    print("RESOLVED wave3: %d entries" % len(log))
    for l in log:
        print(" ", l)
    return 0


if __name__ == "__main__":
    sys.exit(main())
