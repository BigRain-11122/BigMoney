"""R242 bm-a push-collision resolver batch 2: step-7 S6 snapshot/ledger batch.

Classifier: 12 classified + 2 manual (daily_report twins = same-day regen
snapshot, take-new by generated_at). All snapshot ts probes show :3 (my
replayed round commit) newer than :2 (bm-b ~10:59 round) -- take-side whole
bytes for snapshots (R209 law: take-side integral bytes, no re-serialize).

Ledgers: compute_audit history union (r188) + regime_state history/transitions
union + autofill launches union cap50 (R215) / last_tick whole-dict (r203).
Indent mirror: probe base blob first-line nesting (r237 law: compute_audit=2,
autofill=1; NEVER blanket indent). EOL mirror: probe base blob bytes (r223).
CODELY.md: hunk-level memory union (R208/r212).

Zero-loss asserts: history union count == |A identities u B identities|.
"""

import json
import subprocess

def blob(rev):
    return subprocess.run(["git", "show", rev], capture_output=True,
                          check=True).stdout

def jparse(b):
    return json.loads(b.decode("utf-8-sig"))

def ident(e):
    return json.dumps(e, sort_keys=True, ensure_ascii=False)

def probe_indent(b):
    for line in b.decode("utf-8-sig").splitlines():
        line = line.rstrip("\r")
        if line.startswith(" ") and line.strip():
            return len(line) - len(line.lstrip(" "))
    return 2

def probe_crlf(b):
    return b.count(b"\r\n") > 0 and b.count(b"\n") == b.count(b"\r\n")

def write_mirror(path, obj, base_b):
    indent = probe_indent(base_b)
    crlf = probe_crlf(base_b)
    out = json.dumps(obj, indent=indent, ensure_ascii=False)
    nl = "\r\n" if crlf else "\n"
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(nl.join(out.split("\n")))
    return indent, crlf

report = {}

# ---- 1) snapshots: take :3 bytes verbatim (mine newer on every probe) ----
SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/heat_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
    "results/token_usage.json",
]
for p in SNAPSHOTS:
    mine = blob(":3:" + p)
    with open(p, "wb") as f:
        f.write(mine)
    if p.endswith(".json"):
        jparse(open(p, "rb").read())  # parse-verify (r185)
    report[p] = "take-side :3 bytes verbatim"

# ---- 2) compute_audit.json: history union + latest take-new, indent mirror ----
p = "results/compute_audit.json"
o, t, base = jparse(blob(":2:" + p)), jparse(blob(":3:" + p)), blob(":1:" + p)
hist_o, hist_t = o.get("history", []), t.get("history", [])
seen = {}
for e in hist_o + hist_t:
    seen[ident(e)] = e
union = sorted(seen.values(), key=lambda e: str(e.get("ts", "")))
assert len(union) == len({ident(x) for x in hist_o} | {ident(x) for x in hist_t})
latest = t["latest"] if str(t["latest"].get("ts", "")) >= str(o["latest"].get("ts", "")) else o["latest"]
merged = {k: v for k, v in o.items() if k not in ("history", "latest")}
merged.update({k: v for k, v in t.items() if k not in ("history", "latest",)})
merged["history"] = union
merged["latest"] = latest
ind, crlf = write_mirror(p, merged, base)
report[p] = f"history union {len(hist_o)}+{len(hist_t)}->{len(union)} zero-loss, latest ts={latest.get('ts')}, indent={ind} crlf={crlf}"

# ---- 3) regime_state.json: history/transitions union + state take-new ----
p = "results/regime_state.json"
o, t, base = jparse(blob(":2:" + p)), jparse(blob(":3:" + p)), blob(":1:" + p)
merged = dict(o)
for key in ("history", "transitions"):
    ho, ht = o.get(key, []), t.get(key, [])
    seen = {}
    for e in ho + ht:
        seen[ident(e)] = e
    u = sorted(seen.values(), key=lambda e: str(e.get("ts", e.get("date", ""))))
    assert len(u) == len({ident(x) for x in ho} | {ident(x) for x in ht})
    merged[key] = u
    report.setdefault(p, {})[key] = f"{len(ho)}+{len(ht)}->{len(u)}"
# state fields: take the newer asof (same asof here -> either); mine preferred
for k, v in t.items():
    if k not in ("history", "transitions"):
        merged[k] = v
ind, crlf = write_mirror(p, merged, base)
report[p] = str(report[p]) + f" state take-:3, indent={ind} crlf={crlf}"

# ---- 4) autofill_state.json: launches union cap50 + last_tick whole-dict ----
p = "results/autofill_state.json"
o, t, base = jparse(blob(":2:" + p)), jparse(blob(":3:" + p)), blob(":1:" + p)
lo, lt = o.get("launches", []), t.get("launches", [])
seen = {}
for e in lo + lt:
    seen[ident(e)] = e
union = sorted(seen.values(), key=lambda e: str(e.get("ts", "")))
pre_cap = len(union)
capped = union[-50:]
to, tt = o.get("last_tick"), t.get("last_tick")
if not isinstance(to, dict):
    last_tick = tt
elif not isinstance(tt, dict):
    last_tick = to
else:
    last_tick = tt if str(tt.get("ts", "")) > str(to.get("ts", "")) else to
assert isinstance(last_tick, dict)
merged = {k: v for k, v in o.items() if k not in ("launches", "last_tick")}
for k, v in t.items():
    if k not in ("launches", "last_tick") and k not in merged:
        merged[k] = v
merged["launches"] = capped
merged["last_tick"] = last_tick
ind, crlf = write_mirror(p, merged, base)
report[p] = f"launches {len(lo)}+{len(lt)} union {pre_cap} cap->{len(capped)}, last_tick ts={last_tick.get('ts')} indent={ind} crlf={crlf}"

# ---- 5) CODELY.md: hunk-level memory union (ours + theirs-only, dedupe) ----
p = "CODELY.md"
raw = open(p, "rb").read().decode("utf-8-sig")
lines = raw.split("\n")
out, emitted, i = [], set(), 0
hunks = 0
while i < len(lines):
    l = lines[i]
    if l.startswith("<<<<<<<"):
        ours_block, theirs_block = [], []
        i += 1
        while i < len(lines) and not lines[i].startswith("======="):
            ours_block.append(lines[i].rstrip("\r")); i += 1
        i += 1
        while i < len(lines) and not lines[i].startswith(">>>>>>>"):
            theirs_block.append(lines[i].rstrip("\r")); i += 1
        i += 1
        hunks += 1
        for l2 in ours_block + theirs_block:
            key = l2.strip()
            if key and key in emitted:
                continue
            if key:
                emitted.add(key)
            out.append(l2)
        continue
    key = l.strip()
    if key and key not in emitted and not l.startswith(("# ", "## ", "### ")):
        pass  # common context lines always kept (structural dupes outside hunks ok)
    out.append(l.rstrip("\r"))
    if key:
        emitted.add(key)
    i += 1
eol = "\r\n" if probe_crlf(raw.encode("utf-8")) or "\r\n" in raw else "\n"
with open(p, "w", encoding="utf-8", newline="") as f:
    f.write(eol.join(out))
report[p] = f"memory-union hunks={hunks} lines out={len(out)} eol={repr(eol)}"

# ---- final parse-verify all JSON writes (r185) ----
for p2 in ["results/compute_audit.json", "results/regime_state.json",
           "results/autofill_state.json", "results/dashboard_status.json",
           "results/token_usage.json", "docs/daily_report/REPORT-2026-09-26.json"]:
    jparse(open(p2, "rb").read())
print(json.dumps(report, indent=1, ensure_ascii=False))
print("batch2 resolver OK: all parse-verified")
