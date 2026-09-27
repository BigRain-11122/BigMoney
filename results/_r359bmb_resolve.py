# -*- coding: utf-8 -*-
"""r359 bm-b rebase UU resolver: 15 files, classifier GREEN 0 UNKNOWN.

Recipes per bigmoney-conflict-resolve SKILL.md:
- snapshots: take-new via hardened deep-ts probe on STAGED blobs
  (:2: = upstream-landed side, :3: = mine r359) -- r100 key-normalize
  (strip _/- before prefix match), R350 wall-clock values require
  time-of-day, key-exclude lists forbidden, value must be ^20\\d{2}- shaped;
  tie -> HEAD (:2:) per r140.
- rolling-ledgers (compute_audit / regime_state): union list-of-dict keys
  by canonical row (zero loss, |A u B|), state fields from fresher side.
- daily_report twins (.json + .md): SAME side, decided once via the .json.
- dashboard_status.js: take-side whole bytes (js wrapper, R209) side bound
  to its .json twin.
Parse-verify before write-back + add (r185 law).
"""
import json
import re
import subprocess
import sys

TS_SHAPE = re.compile(r"^20\d{2}-\d{2}-\d{2}([T ]\d{2}:\d{2})")
KEY_MARKS = ("generated", "updated", "ts", "asof", "clock", "lastseen",
             "checked", "written")


def blob(side, path):
    r = subprocess.run(["git", "show", f":{side}:{path}"],
                        capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj):
    """Max wall-clock timestamp (values must carry time-of-day, R350)."""
    best = None

    def scan(o):
        nonlocal best
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, str):
                    kn = str(k).replace("_", "").replace("-", "").lower()
                    if any(m in kn for m in KEY_MARKS):
                        m = TS_SHAPE.match(v.strip())
                        if m and m.group(1) and (best is None or v > best):
                            best = v.strip()
                scan(v)
        elif isinstance(o, list):
            for it in o:
                scan(it)

    scan(obj)
    return best


def jside(side, path):
    return json.loads(blob(side, path).decode("utf-8"))


def take_new(path):
    a, b = jside(2, path), jside(3, path)
    pa, pb = deep_ts(a), deep_ts(b)
    side = 2 if (pa or "") >= (pb or "") else 3   # tie -> HEAD/:2: (r140)
    raw = blob(side, path)
    json.loads(raw.decode("utf-8"))               # parse-verify (r185)
    with open(path, "wb") as fh:
        fh.write(raw)
    subprocess.run(["git", "add", path], check=True)
    print(f"  [{path}] take :{side}: (up ts {pa!r} vs my ts {pb!r})")


def take_new_pair(json_path, md_path):
    a, b = jside(2, json_path), jside(3, json_path)
    pa, pb = deep_ts(a), deep_ts(b)
    side = 2 if (pa or "") >= (pb or "") else 3
    for p in (json_path, md_path):                # twins SAME side (r98)
        raw = blob(side, p)
        if p.endswith(".json"):
            json.loads(raw.decode("utf-8"))
        else:
            assert b"<<<<<<<" not in raw and raw.strip()
        with open(p, "wb") as fh:
            fh.write(raw)
        subprocess.run(["git", "add", p], check=True)
    print(f"  [{json_path} + twins] take :{side}: ({pa!r} vs {pb!r})")


def resolve_rolling(path):
    a, b = jside(2, path), jside(3, path)
    pa, pb = deep_ts(a), deep_ts(b)
    base = a if (pa or "") >= (pb or "") else b   # state fields fresher side
    out = dict(base)
    for k in base:
        va, vb = a.get(k), b.get(k)
        if isinstance(va, list) and isinstance(vb, list) and va and vb \
                and isinstance(va[0], dict) and isinstance(vb[0], dict):
            rows = {}
            for r in va:
                rows[json.dumps(r, sort_keys=True, ensure_ascii=False)] = r
            for r in vb:
                rows.setdefault(json.dumps(r, sort_keys=True,
                                           ensure_ascii=False), r)
            merged = list(rows.values())
            if merged and all("ts" in r for r in merged):
                merged.sort(key=lambda r: str(r["ts"]))
            out[k] = merged
            print(f"  [{path}:{k}] union {len(va)}+{len(vb)} -> "
                  f"{len(merged)} rows zero-loss")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    json.load(open(path, encoding="utf-8"))       # parse-verify (r185)
    subprocess.run(["git", "add", path], check=True)
    print(f"  [{path}] rolling resolved (state side "
          f"{':2:' if (pa or '') >= (pb or '') else ':3:'})")


def resolve_js(json_twin, js_path):
    a, b = jside(2, json_twin), jside(3, json_twin)
    pa, pb = deep_ts(a), deep_ts(b)
    side = 2 if (pa or "") >= (pb or "") else 3
    raw = blob(side, js_path)
    txt = raw.decode("utf-8")
    assert txt.lstrip().startswith("window.DASH_DATA") and "};" in txt
    with open(js_path, "wb") as fh:
        fh.write(raw)
    subprocess.run(["git", "add", js_path], check=True)
    print(f"  [{js_path}] take :{side}: whole bytes (R209, twin-bound)")


print("== r359 resolve start ==")
up = subprocess.run(["git", "log", "--oneline", "-2", "HEAD"],
                    capture_output=True, text=True).stdout.strip()
print("rebase base head:\n" + up)

take_new_pair("docs/daily_report/REPORT-2026-09-28.json",
              "docs/daily_report/REPORT-2026-09-28.md")
resolve_rolling("results/compute_audit.json")
for p in ("results/daily_scorecard.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json", "results/token_usage.json",
          "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json",
          "results/lhb_update_status.json",
          "results/prospect_promotion/_summary.json",
          "results/update_status.json", "results/dashboard_status.json"):
    take_new(p)
resolve_js("results/dashboard_status.json", "results/dashboard_status.js")
resolve_rolling("results/regime_state.json")

st = subprocess.run(["git", "status", "--short"], capture_output=True,
                    text=True).stdout
uu = [ln for ln in st.splitlines() if "UU" in ln or "AA" in ln]
print(f"remaining UU/AA: {len(uu)} {uu[:5]}")
assert not uu, "unresolved conflicts remain"
print("== r359 resolve complete: 15 files, parse-verified, staged ==")
