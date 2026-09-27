# -*- coding: utf-8 -*-
"""r354 bm-b rebase-storm resolver (15-UU vs bm-a r372 lane-migration chain).

Stage law (r352 pit-law): REBASE :2: = HEAD = upstream/origin side (bm-a),
:3: = the replayed local commit (bm-b r354 close). Side-identity assert:
st(2,p) == git show HEAD:p (HEAD during rebase = upstream) -- fail-closed.
Recipes per classify_conflicts.py output (15/15 classified, 0 UNKNOWN):
- snapshot family (10): take-new whole doc via hardened deep wall-ts probe
  (R350: time-of-day required in value; key-EXCLUDE forbidden)
- daily twins (2): coupled same-side take-new (r98/99/100)
- dashboard js (1): whole-bytes same side as its .json twin (R209)
- compute_audit (1): history union on ts (zero row loss) + latest take-new
  deep-ts (r311/r319)
- regime_state (1): history union on asof + transitions union + state
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


def head_blob(p):
    r = subprocess.run(["git", "show", f"HEAD:{p}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"HEAD probe fail {p}: {r.stderr[:120]}")
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


def assert_side(p, log):
    """r352 law: :2: must equal HEAD (upstream) during rebase."""
    if st(2, p) != head_blob(p):
        raise RuntimeError(f"side-inversion suspect at {p}: :2: != HEAD: -- "
                           "ABORT resolution, adjudicate manually")


def take_new(p, log):
    a, b = jload(2, p), jload(3, p)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    if not ta and not tb:
        side = 2  # tie/no-probe -> HEAD (r140)
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
    dj = "docs/daily_report/REPORT-2026-09-28.json"
    dm = "docs/daily_report/REPORT-2026-09-28.md"
    all_files = snaps + [dj, dm, "results/dashboard_status.js",
                         "results/compute_audit.json",
                         "results/regime_state.json"]

    # ---- side-identity assert on ALL conflicted files (r352 law) ----
    for p in all_files:
        assert_side(p, log)
    log(f"side-identity assert: :2:==HEAD verified on {len(all_files)} files "
        "(rebase stage law holds)")

    # ---- snapshot family (whole-doc take-new) ----
    for p in snaps:
        take_new(p, log)

    # ---- daily twins: coupled same-side ----
    a, b = jload(2, dj), jload(3, dj)
    ta, tb = wall_ts(a), wall_ts(b)
    side = 2 if (not tb or (ta and ta >= tb)) else 3
    for p in (dj, dm):
        with open(p, "wb") as f:
            f.write(st(side, p))
    log(f"[daily twins] coupled take-side :{side}: (ts2='{ta[:22]}' ts3='{tb[:22]}')")

    # ---- dashboard js: whole bytes, same side as .json twin ----
    side_js = 2  # default HEAD-side tie
    a, b = jload(2, "results/dashboard_status.json"), jload(3, "results/dashboard_status.json")
    ta, tb = wall_ts(a), wall_ts(b)
    side_js = 2 if (not tb or (ta and ta >= tb)) else 3
    with open("results/dashboard_status.js", "wb") as f:
        f.write(st(side_js, "results/dashboard_status.js"))
    log(f"[dashboard_status.js] whole-bytes same side as json twin :{side_js}: (R209)")

    # ---- compute_audit: history union on ts + latest take-new ----
    p = "results/compute_audit.json"
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    hmap = {}
    for row in ha + hb:
        hmap.setdefault(row.get("ts"), row)  # first-writer, same-ts dup collapses
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
        f"-> {len(trans)}; updated='{out.get('updated')}' state='{out.get('state')}'")

    # ---- parse-verify all written json (r185) ----
    ok = 0
    for p in snaps + [dj, "results/compute_audit.json", "results/regime_state.json"]:
        json.load(open(p, encoding="utf-8"))
        ok += 1
    js = open("results/dashboard_status.js", "rb").read()
    assert js.lstrip().startswith(b"window.DASH_DATA") and js.rstrip().endswith(b";"), \
        "js wrapper face broken (R209)"
    for p in all_files:
        blob = open(p, "rb").read()
        assert b"<<<<<<<" not in blob and b">>>>>>>" not in blob, f"conflict markers left in {p}"
    log(f"parse-verify: {ok} json OK + js wrapper face OK + 0 conflict markers in {len(all_files)} files")

    with io.open("results/_r354bmb_resolve.log", "w", encoding="utf-8",
                 newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("RESOLVER DONE -> _r354bmb_resolve.log")


if __name__ == "__main__":
    main()
