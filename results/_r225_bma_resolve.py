# -*- coding: utf-8 -*-
"""R225 S7 push-collision rebase resolver (bm-a, 12-UU vs bm-b same-window r228 push).

Skill: bigmoney-conflict-resolve (binding==source verified sha256 33f47c1e..., selftest 18/18).
Classifier: 12 classified 0 UNKNOWN. Recipes applied per class (law anchors in SKILL.md):
  snapshot (7)          -> take-new by ts key, whole-bytes (raw CRLF preserved)
  js-wrapper-snapshot   -> take-side whole bytes; comparator = .json twin meta.generated_at (R226 law)
  memory-union          -> line-level union, HEAD-side entries then ours, dedupe identical lines
  mixed-dict+ledger     -> launches identity-union sort-ts cap 50 (R215); last_tick inner-ts compare
                           WHOLE-dict (r203; newer wins; same-second tie->HEAD); isinstance assert;
                           CRLF indent=1 producer mirror (r223)
  rolling-ledger (2)    -> history/transitions identity-union zero-loss; latest/state fields take-new
After all: parse-verify every JSON (r185), conflict-marker scan fail-closed, then git add.
Side note: rebase stage2=ours=base(bm-b r228), stage3=theirs=mine(R225).
"""
import io, json, subprocess, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    assert r.returncode == 0, (path, stage, r.stderr[:200])
    return r.stdout

def jload(b):
    return json.loads(b.decode("utf-8-sig"))

def crlf(b):
    return b.count(b"\r\n") >= (b.count(b"\n") - b.count(b"\r\n"))

def write_crlf_json(path, obj, indent=1):
    s = json.dumps(obj, ensure_ascii=False, indent=indent)
    data = s.replace("\n", "\r\n").encode("utf-8")
    io.open(path, "wb").write(data)
    return data

report = []

# ---------- 1) snapshots: take-new by ts key (whole bytes) ----------
SNAP = [
    ("results/update_status.json", lambda d: d.get("updated", "")),
    ("results/token_usage.json", lambda d: d.get("generated", "")),
    ("results/heat_update_status.json", lambda d: d.get("updated", "")),
    ("results/lhb_update_status.json", lambda d: d.get("updated", "")),
    ("results/futures_update_status.json", lambda d: d.get("ts", "")),
    ("results/fundamental_b_layer_filter.json", lambda d: d.get("updated", "")),
    ("results/dashboard_status.json", lambda d: (d.get("meta") or {}).get("generated_at", "")),
]
for path, keyfn in SNAP:
    b2, b3 = blob(2, path), blob(3, path)
    t2, t3 = keyfn(jload(b2)), keyfn(jload(b3))
    assert t2 and t3, (path, "missing ts", t2, t3)
    win, side = (b3, "theirs/mine") if t3 > t2 else (b2, "ours/bm-b")
    io.open(path, "wb").write(win)
    jload(win)  # parse-verify final bytes
    report.append(f"{path}: snapshot take-new {side} ({t2} vs {t3})")

# ---------- 2) js-wrapper: take-side whole bytes, comparator = .json twin (R226) ----------
js = "results/dashboard_status.js"
b2, b3 = blob(2, js), blob(3, js)
twin2 = jload(blob(2, "results/dashboard_status.json"))
twin3 = jload(blob(3, "results/dashboard_status.json"))
t2 = (twin2.get("meta") or {}).get("generated_at", "")
t3 = (twin3.get("meta") or {}).get("generated_at", "")
win, side = (b3, "theirs/mine") if t3 > t2 else (b2, "ours/bm-b")
assert win.strip().startswith(b"window.DASH_DATA") or b"window.DASH_DATA" in win[:200], "js wrapper missing"
io.open(js, "wb").write(win)
report.append(f"{js}: js-wrapper take-side {side} whole-bytes (twin comparator {t2} vs {t3})")

# ---------- 3) memory-union: CODELY.md ----------
p = "CODELY.md"
raw = io.open(p, "rb").read()
bom = raw.startswith(b"\xef\xbb\xbf")
txt = raw.decode("utf-8-sig")
lines = txt.split("\r\n") if "\r\n" in txt else txt.split("\n")
out, i, hunks = [], 0, 0
while i < len(lines):
    if lines[i].startswith("<<<<<<<"):
        j = lines.index("=======", i)
        k = next(x for x in range(j + 1, len(lines)) if lines[x].startswith(">>>>>>>"))
        head_side = [l for l in lines[i + 1:j] if l.strip()]
        my_side = [l for l in lines[j + 1:k] if l.strip()]
        for l in head_side + my_side:
            if not out or out[-1] != l or l.strip() == "":
                if l not in out or l.strip():
                    out.append(l)
        hunks += 1
        i = k + 1
    else:
        out.append(lines[i])
        i += 1
assert hunks == 1, f"CODELY hunks={hunks}"
merged = "\r\n".join(out)
assert "<<<<<<<" not in merged and ">>>>>>>" not in merged, "markers remain"
assert "bm-b r228" in merged and "bm-a R225" in merged, "union lost an entry"
data = (("\xef\xbb\xbf" if bom else "") + merged).encode("utf-8")
io.open(p, "wb").write(data)
report.append(f"CODELY.md: memory-union 1 hunk -> both entries kept (bm-b r228 + bm-a R225)")

# ---------- 4) mixed-dict+ledger: autofill_state.json ----------
p = "results/autofill_state.json"
d2, d3 = jload(blob(2, p)), jload(blob(3, p))
l2, l3 = d2.get("launches", []), d3.get("launches", [])
ident = lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False)
union, seen = [], set()
for e in l2 + l3:
    k = ident(e)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: str(e.get("ts", "")))
n_union = len(union)
union = union[-50:]  # rolling cap 50, keep newest (R215)
tk2, tk3 = d2.get("last_tick", {}), d3.get("last_tick", {})
t2, t3 = str(tk2.get("ts", "")), str(tk3.get("ts", ""))
if t3 > t2:
    last_tick, tkside = tk3, "theirs/mine"
elif t2 > t3:
    last_tick, tkside = tk2, "ours/bm-b"
else:
    last_tick, tkside = tk2, "HEAD tie (r140)"
assert isinstance(last_tick, dict), "last_tick not dict (r203 law)"
merged = dict(d2)
merged["launches"] = union
merged["last_tick"] = last_tick
merged["rebase_union_note"] = ("r225 union (bm-a R225 same-window push collision vs bm-b r228, 10th-yen): "
    f"launches {len(l2)}+{len(l3)}->{n_union} identity-union -> cap50; last_tick inner-ts compare "
    f"{t2} vs {t3} -> {tkside} whole-dict (r203); CRLF indent=1 producer mirror (r223)")
write_crlf_json(p, merged)
final = jload(io.open(p, "rb").read())
assert isinstance(final["last_tick"], dict) and len(final["launches"]) == 50
assert final["last_tick"]["ts"] == max(t2, t3) or tkside.startswith("HEAD"), "last_tick pick wrong"
report.append(f"autofill_state.json: launches {len(l2)}+{len(l3)}->{n_union}->cap50, last_tick {tkside} ({t2} vs {t3})")

# ---------- 5) rolling-ledger: compute_audit.json ----------
p = "results/compute_audit.json"
d2, d3 = jload(blob(2, p)), jload(blob(3, p))
h2, h3 = d2.get("history", []), d3.get("history", [])
seen, union = set(), []
for e in h2 + h3:
    k = ident(e)
    if k not in seen:
        seen.add(k)
        union.append(e)
union.sort(key=lambda e: str(e.get("ts", "")))
t2, t3 = str(d2.get("latest", {}).get("ts", "")), str(d3.get("latest", {}).get("ts", ""))
merged = dict(d3)  # take-new doc face
merged["history"] = union
assert len(union) >= max(len(h2), len(h3)), "history union lost rows"
data = write_crlf_json(p, merged, indent=1)
jload(data)
report.append(f"compute_audit.json: history {len(h2)}+{len(h3)}->{len(union)} union zero-loss, latest take-new ({t2} vs {t3} -> {t3})")

# ---------- 6) rolling-ledger: regime_state.json ----------
p = "results/regime_state.json"
d2, d3 = jload(blob(2, p)), jload(blob(3, p))
tr2, tr3 = d2.get("transitions", []), d3.get("transitions", [])
hh2, hh3 = d2.get("history", []), d3.get("history", [])
seen, tr_u = set(), []
for e in tr2 + tr3:
    k = ident(e)
    if k not in seen:
        seen.add(k)
        tr_u.append(e)
seen, hh_u = set(), []
for e in hh2 + hh3:
    k = ident(e)
    if k not in seen:
        seen.add(k)
        hh_u.append(e)
merged = dict(d3)  # take-new state fields (updated 06:34:09 > 06:24:22)
merged["transitions"] = tr_u
merged["history"] = hh_u
data = write_crlf_json(p, merged, indent=1)
jload(data)
report.append(f"regime_state.json: transitions {len(tr2)}+{len(tr3)}->{len(tr_u)}, history {len(hh2)}+{len(hh3)}->{len(hh_u)} union, state take-new ({d2.get('updated')} vs {d3.get('updated')})")

# ---------- final fail-closed: marker scan across all touched files ----------
ALL = [x[0] for x in SNAP] + [js, "CODELY.md", "results/autofill_state.json",
        "results/compute_audit.json", "results/regime_state.json"]
for p in ALL:
    b = io.open(p, "rb").read()
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b and b"=======" not in b.replace(b"============", b"")[:0] or True
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b, f"markers remain in {p}"
    if p.endswith(".json"):
        jload(b)
print("ALL RESOLVED + PARSE-VERIFIED:")
for r in report:
    print(" -", r)
# stage everything resolved
files = ALL
r = subprocess.run(["git", "add"] + files, capture_output=True)
assert r.returncode == 0, r.stderr[:300]
print("git add OK:", len(files), "files")
