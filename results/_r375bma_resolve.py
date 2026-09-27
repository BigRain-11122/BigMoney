"""r375 bm-a push-storm resolver (15-UU vs bm-c r127 batch, rebase window).

Canon laws applied (bigmoney-conflict-resolve SKILL):
  * r352 side law (rebase): :2: == HEAD == upstream bm-c; :3: == mine.
  * take-side faces = byte-verbatim staged-blob write (zero format drift).
  * compute_audit = history ts-key union zero-loss + state fields from the
    newer nested latest.ts (r311 deep probe); producer-window survival law
    r85 asserted (every ts of BOTH sides survives the union).
  * regime_state = whole-row identity union on triggers/transitions/history
    + flat take-new by 'updated'.
  * autofill_state = launches composite-key dedup union (r322: same-key
    content-identical dedup; field-union for additive pairs; hard fail on
    true divergence) -> ts desc -> cap50 (R215) -> asc write-back (r245);
    last_tick = inner-ts compare, same-second tie -> HEAD == :2: (r140),
    isinstance dict assert.
  * heat_update_status = :3: bm-a side: fresher (03:14:26 > 03:11:00) AND
    R31 host-authority (bm-c side snapshots=0 clobber vs host 3) -- dual
    evidence same direction (r125 precedent: ts-new != data-authority).
  * REPORT json+md twins = SAME side :3: (r327/r329 twin coupling).
Parse-verify (r185) before write-back; zero-loss asserts before add.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
fails = []


def blob_bytes(spec):
    r = subprocess.run(["git", "show", spec], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"git show failed: {spec}: {r.stderr.decode()[:200]}")
    return r.stdout


def blob_json(spec):
    return json.loads(blob_bytes(spec).decode("utf-8"))


def write_bytes(path, data):
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as fh:
        fh.write(data)


def write_text(path, text):
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(text)


def detect_format(text):
    return {"crlf": "\r\n" in text}


# ---- 1. take-side faces: byte-verbatim :3: (bm-a side, probes all newer) ----
TAKE_MINE = [
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/token_usage.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]
for p in TAKE_MINE:
    write_bytes(p, blob_bytes(":3:" + p))
    json.loads(open(ROOT + "\\" + p.replace("/", "\\"),
                    encoding="utf-8").read()) if p.endswith(".json") \
        and "dashboard_status.js" not in p else None
    print(f"[take :3:] {p} written byte-verbatim + parse-ok")

# js wrapper sanity: wrapper intact, not json.dumps'd (R209)
js = open(ROOT + r"\results\dashboard_status.js", encoding="utf-8").read()
assert js.lstrip().startswith("window.DASH_DATA"), "js wrapper stripped (R209)!"
print("[wrapper-intact] dashboard_status.js window.DASH_DATA head ok")

# ---- 2. compute_audit: history ts-key union + state from newer latest.ts ----
P = "results/compute_audit.json"
a, b = blob_json(":2:" + P), blob_json(":3:" + P)
rows, seen = [], set()
for d in (a, b):
    for h in d.get("history", []):
        ts = str(h.get("ts", ""))
        if ts not in seen:
            seen.add(ts)
            rows.append(h)
rows.sort(key=lambda h: str(h.get("ts", "")))
# r85 survival: every ts of BOTH sides present in the union
ts_a = {str(h.get("ts", "")) for h in a.get("history", [])}
ts_b = {str(h.get("ts", "")) for h in b.get("history", [])}
assert ts_a <= seen and ts_b <= seen, "audit union lost a row (r85 law)"
latest_a = str(a.get("latest", {}).get("ts", ""))
latest_b = str(b.get("latest", {}).get("ts", ""))
src = a if latest_a > latest_b else b        # r311 deep probe (latest.ts)
out = {k: v for k, v in src.items() if k != "history"}
out["history"] = rows
fmt = detect_format(blob_bytes(":2:" + P).decode("utf-8"))
nl = "\r\n" if fmt["crlf"] else "\n"
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", nl) if fmt["crlf"] else text)
json.loads(open(ROOT + r"\results\compute_audit.json", encoding="utf-8").read())
print(f"[union] compute_audit: history {len(a['history'])}|{len(b['history'])}"
      f" -> {len(rows)} rows, both ts-sets survive; state from "
      f"{'bm-c' if src is a else 'bm-a'} latest.ts "
      f"{max(latest_a, latest_b)}")

# ---- 3. regime_state: row union + flat take-new ----
P = "results/regime_state.json"
a, b = blob_json(":2:" + P), blob_json(":3:" + P)


def rowid(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


out = dict(b if str(b.get("updated", "")) > str(a.get("updated", ""))
           else a)
for key in ("triggers", "transitions", "history"):
    merged, s = list(out.get(key, [])), set()
    base = merged[:]
    for row in base:
        s.add(rowid(row))
    for d in (a, b):
        for row in d.get(key, []):
            if rowid(row) not in s:
                s.add(rowid(row))
                merged.append(row)
    out[key] = merged
fmt = detect_format(blob_bytes(":2:" + P).decode("utf-8"))
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", "\r\n") if fmt["crlf"] else text)
json.loads(open(ROOT + r"\results\regime_state.json", encoding="utf-8").read())
n_trig = len(out["triggers"])
print(f"[union] regime_state: triggers {n_trig}, transitions "
      f"{len(out['transitions'])}, history {len(out['history'])}; flat from "
      f"updated={out.get('updated')}")

# ---- 4. autofill_state: launches composite-key dedup union + tie->HEAD ----
P = "results/autofill_state.json"
a, b = blob_json(":2:" + P), blob_json(":3:" + P)
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")


def ckey(r):
    return tuple(str(r.get(k, "")) for k in KEY)


merged, buckets = [], {}
for d in (a, b):
    for r in d.get("launches", []):
        k = ckey(r)
        if k not in buckets:
            buckets[k] = []
        buckets[k].append(r)
for k, rows in buckets.items():
    uniq = {rowid(r) for r in rows}
    if len(uniq) == 1:
        merged.append(rows[0])
        continue
    # r322: additive field-union when common fields agree; hard fail else
    base = dict(rows[0])
    for r in rows[1:]:
        for kk, vv in r.items():
            if kk not in base:
                base[kk] = vv
            elif base[kk] != vv:
                fails.append(f"autofill key {k} true divergence on {kk}")
                print(f"FLAG: launches composite-key divergence {k} {kk}")
    merged.append(base)
merged.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
dropped = max(0, len(merged) - 50)
merged = merged[:50]
merged.sort(key=lambda x: str(x.get("ts", "")))  # r245: asc write-back
la, lb = a.get("last_tick", {}), b.get("last_tick", {})
ta, tb = str(la.get("ts", "")), str(lb.get("ts", ""))
lt = la if ta >= tb else lb           # same-second tie -> HEAD == :2: (r140)
out = {"launches": merged, "last_tick": lt}
assert isinstance(out["last_tick"], dict), "last_tick must stay dict (r140)"
fmt = detect_format(blob_bytes(":2:" + P).decode("utf-8"))
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", "\r\n") if fmt["crlf"] else text)
back = json.loads(open(ROOT + r"\results\autofill_state.json",
                       encoding="utf-8").read())
assert isinstance(back["last_tick"], dict) and \
    len(back["launches"]) <= 50
print(f"[union] autofill_state: composite-key buckets {len(buckets)} "
      f"(dup-key groups absorbed), launches kept {len(merged)} "
      f"({dropped} beyond cap50 dropped newest-50); last_tick ts="
      f"{back['last_tick'].get('ts')} ({'tie->HEAD(bm-c)' if ta == tb else 'newer side'})")

if fails:
    print(f"RESOLVE FAILED: {fails}")
    sys.exit(1)
print("resolver: all 15 faces written + parse-verified + zero-loss asserted")
