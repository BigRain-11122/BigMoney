# -*- coding: utf-8 -*-
"""r817 bm-b push-storm resolve (rebase pick-1 UU set, origin=bm-c r828 window).

Canonical recipes per bigmoney-conflict-resolve classifier (evidence:
results/_r817bmb_classify.json -- 7 classified + 8 UNKNOWN hand-classified
per SKILL.md table):
  rolling-ledger union (compute_audit/regime_state, r188/R208) |
  snapshot take-new by ts, tie->ours/HEAD (R208/R216, r140) |
  same-day idempotent regen docs = newest generated wins (T-75/T-105 law) |
  tech.md = append-union (records in ts order) + table-row status union.
Rebase stage mapping: :2 = ours = origin/bm-c side, :3 = theirs = bm-b side.
Zero-loss asserts inline (r185 parse-before-write; r140 same-second tie=HEAD)."""
import json
import re
import subprocess
import sys

FAIL = []


def stage_bytes(n, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show :%d:%s rc=%d" % (n, path, r.returncode))
    return r.stdout


def stage_json(n, path):
    return json.loads(stage_bytes(n, path).decode("utf-8"))


def write_bytes(path, b):
    with open(path, "wb") as f:
        f.write(b)


def take_side(path, side, why):
    b = stage_bytes(2 if side == "ours" else 3, path)
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))  # r185: parse-validate before write
    write_bytes(path, b)
    print("[take-%s] %s (%s)" % (side, path, why))


def newer_side(js_path, ts_key):
    a, b = stage_json(2, js_path), stage_json(3, js_path)
    ta, tb = str(a.get(ts_key) or ""), str(b.get(ts_key) or "")
    side = "theirs" if tb > ta else "ours"  # same-second tie -> ours (r140 HEAD law)
    return side, ta, tb


# ---------- snapshots (classifier R208/R216) ----------
for p, k in [("results/_attrition_guard_scan.json", "ts"),
             ("results/fundamental_b_layer_filter.json", "updated"),
             ("results/futures_update_status.json", "ts"),
             ("results/lhb_update_status.json", "updated"),
             ("results/token_usage.json", "generated"),
             ("results/update_status.json", "updated"),
             ("docs/daily_report/REPORT-2026-10-10.json", "generated_at"),
             ("docs/live_usage/LIVE-2026-10-10.json", "generated"),
             ("docs/live_usage/LIVE-latest.json", "generated")]:
    side, ta, tb = newer_side(p, k)
    take_side(p, side, "%s ours=%s theirs=%s" % (k, ta, tb))

# md twins follow their json side (same regen run wrote both)
for md, js in [("docs/daily_report/REPORT-2026-10-10.md", "docs/daily_report/REPORT-2026-10-10.json"),
               ("docs/live_usage/LIVE-2026-10-10.md", "docs/live_usage/LIVE-2026-10-10.json"),
               ("docs/live_usage/LIVE-latest.md", "docs/live_usage/LIVE-latest.json")]:
    side, ta, tb = newer_side(js, "generated_at" if "REPORT" in js else "generated")
    take_side(md, side, "md twin follows json side (%s %s/%s)" % (js, ta, tb))

# ---------- rolling-ledger: compute_audit.json (history union by ts; latest take-new) ----------
a, b = stage_json(2, "results/compute_audit.json"), stage_json(3, "results/compute_audit.json")
ha, hb = a.get("history") or [], b.get("history") or []
seen = {}
for row in ha:
    seen[str(row.get("ts"))] = row          # ours first = HEAD-side tie law
for row in hb:
    k = str(row.get("ts"))
    if k not in seen:
        seen[k] = row
merged_hist = [seen[k] for k in sorted(seen)]
latest = a.get("latest") if str((a.get("latest") or {}).get("ts", "")) >= \
    str((b.get("latest") or {}).get("ts", "")) else b.get("latest")
ca = {"history": merged_hist, "latest": latest}
json.loads(json.dumps(ca))  # roundtrip validate
write_bytes("results/compute_audit.json", json.dumps(ca, ensure_ascii=False, indent=1).encode("utf-8"))
n_a, n_b = len(ha), len(hb)
if len(merged_hist) < max(n_a, n_b):
    FAIL.append("compute_audit union loss")
print("[union] results/compute_audit.json history %d+%d -> %d rows; latest.ts=%s"
      % (n_a, n_b, len(merged_hist), (latest or {}).get("ts")))

# ---------- rolling-ledger: regime_state.json (history by asof; transitions/triggers row union; scalars take-new) ----------
a, b = stage_json(2, "results/regime_state.json"), stage_json(3, "results/regime_state.json")


def union_rows(la, lb, idf):
    seen = {}
    for r in la:
        seen[idf(r)] = r
    for r in lb:
        k = idf(r)
        if k not in seen:
            seen[k] = r
    return list(seen.values())


rs = dict(a)  # ours = base (HEAD-side tie law on scalars)
rs["history"] = union_rows(a.get("history") or [], b.get("history") or [],
                           lambda r: str(r.get("asof")))
rs["transitions"] = union_rows(a.get("transitions") or [], b.get("transitions") or [],
                              lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
rs["triggers"] = union_rows(a.get("triggers") or [], b.get("triggers") or [],
                           lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
if str(b.get("updated") or "") > str(a.get("updated") or ""):
    for k in b:
        if k not in ("history", "transitions", "triggers"):
            rs[k] = b[k]
json.loads(json.dumps(rs))
write_bytes("results/regime_state.json", json.dumps(rs, ensure_ascii=False, indent=1).encode("utf-8"))
print("[union] results/regime_state.json history %d/%d transitions %d/%d triggers %d/%d; updated=%s"
      % (len(a.get("history") or []), len(rs["history"]),
         len(a.get("transitions") or []), len(rs["transitions"]),
         len(a.get("triggers") or []), len(rs["triggers"]), rs.get("updated")))

# ---------- tech.md: append-union records (ts order) + table-row status union ----------
a_txt = stage_bytes(2, "state/queue/tech.md").decode("utf-8")
b_txt = stage_bytes(3, "state/queue/tech.md").decode("utf-8")
out = a_txt
for row_id in ("T9", "T10"):
    m_b = re.search(r"^\| %s \|.*$" % row_id, b_txt, re.M)
    m_a = re.search(r"^\| %s \|.*$" % row_id, out, re.M)
    if m_b and m_a and m_b.group(0).rstrip().endswith("| done |") and not \
            m_a.group(0).rstrip().endswith("| done |"):
        out = out[:m_a.start()] + m_b.group(0) + out[m_a.end():]
        print("[row-union] tech.md %s -> done (bm-b side row adopted)" % row_id)
new_recs = [ln for ln in b_txt.splitlines()
            if ln.startswith("> r817 ") and ln not in a_txt.splitlines()]
if new_recs:
    m828 = re.search(r"^> r828 .*$", out, re.M)
    ins = "\n".join(new_recs)
    if m828:
        out = out[:m828.start()] + ins + "\n" + out[m828.start():]
        print("[append-union] tech.md r817 record inserted before r828 (ts order)")
    else:
        out = out.rstrip("\n") + "\n" + ins + "\n"
        print("[append-union] tech.md r817 record appended (no r828 anchor)")
write_bytes("state/queue/tech.md", out.encode("utf-8"))

if FAIL:
    print("RESOLVE FAIL:", FAIL)
    sys.exit(1)
print("r817 resolve OK: 15 UU files resolved (7 classifier recipes + 8 hand-classified)")
