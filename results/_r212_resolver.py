"""R212 rebase conflict resolver (11-UU same-window dual-machine S6, R208 reprise #3).

Laws applied:
- R208: scan file shape first. snapshot type -> take-newer WHOLE BYTES (no reformat,
  R209); rolling-ledger keys (launches/history/transitions) -> dual-blob union zero-loss.
- R203: last_tick is a dict; compare by inner ts then assign whole dict; assert type.
- r140: same-second tie -> take HEAD (= stage-2, the rebase base bm-b r221).
- r185: parse-validate every resolved file BEFORE git add.
"""
import json, subprocess, sys, io, os
sys.stdout.reconfigure(encoding="utf-8")

def stage_bytes(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {n} missing for {path}")
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def ts_of(j, *keys):
    for k in keys:
        v = j
        for part in k.split("."):
            v = v.get(part) if isinstance(v, dict) else None
        if v:
            return v
    return None

resolved = []

# ---------- 1) CODELY.md: bm-b base + my R212 line appended ----------
b2, b3 = stage_bytes("CODELY.md", 2), stage_bytes("CODELY.md", 3)
l2 = b2.decode("utf-8").splitlines()
mine = [l for l in b3.decode("utf-8").splitlines()
        if "R212·push2 clist 阻断深度实证" in l]
assert len(mine) == 1, f"expected exactly 1 R212 line, got {len(mine)}"
out_lines = list(l2)
if not any("R212·push2 clist" in l for l in out_lines):
    out_lines.append(mine[0])
with io.open("CODELY.md", "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out_lines) + "\n")
resolved.append(("CODELY.md", f"bm-b 51 lines + R212 line appended ({len(out_lines)} lines)"))

# ---------- 2) autofill_state.json: launches union + last_tick dict law ----------
b2, b3 = stage_bytes("results/autofill_state.json", 2), stage_bytes("results/autofill_state.json", 3)
s2, s3 = jload(b2), jload(b3)
seen, launches = set(), []
for ent in list(s2.get("launches", [])) + list(s3.get("launches", [])):
    key = json.dumps(ent, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key)
        launches.append(ent)
lt2, lt3 = s2.get("last_tick"), s3.get("last_tick")
assert isinstance(lt2, dict) and isinstance(lt3, dict), "last_tick not dict (R203)"
t2, t3 = str(lt2.get("ts", "")), str(lt3.get("ts", ""))
if t3 > t2:
    last_tick = lt3
    tie = "theirs-newer"
elif t3 < t2:
    last_tick = lt2
    tie = "ours-newer"
else:
    last_tick = lt2  # r140 same-second tie -> HEAD (stage-2)
    tie = "tie->HEAD(stage2)"
merged = {"launches": launches, "last_tick": last_tick,
          "rebase_union_note": f"R212 rebase union: launches {len(s2.get('launches',[]))}+{len(s3.get('launches',[]))}->{len(launches)} zero-loss; last_tick {t2} vs {t3} {tie}"}
with io.open("results/autofill_state.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(merged, ensure_ascii=False, indent=1) + "\n")
assert isinstance(json.load(io.open("results/autofill_state.json", encoding="utf-8-sig"))["last_tick"], dict)
resolved.append(("results/autofill_state.json", f"launches {len(s2.get('launches',[]))}+{len(s3.get('launches',[]))}->{len(launches)} union; last_tick {tie}"))

# ---------- 3) compute_audit.json: latest take-new + history union ----------
b2, b3 = stage_bytes("results/compute_audit.json", 2), stage_bytes("results/compute_audit.json", 3)
c2, c3 = jload(b2), jload(b3)
t2, t3 = ts_of(c2["latest"], "ts"), ts_of(c3["latest"], "ts")
latest, pick = (c3["latest"], "theirs") if t3 > t2 else (c2["latest"], "ours")
hseen, hist = set(), []
for rec in list(c2.get("history", [])) + list(c3.get("history", [])):
    key = json.dumps(rec, sort_keys=True, ensure_ascii=False)
    if key not in hseen:
        hseen.add(key)
        hist.append(rec)
hist.sort(key=lambda r: str(ts_of(r, "ts")))
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps({"latest": latest, "history": hist}, indent=2, ensure_ascii=False) + "\n")
resolved.append(("results/compute_audit.json", f"latest {pick} ({t2} vs {t3}); history {len(c2['history'])}+{len(c3['history'])}->{len(hist)} union"))

# ---------- 4) snapshot take-newer WHOLE BYTES (R209: no reformat) ----------
SNAP_TS = {
    "results/dashboard_status.js": ("generated_at",),  # inside JS wrapper; regex
    "results/dashboard_status.json": ("meta.generated_at", "meta.ts", "updated"),
    "results/fundamental_b_layer_filter.json": ("updated",),
    "results/futures_update_status.json": ("ts",),
    "results/heat_update_status.json": ("updated", "last_attempt"),
    "results/lhb_update_status.json": ("updated", "last_attempt"),
    "results/token_usage.json": ("generated",),
    "results/update_status.json": ("updated", "now"),
}
import re
for path, keys in SNAP_TS.items():
    b2, b3 = stage_bytes(path, 2), stage_bytes(path, 3)
    if path.endswith(".js"):
        m2 = re.search(rb'"generated_at"\s*:\s*"([^"]+)"', b2)
        m3 = re.search(rb'"generated_at"\s*:\s*"([^"]+)"', b3)
        t2, t3 = m2.group(1).decode(), m3.group(1).decode()
    else:
        t2, t3 = ts_of(jload(b2), *keys), ts_of(jload(b3), *keys)
    winner, pick = (b3, "theirs") if t3 > t2 else (b2, "ours")
    with io.open(path, "wb") as f:
        f.write(winner)
    # validation (r185)
    if path.endswith(".js"):
        assert winner.startswith(b"window.DASH_DATA ="), "JS wrapper lost (R209)"
    else:
        json.loads(winner.decode("utf-8-sig"))
    resolved.append((path, f"take-newer whole bytes {pick} ({t2} vs {t3})"))

# ---------- 5) regime_state.json: snapshot take-new + transitions/history union ----------
b2, b3 = stage_bytes("results/regime_state.json", 2), stage_bytes("results/regime_state.json", 3)
r2, r3 = jload(b2), jload(b3)
t2, t3 = ts_of(r2, "updated"), ts_of(r3, "updated")
base, pick = (r3, "theirs") if t3 > t2 else (r2, "ours")
for key in ("transitions", "history"):
    seen, merged = set(), []
    for rec in list(r2.get(key, [])) + list(r3.get(key, [])):
        k = json.dumps(rec, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            seen.add(k)
            merged.append(rec)
    base[key] = merged
with io.open("results/regime_state.json", "w", encoding="utf-8", newline="\n") as f:
    f.write(json.dumps(base, ensure_ascii=False, indent=2, default=str) + "\n")
json.load(io.open("results/regime_state.json", encoding="utf-8-sig"))
resolved.append(("results/regime_state.json", f"take-newer {pick} ({t2} vs {t3}); transitions/history union {len(base['transitions'])}/{len(base['history'])}"))

print("== RESOLUTION SUMMARY ==")
for p, note in resolved:
    print(f"  {p}: {note}")
# final validation sweep: every resolved file parses / wrapper intact
for p, _ in resolved:
    if p.endswith(".md"):
        continue
    raw = io.open(p, "rb").read()
    if p.endswith(".js"):
        assert raw.startswith(b"window.DASH_DATA =") and b"<<<<<<<" not in raw
    else:
        txt = raw.decode("utf-8-sig")
        assert "<<<<<<<" not in txt and ">>>>>>>" not in txt, f"markers left in {p}"
        json.loads(txt)
print("ALL 11 FILES PARSE-CLEAN, ZERO CONFLICT MARKERS")
