"""_r423bmb_pushstorm_resolve.py -- r423 bm-b push-storm 31-UU canon resolver.

Trigger: S7 push rejected (origin advanced bm-c r216 mid-round) -> pull --rebase
retry -> 31 UU (same storm shape as r422 31-UU / bm-c r216 30-UU).

Recipes per bigmoney-conflict-resolve SKILL.md classification (2026-09-29 12:2x
classifier run, 27 classified + 4 LIVE same-day idempotent twins manual-determined
per r422 precedent):
  memory-union        CODELY.md                     line-level union dedupe
  rolling-ledger       compute_audit/regime_state    ledger union + state take-new
  append-log           x2_watch_log.jsonl            line-level union zero loss
  js-wrapper-snapshot  dashboard_status.js          take side whole bytes (twin
                                                      coherence with dashboard_status.json winner)
  snapshot x22         take-new by deep ts probe (r311/D-20260927-09; tie -> stage2/HEAD per r140)
  LIVE twins x4 (UNKNOWN) same-day idempotent regeneration twins (r422 手定):
                      take-new by generated ts; .md/.latest follow .json winner side.

Stage semantics in rebase: :2 = ours = new base (bm-c r216 side), :3 = theirs =
my r423 replay side. Zero force-push; resolve-verify-before-write (r185).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TS_KEY_RE = re.compile(r"^(generated|ts|updated|written|lastseen|asof|cutoffts|date)", re.I)
TS_VAL_RE = re.compile(r"^20\d{2}-")


def git_bytes(spec: str) -> bytes:
    return subprocess.run(["git", "show", spec], capture_output=True, check=True).stdout


def stage(path: str, n: int) -> bytes:
    return git_bytes(f":{n}:{path}")


def deep_ts(obj, best=""):
    """Recursive max-ts probe (r311 hardening: strip _/-, value ^20\\d{2}-; wall-clock keys need time-of-day)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            kn = re.sub(r"[_-]", "", str(k)).lower()
            if isinstance(v, str) and TS_KEY_RE.match(kn) and TS_VAL_RE.match(v):
                if "T" in v or re.search(r"\d{2}:\d{2}", v):  # wall-clock key requires time-of-day
                    if v > best:
                        best = v
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best


def parse(b: bytes):
    return json.loads(b.decode("utf-8-sig"))


def take_new_json(path: str, b2: bytes, b3: bytes) -> bytes:
    o2, o3 = parse(b2), parse(b3)
    t2, t3 = deep_ts(o2), deep_ts(o3)
    winner = b3 if t3 > t2 else b2  # tie -> stage2 (HEAD, r140)
    json.loads(winner.decode("utf-8-sig"))  # parse-verify before write (r185)
    return winner


def union_lines(b2: bytes, b3: bytes) -> bytes:
    l2 = b2.decode("utf-8-sig").splitlines()
    l3 = b3.decode("utf-8-sig").splitlines()
    seen, out = set(), []
    for ln in l2 + l3:
        if ln not in seen:
            seen.add(ln)
            out.append(ln)
    assert len(out) == len(set(l2) | set(l3)), "union zero-loss check failed"
    body = "\n".join(out) + ("\n" if out else "")
    return body.encode("utf-8")


LEDGER_KEYS = ("history", "launches", "transitions", "events")


def rolling_union(path: str, b2: bytes, b3: bytes) -> bytes:
    o2, o3 = parse(b2), parse(b3)
    merged = dict(o2 if deep_ts(o3) <= deep_ts(o2) else o3)  # state fields take-new (tie->2)
    other = o3 if merged is o2 else o2
    for k in LEDGER_KEYS:
        if k in other or k in merged:
            a = merged.get(k, [])
            b = other.get(k, [])
            seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a}
            out = list(a)
            for x in b:
                sig = json.dumps(x, sort_keys=True, ensure_ascii=False)
                if sig not in seen:
                    seen.add(sig)
                    out.append(x)
            if a or b:
                assert len(out) >= max(len(a), len(b)), "ledger union zero-loss failed"
            merged[k] = out
    body = json.dumps(merged, ensure_ascii=False, indent=1) + "\n"
    json.loads(body)  # parse-verify
    return body.encode("utf-8")


def main() -> int:
    status = subprocess.run(["git", "status", "--porcelain=v1"], capture_output=True,
                            text=True, encoding="utf-8").stdout
    uu = [ln[3:].strip() for ln in status.splitlines()
          if ln.startswith("UU") or ln.startswith("AA")]
    assert uu, "no UU/AA entries -- nothing to resolve"

    json_side_wins = {}  # json twin winner -> side index for md/js byte twins

    for path in uu:
        b2, b3 = stage(path, 2), stage(path, 3)
        if path == "CODELY.md":
            body = union_lines(b2, b3)
            kind = "memory-union"
        elif path in ("results/compute_audit.json", "results/regime_state.json"):
            body = rolling_union(path, b2, b3)
            kind = "rolling-ledger"
        elif path == "results/x2_watch_log.jsonl":
            body = union_lines(b2, b3)
            kind = "append-log"
        elif path == "results/dashboard_status.js":
            w = json_side_wins.get("results/dashboard_status.json", 3)
            body = b3 if w == 3 else b2
            kind = f"js-wrapper-snapshot (twin side={w})"
        elif path in ("docs/live_usage/LIVE-2026-09-29.json",
                      "docs/live_usage/LIVE-2026-09-29.md",
                      "docs/live_usage/LIVE-latest.json",
                      "docs/live_usage/LIVE-latest.md"):
            if path.endswith(".json"):
                o2, o3 = parse(b2), parse(b3)
                t2, t3 = deep_ts(o2), deep_ts(o3)
                w = 3 if t3 > t2 else 2
                json_side_wins[path] = w
                body = b3 if w == 3 else b2
                json.loads(body.decode("utf-8-sig"))
            else:
                stem = path.replace("LIVE-latest", "LIVE-2026-09-29")
                w = json_side_wins.get(stem, json_side_wins.get(
                    "docs/live_usage/LIVE-2026-09-29.json", 3))
                body = b3 if w == 3 else b2
            kind = "LIVE same-day idempotent twin (r422 manual-determination)"
        else:
            if path.endswith(".json"):
                body = take_new_json(path, b2, b3)
                kind = "snapshot take-new"
                o2, o3 = parse(b2), parse(b3)
                json_side_wins[path] = 3 if deep_ts(o3) > deep_ts(o2) else 2
            else:
                # md snapshot twin: byte-take the side matching its .json twin winner
                twin = path[:-3] + ".json"
                w = json_side_wins.get(twin, 3)
                body = b3 if w == 3 else b2
                kind = f"snapshot md twin (json twin side={w})"
        Path(path).write_bytes(body)
        subprocess.run(["git", "add", "--", path], check=True)
        print(f"resolved {kind}: {path}")

    # dashboard_status.js twin coherence fallback if json key missing
    print(f"resolved {len(uu)} files; side map: {json_side_wins}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
