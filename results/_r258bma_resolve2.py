# -*- coding: utf-8 -*-
"""R258 resolver pass 2: compute_audit latest take-new fix (nested latest.ts)
+ remaining snapshots (dashboard meta.generated_at probe) + js + daily pair.
Ours = HEAD (bm-b latest), theirs = REBASE_HEAD (c6a7607c mine)."""
import json
import subprocess
import sys

TS_KEYS = ["ts", "updated", "generated", "generated_at", "as_of",
           "last_attempt"]


def sh(*args):
    return subprocess.run(list(args), capture_output=True).stdout


def side_obj(rev, path):
    raw = sh("git", "show", f"{rev}:{path}")
    return raw, json.loads(raw.decode("utf-8-sig"))


def probe_ts(obj):
    """Root ts-family key; else meta.generated_at (R257 dashboard face)."""
    if not isinstance(obj, dict):
        return None, None
    for k in TS_KEYS:
        v = obj.get(k)
        if v is not None and not isinstance(v, (dict, list)):
            return k, v
    meta = obj.get("meta")
    if isinstance(meta, dict):
        v = meta.get("generated_at")
        if v is not None:
            return "meta.generated_at", v
    return None, None


def faces(ref_raw):
    txt = ref_raw.decode("utf-8-sig")
    eol = "\r\n" if "\r\n" in txt[:2000] else "\n"
    lines = txt.split("\r\n" if eol == "\r\n" else "\n")
    ind = 1
    if len(lines) > 1 and lines[1].startswith(" "):
        ind = len(lines[1]) - len(lines[1].lstrip(" "))
    return eol, ind, "\\u" in txt[:3000], txt.endswith("\n")


def dump(obj, ref_raw):
    eol, ind, asc, endnl = faces(ref_raw)
    txt = json.dumps(obj, ensure_ascii=asc, indent=ind).replace("\n", eol)
    if endnl:
        txt += eol
    return txt.encode("utf-8")


def union(la, lb):
    seen = set(json.dumps(x, sort_keys=True, ensure_ascii=False) for x in la)
    out = list(la)
    for x in lb:
        k = json.dumps(x, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            out.append(x)
            seen.add(k)
    return out


def take_bytes(path, raw, note):
    with open(path, "wb") as f:
        f.write(raw)
    sh("git", "add", "--", path)
    print(f"  {path}: {note} staged")


def main():
    # 1) compute_audit redo: latest take-new by latest.ts; history union ts-asc
    p = "results/compute_audit.json"
    ra, ja = side_obj("HEAD", p)
    rb, jb = side_obj("REBASE_HEAD", p)
    ta = (ja.get("latest") or {}).get("ts") or ""
    tb = (jb.get("latest") or {}).get("ts") or ""
    base = ja if ta >= tb else jb
    hist = union(ja.get("history", []), jb.get("history", []))
    hist.sort(key=lambda r: r.get("ts", ""))
    out = {"latest": base["latest"], "history": hist}
    print(f"  compute_audit: latest take {'ours' if base is ja else 'theirs'} "
          f"({ta} vs {tb}); history union ts-asc -> {len(hist)}")
    take_bytes(p, dump(out, ra), "rebuilt (latest fix + ts-asc union)")
    json.loads(open(p, encoding="utf-8-sig").read())          # parse-verify

    # 2) snapshots with meta probe
    for p in ("results/dashboard_status.json", "results/update_status.json",
              "results/token_usage.json",
              "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json"):
        ra, ja = side_obj("HEAD", p)
        rb, jb = side_obj("REBASE_HEAD", p)
        ka, va = probe_ts(ja)
        kb, vb = probe_ts(jb)
        if va is None and vb is None:
            print(f"  {p}: UNKNOWN both-absent -> ABORT"); return 2
        raw, which = (ra, "ours") if (va or "") >= (vb or "") else (rb, "theirs")
        print(f"  {p}: take {which} ({ka}={va} vs {kb}={vb})")
        take_bytes(p, raw, f"take-new {which}")
        json.loads(raw.decode("utf-8-sig"))                     # parse-verify

    # 3) dashboard_status.js whole bytes by meta.generated_at
    p = "results/dashboard_status.js"
    ra = sh("git", "show", f"HEAD:{p}")
    rb = sh("git", "show", f"REBASE_HEAD:{p}")
    va = json.loads(ra.decode("utf-8-sig").split("=", 1)[1].rsplit(";", 1)[0])["meta"]["generated_at"]
    vb = json.loads(rb.decode("utf-8-sig").split("=", 1)[1].rsplit(";", 1)[0])["meta"]["generated_at"]
    raw, which = (ra, "ours") if va >= vb else (rb, "theirs")
    print(f"  dashboard_status.js: take {which} whole bytes "
          f"(meta.generated_at {va} vs {vb})")
    take_bytes(p, raw, f"whole-bytes {which}")

    # 4) daily_report pair: json generated_at decides, md same side
    jp = "docs/daily_report/REPORT-2026-09-26.json"
    mp = "docs/daily_report/REPORT-2026-09-26.md"
    ra, ja = side_obj("HEAD", jp)
    rb, jb = side_obj("REBASE_HEAD", jp)
    va, vb = ja.get("generated_at"), jb.get("generated_at")
    if va is None and vb is None:
        print("  daily_report: generated_at absent both -> ABORT"); return 2
    raw, which = (ra, "ours") if (va or "") >= (vb or "") else (rb, "theirs")
    print(f"  daily_report.json: take {which} (generated_at {va} vs {vb})")
    take_bytes(jp, raw, f"take-new {which}")
    mraw = sh("git", "show", f"{'HEAD' if which == 'ours' else 'REBASE_HEAD'}:{mp}")
    take_bytes(mp, mraw, f"same-side {which} whole bytes")

    st = sh("git", "status", "--porcelain").decode()
    uu = [l for l in st.split("\n") if l[:2] in ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
    print("remaining conflict states:", uu)
    return 0 if not uu else 2


if __name__ == "__main__":
    sys.exit(main())
