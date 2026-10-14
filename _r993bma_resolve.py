# r993 rebase UU resolver (r992/r933/r863 law: snapshots deep-ts, twins take-newer, host faces take-local)
# During rebase: stage2(ours)=origin side, stage3(theirs)=my replayed commit fe4d3b0d5
import subprocess, json, sys, re, os

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def git(*args):
    return subprocess.run([GIT, "-C", ROOT] + list(args), capture_output=True, text=True, encoding="utf-8", errors="replace")

def stage(path, n):
    r = git("show", f":{n}:{path}")
    return r.stdout if r.returncode == 0 else None

HOST_FACES = {
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/strategy_scorecard.json", "results/scorecard_v1.json",
}

TS_KEYS = ["generated", "generated_at", "ts", "asof", "updated", "updated_at", "last_run", "now", "timestamp", "generated_utc", "cutoff", "date"]

def extract_ts(obj):
    """Recursively find the newest plausible timestamp string/epoch in a JSON face."""
    best = None
    def scan(o, depth=0):
        nonlocal best
        if depth > 6: return
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?", v):
                    if best is None or v > best: best = v
                elif k in TS_KEYS and isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]?[\dT:.+-]*", v):
                    if best is None or v > best: best = v[:19]
                elif k in TS_KEYS and isinstance(v, (int, float)):
                    c = str(v)
                    if best is None or c > best: best = c
                else:
                    scan(v, depth+1)
        elif isinstance(o, list):
            for it in o[:80]:
                scan(it, depth+1)
    scan(obj)
    return best

def resolve():
    r = git("status", "--porcelain")
    ufiles = [l[3:].strip().strip('"') for l in r.stdout.splitlines() if l.startswith("UU")]
    print(f"UU files: {len(ufiles)}")
    receipt = []
    for path in ufiles:
        a = stage(path, 2)  # origin side
        b = stage(path, 3)  # my replayed commit
        choice = None; why = ""
        if path in HOST_FACES:
            choice = "theirs"; why = "host face bm-a take-local (r992 law)"
        else:
            # deep-ts compare on JSON; text twins -> take origin (newer commit time 16:55 vs 16:50)
            ta = tb = None
            try:
                ja = json.loads(a); ta = extract_ts(ja)
            except Exception: pass
            try:
                jb = json.loads(b); tb = extract_ts(jb)
            except Exception: pass
            if ta and tb and ta != tb:
                choice = "ours" if ta > tb else "theirs"
                why = f"deep-ts origin={ta} mine={tb} -> {choice}"
            elif ta and not tb:
                choice = "ours"; why = f"deep-ts origin={ta} mine=none"
            elif tb and not ta:
                choice = "theirs"; why = f"deep-ts mine={tb} origin=none"
            else:
                choice = "ours"; why = f"ts-tie/unparseable -> take-newer-commit-side origin (ta={ta} tb={tb})"
        rc = git("checkout", f"--{choice}", "--", path)
        git("add", "--", path)
        receipt.append({"path": path, "choice": choice, "why": why, "rc": rc.returncode})
        print(f"  {path}: {choice} ({why}) rc={rc.returncode}")
    with open(os.path.join(ROOT, "results", "_r993bma_resolve_receipt.json"), "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=1)
    bad = [x for x in receipt if x["rc"] != 0]
    print(f"BAD={len(bad)}")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(resolve())
