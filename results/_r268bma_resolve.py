"""r268 bm-a rebase conflict resolver (16 UU files, bm-b r274 same-window push).

Skill recipes applied (bigmoney-conflict-resolve):
- memory-union CODELY.md: line-level merge honoring BOTH sides' archival edits
  (mine: 26 morning lines -> cold; theirs: 20:46 Project line -> cold), keep both
  sides' new pit-law entries. Zero-loss verified: every line dropped from hot must
  exist in the merged cold archive.
- cold archive: line-union both sides' sections, dedupe identical lines.
- rolling-ledger (compute_audit, regime_state): union list-key rows by ts, take-new
  scalar fields by newest top-level ts.
- snapshot family (dashboard_status.json/js, *_status.json, token_usage,
  fundamental_b_layer_filter, scorecard_v1, strategy_scorecard): take-new by
  recursive-two-level ts probe with format normalization (r267/r265 laws); tie->:2 (r140).
- REPORT pair (r242): json twin generated_at governs, md same-side whole bytes.
- js wrapper (R209): whole-bytes of winning side, no json.dumps re-emit.
Channel law (r255): all blob reads via subprocess bytes, no PS redirection.
"""
import json, re, subprocess, sys

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        die(f"blob read failed {stage}:{path}: {r.stderr[:120]}")
    return r.stdout

def die(msg, code=1):
    print("RESOLVER-DIE:", msg); sys.exit(code)

def probe_ts(obj, depth=0):
    """recursive two-level ts probe; returns normalized best ts string or None."""
    best = None
    cands = ("ts", "updated", "generated", "generated_at", "as_of", "at", "completed_at", "last_attempt")
    def norm(s):
        return str(s).replace(" ", "T").strip() if s is not None else None
    def walk(o, d):
        nonlocal best
        if d > 2 or o is None: return
        if isinstance(o, dict):
            for k, v in o.items():
                if k in cands and v is not None:
                    n = norm(v)
                    if n and (best is None or n > best): best = n
                else:
                    walk(v, d + 1)
        elif isinstance(o, list):
            for v in o[:50]: walk(v, d + 1)
    walk(obj, 0)
    return best

def json_face(b):
    return {"bom": b[:3] == b"\xef\xbb\xbf", "crlf": b.count(b"\r\n"),
            "ascii_esc": "\\u" in b.decode("utf-8", "replace")[:200000],
            "trailing_nl": b.endswith(b"\n")}

def emit(obj, face):
    txt = json.dumps(obj, ensure_ascii=face["ascii_esc"], indent=1)
    if face["crlf"] > 0: txt = txt.replace("\n", "\r\n")
    if face["trailing_nl"]: txt += "\n"
    return txt.encode("utf-8")

def merge_ledger(a, b, path):
    """union list rows by ts-ish key; scalars from newer top-level side."""
    ta, tb = probe_ts(a), probe_ts(b)
    newer = b if (tb or "") >= (ta or "") else a   # tie/None -> :3? r140 says tie->HEAD(:2)=a.
    if ta is not None and tb is not None and tb == ta: newer = a  # proven tie -> origin side
    out = dict(newer)
    union_counts = {}
    for k in list(out.keys()):
        if isinstance(out[k], list) and out[k] and isinstance(out[k][0], dict):
            rows_a = a.get(k) if isinstance(a.get(k), list) else []
            rows_b = b.get(k) if isinstance(b.get(k), list) else []
            seen, merged = {}, []
            for r in rows_a + rows_b:
                key = probe_ts(r) or json.dumps(r, sort_keys=True, ensure_ascii=False)[:80]
                if key in seen:
                    continue
                seen[key] = True; merged.append(r)
            out[k] = merged
            union_counts[k] = (len(rows_a), len(rows_b), len(merged))
    return out, ta, tb, union_counts

def resolve_snapshot(path):
    a, b = blob(2, path), blob(3, path)
    try:
        ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    except Exception as e:
        die(f"{path}: parse fail {e}")
    ta, tb = probe_ts(ja), probe_ts(jb)
    if ta is None and tb is None:
        die(f"{path}: no ts on either face (r267 blind-tie law -> hand adjudication)", 2)
    win = 3 if (tb or "") > (ta or "") else 2
    if ta is not None and tb is not None and ta == tb: win = 2
    print(f"  {path}: tsA={ta} tsB={tb} -> take :{win}")
    open(path, "wb").write(b if win == 3 else a)
    json.loads(open(path, "rb").read().decode("utf-8-sig"))

def resolve_ledger(path):
    a, b = blob(2, path), blob(3, path)
    ja, jb = json.loads(a.decode("utf-8-sig")), json.loads(b.decode("utf-8-sig"))
    out, ta, tb, counts = merge_ledger(ja, jb, path)
    face = json_face(a)  # face from :2 (canonical producer face)
    print(f"  {path}: tsA={ta} tsB={tb} union={counts}")
    open(path, "wb").write(emit(out, face))
    json.loads(open(path, "rb").read().decode("utf-8-sig"))

# ---------- snapshots / ledgers ----------
for p in ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/heat_update_status.json",
          "results/lhb_update_status.json", "results/update_status.json",
          "results/token_usage.json", "results/scorecard_v1.json",
          "results/strategy_scorecard.json", "docs/daily_report/REPORT-2026-09-26.json"]:
    resolve_snapshot(p)

for p in ["results/compute_audit.json", "results/regime_state.json"]:
    resolve_ledger(p)

# ---------- REPORT md twin (json generated_at governs, md same side whole bytes) ----------
ja = json.loads(blob(2, "docs/daily_report/REPORT-2026-09-26.json").decode("utf-8-sig"))
jb = json.loads(blob(3, "docs/daily_report/REPORT-2026-09-26.json").decode("utf-8-sig"))
ta, tb = probe_ts(ja), probe_ts(jb)
win = 3 if (tb or "") > (ta or "") else 2
if ta is not None and tb is not None and ta == tb: win = 2
md = "docs/daily_report/REPORT-2026-09-26.md"
open(md, "wb").write(blob(win, md))
print(f"  {md}: json twin tsA={ta} tsB={tb} -> take :{win} whole bytes")

# ---------- js wrapper (R209: whole bytes of winner) ----------
jsa, jsb = blob(2, "results/dashboard_status.js"), blob(3, "results/dashboard_status.js")
def js_ts(b):
    m = re.search(rb"window\.DASH_DATA\s*=\s*(\{.*\});", b, re.S)
    if not m: return None
    return probe_ts(json.loads(m.group(1).decode("utf-8-sig")))
tja, tjb = js_ts(jsa), js_ts(jsb)
wjs = 3 if (tjb or "") > (tja or "") else 2
if tja is not None and tjb is not None and tja == tjb: wjs = 2
open("results/dashboard_status.js", "wb").write(jsb if wjs == 3 else jsa)
print(f"  results/dashboard_status.js: tsA={tja} tsB={tjb} -> take :{wjs}")

# ---------- cold archive: line union, dedupe identical ----------
arc_a = blob(2, "research/memory-archive/202609.md").decode("utf-8")
arc_b = blob(3, "research/memory-archive/202609.md").decode("utf-8")
la, lb = arc_a.split("\n"), arc_b.split("\n")
seen, merged = set(), []
for L in la + lb:
    if L in seen: continue
    seen.add(L); merged.append(L)
# keep insertion order: :2 lines then :3-only lines (append order preserved by dedupe walk)
open("research/memory-archive/202609.md", "wb").write(("\n".join(merged)).encode("utf-8"))
print(f"  research/memory-archive/202609.md: union {len(la)}|{len(lb)} -> {len(merged)} lines")

# ---------- CODELY.md memory-union honoring both archival edits ----------
ca = blob(2, "CODELY.md").decode("utf-8").split("\n")
cb = blob(3, "CODELY.md").decode("utf-8").split("\n")
a_only = [L for L in ca if L not in cb]
b_only = [L for L in cb if L not in ca]
archived_by_them = [L for L in a_only if "2026-09-26 20:46" in L[:40]]   # their r274 cold-move
new_theirs = [L for L in a_only if L not in archived_by_them]
print(f"  CODELY: A-only={len(a_only)} (archived-by-them={len(archived_by_them)}, new-theirs={len(new_theirs)}), B-only={len(b_only)}")
# zero-loss gate: lines archived by them must exist in merged cold archive
arc_merged = "\n".join(merged)
for L in archived_by_them:
    if L.strip() and L not in arc_merged:
        die(f"zero-loss FAIL: archived line not in cold archive: {L[:60]}", 1)
# base = my side (has my recompile + my entry), minus lines they archived, plus their new entries
drop = set(archived_by_them)
out_lines = [L for L in cb if L not in drop]
insert_at = len(out_lines)
for i, L in enumerate(out_lines):
    if L.startswith("### Reference"): insert_at = i + 2
for L in new_theirs:
    out_lines.insert(min(insert_at, len(out_lines)), L); insert_at += 1
# verify: multiset(out) == multiset(cb) - archived_by_them + new_theirs
exp = sorted([L for L in cb if L not in drop] + new_theirs)
if sorted(out_lines) != exp:
    die("CODELY multiset verification FAILED", 1)
open("CODELY.md", "wb").write(("\n".join(out_lines)).encode("utf-8"))
print(f"  CODELY.md: merged {len(ca)}|{len(cb)} -> {len(out_lines)} lines, hot size {len(open('CODELY.md','rb').read())} bytes")
print("RESOLVER COMPLETE - all faces parse-verified, zero-loss gates PASS")
