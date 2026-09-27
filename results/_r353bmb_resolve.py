# -*- coding: utf-8 -*-
"""r353 bm-b rebase-storm resolver (16-UU vs bm-a r371 chain).

Stage law (r352 pit-law): REBASE :2: = HEAD = upstream/origin side (bm-a),
:3: = the replayed local commit (bm-b r353 close). All probes read STAGED
blobs via subprocess (no PS redirect, r209/r352 law). Recipes per
classify_conflicts.py output (16/16 classified, 0 UNKNOWN):
- snapshot family: take-new whole doc via hardened deep wall-ts probe
  (R350: time-of-day required in value; key-EXCLUDE forbidden)
- daily twins: coupled same-side take-new (r98/99/100)
- dashboard js: whole-bytes same side as its .json twin (R209)
- autofill_state: launches composite-key union -> ts sort -> cap 50 ->
  re-sort ascending on write-back (r245); last_tick whole-dict by inner
  ts, tie -> HEAD/:2: (r140); CRLF mirror (r223/r234)
- compute_audit: history union on ts (zero row loss) + latest take-new
  deep-ts (r311/r319)
- regime_state: history union on asof + transitions union + state
  fields take-new
Parse-verify before write-back (r185). Zero-loss counts printed."""
import io
import json
import re
import subprocess

WALL = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def st(n, p):
    r = subprocess.run(["git", "show", f":{n}:{p}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} probe fail {p}: {r.stderr[:120]}")
    return r.stdout


def wall_ts(obj):
    """Hardened deep wall-clock probe (R350): collect ts-shaped values
    that carry time-of-day; date-only values never feed the max."""
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


def crlf_of(raw):
    return b"\r\n" in raw


def dump_bytes(obj, crlf):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    if crlf:
        s = s.replace("\n", "\r\n")
    return s.encode("utf-8")


def take_new(p, log):
    a, b = jload(2, p), jload(3, p)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    if not ta and not tb:
        side = 2  # tie/no-probe -> HEAD (r140)
    obj = a if side == 2 else b
    with open(p, "wb") as f:
        raw = st(side, p)
        f.write(raw)
    log(f"[{p}] snapshot take-side :{side}: (ts2='{ta[:22]}' ts3='{tb[:22]}')")
    return side


def main():
    lines = []

    def log(s):
        lines.append(s)
        print(s)

    # ---- snapshot family (whole-doc take-new) ----
    snaps = ["results/fundamental_b_layer_filter.json",
             "results/futures_update_status.json",
             "results/heat_update_status.json",
             "results/lhb_update_status.json",
             "results/update_status.json",
             "results/prospect_promotion/_summary.json",
             "results/scorecard_v1.json",
             "results/strategy_scorecard.json",
             "results/token_usage.json",
             "results/dashboard_status.json"]
    for p in snaps:
        take_new(p, log)

    # ---- daily twins: coupled same-side ----
    dj = "docs/daily_report/REPORT-2026-09-28.json"
    a, b = jload(2, dj), jload(3, dj)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    for p in (dj, "docs/daily_report/REPORT-2026-09-28.md"):
        with open(p, "wb") as f:
            f.write(st(side, p))
    log(f"[daily twins] coupled take-side :{side}: "
        f"(ts2='{ta[:22]}' ts3='{tb[:22]}')")

    # ---- dashboard js: whole bytes, same side as .json twin ----
    side_js = take_new("results/dashboard_status.json", log)
    with open("results/dashboard_status.js", "wb") as f:
        f.write(st(side_js, "results/dashboard_status.js"))
    log(f"[dashboard_status.js] whole-bytes same side :{side_js}: (R209)")

    # ---- autofill_state: composite-key union + last_tick take-new ----
    p = "results/autofill_state.json"
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    la, lb = a.get("launches", []), b.get("launches", [])
    seen, union = set(), []
    for rec in la + lb:
        key = (rec.get("machine"), rec.get("ts"), rec.get("shard"),
               rec.get("pid"), rec.get("entry"), rec.get("verdict"))
        if key in seen:
            continue
        seen.add(key)
        union.append(rec)
    union.sort(key=lambda r: r.get("ts", ""))
    n_union = len(union)
    if n_union > 50:
        union = union[-50:]
    union.sort(key=lambda r: r.get("ts", ""))  # r245: append-order write-back
    t2 = a.get("last_tick", {}).get("ts", "")
    t3 = b.get("last_tick", {}).get("ts", "")
    last = a["last_tick"] if t2 >= t3 else b["last_tick"]  # tie -> :2: HEAD
    out = {"last_tick": last, "launches": union}
    assert isinstance(out["last_tick"], dict), "last_tick must be dict"
    with open(p, "wb") as f:
        f.write(dump_bytes(out, crlf_of(raw3) or crlf_of(raw2)))
    log(f"[autofill_state] launches {len(la)}+{len(lb)} -> union "
        f"{n_union} cap-> {len(union)} (zero-loss idents={n_union}); "
        f"last_tick take-new ts='{last.get('ts')}' verdict="
        f"'{last.get('verdict')}' (t2='{t2}' t3='{t3}')")

    # ---- compute_audit: history union on ts + latest take-new ----
    p = "results/compute_audit.json"
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    hmap = {}
    for row in ha + hb:
        hmap.setdefault(row.get("ts"), row)  # first-writer, later same-ts dup
    hist = [hmap[k] for k in sorted(hmap)]
    latest = (a if wall_ts(a.get("latest", {})) >=
              wall_ts(b.get("latest", {})) else b)["latest"]
    out = {"latest": latest, "history": hist}
    with open(p, "wb") as f:
        f.write(dump_bytes(out, crlf_of(raw3) or crlf_of(raw2)))
    log(f"[compute_audit] history {len(ha)}+{len(hb)} -> {len(hist)} "
        f"(dedup-by-ts zero-loss); latest ts='{wall_ts(latest)[:22]}'")

    # ---- regime_state: history union on asof + state take-new ----
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
    with open(p, "wb") as f:
        f.write(dump_bytes(out, crlf_of(raw3) or crlf_of(raw2)))
    log(f"[regime_state] history {len(a.get('history', []))}+"
        f"{len(b.get('history', []))} -> {len(hist)}; transitions "
        f"{len(a.get('transitions', []))}+{len(b.get('transitions', []))} "
        f"-> {len(trans)}; updated='{out.get('updated')}' state="
        f"'{out.get('state')}'")

    # ---- parse-verify all written json (r185) ----
    ok = 0
    for p in snaps + [dj, "results/autofill_state.json",
                      "results/compute_audit.json", "results/regime_state.json"]:
        json.load(open(p, encoding="utf-8"))
        ok += 1
    js = open("results/dashboard_status.js", "rb").read()
    assert js.lstrip().startswith(b"window.DASH_DATA") and js.rstrip(
    ).endswith(b";"), "js wrapper face broken (R209)"
    log(f"parse-verify: {ok} json files OK + js wrapper face OK")

    with io.open("results/_r353bmb_resolve.log", "w", encoding="utf-8",
                 newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("RESOLVER DONE -> _r353bmb_resolve.log")


if __name__ == "__main__":
    main()
