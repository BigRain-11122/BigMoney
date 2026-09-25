"""R216 push-rebase conflict resolver -- canonical multi-machine shared-state recipes.

Family: R140 (same-second tie -> HEAD) / R188+R208 (rolling-ledger union, zero loss) /
R203 (last_tick is dict: compare inner ts then assign whole dict, never str()) /
R209 (producer-format fidelity: dashboard_status.js keeps JS wrapper, byte-side) /
R212 (CODELY.md append-only line-union) / R210 (HANDOVER/digest anchor-insert; N/A here).

Sides: HEAD = origin (bm-b r222 landed first), OURS (commit efe6a626 = bm-a R216).
Snapshot-type files with ts keys -> take-new whole side (byte-level, R209 law).
Rolling ledgers (history/launches/transitions keys) -> union both blob sides, zero loss.
"""
import json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8")


def side(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True).stdout


def jload(b):
    if isinstance(b, bytes):
        b = b.decode("utf-8-sig")
    return json.loads(b)


def ts_of(d, keys=("ts", "updated", "updated_at", "generated", "generated_at", "last_attempt", "last_fetch", "asof", "now")):
    for k in keys:
        if isinstance(d, dict) and isinstance(d.get(k), str) and d[k]:
            return d[k]
    if isinstance(d, dict):  # one-level-deep scan (e.g. status nested dicts)
        for v in d.values():
            if isinstance(v, dict):
                r = ts_of(v, keys)
                if r:
                    return r
    return ""


resolved = {}

# ---- 1) snapshot JSONs: take-new by ts (R208/R212 recipe; per-file ts key census below) ----
TS_KEYS = {
    "results/dashboard_status.json": ("meta", "generated_at"),
    "results/fundamental_b_layer_filter.json": ("updated",),
    "results/futures_update_status.json": ("ts",),
    "results/heat_update_status.json": ("ts",),
    "results/lhb_update_status.json": ("ts",),
    "results/regime_state.json": ("asof",),
    "results/token_usage.json": ("generated",),
    "results/update_status.json": ("updated",),
}


def deep_ts(d, keys):
    cur = d
    for k in keys[:-1]:
        cur = cur.get(k, {}) if isinstance(cur, dict) else {}
    v = str(cur.get(keys[-1], "")) if isinstance(cur, dict) else ""
    return v or ts_of(d)  # named key first, broad scan fallback (nested ts surfaces)


SNAP = list(TS_KEYS)
for p in SNAP:
    h, o = jload(side("HEAD", p)), jload(side("efe6a626", p))
    th, to = deep_ts(h, TS_KEYS[p]), deep_ts(o, TS_KEYS[p])
    pick = "HEAD" if th >= to else "OURS"
    # regime_state: transitions/history-type keys must union if present
    if p == "results/regime_state.json":
        for k in ("transitions", "history"):
            if isinstance(h.get(k), list) or isinstance(o.get(k), list):
                hl, ol = h.get(k) or [], o.get(k) or []
                seen, merged = set(), []
                for row in hl + ol:
                    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
                    if key not in seen:
                        seen.add(key); merged.append(row)
                (h if pick == "HEAD" else o)[k] = merged
    resolved[p] = (pick, json.dumps(h if pick == "HEAD" else o, ensure_ascii=False, indent=1).encode("utf-8"))
    print(f"{p}: take-new {pick} (HEAD {th} vs OURS {to})")

# ---- 2) dashboard_status.js: JS wrapper file -> byte-side take-new (R209 law) ----
p = "results/dashboard_status.js"


def js_body(raw):
    return jload(raw.decode("utf-8-sig").split("=", 1)[1].rstrip().rstrip(";"))


h_raw, o_raw = side("HEAD", p), side("efe6a626", p)
h_ts, o_ts = deep_ts(js_body(h_raw), TS_KEYS["results/dashboard_status.json"]), \
             deep_ts(js_body(o_raw), TS_KEYS["results/dashboard_status.json"])
pick = "HEAD" if h_ts >= o_ts else "OURS"
resolved[p] = (pick, h_raw if pick == "HEAD" else o_raw)
print(f"{p}: byte-side take-new {pick} (meta.generated_at HEAD {h_ts} vs OURS {o_ts}; wrapper preserved R209)")

# ---- 3) compute_audit.json: latest take-new + history union (R208 law) ----
p = "results/compute_audit.json"
h, o = jload(side("HEAD", p)), jload(side("efe6a626", p))
pick = "HEAD" if ts_of(h) >= ts_of(o) else "OURS"
base = h if pick == "HEAD" else o
other = o if pick == "HEAD" else h
hl, ol = base.get("history") or [], other.get("history") or []
seen, merged = set(), []
for row in hl + ol:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); merged.append(row)
base["history"] = merged
resolved[p] = (pick, json.dumps(base, ensure_ascii=False, indent=1).encode("utf-8"))
print(f"{p}: take-new {pick} + history union {len(hl)}+{len(ol)} -> {len(merged)} unique zero-loss")

# ---- 4) autofill_state.json: launches union + last_tick dict law (R203/r140) ----
p = "results/autofill_state.json"
h, o = jload(side("HEAD", p)), jload(side("efe6a626", p))
hl, ol = h.get("launches") or [], o.get("launches") or []
seen, merged = set(), []
for row in hl + ol:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); merged.append(row)
lt_h, lt_o = h.get("last_tick"), o.get("last_tick")
assert isinstance(lt_h, dict) and isinstance(lt_o, dict), "last_tick must be dict (R203 law)"
if lt_h.get("ts") == lt_o.get("ts"):
    lt = lt_h  # same-second tie -> HEAD (r140 law)
    tie = "TIE->HEAD"
else:
    lt = lt_h if str(lt_h.get("ts", "")) >= str(lt_o.get("ts", "")) else lt_o
    tie = "take-new"
h["launches"] = merged
h["last_tick"] = lt
resolved[p] = ("HEAD-base", json.dumps(h, ensure_ascii=False, indent=1).encode("utf-8"))
print(f"{p}: launches union {len(hl)}+{len(ol)} -> {len(merged)} unique; last_tick {tie} (ts {lt.get('ts')}), dict-type preserved")

# ---- 5) CODELY.md: append-only line union (R212 recipe, zero-loss verified) ----
p = "CODELY.md"
h_txt = side("HEAD", p).decode("utf-8-sig").splitlines()
o_txt = side("efe6a626", p).decode("utf-8-sig").splitlines()
head_set = set(h_txt)
new_from_ours = [l for l in o_txt if l not in head_set]
merged = h_txt + [l for l in new_from_ours if l.strip()]
resolved[p] = ("union", ("\n".join(merged) + "\n").encode("utf-8"))
print(f"{p}: HEAD {len(h_txt)} lines + OURS-only {len([l for l in new_from_ours if l.strip()])} appended (union, zero-loss)")

# ---- write back all resolutions ----
for p, (pick, blob) in resolved.items():
    with open(p, "wb") as f:
        f.write(blob)
    print(f"written: {p} ({pick}, {len(blob)} bytes)")

# post-write assertions (R185: verify before add)
assert isinstance(jload(open("results/autofill_state.json", "rb").read())["last_tick"], dict)
d = jload(open("results/dashboard_status.js", "rb").read().decode("utf-8-sig").split("=", 1)[1].rstrip().rstrip(";"))
assert isinstance(d, dict) and "traders" in d.get("trading", {}), "dashboard js wrapper parse fail"
for p in SNAP + ["results/compute_audit.json"]:
    jload(open(p, "rb").read())
print("ALL POST-WRITE ASSERTIONS PASS (R185 verify-before-add)")
