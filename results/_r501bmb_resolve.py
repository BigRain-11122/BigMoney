"""r501 bm-b rebase resolver: 14 UU S6-derived faces (all classified, 0 UNKNOWN).

Conflict: replay of local round-500 carry commits (1a82c466b + 2 carry) onto
origin 43d4cbc49 (bm-a r509 carry3 + bm-c r308 + harvest flips).
Stage semantics during rebase: :2: = OURS = new base (origin side),
:3: = THEIRS = the replayed local commit side.

Recipes (classifier output + SKILL.md canon):
- snapshot faces (REPORT/LIVE twins, dashboard_status.json, scorecard_v1,
  strategy_scorecard, token_usage, update_status): take-new by hardened
  deep-ts probe on STAGED blobs (r100: strip _/- before prefix match is
  not needed since we scan VALUES; R350: wall-clock values require
  time-of-day, date-only values excluded; tie -> :2: r140).
  Twins (.md/.json + LIVE-latest pointers) MUST take the SAME side --
  probe the .json member, apply winner to whole twin group.
- dashboard_status.js: js-wrapper-snapshot -> whole-bytes take of the side
  that wins the dashboard_status.json probe (same producer run).
- rolling-ledgers (compute_audit.json history, regime_state.json
  history/transitions): union both blobs zero row loss (dedup by inner
  ts/dedup key, keep origin order), snapshot fields take-new.
Write-back: parse-verify (r185) + format mirror probed per winning side.
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def blob(stage, path):
    return subprocess.check_output(
        ["git", "-C", ROOT, "show", f":{stage}:{path}"])


def probe_face(b: bytes):
    indent, crlf, trailing = 2, True, False
    nl = b.count(b"\n")
    crlf = b.count(b"\r\n") >= max(1, nl) // 2
    trailing = b.endswith(b"\n")
    for line in b.decode("utf-8", errors="replace").split("\n"):
        s = line.strip()
        if s.startswith('"'):
            indent = len(line) - len(line.lstrip(" "))
            break
    return indent, crlf, trailing


def write_mirror(path, obj, face):
    indent, crlf, trailing = face
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    if crlf:
        s = s.replace("\n", "\r\n")
    if trailing and not s.endswith("\n"):
        s += "\r\n" if crlf else "\n"
    with open(path, "wb") as f:
        f.write(s.encode("utf-8"))


def deep_ts(obj):
    """Max wall-clock timestamp (must contain time-of-day, R350) in tree."""
    best = ""
    if isinstance(obj, dict):
        for v in obj.values():
            t = deep_ts(v)
            if t > best:
                best = t
    elif isinstance(obj, list):
        for v in obj:
            t = deep_ts(v)
            if t > best:
                best = t
    elif isinstance(obj, str) and TS_RE.match(obj):
        # normalize space form to T form for comparable max
        best = obj.replace(" ", "T", 1) if obj[10] == " " else obj
    return best


def pick(ours_b, theirs_b, path):
    """take-new adjudication; returns (winner_stage, evidence).
    Parses JSON first -- deep_ts on raw BYTES returns '' for every face
    (isinstance checks miss bytes) = silent tie = wrong-side live-fire."""
    o = json.loads(ours_b.decode("utf-8"))
    t = json.loads(theirs_b.decode("utf-8"))
    ts_o = deep_ts(o)
    ts_t = deep_ts(t)
    if ts_t > ts_o:
        return 3, f"ts ours(base)={ts_o!r} theirs(replay)={ts_t!r} -> :3:"
    # tie or base fresher -> :2: (r140 same-second tie takes HEAD/base)
    return 2, f"ts ours(base)={ts_o!r} theirs(replay)={ts_t!r} -> :2:"


def union_list(a, b, dedup_keys):
    """union entries by first available dedup key; zero row loss."""
    out, seen = [], set()
    for e in a + b:
        k = None
        for dk in dedup_keys:
            if isinstance(e, dict) and dk in e:
                k = (dk, e[dk])
                break
        if k is None:
            k = ("json", json.dumps(e, sort_keys=True, default=str))
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out


def main():
    ok = True
    decisions = {}

    # ---- twin groups: probe .json member once, apply winner to all ----
    groups = [
        ("docs/daily_report/REPORT-2026-10-01", [".json", ".md"]),
        ("docs/live_usage/LIVE-2026-10-01", [".json", ".md"]),
        ("docs/live_usage/LIVE-latest", [".json", ".md"]),
    ]
    for stem, exts in groups:
        pj = stem + ".json"
        stage, ev = pick(blob(2, pj), blob(3, pj), pj)
        decisions[stem] = (stage, ev)
        for ext in exts:
            p = stem + ext
            raw = blob(stage, p)
            if ext == ".json":
                json.loads(raw.decode("utf-8"))  # parse-verify before write
                write_mirror(f"{ROOT}\\{p}".replace("\\\\", "\\"),
                             json.loads(raw.decode("utf-8")),
                             probe_face(raw))
            else:
                with open(f"{ROOT}\\{p}".replace("\\\\", "\\"), "wb") as f:
                    f.write(raw)
        print(f"snapshot-group {stem}: {ev}")

    # ---- dashboard_status.js mirrors .json winner (same producer run) ----
    pj = "results/dashboard_status.json"
    stage, ev = pick(blob(2, pj), blob(3, pj), pj)
    raw = blob(stage, pj)
    obj = json.loads(raw.decode("utf-8"))
    write_mirror(f"{ROOT}\\{pj}".replace("\\\\", "\\"), obj, probe_face(raw))
    pjs = "results/dashboard_status.js"
    with open(f"{ROOT}\\{pjs}".replace("\\\\", "\\"), "wb") as f:
        f.write(blob(stage, pjs))  # whole bytes, producer format kept
    print(f"dashboard_status(.json+.js): {ev}")

    # ---- plain take-new snapshots ----
    for p in ["results/scorecard_v1.json", "results/strategy_scorecard.json",
              "results/token_usage.json", "results/update_status.json"]:
        stage, ev = pick(blob(2, p), blob(3, p), p)
        raw = blob(stage, p)
        obj = json.loads(raw.decode("utf-8"))
        write_mirror(f"{ROOT}\\{p}".replace("\\\\", "\\"), obj,
                     probe_face(raw))
        print(f"snapshot {p}: {ev}")

    # ---- rolling-ledger: compute_audit.json (history union + take-new) ----
    p = "results/compute_audit.json"
    o = json.loads(blob(2, p).decode("utf-8"))
    t = json.loads(blob(3, p).decode("utf-8"))
    hist_o = o.get("history", [])
    hist_t = t.get("history", [])
    merged_hist = union_list(hist_o, hist_t, ["ts", "generated_at", "id"])
    ts_o = deep_ts(o)
    ts_t = deep_ts(t)
    base = o if (ts_t <= ts_o) else t   # snapshot fields take-new
    m = {**o, **base}                    # base keys overlay; then union hist
    m["history"] = merged_hist
    if len(hist_o) + len(hist_t) - len(merged_hist) > 0:
        # dup-collapsed only on identical dedup keys is expected; report
        print(f"  compute_audit: union hist {len(hist_o)}+{len(hist_t)}"
              f" -> {len(merged_hist)} (dedup collapse"
              f" {len(hist_o) + len(hist_t) - len(merged_hist)})")
    write_mirror(f"{ROOT}\\{p}".replace("\\\\", "\\"), m,
                 probe_face(blob(2, p)))
    print(f"rolling-ledger {p}: base-winner ts ours={ts_o!r} "
          f"theirs={ts_t!r}")

    # ---- rolling-ledger: regime_state.json (history+transitions union) ----
    p = "results/regime_state.json"
    o = json.loads(blob(2, p).decode("utf-8"))
    t = json.loads(blob(3, p).decode("utf-8"))
    ts_o = deep_ts(o)
    ts_t = deep_ts(t)
    base = o if (ts_t <= ts_o) else t
    m = {**o, **base}
    for key, dks in [("history", ["ts", "date", "as_of", "id"]),
                     ("transitions", ["ts", "date", "as_of", "id"])]:
        if key in o or key in t:
            m[key] = union_list(o.get(key, []), t.get(key, []), dks)
            print(f"  regime_state.{key}: union "
                  f"{len(o.get(key, []))}+{len(t.get(key, []))} -> "
                  f"{len(m[key])}")
    write_mirror(f"{ROOT}\\{p}".replace("\\\\", "\\"), m,
                 probe_face(blob(2, p)))
    print(f"rolling-ledger {p}: base-winner ts ours={ts_o!r} "
          f"theirs={ts_t!r}")

    # ---- post-write parse verify (r185 law) ----
    for p in [g + e for g, ex in groups for e in ex] + [
            "results/dashboard_status.json", p if False else
            "results/scorecard_v1.json", "results/strategy_scorecard.json",
            "results/token_usage.json", "results/update_status.json",
            "results/compute_audit.json", "results/regime_state.json"]:
        if p.endswith(".md") or p.endswith(".js"):
            continue
        json.load(open(f"{ROOT}\\{p}".replace("\\\\", "\\"), encoding="utf-8"))
    print("resolve OK: all json faces re-parsed clean post-write")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
