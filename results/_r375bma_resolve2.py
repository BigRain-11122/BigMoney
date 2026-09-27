"""r375 bm-a wave-2 resolver (13-UU vs bm-b r356, rebase window).

Same recipe set as wave-1 (results/_r375bma_resolve.py); upstream side now
bm-b (:2:), mine :3:. Probes (results/_r375bma_probe2.py): my side fresher
on every snapshot face; heat = dual evidence (host authority + fresher ts).
compute_audit my side carries wave-1's 15-row union; bm-b side also 15 --
ts-key union keeps every row of BOTH (r85 survival assert).
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


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


# ---- 1. take-side faces: byte-verbatim :3: (bm-a side, all probes newer;
#         heat = fresher AND R31 host authority, dual evidence) ----------
TAKE_MINE = [
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",   # not conflicted this wave; no-op
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
import subprocess as sp
conflicted = set()
r = sp.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True)
for ln in r.stdout.decode().splitlines():
    if ln.strip():
        conflicted.add(ln.strip())
for p in TAKE_MINE:
    if p not in conflicted:
        continue
    write_bytes(p, blob_bytes(":3:" + p))
    if p.endswith(".json"):
        json.loads(open(ROOT + "\\" + p.replace("/", "\\"),
                        encoding="utf-8").read())
    print(f"[take :3:] {p} written byte-verbatim + parse-ok")

js = open(ROOT + r"\results\dashboard_status.js", encoding="utf-8").read()
assert js.lstrip().startswith("window.DASH_DATA"), "js wrapper stripped (R209)!"
print("[wrapper-intact] dashboard_status.js ok")

# ---- 2. compute_audit union ----
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
ts_a = {str(h.get("ts", "")) for h in a.get("history", [])}
ts_b = {str(h.get("ts", "")) for h in b.get("history", [])}
assert ts_a <= seen and ts_b <= seen, "audit union lost a row (r85)"
la = str(a.get("latest", {}).get("ts", ""))
lb = str(b.get("latest", {}).get("ts", ""))
src = a if la > lb else b
out = {k: v for k, v in src.items() if k != "history"}
out["history"] = rows
raw = blob_bytes(":2:" + P).decode("utf-8")
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", "\r\n") if "\r\n" in raw else text)
json.loads(open(ROOT + r"\results\compute_audit.json", encoding="utf-8").read())
print(f"[union] compute_audit {len(a['history'])}|{len(b['history'])} -> "
      f"{len(rows)} rows both-survive; state from latest.ts {max(la, lb)}")

# ---- 3. regime_state union ----
P = "results/regime_state.json"
a, b = blob_json(":2:" + P), blob_json(":3:" + P)


def rowid(x):
    return json.dumps(x, sort_keys=True, ensure_ascii=False)


out = dict(b if str(b.get("updated", "")) > str(a.get("updated", "")) else a)
for key in ("triggers", "transitions", "history"):
    merged, s = list(out.get(key, [])), set()
    for row in merged:
        s.add(rowid(row))
    for d in (a, b):
        for row in d.get(key, []):
            if rowid(row) not in s:
                s.add(rowid(row))
                merged.append(row)
    out[key] = merged
raw = blob_bytes(":2:" + P).decode("utf-8")
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", "\r\n") if "\r\n" in raw else text)
json.loads(open(ROOT + r"\results\regime_state.json", encoding="utf-8").read())
print(f"[union] regime_state triggers={len(out['triggers'])} "
      f"transitions={len(out['transitions'])} history={len(out['history'])} "
      f"updated={out.get('updated')}")

# ---- 4. autofill_state union ----
P = "results/autofill_state.json"
a, b = blob_json(":2:" + P), blob_json(":3:" + P)
KEY = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
buckets = {}
for d in (a, b):
    for r_ in d.get("launches", []):
        buckets.setdefault(tuple(str(r_.get(k, "")) for k in KEY), []).append(r_)
merged, flags = [], []
for k, rows in buckets.items():
    uniq = {rowid(r_) for r_ in rows}
    if len(uniq) == 1:
        merged.append(rows[0])
        continue
    base = dict(rows[0])
    for r_ in rows[1:]:
        for kk, vv in r_.items():
            if kk not in base:
                base[kk] = vv
            elif base[kk] != vv:
                flags.append((k, kk))
    merged.append(base)
assert not flags, f"launches true divergence: {flags}"
merged.sort(key=lambda x: str(x.get("ts", "")), reverse=True)
merged = merged[:50]
merged.sort(key=lambda x: str(x.get("ts", "")))
la, lb = a.get("last_tick", {}), b.get("last_tick", {})
ta, tb = str(la.get("ts", "")), str(lb.get("ts", ""))
lt = la if ta >= tb else lb           # tie -> HEAD == :2: (r140)
out = {"launches": merged, "last_tick": lt}
assert isinstance(out["last_tick"], dict)
raw = blob_bytes(":2:" + P).decode("utf-8")
text = json.dumps(out, ensure_ascii=False, indent=1)
write_text(P, text.replace("\n", "\r\n") if "\r\n" in raw else text)
back = json.loads(open(ROOT + r"\results\autofill_state.json",
                       encoding="utf-8").read())
assert isinstance(back["last_tick"], dict) and len(back["launches"]) <= 50
print(f"[union] autofill_state buckets={len(buckets)} kept={len(merged)} "
      f"last_tick={back['last_tick'].get('ts')} "
      f"({'tie->HEAD(bm-b)' if ta == tb else 'newer'})")

print("wave-2 resolver: all conflicted faces written + verified")
