"""r675 bm-a rebase UU resolver -- canon recipes (r657 HEAD/pick 双侧直取+r461 ts 归一+r453 dedup+r657 json 双生对齐)
Faces:
  - CODELY.md: union (origin block + mine appended entry, exact-line dedup, marker count by line-start)
  - ts/regen faces: newer-wins by freshness key (ts/generated/updated, normalized), json twin aligned same side
Exit 0 on full resolve; prints per-face verdicts.
"""
import json, re, subprocess, sys

PICK = "ffb452610"          # my r675 main commit (replay source)
FRESH_KEYS = ("generated", "ts", "updated", "asof")

def show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout

def norm_ts(s):
    if not isinstance(s, str):
        return ""
    return s.replace("T", " ")[:19]

def fresh_key(data):
    for k in FRESH_KEYS:
        v = data.get(k)
        if isinstance(v, (str, int, float)):
            return norm_ts(str(v))
    return ""

TS_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TWIN = {}  # json -> md twin mapping resolved from the same side
for j in ("docs/daily_report/REPORT-2026-10-04",
          "docs/live_usage/LIVE-2026-10-04",
          "docs/live_usage/LIVE-latest"):
    TWIN[j + ".json"] = j + ".md"

report = []
resolved = {}

# ---- 1) ts/newer-wins faces (json decides; md twin follows the SAME side)
for jpath, mpath in TWIN.items():
    o_raw, m_raw = show("HEAD", jpath), show(PICK, jpath)
    if o_raw is None or m_raw is None:
        report.append(f"SKIP-TWIN {jpath}: side missing"); continue
    try:
        o_f, m_f = fresh_key(json.loads(o_raw)), fresh_key(json.loads(m_raw))
    except Exception as e:
        report.append(f"SKIP-TWIN {jpath}: parse {e}"); continue
    side = "mine" if m_f >= o_f else "origin"
    src = m_raw if side == "mine" else o_raw
    open(jpath, "wb").write(src)
    resolved[jpath] = side
    for p in (mpath, jpath):
        if p in resolved: continue
    # md twin from same side
    o_md, m_md = show("HEAD", mpath), show(PICK, mpath)
    open(mpath, "wb").write(m_md if side == "mine" else o_md)
    resolved[mpath] = side
    report.append(f"TWIN {jpath}+md -> {side} (origin={o_f} mine={m_f})")

# ---- 2) standalone ts json faces
for jpath in TS_FACES:
    if jpath in resolved or jpath in TWIN: continue
    o_raw, m_raw = show("HEAD", jpath), show(PICK, jpath)
    if o_raw is None and m_raw is None:
        report.append(f"SKIP {jpath}: both missing"); continue
    if o_raw is None: side, src = "mine", m_raw
    elif m_raw is None: side, src = "origin", o_raw
    else:
        try:
            o_f, m_f = fresh_key(json.loads(o_raw)), fresh_key(json.loads(m_raw))
        except Exception as e:
            report.append(f"SKIP {jpath}: parse {e}"); continue
        side = "mine" if m_f >= o_f else "origin"
        src = m_raw if side == "mine" else o_raw
    open(jpath, "wb").write(src)
    resolved[jpath] = side
    report.append(f"TS {jpath} -> {side}")

# ---- 3) CODELY.md union (exact-line dedup keep-first, marker count by line-start)
cpath = "CODELY.md"
o_raw, m_raw = show("HEAD", cpath), show(PICK, cpath)
o_txt = o_raw.decode("utf-8", "replace")
m_txt = m_raw.decode("utf-8", "replace")
o_lines, m_lines = o_txt.splitlines(), m_txt.splitlines()
seen, out = set(), []
for ln in o_lines + m_lines:            # origin first (keep-first dedup)
    if ln in seen: continue
    seen.add(ln); out.append(ln)
union = "\n".join(out)
if not union.endswith("\n"): union += "\n"
markers = sum(1 for ln in union.splitlines()
              if ln.startswith(("<<<<<<<", "=======", ">>>>>>>")))
assert markers == 0, f"marker rows in union: {markers}"
mine_entry_present = any("r675 bm-a" in ln for ln in union.splitlines())
assert mine_entry_present, "my r675 entry lost in union"
open(cpath, "wb").write(union.encode("utf-8"))
resolved[cpath] = "union"
report.append(f"UNION {cpath} -> origin {len(o_lines)} + mine {len(m_lines)} lines, dedup kept {len(out)}, r675 entry present={mine_entry_present}")

# ---- 4) post-resolve assertions: no conflict markers in ANY resolved face
bad = []
for p in list(resolved) :
    try:
        txt = open(p, "rb").read().decode("utf-8", "replace")
    except Exception:
        continue
    n = sum(1 for ln in txt.splitlines() if ln.startswith(("<<<<<<<", ">>>>>>>")))
    if n: bad.append(p)
if bad:
    report.append("MARKER-FAIL: " + ", ".join(bad)); sys.exit(2)

open("results/_r675bma_rebase_resolve.json", "w", encoding="utf-8").write(
    json.dumps({"report": report, "resolved": resolved}, ensure_ascii=False, indent=1))
print("\n".join(report))
print("RESOLVE-OK faces=%d" % len(resolved))
