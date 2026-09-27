"""r373 bm-a push-storm resolver: 3-UU vs origin chain (bm-c r125 family
landed in-window before my push; commit 11d6f0fa replayed).

Sides: rebase stage :2: = origin (bm-c r125 base), stage :3: = mine
(replayed 11d6f0fa).  Side-assert fingerprint (r352 law): my S6
compute_audit leg ran at 2026-09-28 02:44:32 -> :3: latest.ts MUST
equal it; halt otherwise.

Classifier GREEN 3/3 (0 UNKNOWN):
  CODELY.md            -> memory-union.  Prefix assertion failed on the
                          BYTE face because my replace-tool edit
                          normalized every line ending to CRLF (base is
                          mixed LF); after \r\n -> \n normalization the
                          prefix assertion PASSES on BOTH sides =
                          pure-append on both (r327/r329 entry-level
                          route, no in-place edit).  Union = origin
                          bytes verbatim + my entry re-terminated to
                          origin tail style (byte-stable upstream face,
                          r223/r234); entries ordered by their own
                          header ts (bm-c 02:4x < bm-a 02:5x).
  autofill_state       -> launches composite-key union (r322 field-
                          superset law, true divergence = fail-closed),
                          desc cap50 -> asc write-back (r245); last_tick
                          inner-ts dict compare, tie -> origin/HEAD (r140)
  compute_audit        -> history ts-key union zero-loss (r85 key-set
                          survival assert), state fields from newer deep
                          latest.ts probe (r311/D-09; mine 02:44:32 >
                          origin 02:33:48)
All probes read STAGED BLOBS (:2:/:3:), never the working tree (R350).
Union faces mirror origin (:2:) blob BOM/CRLF/indent/tail (r223/r234).
Parse-verify every JSON before write-back (r185). Zero PS redirects (r209).
"""
import json
import re
import subprocess

MY_AUDIT_TS = "2026-09-28 02:44:32"   # side-assert fingerprint (r352 law)
BASE_COMMIT = "6ad8635f"              # S0 pull tip = my commit's parent


def blob(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show {spec} rc={r.returncode} "
                         f"{r.stderr[:200]!r}")
    return r.stdout


def faces(b):
    return dict(bom=b.startswith(b"\xef\xbb\xbf"), crlf=b"\r\n" in b,
                tail=b.endswith(b"\n"))


def parse(b):
    return json.loads(b.decode("utf-8-sig"))


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


def side_assert():
    mine = parse(blob(":3:results/compute_audit.json"))
    ts = str((mine.get("latest") or {}).get("ts", ""))
    assert ts == MY_AUDIT_TS, (
        f"side-assert FAIL: :3: audit latest.ts={ts!r} != {MY_AUDIT_TS!r} "
        f"-- stage mapping assumption broken, re-derive sides first")
    head = parse(blob("HEAD:results/compute_audit.json"))
    print(f"side-assert PASS: :3: = mine (audit {ts!r}); "
          f":2: = HEAD/origin (audit "
          f"{str((head.get('latest') or {}).get('ts', ''))!r})")


def resolve_codely():
    p = "CODELY.md"
    base = blob(f"{BASE_COMMIT}:{p}")
    o = blob(f":2:{p}")
    m = blob(f":3:{p}")
    norm = lambda b: b.replace(b"\r\n", b"\n")
    nb, no_, nm = norm(base), norm(o), norm(m)
    # r327 entry-level route: normalize line endings, then require
    # pure-append on BOTH sides (prefix identity)
    assert no_.startswith(nb), "origin made in-place edits -- manual review"
    assert nm.startswith(nb), "mine made in-place edits -- manual review"
    osuf, msuf = no_[len(nb):], nm[len(nb):]
    for suf, who in ((osuf, "origin"), (msuf, "mine")):
        assert suf.lstrip().startswith(b"- [2026-09-28 02:"), (
            f"{who} suffix not a complete pit-law entry: {suf[:60]!r}")
    # order by each entry's own header ts (bm-c 02:4x < bm-a 02:5x)
    ots = re.search(rb"\[2026-09-28 (02:\d+x)", osuf).group(1)
    mts = re.search(rb"\[2026-09-28 (02:\d+x)", msuf).group(1)
    assert ots <= mts, f"unexpected entry order {ots!r} vs {mts!r}"
    # byte-stable upstream face: origin verbatim + my entry re-terminated
    # to origin tail style (origin file ends with CRLF)
    assert o.endswith(b"\r\n"), "origin tail not CRLF -- adjust re-term"
    union = o + msuf.replace(b"\n", b"\r\n")
    assert norm(union) == nb + osuf + msuf, "union content drift"
    write(p, union)
    print(f"  CODELY.md: memory-union base {len(base)}B + origin-suffix "
          f"{len(osuf)}B (bm-c r125 {ots.decode()}) + mine-suffix "
          f"{len(msuf)}B (r373 {mts.decode()}) -> {len(union)}B "
          f"(origin byte-stable, mine re-terminated CRLF)")
    RESOLVED.append(p)


def resolve_autofill():
    p = "results/autofill_state.json"
    s2, s3 = blob(f":2:{p}"), blob(f":3:{p}")
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
                shared = set(old) & set(r)
                same_shared = all(old[f] == r[f] for f in shared)
                if same_shared and (set(old) <= set(r) or set(r) <= set(old)):
                    keyed[k] = {**old, **r}
                    print(f"  autofill: field-superset merge on key {k}")
                else:
                    raise SystemExit(f"autofill TRUE DIVERGENCE key {k}: "
                                    f"flag-escalation, no silent double-keep")
    rows = [keyed[k] for k in order]
    rows.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
    rows = rows[:50]
    rows.sort(key=lambda x: str(x.get("ts", "")))  # r245 asc write-back
    lt2 = (a.get("last_tick") or {}).get("ts", "")
    lt3 = (b.get("last_tick") or {}).get("ts", "")
    last_tick = (a if lt2 >= lt3 else b).get("last_tick")  # tie->origin r140
    assert isinstance(last_tick, dict), "last_tick must stay dict (r140)"
    out = {"last_tick": last_tick, "launches": rows}
    write(p, emit(out, s2))
    print(f"  autofill: launches |{len(a.get('launches', []))}|+"
          f"|{len(b.get('launches', []))}| -> {len(rows)} (cap50 asc); "
          f"last_tick ts={str(last_tick.get('ts'))!r} "
          f"({'origin-tie-or-newer' if lt2 >= lt3 else 'mine-newer'})")
    RESOLVED.append(p)


def resolve_compute_audit():
    p = "results/compute_audit.json"
    s2, s3 = blob(f":2:{p}"), blob(f":3:{p}")
    a, b = parse(s2), parse(s3)
    hist, seen = [], set()
    for src in (a, b):
        for h in src.get("history", []):
            ts = str(h.get("ts", ""))
            if ts not in seen:
                seen.add(ts)
                hist.append(h)
    hist.sort(key=lambda h: str(h.get("ts", "")))
    k2 = {str(h.get("ts", "")) for h in a.get("history", [])}
    k3 = {str(h.get("ts", "")) for h in b.get("history", [])}
    assert seen == k2 | k3, "audit history key-set loss (r85)"
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


print("== side-assert ==")
side_assert()
print("== CODELY.md (memory-union, entry-level route) ==")
resolve_codely()
print("== autofill_state ==")
resolve_autofill()
print("== compute_audit ==")
resolve_compute_audit()
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
assert len(RESOLVED) == 3, "expected exactly the 3 classified UU files"
print("RESOLVED 3/3 UU (CODELY.md + autofill_state + compute_audit)")
