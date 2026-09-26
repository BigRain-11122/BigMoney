# -*- coding: utf-8 -*-
"""R258 bm-a push-collision rebase resolver (skill recipes, zero-loss).

Sides during rebase: :2 ours = origin/bm-b latest (landed first), :3 theirs =
bm-a c6a7607c (this round). Take-new/freshness decided by CONTENT ts fields
(probed per family, R242 law), never commit order; same-value tie -> ours/HEAD
(r140 law). Parse-verify before write-back (r185). Union ledgers zero-loss.
"""
import json
import subprocess
import sys

TS_KEYS = ["ts", "updated", "generated", "generated_at", "as_of",
           "last_attempt"]


def sh(*args):
    return subprocess.run(list(args), capture_output=True).stdout


def blob(stage, path):
    info = sh("git", "ls-files", "-u", "--", path).decode()
    line = [l for l in info.strip().split("\n")
            if l.split()[2] == str(stage) and l.split()[3] == path]
    if not line:
        return None
    return sh("git", "cat-file", "blob", line[0].split()[1])


def probe_ts(obj):
    """Return (key, value) of first non-None ts-family key, else (None, None)."""
    if not isinstance(obj, dict):
        return None, None
    for k in TS_KEYS:
        v = obj.get(k)
        if v is not None and not isinstance(v, (dict, list)):
            return k, v
    return None, None


def resolve_snapshot(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    ka, va = probe_ts(ja)
    kb, vb = probe_ts(jb)
    if va is None and vb is None:
        print(f"  {path}: both ts-absent -> UNKNOWN, manual"); return None
    if va is None:
        side = b
    elif vb is None:
        side = a
    else:
        side = a if va >= vb else b       # tie -> ours (r140)
    print(f"  {path}: take {'ours' if side is a else 'theirs'} "
          f"(ts {ka}={va} vs {kb}={vb})")
    return side


def eol_write(path, raw):
    with open(path, "wb") as f:
        f.write(raw)


def take(path, raw, note):
    eol_write(path, raw)
    json.loads(raw.decode("utf-8-sig"))     # parse-verify (r185)
    sh("git", "add", "--", path)
    print(f"  {path}: {note} -> staged")


def union_lists(la, lb, keyf):
    """Zero-loss union by key identity, preserving order (la then lb-new)."""
    seen = set(keyf(x) for x in la)
    out = list(la)
    for x in lb:
        k = keyf(x)
        if k not in seen:
            out.append(x)
            seen.add(k)
    return out


def resolve_compute_audit(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    ha, hb = ja.get("history", []), jb.get("history", [])
    keyf = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
    merged = union_lists(ha, hb, keyf)
    n0 = len(ha) + len(hb)
    base = ja if (ja.get("ts", "") or "") >= (jb.get("ts", "") or "") else jb
    base["history"] = merged
    print(f"  compute_audit: history union {len(ha)}|{len(hb)} -> {len(merged)} "
          f"(zero-loss vs {n0} means dupes were true dupes); fields take "
          f"ts={base.get('ts')}")
    return base


def resolve_regime(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    keyf = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
    out = dict(ja)
    for k in ("history", "transitions"):
        la, lb = ja.get(k, []), jb.get(k, [])
        merged = union_lists(la, lb, keyf)
        out[k] = merged
        print(f"  regime_state.{k}: {len(la)}|{len(lb)} -> {len(merged)}")
    # state fields take-new by ts
    ka, va = probe_ts(ja); kb, vb = probe_ts(jb)
    src = ja if (va or "") >= (vb or "") else jb
    for k, v in src.items():
        if k not in ("history", "transitions"):
            out[k] = v
    print(f"  regime_state fields take ts={probe_ts(src)[1]}")
    return out


def resolve_autofill(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    out = dict(ja)
    la = ja.get("launches", []); lb = jb.get("launches", [])
    keyf = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
    merged = union_lists(la, lb, keyf)
    # cap semantics: keep newest 50 by ts desc, then RE-SORT ts asc on
    # write-back (bm-b r245: producer append order, desc write = stuck spin)
    tsk = "ts"
    def _ts(r):
        for k in TS_KEYS:
            v = r.get(k) if isinstance(r, dict) else None
            if v:
                return v
        return ""
    merged.sort(key=_ts, reverse=True)
    merged = merged[:50]
    merged.sort(key=_ts)                      # ascending on write-back
    out["launches"] = merged
    ta, tb = ja.get("last_tick") or {}, jb.get("last_tick") or {}
    _, tsa = probe_ts(ta); _, tsb = probe_ts(tb)
    out["last_tick"] = ta if (tsa or "") >= (tsb or "") else tb
    assert isinstance(out["last_tick"], dict), "last_tick must be dict"
    print(f"  autofill: launches union->cap50->asc {len(la)}|{len(lb)} -> "
          f"{len(merged)}; last_tick ts {tsa} vs {tsb}")
    return out


def resolve_dashboard_js(path):
    a, b = blob(2, path), blob(3, path)
    ta = ta_ = json.loads(a.decode("utf-8-sig").split("=", 1)[1].rsplit(";", 1)[0])
    tb = json.loads(b.decode("utf-8-sig").split("=", 1)[1].rsplit(";", 1)[0])
    va = (ta.get("meta") or {}).get("generated_at")
    vb = (tb.get("meta") or {}).get("generated_at")
    side = a if (va or "") >= (vb or "") else b
    print(f"  dashboard_status.js: take {'ours' if side is a else 'theirs'} "
          f"(meta.generated_at {va} vs {vb}) whole bytes (wrapper intact)")
    return None, side          # raw bytes path


def resolve_daily_report_pair():
    jp = "docs/daily_report/REPORT-2026-09-26.json"
    mp = "docs/daily_report/REPORT-2026-09-26.md"
    a, b = blob(2, jp), blob(3, jp)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    va, vb = ja.get("generated_at"), jb.get("generated_at")
    if va is None and vb is None:
        print("  daily_report: generated_at absent both -> UNKNOWN manual"); return None, None
    json_side = a if (va or "") >= (vb or "") else b
    which = "ours" if json_side is a else "theirs"
    md_side = blob(2, mp) if json_side is a else blob(3, mp)
    print(f"  daily_report pair: json take {which} (generated_at {va} vs {vb}); "
          f"md same-side whole bytes (r242/R257 precedent)")
    return (jp, json_side), (mp, md_side)


def dump_json(obj, ref_raw):
    """Dump mirroring EOL + indent + ensure_ascii faces of reference blob
    (r245/R209 mirror-producer law: detection on raw bytes, write translated)."""
    txt_ref = ref_raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in txt_ref[:2000] else "\n"
    lines = txt_ref.split("\r\n" if eol == "\r\n" else "\n")
    ind = 1
    if len(lines) > 1 and lines[1].startswith(" "):
        ind = len(lines[1]) - len(lines[1].lstrip(" "))
    ascii_esc = "\\u" in txt_ref[:3000]
    txt = json.dumps(obj, ensure_ascii=ascii_esc, indent=ind)
    txt = txt.replace("\n", eol)
    if txt_ref.endswith("\n"):
        txt += eol
    return txt.encode("utf-8")


def main():
    raw_resolved = {}
    # rolling ledgers / mixed -> dict rebuilds
    for path, fn in ((("results/compute_audit.json"), resolve_compute_audit),
                     (("results/regime_state.json"), resolve_regime),
                     (("results/autofill_state.json"), resolve_autofill)):
        a = blob(2, path)
        obj = fn(path)
        raw = dump_json(obj, a)
        take(path, raw, "rebuilt union/take-new")
    # snapshots
    for path in ("results/dashboard_status.json",
                 "results/fundamental_b_layer_filter.json",
                 "results/futures_update_status.json",
                 "results/heat_update_status.json",
                 "results/lhb_update_status.json",
                 "results/token_usage.json",
                 "results/update_status.json"):
        raw = resolve_snapshot(path)
        if raw is None:
            print("ABORT: UNKNOWN snapshot, manual needed"); return 2
        take(path, raw, "take-new whole")
    # js wrapper whole bytes
    _, side = resolve_dashboard_js("results/dashboard_status.js")
    eol_write("results/dashboard_status.js", side)
    sh("git", "add", "--", "results/dashboard_status.js")
    print("  dashboard_status.js staged whole-bytes")
    # daily report pair UNKNOWN -> r242/R257 precedent manual classification
    jres, mres = resolve_daily_report_pair()
    if jres is None:
        print("ABORT: daily_report manual"); return 2
    take(jres[0], jres[1], "take-new generated_at")
    eol_write(mres[0], mres[1])
    sh("git", "add", "--", mres[0])
    print("  daily md staged same-side")
    # verify no UU remains
    st = sh("git", "status", "--porcelain").decode()
    uu = [l for l in st.split("\n") if l.startswith("UU") or l.startswith("AA")]
    print("remaining UU/AA:", uu)
    return 0 if not uu else 2


if __name__ == "__main__":
    sys.exit(main())
