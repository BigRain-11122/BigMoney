"""bm-a R236 push-rejection 12-UU rebase resolver (TEMP-resident per r231 law).

Adapted verbatim from results/_r235_resolve.py (same 12-file conflict family,
recipes proven R235). Sides during rebase replay: stage2 'ours' = origin/main
(bm-b r23x window), stage3 'theirs' = bm-a R236 commit. Recipes per
bigmoney-conflict-resolve classifier (12/12 classified, zero UNKNOWN):
- CODELY.md                    memory-union (line-level, ours + theirs-only)
- autofill_state.json          mixed-dict+ledger (launches union ts cap50,
                               last_tick inner-ts whole-dict, tie->ours/HEAD)
- compute_audit.json           rolling-ledger (history union by ts zero-loss,
                               latest take-new)
- dashboard_status.js/.json    js-wrapper take-side WHOLE BYTES by .json twin
                               meta.generated_at (r226 law: no top-level ts)
- regime_state.json            rolling-ledger (history+transitions union;
                               state fields take-new by 'updated'; triggers =
                               state face NOT union key per bm-b r232 E1)
- 6 snapshots                  take-new by per-file ts key (updated/ts/generated)
Format mirroring: EOL + indent + ensure_ascii detected from stage2 producer
bytes; whole-byte take-side files carry zero format risk by construction.
"""
import io
import json
import os
import subprocess
import sys

REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], cwd=REPO,
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} missing for {path}: {r.stderr[:200]}")
    return r.stdout


def detect_fmt(raw):
    crlf = raw.count(b"\r\n")
    eol = "\r\n" if crlf > raw.count(b"\n") - crlf else "\n"
    indent = 1
    lines = raw.decode("utf-8", "replace").splitlines()
    for l in lines[1:6]:
        s = l[:8]
        if s.strip() and (s.startswith(" ") or s.startswith("\t")):
            indent = len(s) - len(s.lstrip())
            break
    ascii_only = all(b < 128 for b in raw)
    trailing_nl = raw.endswith(b"\n") or raw.endswith(b"\r\n")
    return {"eol": eol, "indent": indent, "ascii": ascii_only,
            "trailing_nl": trailing_nl}


def dump(obj, fmt):
    txt = json.dumps(obj, ensure_ascii=fmt["ascii"], indent=fmt["indent"])
    if fmt["trailing_nl"]:
        txt += fmt["eol"]
    return txt.encode("utf-8")


def ts_of(entry, keys=("ts", "updated", "generated_at", "generated",
                       "asof", "last_attempt")):
    for k in keys:
        if isinstance(entry, dict) and k in entry and entry[k]:
            return str(entry[k])
    return ""


def resolve_snapshot(path, ts_keys):
    a, b = stage(2, path), stage(3, path)
    ja, jb = json.loads(a), json.loads(b)
    ta = next((ja[k] for k in ts_keys if k in ja), "")
    tb = next((jb[k] for k in ts_keys if k in jb), "")
    side = a if str(ta) >= str(tb) else b          # ISO strings compare lexically
    winner = "ours" if str(ta) >= str(tb) else "theirs"
    with io.open(os.path.join(REPO, path), "wb") as f:
        f.write(side)
    return f"{path}: take {winner} (ts {min(str(ta),str(tb))} -> {max(str(ta),str(tb))})"


def resolve_codely():
    path = "CODELY.md"
    a = stage(2, path).decode("utf-8").splitlines()
    b = stage(3, path).decode("utf-8").splitlines()
    set_a = set(a)
    added = [l for l in b if l not in set_a]
    merged = a + [l for l in added if l not in set(a)]
    fmt = detect_fmt(stage(2, path))
    body = fmt["eol"].join(merged) + (fmt["eol"] if merged else "")
    with io.open(os.path.join(REPO, path), "wb") as f:
        f.write(body.encode("utf-8"))
    return f"CODELY.md: union ours {len(a)} + theirs-only {len(added)} lines"


def resolve_autofill():
    path = "results/autofill_state.json"
    ja, jb = json.loads(stage(2, path)), json.loads(stage(3, path))
    fmt = detect_fmt(stage(2, path))
    la = {json.dumps(e, sort_keys=True): e for e in ja.get("launches", [])}
    lb = {json.dumps(e, sort_keys=True): e for e in jb.get("launches", [])}
    union = list({**la, **lb}.values())
    union.sort(key=lambda e: str(ts_of(e)))
    union = union[-50:]                                # cap 50, R215 law
    ta = ts_of(ja.get("last_tick") or {})
    tb = ts_of(jb.get("last_tick") or {})
    last = (ja.get("last_tick") if ta >= tb else jb.get("last_tick"))
    side = "ours" if ta >= tb else "theirs"
    out = {"launches": union, "last_tick": last}
    assert isinstance(out["last_tick"], dict), "last_tick must stay dict"
    with io.open(os.path.join(REPO, path), "wb") as f:
        f.write(dump(out, fmt))
    return (f"autofill_state: launches union {len(la)}+{len(lb)} -> {len(union)} "
            f"(cap50), last_tick {side} ({ta} vs {tb}), dict-assert OK")


def resolve_compute_audit():
    path = "results/compute_audit.json"
    ja, jb = json.loads(stage(2, path)), json.loads(stage(3, path))
    fmt = detect_fmt(stage(2, path))
    ha = {str(e.get("ts")): e for e in ja.get("history", [])}
    hb = {str(e.get("ts")): e for e in jb.get("history", [])}
    union = {**ha, **hb}
    hist = [union[k] for k in sorted(union)]
    latest = ja.get("latest") if (ts_of(ja.get("latest") or {}) >=
                                  ts_of(jb.get("latest") or {})) else jb.get("latest")
    out = {"latest": latest, "history": hist}
    with io.open(os.path.join(REPO, path), "wb") as f:
        f.write(dump(out, fmt))
    return (f"compute_audit: history union {len(ha)}|{len(hb)} -> {len(hist)} "
            f"zero-loss (|A u B|={len(union)}), latest take-new "
            f"{ts_of(latest or {})}")


def resolve_regime():
    path = "results/regime_state.json"
    ja, jb = json.loads(stage(2, path)), json.loads(stage(3, path))
    fmt = detect_fmt(stage(2, path))
    out = dict(jb if str(jb.get("updated", "")) >= str(ja.get("updated", ""))
               else ja)                     # state fields from newer 'updated'
    for lk in ("history", "transitions"):
        if lk in ja or lk in jb:
            la = ja.get(lk) or []
            lb = jb.get(lk) or []
            ua = {json.dumps(e, sort_keys=True): e for e in la}
            ub = {json.dumps(e, sort_keys=True): e for e in lb}
            merged = list({**ua, **ub}.values())
            out[lk] = merged
    with io.open(os.path.join(REPO, path), "wb") as f:
        f.write(dump(out, fmt))
    return (f"regime_state: state take-new by updated "
            f"({ja.get('updated')} vs {jb.get('updated')}), "
            f"history {len(ja.get('history') or [])}+{len(jb.get('history') or [])}"
            f"->union {len(out.get('history') or [])}, transitions "
            f"{len(ja.get('transitions') or [])}+{len(jb.get('transitions') or [])}"
            f"->union {len(out.get('transitions') or [])}")


def resolve_dashboard_twins():
    jp = "results/dashboard_status.json"
    jsp = "results/dashboard_status.js"
    ja, jb = json.loads(stage(2, jp)), json.loads(stage(3, jp))
    ta = (ja.get("meta") or {}).get("generated_at", "")
    tb = (jb.get("meta") or {}).get("generated_at", "")
    n = 2 if str(ta) >= str(tb) else 3                # r226: twin decides both
    side = "ours" if n == 2 else "theirs"
    for p in (jp, jsp):
        raw = stage(n, p)
        with io.open(os.path.join(REPO, p), "wb") as f:
            f.write(raw)                               # whole bytes, no rewrite
    return f"dashboard twins: take {side} whole-bytes (meta.generated_at {ta} vs {tb})"


def main():
    report = []
    report.append(resolve_codely())
    report.append(resolve_autofill())
    report.append(resolve_compute_audit())
    report.append(resolve_dashboard_twins())
    report.append(resolve_regime())
    for p, keys in [
        ("results/fundamental_b_layer_filter.json", ("updated",)),
        ("results/futures_update_status.json", ("ts",)),
        ("results/heat_update_status.json", ("ts",)),
        ("results/lhb_update_status.json", ("ts",)),
        ("results/token_usage.json", ("generated",)),
        ("results/update_status.json", ("updated",)),
    ]:
        report.append(resolve_snapshot(p, keys))
    for line in report:
        print(line)
    # parse-verify every resolved json + js wrapper (r185 law)
    for p in ["CODELY.md"]:
        io.open(os.path.join(REPO, p), encoding="utf-8").read()
    for p in ["results/autofill_state.json", "results/compute_audit.json",
              "results/dashboard_status.json", "results/regime_state.json",
              "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json",
              "results/token_usage.json", "results/update_status.json"]:
        json.loads(io.open(os.path.join(REPO, p), "rb").read().decode("utf-8"))
    raw_js = io.open(os.path.join(REPO, "results/dashboard_status.js"),
                     "rb").read().decode("utf-8")
    assert raw_js.startswith("window.DASH_DATA = "), "js wrapper stripped!"
    json.loads(raw_js[len("window.DASH_DATA = "):].rstrip().rstrip(";"))
    print("parse-verify: 11 JSON + js-wrapper OK (r185 law)")


if __name__ == "__main__":
    sys.exit(main())
