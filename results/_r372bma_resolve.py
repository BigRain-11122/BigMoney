"""r372 bm-a push-storm resolver: 15-UU vs origin chain (bm-c r124 S6 family,
commit 9595c9f4 landed in-window before my push).

Sides: rebase stage :2: = origin (bm-c r124 base), stage :3: = mine
(replayed b884dc12).  Side-assert fingerprint (r352 law): my S6
compute_audit leg ran at 2026-09-28 02:25:33 -> :3: latest.ts MUST
equal it; halt otherwise.

Recipes per classifier GREEN 15/15 (0 UNKNOWN):
  twins REPORT json+md  -> json generated probe decides side, md
                           byte-copies SAME side (r327/r329)
  autofill_state        -> launches composite-key union (r322 field-
                           superset law, true divergence = fail-closed),
                           desc cap50 -> asc write-back (r245); last_tick
                           inner-ts dict compare, tie -> origin/HEAD (r140)
  compute_audit         -> history ts-key union zero-loss (r85 key-set
                           survival assert), state fields from newer deep
                           latest.ts probe (r311/D-09)
  regime_state          -> triggers/transitions/history whole-row identity
                           union, flat keys from newer 'updated' side
  dashboard json+js     -> json probe decides, js byte-copies SAME side
                           (R209 pair, no json.dumps strip)
  snapshots x10         -> take-new whole blob by hardened wall-clock probe
                           (r100 key-normalize + R350 time-of-day value
                           gate), tie -> origin; byte-copy, zero re-serialization
All probes read STAGED BLOBS (:2:/:3:), never the working tree (R350).
Union faces mirror base (:2:) blob indent/CRLF/tail/BOM (r223/r234).
Parse-verify every JSON before write-back (r185). Zero PS redirects (r209).
"""
import json
import re
import subprocess

UU = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/autofill_state.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TS_KEY_PREFIXES = ("generated", "updated", "ts", "stateupdated", "latest",
                   "asof")
WALLCLOCK = re.compile(r"^20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}")
MY_AUDIT_TS = "2026-09-28 02:25:27"   # side-assert fingerprint (r352 law)


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show :{stage}:{path} rc={r.returncode} "
                         f"{r.stderr[:200]!r}")
    return r.stdout


def faces(b):
    return dict(bom=b.startswith(b"\xef\xbb\xbf"), crlf=b"\r\n" in b,
                tail=b.endswith(b"\n"))


def parse(b):
    return json.loads(b.decode("utf-8-sig"))


def probe_wallclock(obj):
    """Hardened deep ts probe: key-normalized positive list (r100) + value
    must carry time-of-day (R350 date-only gate); staged blob only."""
    best = ""

    def walk(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                nk = re.sub(r"[_-]", "", str(k)).lower()
                if isinstance(v, str) and WALLCLOCK.match(v.strip()):
                    for pref in TS_KEY_PREFIXES:
                        if nk.startswith(pref):
                            if v.strip() > best:
                                best = v.strip()
                            break
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)

    walk(obj)
    return best


def row_id(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


def detect_indent(b):
    m = re.search(rb"\n( +)\S", b)
    return max(1, len(m.group(1))) if m else 1


def emit(obj, base_bytes):
    f = faces(base_bytes)
    unit = detect_indent(base_bytes)
    out = json.dumps(obj, ensure_ascii=False, indent=unit)
    if f["crlf"]:
        out = out.replace("\n", "\r\n")
    if f["tail"]:
        out += "\r\n" if f["crlf"] else "\n"
    return (b"\xef\xbb\xbf" if f["bom"] else b"") + out.encode("utf-8")


def write(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


RESOLVED = []


def take_new(path, probe=probe_wallclock):
    s2, s3 = blob(2, path), blob(3, path)
    t2, t3 = probe(parse(s2)), probe(parse(s3))
    win = 2 if t2 >= t3 else 3
    print(f"  {path}: take :{win}: ({t2!r} vs {t3!r})")
    write(path, s2 if win == 2 else s3)
    RESOLVED.append(path)


def twins(json_path, md_path):
    s2j, s3j = blob(2, json_path), blob(3, json_path)
    t2, t3 = probe_wallclock(parse(s2j)), probe_wallclock(parse(s3j))
    win = 2 if t2 >= t3 else 3
    print(f"  {json_path}: twin json decides :{win}: ({t2!r} vs {t3!r})")
    write(json_path, s2j if win == 2 else s3j)
    s2m, s3m = blob(2, md_path), blob(3, md_path)
    write(md_path, s2m if win == 2 else s3m)  # md byte-copy SAME side (r329)
    print(f"  {md_path}: md byte-copied same side :{win}")
    RESOLVED.extend([json_path, md_path])


def resolve_autofill():
    p = "results/autofill_state.json"
    s2, s3 = blob(2, p), blob(3, p)
    a, b = parse(s2), parse(s3)
    comp_key = lambda x: tuple(str(x.get(k, "")) for k in
                               ("ts", "machine", "pid", "runner_sha256",
                                "entry", "shard"))
    keyed = {}
    order = []
    for src, rows in ((a, a.get("launches", [])), (b, b.get("launches", []))):
        for r in rows:
            k = comp_key(r)
            if k not in keyed:
                keyed[k] = r
                order.append(k)
            else:
                old = keyed[k]
                if row_id(old) == row_id(r):
                    continue
                # r322 field-superset law: shared fields equal + one side
                # only ADDS fields -> field-union keep-one; else fail-closed
                shared = set(old) & set(r)
                same_shared = all(old[f] == r[f] for f in shared)
                if same_shared and (set(old) <= set(r) or set(r) <= set(old)):
                    keyed[k] = {**old, **r}
                    print(f"  autofill: key {k[0]} {k[1]} field-superset "
                          f"merge -> {len(keyed[k])} fields")
                else:
                    raise SystemExit(f"autofill TRUE DIVERGENCE on key {k}: "
                                    f"flag-escalation, no silent double-keep")
    rows = [keyed[k] for k in order]
    rows.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
    rows = rows[:50]
    rows.sort(key=lambda x: str(x.get("ts", "")))  # r245 asc write-back
    lt2, lt3 = (a.get("last_tick") or {}).get("ts", ""), \
               (b.get("last_tick") or {}).get("ts", "")
    last_tick = (a if lt2 >= lt3 else b).get("last_tick")  # tie -> origin r140
    assert isinstance(last_tick, dict), "last_tick must stay dict (r140)"
    out = {"last_tick": last_tick, "launches": rows}
    write(p, emit(out, s2))
    print(f"  autofill: launches union |{len(a.get('launches', []))}|+"
          f"|{len(b.get('launches', []))}| -> {len(rows)} (cap50 asc); "
          f"last_tick ts={str(last_tick.get('ts'))!r} "
          f"({'origin-tie-or-newer' if lt2 >= lt3 else 'mine-newer'})")
    RESOLVED.append(p)


def resolve_compute_audit():
    p = "results/compute_audit.json"
    s2, s3 = blob(2, p), blob(3, p)
    a, b = parse(s2), parse(s3)
    hist, seen = [], set()
    for src in (a, b):
        for h in src.get("history", []):
            ts = str(h.get("ts", ""))
            if ts not in seen:
                seen.add(ts)
                hist.append(h)
    hist.sort(key=lambda h: str(h.get("ts", "")))
    # r85 zero-loss: key-set survival (window shrink is producer semantics)
    k2 = {str(h.get("ts", "")) for h in a.get("history", [])}
    k3 = {str(h.get("ts", "")) for h in b.get("history", [])}
    assert seen == k2 | k3, "audit history key-set loss"
    t2 = (a.get("latest") or {}).get("ts", "")
    t3 = (b.get("latest") or {}).get("ts", "")
    win_src = a if t2 >= t3 else b  # deep probe latest.ts; tie -> origin
    out = {k: v for k, v in win_src.items() if k != "history"}
    out["history"] = hist
    write(p, emit(out, s2))
    print(f"  audit: history |{len(k2)}|+|{len(k3)}| -> {len(hist)} "
          f"(key-union zero-loss); state fields from "
          f"{'origin' if t2 >= t3 else 'mine'} latest.ts "
          f"({t2!r} vs {t3!r})")
    RESOLVED.append(p)


def resolve_regime():
    p = "results/regime_state.json"
    s2, s3 = blob(2, p), blob(3, p)
    a, b = parse(s2), parse(s3)
    win_src = a if str(a.get("updated", "")) >= str(b.get("updated", "")) else b
    out = dict(win_src)
    for k in ("triggers", "transitions", "history"):
        rows, seenrows = [], set()
        for src in (a, b):
            for r in src.get(k, []):
                rid = row_id(r)
                if rid not in seenrows:
                    seenrows.add(rid)
                    rows.append(r)
        out[k] = rows
        print(f"  regime {k}: union -> {len(rows)}")
    write(p, emit(out, s2))
    print(f"  regime: flat from {'origin' if win_src is a else 'mine'} "
          f"updated={win_src.get('updated')!r}")
    RESOLVED.append(p)


def resolve_dashboard_pair():
    pj = "results/dashboard_status.json"
    ps = "results/dashboard_status.js"
    s2j, s3j = blob(2, pj), blob(3, pj)
    t2, t3 = probe_wallclock(parse(s2j)), probe_wallclock(parse(s3j))
    win = 2 if t2 >= t3 else 3
    write(pj, s2j if win == 2 else s3j)
    s2s, s3s = blob(2, ps), blob(3, ps)
    write(ps, s2s if win == 2 else s3s)  # R209: js byte-copy same side
    print(f"  dashboard pair -> side :{win}: ({t2!r} vs {t3!r}), js wrapper "
          f"byte-copied (no json.dumps strip)")
    RESOLVED.extend([pj, ps])


def side_assert():
    """r352 law: rebase :2: = upstream/origin, :3: = replayed mine.
    Fingerprint = my S6 audit leg ts."""
    mine = parse(blob(3, "results/compute_audit.json"))
    ts = str((mine.get("latest") or {}).get("ts", ""))
    assert ts == MY_AUDIT_TS, (
        f"side-assert FAIL: :3: compute_audit latest.ts={ts!r} != "
        f"{MY_AUDIT_TS!r} -- stage mapping assumption broken, re-derive "
        f"sides before any write")
    print(f"side-assert PASS: :3: = mine (audit latest.ts {ts!r}); "
          f":2: = origin (bm-c r124)")


print("== side-assert ==")
side_assert()
print("== twins ==")
twins(UU[0], UU[1])
print("== autofill_state ==")
resolve_autofill()
print("== compute_audit ==")
resolve_compute_audit()
print("== regime_state ==")
resolve_regime()
print("== dashboard pair ==")
resolve_dashboard_pair()
print("== take-new snapshots ==")
for p in UU[6:10] + UU[11:]:  # skip index 10 (regime union done above)
    take_new(p)

print("== parse-verify (r185) ==")
for p in RESOLVED:
    if p.endswith(".json"):
        parse(open(p, "rb").read())
        print(f"  parse ok: {p}")
print("== conflict-marker scan ==")
bad = [p for p in RESOLVED
       if re.search(rb"^(<{7}|={7}|>{7})", open(p, "rb").read(), re.M)]
assert not bad, f"markers remain: {bad}"
print("  zero markers in all", len(RESOLVED), "resolved files")
missing = [p for p in UU if p not in RESOLVED]
assert not missing, f"unresolved UU: {missing}"
print(f"RESOLVED {len(RESOLVED)} files, all 15 UU covered")
