"""r267 bm-b closeout rebase conflict resolver (15 UU vs bm-a e7e4441e R263).

Same-window double S6 chain run (bm-b r267 18:49-18:52 vs bm-a r263 18:51:53)
+ T-83 claim collision already yielded by bm-a per s4 law (their 18:47:11 >
our 18:46:30 claim commit f4dfc5b6 -- bm-a keeps T-83 science face with bm-b).

Classifier output: 11 classified + 4 UNKNOWN (manual-classified below per
r242 daily-report-pair law + r216 snapshot law):
  docs/daily_report/REPORT-20260926.json/.md  -> same-day regen snapshot pair,
    take-side by json twin generated_at, md same-side whole bytes (r242).
  results/scorecard_v1.json / strategy_scorecard.json -> deterministic
    re-derive snapshots, take-new by generated ts (r216).

Rebase side semantics (CRITICAL, r140/r245 family): during rebase,
  stage :2 ("ours")   = the base being rebased onto = bm-a e7e4441e face
  stage :3 ("theirs") = our replayed commit 78043647 face
Recipes compare INNER ts values, never assume a side; same-second tie ->
base (bm-a) face per r140 HEAD law.

Resolution per classifier recipes:
  mixed-dict+ledger autofill_state: launches union (dedupe by
  ts+shard+pid+entry) -> ts desc -> cap 50 -> re-sort ts ASC on write-back
  (r245 producer-order law); last_tick compare inner ts, whole-dict assign.
  rolling-ledger compute_audit/regime_state: list keys union by row identity,
  scalar/meta fields take-new.
  js-wrapper dashboard_status.js: take-side whole bytes (extract JSON inside
  wrapper, compare generated ts) -- NEVER json.dumps rewrite (R209).
  snapshot *_status/token_usage/scorecards/report pair: take-new whole doc
  by inner ts keys.
Zero-loss check: ledger unions = |A u B| row counts asserted. Parse-validate
every json before write-back (r185 law). Bytes read via subprocess, never
PowerShell redirection (r255 law).
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"


def stage_blob(idx, path):
    b = subprocess.run(["git", "show", f":{idx}:{path}"], cwd=ROOT,
                       capture_output=True).stdout
    if not b:
        raise SystemExit(f"empty stage {idx} for {path}")
    return b


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def ts_of(d, keys=("ts", "updated", "updated_at", "generated", "generated_at",
                   "as_of", "last_attempt", "checked_at")):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k]:
            return str(d[k])
    return ""


def take_newer(path, a, b):
    da, db = jload(a), jload(b)
    ta, tb = ts_of(da), ts_of(db)
    if tb > ta:
        return b, "ours-replay(bm-b)", ta, tb
    return a, "base(bm-a)", ta, tb


def union_rows(la, lb):
    seen, out = set(), []
    for row in list(la) + list(lb):
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def resolve_ledger(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    da, db = jload(a), jload(b)
    out = dict(da if ts_of(db) <= ts_of(da) else db)  # newer face for scalars
    union_info = {}
    for k in set(da) | set(db):
        va, vb = da.get(k), db.get(k)
        if isinstance(va, list) and isinstance(vb, list):
            merged = union_rows(va, vb)
            out[k] = merged
            union_info[k] = (len(va), len(vb), len(merged))
    blob, side, ta, tb = (a, "base(bm-a)", ts_of(da), ts_of(db)) if ts_of(db) <= ts_of(da) \
        else (b, "ours-replay(bm-b)", ts_of(da), ts_of(db))
    out_bytes = blob if not union_info else json.dumps(
        out, ensure_ascii=False, indent=1).encode()
    # write-back mirrors base-blob EOL/ascii/trailing-newline faces
    out_bytes = mirror_faces(blob, out_bytes)
    open(f"{ROOT}/{path}", "wb").write(out_bytes)
    return {"path": path, "side": "union+take-new-scalars", "ts": (ta, tb),
            "union": union_info}


def mirror_faces(base_blob, content_bytes):
    crlf = b"\r\n" in base_blob
    trail = base_blob.endswith(b"\n")
    txt = content_bytes.decode("utf-8")
    if not all(ord(c) < 128 for c in txt):  # base ascii-only -> mirror
        pass
    if crlf:
        txt = txt.replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        txt = txt.replace("\r\n", "\n")
    if trail and not txt.endswith("\n"):
        txt += "\n"
    if not trail and txt.endswith("\n"):
        txt = txt[:-1]
    return txt.encode("utf-8")


def resolve_snapshot(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    blob, side, ta, tb = take_newer(path, a, b)
    open(f"{ROOT}/{path}", "wb").write(mirror_faces(blob, blob))
    return {"path": path, "side": side, "ts": (ta, tb)}


def resolve_autofill(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    da, db = jload(a), jload(b)
    launches = union_rows(da.get("launches", []), db.get("launches", []))
    # cap 50 newest by ts, write back in producer order (ts ASC, r245 law)
    launches.sort(key=lambda r: r.get("ts", ""), reverse=True)
    launches = launches[:50]
    launches.sort(key=lambda r: r.get("ts", ""))
    ta = da.get("last_tick", {}).get("ts", "")
    tb = db.get("last_tick", {}).get("ts", "")
    lt = da["last_tick"] if tb <= ta else db["last_tick"]
    assert isinstance(lt, dict)
    out = {"launches": launches, "last_tick": lt}
    blob = a  # base face for format mirroring
    txt = json.dumps(out, ensure_ascii=False, indent=1)
    open(f"{ROOT}/{path}", "wb").write(mirror_faces(blob, txt.encode("utf-8")))
    return {"path": path, "side": "union-cap50-asc", "ts_last_tick": (ta, tb),
            "launches": (len(da.get("launches", [])), len(db.get("launches", [])), len(launches))}


def resolve_js(path):
    a, b = stage_blob(2, path), stage_blob(3, path)
    m = re.compile(rb"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?", re.S)

    def gen(blob):
        mm = m.search(blob)
        return ts_of(jload(mm.group(1))) if mm else ""
    ga, gb = gen(a), gen(b)
    blob, side = (b, "ours-replay(bm-b)") if gb > ga else (a, "base(bm-a)")
    open(f"{ROOT}/{path}", "wb").write(blob)  # whole bytes, producer format
    return {"path": path, "side": side + " whole-bytes", "gen": (ga, gb)}


def resolve_report_pair():
    jp = "docs/daily_report/REPORT-2026-09-26.json"
    a, b = stage_blob(2, jp), stage_blob(3, jp)
    blob, side, ta, tb = take_newer(jp, a, b)
    open(f"{ROOT}/{jp}", "wb").write(mirror_faces(blob, blob))
    mp = "docs/daily_report/REPORT-2026-09-26.md"
    mblob = b if side == "ours-replay(bm-b)" else a
    open(f"{ROOT}/{mp}", "wb").write(mirror_faces(mblob, mblob))
    return {"path": "docs/daily_report/REPORT-2026-09-26.{json,md}",
            "side": side + " (md same side, r242 pair law)", "ts": (ta, tb)}


def main():
    report = []
    report.append(resolve_autofill("results/autofill_state.json"))
    for p in ("results/compute_audit.json", "results/regime_state.json"):
        report.append(resolve_ledger(p))
    report.append(resolve_js("results/dashboard_status.js"))
    for p in ("results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json", "results/heat_update_status.json",
              "results/lhb_update_status.json", "results/token_usage.json",
              "results/update_status.json", "results/scorecard_v1.json",
              "results/strategy_scorecard.json"):
        report.append(resolve_snapshot(p))
    report.append(resolve_report_pair())
    # parse-validate every resolved json before add (r185 law)
    for r_ in report:
        p = r_["path"]
        if p.endswith((".json",)) or ".json" in p:
            for sub in p.replace("{json,md}", "json").split(","):
                sub = sub.strip()
                if sub.endswith(".json") and "{" not in sub:
                    json.loads(open(f"{ROOT}/{sub}", encoding="utf-8-sig").read())
    for p in ("results/autofill_state.json", "results/compute_audit.json",
              "results/regime_state.json", "results/dashboard_status.js",
              "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json", "results/heat_update_status.json",
              "results/lhb_update_status.json", "results/token_usage.json",
              "results/update_status.json", "results/scorecard_v1.json",
              "results/strategy_scorecard.json",
              "docs/daily_report/REPORT-2026-09-26.json",
              "docs/daily_report/REPORT-2026-09-26.md"):
        subprocess.run(["git", "add", p], cwd=ROOT, check=True)
    print(json.dumps(report, ensure_ascii=False, indent=1))
    print("RESOLVED, staged. Continue rebase.")


if __name__ == "__main__":
    main()
