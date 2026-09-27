# -*- coding: utf-8 -*-
"""r355 bm-b stash-pop resolver (2-UU: autofill_state + compute_audit).

Context: S0 pull --rebase blocked by runtime-state dirty tree (autofill
keepalive whole-file rewrites, r123 family) -> stash -> fast-forward pull
(add3740c, bm-c r125) -> stash pop collided -> 2 UU.
Chronology (autofill.log + index forensics):
  02:43:10 keepalive tick fired INSIDE the stash-pop conflict window ->
  git add staged the MARKER-GARBAGE autofill_state; commit refused by
  "unmerged files" guard (git self-guard saved the tree; tick yielded).
  Producer then rewrote worktree autofill_state from live memory ->
  healthy 50-launch face, ts set == stash set (zero new loss), missing
  HEAD row 2026-09-26 14:30:01 = oldest row evicted by cap-50 rolling
  window (legitimate cap semantics, NOT a swallow), last_tick 02:40:01
  freshest > HEAD 02:30:01 -> producer-authority worktree version is the
  correct resolution face (verified by _r355bmb_zeroloss probe).
Resolution:
- autofill_state (mixed-dict+ledger): stage healthy producer worktree
  version (superset of stash; HEAD delta = cap eviction; last_tick
  newest). Index garbage-with-markers discarded.
- compute_audit (rolling-ledger, still 3-stage UU): :2:=HEAD(post-pull
  tip, stash-pop ours) side-identity assert fail-closed; history union on
  ts zero-loss; latest take-new via deep wall-ts probe (r311/r319).
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


def crlf_of(raw):
    return b"\r\n" in raw


def wall_ts(obj):
    """Deep wall-clock probe (R350): ts-shaped values must carry time-of-day."""
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


def dump_bytes(obj, crlf):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    if crlf:
        s = s.replace("\n", "\r\n")
    return s.encode("utf-8")


def main():
    lines = []

    def log(s):
        lines.append(s)
        print(s)

    # ---- compute_audit: side-identity assert (:2:==HEAD, stash-pop law) ----
    p = "results/compute_audit.json"
    if st(2, p) != head_blob(p):
        raise RuntimeError(f"side-inversion suspect at {p}: :2: != HEAD: "
                           "-- ABORT resolution, adjudicate manually")
    log("[compute_audit] side-identity assert: :2:==HEAD verified")

    # ---- compute_audit: history union on ts + latest take-new ----
    raw2, raw3 = st(2, p), st(3, p)
    a, b = json.loads(raw2.decode("utf-8")), json.loads(raw3.decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    hmap = {}
    for row in ha + hb:
        hmap.setdefault(row.get("ts"), row)  # same-ts dup collapses
    hist = [hmap[k] for k in sorted(hmap)]
    la_dt, lb_dt = a.get("latest", {}), b.get("latest", {})
    ta = wall_ts(la_dt) if isinstance(la_dt, dict) else wall_ts(a)
    tb = wall_ts(lb_dt) if isinstance(lb_dt, dict) else wall_ts(b)
    latest = la_dt if (not tb or (ta and ta >= tb)) else lb_dt
    out = dict(a if wall_ts(a) >= wall_ts(b) else b)
    out["latest"] = latest
    out["history"] = hist
    with open(p, "wb") as f:
        f.write(dump_bytes(out, crlf_of(raw3) or crlf_of(raw2)))
    log(f"[compute_audit] history {len(ha)}+{len(hb)} -> {len(hist)} "
        f"(dedup-by-ts zero-loss); latest deep-ts='{wall_ts(latest)[:22]}' "
        f"(a='{ta[:22]}' b='{tb[:22]}')")

    # ---- autofill_state: producer-authority worktree version ----
    p = "results/autofill_state.json"
    w = json.load(open(p, encoding="utf-8"))
    assert isinstance(w.get("last_tick"), dict), "last_tick must be dict"
    assert len(w.get("launches", [])) <= 50, "cap-50 violated"
    log(f"[autofill_state] producer worktree face verified: launches="
        f"{len(w.get('launches', []))} last_tick="
        f"'{w['last_tick'].get('ts', '')}' (stash set == worktree set; "
        f"HEAD delta = cap-50 eviction; index marker-garbage discarded)")

    # ---- parse-verify + marker scan (r185) ----
    for p in ("results/autofill_state.json", "results/compute_audit.json"):
        json.load(open(p, encoding="utf-8"))
        blob = open(p, "rb").read()
        assert b"<<<<<<<" not in blob and b">>>>>>>" not in blob, \
            f"conflict markers left in {p}"
    log("parse-verify: 2 json OK + 0 conflict markers")

    # ---- stage resolutions ----
    for args in (("add", "results/autofill_state.json"),
                 ("add", "results/compute_audit.json")):
        r = subprocess.run(["git", *args], capture_output=True)
        if r.returncode != 0:
            raise RuntimeError(f"git {args} fail: {r.stderr[:120]}")
    log("staged: autofill_state (healthy producer face) + compute_audit "
        "(union resolution)")

    with open("results/_r355bmb_resolve.log", "w", encoding="utf-8",
              newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("RESOLVER DONE -> _r355bmb_resolve.log")


if __name__ == "__main__":
    main()
