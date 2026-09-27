# -*- coding: utf-8 -*-
"""r355 bm-b rebase-storm resolver #2 (15-UU vs bm-a r373 lane-migration chain).

Trigger: S7 push of round-close commit 1166b7bc rejected (origin moved
8633afce..f64d23b1 = bm-a r373 closeout + addendum) -> pull --rebase ->
15-UU. Skill exception face (push-rejection collision batch), canon
resolve per classify_conflicts.py 16/16 GREEN 0 UNKNOWN.

Stage law (r352): REBASE :2: = HEAD = upstream (bm-a side),
:3: = replayed local commit (bm-b round-close). Side assert
st(2,p)==git show HEAD:p -- fail-closed.

Recipes:
- CODELY.md (memory-union, D-20260927-09): merge-base :1: prefix-identity
  assertion on BOTH sides (normalized fallback per bm-a r373 byte-face
  law), then DIRECT-CONCAT: new = base + A-suffix + B-suffix, entries
  verbatim, NO line-dedupe (union-dedupe collapses structure live-fire).
- daily twins (json+md): coupled SAME-side take-new by inner generated
  ts (r98/99/100).
- dashboard_status.js: whole bytes, same side as .json twin (R209).
- compute_audit: history union dedup-by-ts (upstream first-writer,
  zero row loss) + latest take-new deep-ts (r311/r319).
- regime_state: history union on asof + transitions union + state
  take-new by updated.
- snapshot family (10): take-new via hardened deep wall-ts probe
  (R350: time-of-day required in value, key-EXCLUDE forbidden, staged
  blob probed); lane-status trio (futures/heat/lhb) scalar-diff pre-probed
  = probe-ts-only deltas, faces identical -> take-new safe (R31
  authority faces preserved on both sides).
Parse-verify + marker scan before staging (r185)."""
import json
import re
import subprocess

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def st(n, p):
    r = subprocess.run(["git", "show", f":{n}:{p}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} probe fail {p}: {r.stderr[:120]}")
    return r.stdout


def head_blob(p):
    r = subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"HEAD probe fail {p}: {r.stderr[:120]}")
    return r.stdout


def wall_ts(obj):
    """Hardened deep wall-clock probe (R350): values must carry time-of-day."""
    best = ""
    if isinstance(obj, dict):
        it = obj.values()
    elif isinstance(obj, list):
        it = obj
    else:
        return best
    for v in it:
        if isinstance(v, (dict, list)):
            b = wall_ts(v)
            if b > best:
                best = b
        elif isinstance(v, str) and WALL.match(v) and v > best:
            best = v
    return best


def jload(n, p):
    return json.loads(st(n, p).decode("utf-8"))


def take_new_raw(p, log, tag=""):
    """Snapshot family: whole-doc side take by deep wall-ts (raw bytes)."""
    a, b = jload(2, p), jload(3, p)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    if not ta and not tb:
        side = 2  # tie/no-probe -> upstream/HEAD (r140)
    raw = st(side, p)
    with open(p, "wb") as f:
        f.write(raw)
    log(f"[{p}]{tag} snapshot take-side :{side}: (ts2='{ta[:22]}' "
        f"ts3='{tb[:22]}')")
    return side


def main():
    lines = []

    def log(s):
        lines.append(s)
        print(s)

    snaps = ["results/dashboard_status.json",
             "results/fundamental_b_layer_filter.json",
             "results/futures_update_status.json",
             "results/heat_update_status.json",
             "results/lhb_update_status.json",
             "results/prospect_promotion/_summary.json",
             "results/scorecard_v1.json",
             "results/strategy_scorecard.json",
             "results/token_usage.json",
             "results/update_status.json"]
    dj = "docs/daily_report/REPORT-2026-09-28.json"
    dm = "docs/daily_report/REPORT-2026-09-28.md"
    all_files = snaps + [dj, dm, "results/dashboard_status.js",
                         "results/compute_audit.json",
                         "results/regime_state.json", "CODELY.md"]

    # ---- side-identity assert on ALL conflicted files (r352 law) ----
    for p in all_files:
        if st(2, p) != head_blob(p):
            raise RuntimeError(f"side-inversion suspect at {p}: :2: != HEAD: "
                               "-- ABORT resolution, adjudicate manually")
    log(f"side-identity assert: :2:==HEAD verified on {len(all_files)} files "
        "(rebase stage law holds)")

    # ---- CODELY.md: memory-union direct-concat (D-20260927-09) ----
    p = "CODELY.md"
    base, A, B = st(1, p), st(2, p), st(3, p)
    bn, An, Bn = (x.replace(b"\r\n", b"\n") for x in (base, A, B))
    if An.startswith(bn) and Bn.startswith(bn):
        out = An + Bn[len(bn):]
        mode = "normalized-prefix PASS (CRLF face), LF write"
    elif A.startswith(base) and B.startswith(base):
        out = A + B[len(base):]
        mode = "exact-prefix PASS"
    else:
        raise RuntimeError("CODELY.md prefix-identity FAIL = in-place edit "
                           "not append -- manual review required")
    with open(p, "wb") as f:
        f.write(out)
    log(f"[CODELY.md] memory-union direct-concat: base {len(base)}B + "
        f"A-suffix {len(An) - len(bn)}B + B-suffix {len(Bn) - len(bn)}B = "
        f"{len(out)}B zero-loss ({mode}; NO line-dedupe per D-20260927-09)")

    # ---- snapshot family (whole-doc take-new, raw bytes) ----
    for p in snaps:
        take_new_raw(p, log)

    # ---- daily twins: coupled same-side (r98/99/100) ----
    a, b = jload(2, dj), jload(3, dj)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    if not ta and not tb:
        side = 2
    for p in (dj, dm):
        with open(p, "wb") as f:
            f.write(st(side, p))
    log(f"[daily twins] coupled take-side :{side}: "
        f"(ts2='{ta[:22]}' ts3='{tb[:22]}')")

    # ---- dashboard js: whole bytes, same side as .json twin ----
    a, b = jload(2, "results/dashboard_status.json"), \
        jload(3, "results/dashboard_status.json")
    ta, tb = wall_ts(a), wall_ts(b)
    side_js = 2 if (not tb or (ta and ta >= tb)) else 3
    with open("results/dashboard_status.js", "wb") as f:
        f.write(st(side_js, "results/dashboard_status.js"))
    log(f"[dashboard_status.js] whole-bytes same side as json twin "
        f":{side_js}: (R209)")

    # ---- compute_audit: history union on ts + latest take-new ----
    p = "results/compute_audit.json"
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    hmap = {}
    for row in ha + hb:
        hmap.setdefault(row.get("ts"), row)  # upstream first-writer
    hist = [hmap[k] for k in sorted(hmap)]
    la, lb = a.get("latest", {}), b.get("latest", {})
    ta, tb = wall_ts(la), wall_ts(lb)
    latest = la if (not tb or (ta and ta >= tb)) else lb
    out = dict(a if wall_ts(a) >= wall_ts(b) else b)
    out["latest"] = latest
    out["history"] = hist
    crlf = b"\r\n" in raw3 or b"\r\n" in raw2
    s = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        s = s.replace("\n", "\r\n")
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))
    log(f"[compute_audit] history {len(ha)}+{len(hb)} -> {len(hist)} "
        f"(dedup-by-ts zero-loss); latest deep-ts='{wall_ts(latest)[:22]}' "
        f"(a='{ta[:22]}' b='{tb[:22]}')")

    # ---- regime_state: history union on asof + transitions + take-new ----
    p = "results/regime_state.json"
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    hm = {}
    for row in a.get("history", []) + b.get("history", []):
        hm.setdefault(row.get("asof"), row)
    hist = [hm[k] for k in sorted(hm)]
    tm = {}
    for row in a.get("transitions", []) + b.get("transitions", []):
        tm.setdefault(row.get("asof") or row.get("ts") or str(len(tm)), row)
    trans = [tm[k] for k in sorted(tm)]
    base = a if a.get("updated", "") >= b.get("updated", "") else b
    out = dict(base)
    out["history"] = hist
    out["transitions"] = trans
    crlf = b"\r\n" in raw3 or b"\r\n" in raw2
    s = json.dumps(out, ensure_ascii=False, indent=1)
    if crlf:
        s = s.replace("\n", "\r\n")
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))
    log(f"[regime_state] history {len(a.get('history', []))}+"
        f"{len(b.get('history', []))} -> {len(hist)}; transitions "
        f"{len(a.get('transitions', []))}+{len(b.get('transitions', []))} "
        f"-> {len(trans)}; updated='{out.get('updated', '')[:22]}'")

    # ---- parse-verify + marker scan (r185) ----
    for p in snaps + [dj, "results/compute_audit.json",
                      "results/regime_state.json"]:
        json.load(open(p, encoding="utf-8"))
    js = open("results/dashboard_status.js", "rb").read()
    assert js.lstrip().startswith(b"window.DASH_DATA") and \
        js.rstrip().endswith(b";"), "js wrapper face broken (R209)"
    for p in all_files:
        blob = open(p, "rb").read()
        assert b"<<<<<<<" not in blob and b">>>>>>>" not in blob, \
            f"conflict markers left in {p}"
    log(f"parse-verify: {len(snaps) + 4} json OK + js wrapper OK + 0 "
        f"conflict markers in {len(all_files)} files")

    # ---- stage resolutions ----
    for p in all_files:
        r = subprocess.run(["git", "add", p], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"git add fail {p}: {r.stderr[:120]}")
    log(f"staged: {len(all_files)} resolved files")

    with open("results/_r355bmb_resolve2.log", "w", encoding="utf-8",
              newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("RESOLVER DONE -> _r355bmb_resolve2.log")


if __name__ == "__main__":
    main()
