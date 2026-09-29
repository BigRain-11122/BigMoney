"""r241 bm-c rebase resolver trail (r440/_r240bmc_resolve.py + r444 canon precedent).

Conflict surface: 30 files, all S6/S7 regen faces + append ledgers, both sides
products of the two concurrent killed ticks (bm-a r446 absorbed 21:33, bm-c
r240 killed 21:30) running the same 09-29 bar -> stripped-equal content with
wall-clock ts deltas.

Rules (regen faces take-union/newer canon):
  - .jsonl : line union, dedupe exact, sort by ts
  - .json  : strip runtime keys -> equal ? take side w/ newer ts : deep-merge union
              (list-of-dict key-dedupe later-ts, scalar leaves prefer newer-ts side)
  - .md/.js: take side with newer max embedded ts, tie -> theirs (:3: = replayed bm-c)
Stages: :2: = ours (onto side = origin/main bm-a), :3: = theirs (replayed bm-c r240).
"""
import json, re, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RUNTIME_KEYS = {"ts", "updated", "generated", "generated_at", "elapsed_sec", "elapsed",
                "as_of", "executed_at", "last_run", "wall_clock", "runtime", "now"}
TS_RE = re.compile(r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True).stdout


def stage(path, n):
    out = git("show", f":{n}:{path}")
    return out.decode("utf-8", errors="replace") if out else ""


def strip_rt(o):
    if isinstance(o, dict):
        return {k: strip_rt(v) for k, v in o.items() if k not in RUNTIME_KEYS}
    if isinstance(o, list):
        return [strip_rt(x) for x in o]
    return o


def max_ts(o, best=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and TS_RE.fullmatch(v.strip()) and v > best:
                best = v.strip()
            best = max_ts(v, best)
    elif isinstance(o, list):
        for x in o:
            best = max_ts(x, best)
    elif isinstance(o, str) and TS_RE.fullmatch(o.strip()) and o.strip() > best:
        best = o.strip()
    return best


def pref_side(a, b):
    # a=ours(bm-a), b=theirs(bm-c); returns (winner_dict, tag)
    ta, tb = max_ts(a) or "", max_ts(b) or ""
    if tb > ta:
        return b, "theirs(bm-c)"
    if ta > tb:
        return a, "ours(bm-a)"
    return b, "theirs(bm-c,tie)"


def deep_merge(a, b):
    w, _ = pref_side(a, b)
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = deep_merge(out[k], v) if k in out else v
        return out
    if isinstance(a, list) and isinstance(b, list):
        if a and b and all(isinstance(x, dict) for x in a + b):
            keyf = None
            for cand in ("ts", "date", "day", "id", "trader", "name", "cutoff"):
                if all(cand in x for x in a + b):
                    keyf = cand
                    break
            if keyf:
                seen = {}
                for x in a + b:
                    seen[x[keyf]] = x
                return sorted(seen.values(), key=lambda r: str(r.get(keyf, "")))
        return w
    return w


def resolve(path):
    A, B = stage(path, 2), stage(path, 3)
    if path.endswith(".jsonl"):
        lines = []
        for chunk in (A, B):
            for ln in chunk.splitlines():
                if ln.strip() and ln not in lines:
                    lines.append(ln)
        open(f"{ROOT}\\{path}", "w", encoding="utf-8", newline="\n").write(
            "\n".join(lines) + ("\n" if lines else ""))
        return "jsonl-union", f"{len(lines)} lines"
    if path.endswith(".json"):
        try:
            a, b = json.loads(A), json.loads(B)
        except Exception:
            ta = TS_RE.findall(A)[-1:] or ["?"]
            tb = TS_RE.findall(B)[-1:] or ["?"]
            win = B if tb >= ta else A
            open(f"{ROOT}\\{path}", "w", encoding="utf-8", newline="").write(win)
            return "json-parse-fail text-newer-ts", f"{ta[0]} vs {tb[0]}"
        if strip_rt(a) == strip_rt(b):
            w, tag = pref_side(a, b)
            open(f"{ROOT}\\{path}", "w", encoding="utf-8", newline="").write(
                json.dumps(w, ensure_ascii=False, indent=1))
            return "stripped-equal take-newer-ts", tag
        m = deep_merge(a, b)
        open(f"{ROOT}\\{path}", "w", encoding="utf-8", newline="").write(
            json.dumps(m, ensure_ascii=False, indent=1))
        return "content-divergent deep-merge-union", "merged"
    ta = TS_RE.findall(A)[-1:] or ["?"]
    tb = TS_RE.findall(B)[-1:] or ["?"]
    win = B if tb >= ta else A
    open(f"{ROOT}\\{path}", "w", encoding="utf-8", newline="").write(win)
    return "text-newer-ts", f"{ta[0]} vs {tb[0]} -> {'bm-c' if win is B else 'bm-a'}"


def main():
    files = git("diff", "--name-only", "--diff-filter=U").decode().split()
    print(f"conflicted: {len(files)}")
    for f in files:
        rule, note = resolve(f)
        git("add", "--", f)
        print(f"  {f} -> {rule} [{note}]")
    left = git("diff", "--name-only", "--diff-filter=U").decode().split()
    print(f"remaining U: {len(left)} {left if left else ''}")


if __name__ == "__main__":
    main()
