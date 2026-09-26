# -*- coding: utf-8 -*-
"""R262 bm-b: wave-2 resolver (15 recipe-family conflicts, no UNKNOWN).
Stages: :1=ancestor(3dd2bd69), :2=bm-a closeout (17:2x), :3=my replayed commit.
Same recipes as wave 1; take-new adjudicated per-file by real ts probes."""
import io
import json
import re
import subprocess

TS_KEYS = ("ts", "updated", "generated", "as_of", "last_attempt",
           "generated_at")


def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout


def jload(n, path):
    return json.loads(stage(n, path).decode("utf-8-sig"))


def face_of(raw):
    return {"bom": raw.startswith(b"\xef\xbb\xbf"),
            "crlf": b"\r\n" in raw,
            "trailing_nl": raw.endswith(b"\n")}


def dump_face(d, face):
    txt = json.dumps(d, ensure_ascii=False, indent=1)
    if not face["trailing_nl"]:
        txt = txt.rstrip("\n")
    out = txt.encode("utf-8")
    if face["bom"]:
        out = b"\xef\xbb\xbf" + out
    if face["crlf"]:
        out = out.replace(b"\n", b"\r\n")
    return out


def deep_ts(d):
    """top-level or meta.latest ts probe (per-file key families)."""
    if not isinstance(d, dict):
        return None
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    for sub in ("meta", "latest"):
        s = d.get(sub)
        if isinstance(s, dict):
            for k in TS_KEYS:
                v = s.get(k)
                if isinstance(v, str) and v:
                    return v
    return None


log = []


def note(m):
    log.append(m)
    print(m, flush=True)

# ---- 1. CODELY.md: :3 + :2's missing lines (their prev-echo entry) ----
p = "CODELY.md"
l3 = stage(3, p).decode("utf-8").splitlines()
l2 = stage(2, p).decode("utf-8").splitlines()
missing = [x for x in l2 if x not in l3]
out = l3 + [x for x in missing if x.strip()]
io.open(p, "wb").write(("\n".join(out) + "\n").encode("utf-8"))
note(f"CODELY union: :3 {len(l3)} lines + :2 missing {len(missing)} -> {len(out)}")

# ---- 2. daily_report pair: generated_at take-new ----
d2 = jload(2, "docs/daily_report/REPORT-2026-09-26.json")
d3 = jload(3, "docs/daily_report/REPORT-2026-09-26.json")
t2, t3 = d2.get("generated_at"), d3.get("generated_at")
win = 2 if (t2 or "") >= (t3 or "") else 3
for p in ("docs/daily_report/REPORT-2026-09-26.json",
          "docs/daily_report/REPORT-2026-09-26.md"):
    io.open(p, "wb").write(stage(win, p))
note(f"daily_report pair: take :{win} ({t2} vs {t3})")

# ---- 3. autofill_state: launches union asc cap50 + last_tick whole-dict ----
p = "results/autofill_state.json"
a2, a3 = jload(2, p), jload(3, p)
face = face_of(stage(2, p))
l2, l3 = a2.get("launches", []), a3.get("launches", [])
k = next((x for x in TS_KEYS if l2 and l2[0].get(x)), None)
assert k, "launches ts key missing"
seen = {}
for row in l2 + l3:
    seen[row.get(k)] = row
union = sorted(seen.values(), key=lambda r: r[k])[-50:]
union = sorted(union, key=lambda r: r[k])
lt2 = a2.get("last_tick", {})
lt3 = a3.get("last_tick", {})
t2 = deep_ts(lt2)
t3 = deep_ts(lt3)
out = a2 if (deep_ts(a2) or "") >= (deep_ts(a3) or "") else a3
if (t3 or "") >= (t2 or ""):
    out["last_tick"] = lt3
out["launches"] = union
io.open(p, "wb").write(dump_face(out, face))
chk = json.loads(io.open(p, encoding="utf-8-sig").read())
assert isinstance(chk["last_tick"], dict)
note(f"autofill: union |{len(l2)}+{len(l3)}| -> {len(union)} asc-cap50, "
     f"last_tick by ts ({t3} vs {t2})")

# ---- 4. compute_audit: history union + latest take-new ----
p = "results/compute_audit.json"
c2, c3 = jload(2, p), jload(3, p)
face = face_of(stage(2, p))
h2, h3 = c2["history"], c3["history"]
k = next((x for x in TS_KEYS if h2 and h2[0].get(x)), None)
assert k, "compute_audit history ts key missing"
seen = {}
for row in h2 + h3:
    seen[(row.get(k), json.dumps(row, sort_keys=True, ensure_ascii=False))] = row
union = sorted(seen.values(), key=lambda r: r[k])
out = c2 if (deep_ts(c2) or "") >= (deep_ts(c3) or "") else c3
out["history"] = union
io.open(p, "wb").write(dump_face(out, face))
json.loads(io.open(p, encoding="utf-8-sig").read())
note(f"compute_audit: history union |{len(h2)}+{len(h3)}| -> {len(union)}, "
     f"latest take-new ({deep_ts(c2)} vs {deep_ts(c3)})")

# ---- 5. regime_state: transitions dedupe union + state take-new ----
p = "results/regime_state.json"
r2, r3 = jload(2, p), jload(3, p)
face = face_of(stage(2, p))
t2l, t3l = r2.get("transitions", []), r3.get("transitions", [])
seen = {}
for row in t2l + t3l:
    seen[json.dumps(row, sort_keys=True, ensure_ascii=False)] = row
union = list(seen.values())
out = r2 if (deep_ts(r2) or "") >= (deep_ts(r3) or "") else r3
out["transitions"] = union
io.open(p, "wb").write(dump_face(out, face))
json.loads(io.open(p, encoding="utf-8-sig").read())
note(f"regime: transitions dedupe |{len(t2l)}+{len(t3l)}| -> {len(union)}, "
     f"state take-new ({deep_ts(r2)} vs {deep_ts(r3)})")

# ---- 6. dashboard js (wrapper, whole-byte by generated_at) + json ----
p = "results/dashboard_status.js"
j2, j3 = stage(2, p), stage(3, p)
g2 = (re.search(rb'"generated_at"\s*:\s*"([^"]+)"', j2) or [None, b""])[1]
g3 = (re.search(rb'"generated_at"\s*:\s*"([^"]+)"', j3) or [None, b""])[1]
win = 2 if g2.decode() >= g3.decode() else 3
io.open(p, "wb").write(stage(win, p))
note(f"dashboard_status.js: take :{win} ({g2.decode()} vs {g3.decode()})")

SNAPS = ["results/dashboard_status.json", "results/daily_scorecard.json",
         "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json",
         "results/heat_update_status.json",
         "results/lhb_update_status.json",
         "results/token_usage.json",
         "results/update_status.json"]
for p in SNAPS:
    d2, d3 = jload(2, p), jload(3, p)
    t2, t3 = deep_ts(d2), deep_ts(d3)
    assert t2 and t3, f"ts probe failed for {p}"
    win = 2 if t2 >= t3 else 3
    io.open(p, "wb").write(stage(win, p))
    json.loads(io.open(p, encoding="utf-8-sig").read())
    note(f"{p}: take :{win} ({t2} vs {t3})")

io.open("results/_r262bmb_resolve2_log.json", "w", encoding="utf-8",
        newline="\n").write(json.dumps(log, ensure_ascii=False, indent=1) + "\n")
print("WAVE-2 RESOLVER DONE:", len(log))
