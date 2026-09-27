"""r366 bm-a storm resolver (15 UU, rebase replay of round-366 commit vs bm-b r349 closeout).

Recipes per bigmoney-conflict-resolve SKILL.md (classifier 15/15 green):
- snapshot family: take-new by DEEP wall-clock ts probe (R350: value-shape only,
  wall-clock requires time-of-day; no key-exclude lists), tie -> :2: (HEAD=origin,
  r140); winner RAW BYTES verbatim (preserves producer line endings/indent/key order).
- twin coupling: REPORT json+md and dashboard json+js take the SAME side, decided
  from the json face (r329: md twin is not JSON - copy same-side bytes directly).
- autofill_state mixed-dict+ledger: launches union by composite key
  (ts,machine,pid,runner_sha256,entry,shard) with r322 field-union merge on collision,
  ts desc cap 50 (r215), write-back re-sorted asc (r245); last_tick = whole-dict by
  inner ts, same-second tie -> :2: (r140); isinstance(dict) assert; mirror winner
  blob line ending + indent=1 producer format.
- compute_audit / regime_state rolling-ledger: ledger rows union by (ts,machine)
  row identity, zero-loss |A U B|, NO resolver-invented cap (r360 law; producer
  rolling window owns truncation per r85); non-ledger snapshot fields take-new by
  deep ts; mirror winner blob format (indent=1, CRLF if winner CRLF).
Parse-verify before write-back (r185). Zero-loss assertions per family.
"""
import subprocess, json, re, sys, time, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def blob(rev, path, tries=4):
    last = b""
    for i in range(tries):
        r = subprocess.run(["git", "show", f"{rev}{path}"],
                            capture_output=True, cwd=ROOT)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        last = r.stderr
        time.sleep(0.5)
    raise RuntimeError(f"blob {rev}:{path} unreadable: {last.decode(errors='replace')[:150]}")


TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def deep_ts(obj):
    """Max wall-clock ts (value-shape only; date-only values never feed the max)."""
    best = None
    if isinstance(obj, dict):
        for v in obj.values():
            b = deep_ts(v)
            if b and (best is None or b > best):
                best = b
    elif isinstance(obj, list):
        for it in obj:
            b = deep_ts(it)
            if b and (best is None or b > best):
                best = b
    elif isinstance(obj, str) and TS_RE.match(obj):
        best = obj
    return best


def side_ts(b):
    return deep_ts(json.loads(b))


def pick_side(b2, b3):
    t2, t3 = side_ts(b2), side_ts(b3)
    if t3 is not None and (t2 is None or t3 > t2):
        return 3, t2, t3
    return 2, t2, t3          # tie or origin newer -> :2: (HEAD=origin, r140)


report = []


def resolve_snapshot(path, b2, b3):
    s, t2, t3 = pick_side(b2, b3)
    win = b3 if s == 3 else b2
    json.loads(win)                       # parse-verify before write (r185)
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(win)
    report.append(f"snapshot {path}: side=:{s}: ts {t2} vs {t3} raw-bytes")
    return s


def resolve_twin(json_path, md_path):
    b2, b3 = blob(":2:", json_path), blob(":3:", json_path)
    s = resolve_snapshot(json_path, b2, b3)
    b2m, b3m = blob(":2:", md_path), blob(":3:", md_path)
    win = b3m if s == 3 else b2m
    with open(os.path.join(ROOT, md_path), "wb") as fh:
        fh.write(win)
    report.append(f"twin {md_path}: same side =:{s}: bytes-copied (r329)")


def mirror_write(path, obj, winner_bytes):
    text = json.dumps(obj, ensure_ascii=False, indent=1)
    if b"\r\n" in winner_bytes:
        text = text.replace("\n", "\r\n")
    data = text.encode("utf-8")
    json.loads(data)                      # parse-verify (r185)
    with open(os.path.join(ROOT, path), "wb") as fh:
        fh.write(data)
    return data


def resolve_autofill_state():
    path = "results/autofill_state.json"
    b2, b3 = blob(":2:", path), blob(":3:", path)
    a2, a3 = json.loads(b2), json.loads(b3)
    seen = {}
    collisions = 0
    for src in (a2, a3):
        for rec in src.get("launches", []):
            key = tuple(rec.get(f) for f in
                        ("ts", "machine", "pid", "runner_sha256", "entry", "shard"))
            if key in seen:
                prev = seen[key]
                for k, v in rec.items():
                    if k not in prev:
                        prev[k] = v          # r322 field-union supplement
                collisions += 1
            else:
                seen[key] = dict(rec)
    launches = sorted(seen.values(),
                      key=lambda r: r.get("ts", ""), reverse=True)[:50]
    launches.sort(key=lambda r: r.get("ts", ""))       # write-back asc (r245)
    lt2, lt3 = a2.get("last_tick"), a3.get("last_tick")
    t2, t3 = deep_ts(lt2), deep_ts(lt3)
    last_tick = lt3 if (t3 is not None and (t2 is None or t3 > t2)) else lt2  # tie -> :2:
    assert isinstance(last_tick, dict), "last_tick must be dict"
    s, g2, g3 = pick_side(b2, b3)
    base = a3 if s == 3 else a2
    base["launches"] = launches
    base["last_tick"] = last_tick
    win = b3 if s == 3 else b2
    mirror_write(path, base, win)
    n2, n3 = len(a2.get("launches", [])), len(a3.get("launches", []))
    report.append(f"autofill_state: |A|={n2} |B|={n3} union_dedup={len(seen)} "
                  f"collisions_merged={collisions} cap50_kept={len(launches)} "
                  f"base=:{s}: last_tick ts {t2} vs {t3}")


def row_ident(rec):
    """r319 law: dedup key must EXIST inside the entry -- probe per-face.
    compute_audit rows carry (ts,machine); regime_state rows carry asof
    dates (shared market state, same-date = same logical row)."""
    if isinstance(rec, dict):
        if "ts" in rec:
            return ("ts", rec.get("ts"), rec.get("machine"))
        for k in ("asof", "date", "day"):
            if k in rec:
                return (k, rec.get(k))
    return ("raw", json.dumps(rec, sort_keys=True, ensure_ascii=False))


def resolve_rolling(path, ledger_keys):
    b2, b3 = blob(":2:", path), blob(":3:", path)
    a2, a3 = json.loads(b2), json.loads(b3)
    s, _, _ = pick_side(b2, b3)
    newer, older = (a3, a2) if s == 3 else (a2, a3)
    base = dict(newer)
    for k in ledger_keys:
        if not (isinstance(a2.get(k), list) and isinstance(a3.get(k), list)):
            continue
        seen = {}
        for src_newer in (True, False):
            src = newer if src_newer else older
            for rec in src[k]:
                ident = row_ident(rec)
                if ident in seen and not src_newer:
                    continue          # same logical row: newer side wins
                seen[ident] = rec    # first pass=newer (claims identity),
        merged = list(seen.values())  # second pass=older (fills gaps only)
        idents_all = {row_ident(r) for r in a2[k]} | {row_ident(r) for r in a3[k]}
        assert len(merged) == len(idents_all), f"{path} {k} identity-union loss"
        merged.sort(key=lambda r: r.get("ts", r.get("asof", r.get("date", "")))
                    if isinstance(r, dict) else "")
        base[k] = merged
        n2, n3 = len(a2[k]), len(a3[k])
        report.append(f"rolling {path} {k}: |A|={n2} |B|={n3} "
                      f"|AUB|identities={len(merged)} side=:{s}: newer-row-wins "
                      f"(no resolver cap, r360; producer window owns truncation r85)")
    win = b3 if s == 3 else b2
    mirror_write(path, base, win)


def main():
    # snapshot singles
    singles = [
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in singles:
        resolve_snapshot(p, blob(":2:", p), blob(":3:", p))
    # twins (side decided from json face)
    resolve_twin("docs/daily_report/REPORT-2026-09-28.json",
                 "docs/daily_report/REPORT-2026-09-28.md")
    resolve_twin("results/dashboard_status.json", "results/dashboard_status.js")
    # ledgers
    resolve_autofill_state()
    resolve_rolling("results/compute_audit.json", ["history"])
    resolve_rolling("results/regime_state.json",
                    ["history", "transitions", "daily"])
    for line in report:
        print(line)
    print(f"RESOLVED {len(report)} faces, parse-verify all passed")


if __name__ == "__main__":
    main()
