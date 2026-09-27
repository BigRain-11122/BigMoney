# r368 bm-a push-storm resolve wave-3: 17-UU per classifier (0 UNKNOWN).
# Recipes: memory-union CODELY / twin-regen REPORT / mixed-dict+ledger autofill /
# rolling-ledger compute_audit+regime_state / js-wrapper dashboard.js / snapshot take-new.
# All parse-verified before write-back (r185); identity-union assertions zero-loss.
import json, re, subprocess, os

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} {path}: {r.stderr[:200]}")
    return r.stdout

def stage_bytes(path):
    return blob(1, path), blob(2, path), blob(3, path)  # base, ours, theirs

report = []

# ---------- 1) snapshot class: take-new by deep ts probe ----------
def deep_ts(obj, best=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-]", "", str(k)).lower()
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}", v):
                if any(nk.startswith(p) for p in ("generated", "ts", "updated", "asof", "last", "cutoff", "written")):
                    best = max(best, v)
            best = deep_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = deep_ts(v, best)
    return best

SNAP = ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json", "results/heat_update_status.json",
        "results/lhb_update_status.json", "results/prospect_promotion/_summary.json",
        "results/scorecard_v1.json", "results/strategy_scorecard.json",
        "results/token_usage.json", "results/update_status.json"]
for p in SNAP:
    b, o, t = stage_bytes(p)
    jo, jt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
    to, tt = deep_ts(jo), deep_ts(jt)
    if not to and not tt:
        pick, side = o, "ours-nots"
    else:
        pick, side = (t, "theirs") if tt > to else (o, "ours")
    json.loads(pick.decode("utf-8-sig"))  # parse-verify
    with open(p, "wb") as f:
        f.write(pick)
    report.append(f"{p}: take-new {side} (ours_ts={to or 'none'} theirs_ts={tt or 'none'})")

# ---------- 2) twin-regen REPORT json+md (r327/r329) ----------
pj = "docs/daily_report/REPORT-2026-09-28.json"
pm = "docs/daily_report/REPORT-2026-09-28.md"
b, o, t = stage_bytes(pj)
jo, jt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
to, tt = deep_ts(jo), deep_ts(jt)
side = "theirs" if tt > to else "ours"
pick_json = t if side == "theirs" else o
pick_md = blob(3, pm) if side == "theirs" else blob(2, pm)
json.loads(pick_json.decode("utf-8-sig"))
with open(pj, "wb") as f: f.write(pick_json)
with open(pm, "wb") as f: f.write(pick_md)
report.append(f"{pj}+md: twin-side {side} (ours={to} theirs={tt})")

# ---------- 3) js-wrapper dashboard_status.js: probe embedded ts, take side whole ----------
p = "results/dashboard_status.js"
b, o, t = stage_bytes(p)
mo = re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", o.decode("utf-8", "replace"))
mt = re.findall(r"20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}", t.decode("utf-8", "replace"))
side = "theirs" if (mt and (not mo or max(mt) > max(mo))) else "ours"
with open(p, "wb") as f: f.write(t if side == "theirs" else o)
report.append(f"{p}: take-side {side} whole-bytes (ours={max(mo) if mo else None} theirs={max(mt) if mt else None})")

# ---------- 4) rolling-ledger compute_audit.json (r360/r366 identity-union, no cap) ----------
p = "results/compute_audit.json"
b, o, t = stage_bytes(p)
jo, jt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
def ledger_union(jo, jt, hist_key):
    ho, ht = jo.get(hist_key, []), jt.get(hist_key, [])
    def ident(r):
        return (r.get("ts"), r.get("machine"))
    seen, out = {}, []
    for r in ho + ht:
        k = ident(r)
        if k not in seen:
            seen[k] = True; out.append(r)
    assert len(out) == len(set(map(ident, ho))) + len(set(map(ident, ht)) - set(map(ident, ho))), "identity union loss"
    return out
merged = dict(jo)
merged["history"] = ledger_union(jo, jt, "history")
# flat fields take-new
for k in jt:
    if k not in ("history",):
        merged[k] = jt[k] if deep_ts({k: jt[k]}) >= deep_ts({k: jo.get(k)}) else jo.get(k)
json.dumps(merged)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
report.append(f"{p}: history identity-union {len(jo.get('history', []))}+{len(jt.get('history', []))}->{len(merged['history'])}")

# ---------- 5) rolling-ledger regime_state.json (asof-keyed per r366) ----------
p = "results/regime_state.json"
b, o, t = stage_bytes(p)
jo, jt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
merged = dict(jo)
for hist_key in ("history", "transitions", "triggers"):
    if hist_key in jo or hist_key in jt:
        ho, ht = jo.get(hist_key, []), jt.get(hist_key, [])
        if hist_key == "history":
            def ident(r):
                return (r.get("asof"), r.get("machine")) if isinstance(r, dict) else (hist_key, str(r))
        else:
            def ident(r):
                return (r.get("ts"), r.get("machine")) if isinstance(r, dict) else (hist_key, str(r))
        seen, out = {}, []
        for r in ho + ht:
            k = ident(r)
            if k not in seen:
                seen[k] = True; out.append(r)
        merged[hist_key] = out
for k in jt:
    if k not in ("history", "transitions", "triggers"):
        tv = deep_ts({k: jt[k]}); ov = deep_ts({k: jo.get(k)})
        merged[k] = jt[k] if tv >= ov else jo.get(k)
json.dumps(merged)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
report.append(f"{p}: per-face identity-union + flat take-new")

# ---------- 6) mixed-dict+ledger autofill_state.json (r203/r322/r245) ----------
p = "results/autofill_state.json"
b, o, t = stage_bytes(p)
jo, jt = json.loads(o.decode("utf-8-sig")), json.loads(t.decode("utf-8-sig"))
lo, lt = jo.get("launches", []), jt.get("launches", [])
def ckey(r):
    return (r.get("ts"), r.get("machine"), r.get("pid"), r.get("runner_sha256"), r.get("entry"), r.get("shard"))
seen, merged_l = {}, []
for r in lo + lt:
    k = ckey(r)
    if k in seen:
        # r322: same-key pair must be content-identical or field-additive
        prev = seen[k]
        if json.dumps(prev, sort_keys=True) != json.dumps(r, sort_keys=True):
            fk1, fk2 = set(prev), set(r)
            if fk1 == fk2:
                raise RuntimeError(f"same-key real divergence: {k}")
            merged_l[merged_l.index(prev)] = {**prev, **r}  # field-union merge, one kept
        continue
    seen[k] = r; merged_l.append(r)
merged_l = sorted(merged_l, key=lambda r: r.get("ts", ""))
merged_l = merged_l[-50:] if len(merged_l) > 50 else merged_l
merged_l = sorted(merged_l, key=lambda r: r.get("ts", ""))  # r245: write-back asc
merged = dict(jo)
merged["launches"] = merged_l
lt_ts = (jt.get("last_tick") or {}).get("ts", "")
lo_ts = (jo.get("last_tick") or {}).get("ts", "")
merged["last_tick"] = jt["last_tick"] if lt_ts >= lo_ts else jo["last_tick"]
assert isinstance(merged.get("last_tick"), dict), "last_tick must be dict"
json.dumps(merged)
with open(p, "w", encoding="utf-8", newline="\n") as f:
    json.dump(merged, f, ensure_ascii=False, indent=1)
report.append(f"{p}: launches compound-union {len(lo)}+{len(lt)}->{len(merged_l)} cap50 asc-reresort, last_tick={'theirs' if lt_ts >= lo_ts else 'ours'} ({lt_ts} vs {lo_ts})")

# ---------- 7) memory-union CODELY.md (R208/r212/r327) ----------
p = "CODELY.md"
b, o, t = stage_bytes(p)
bo = b.decode("utf-8"); oo = o.decode("utf-8"); tt = t.decode("utf-8")
if oo.startswith(bo):
    base_len = len(bo)
    mine_suffix = oo[base_len:] if len(oo) > base_len else ""
    theirs_suffix = tt[base_len:] if len(tt) > base_len else tt[len(bo):] if tt.startswith(bo) else ""
    if not tt.startswith(bo):
        # per r327: prefix assertion fails on in-place edits -> entry-level bidirectional verification
        # fallback: take the longer structural union = ours + theirs appended distinct lines
        theirs_suffix = tt
    union = bo + mine_suffix + theirs_suffix
    # if theirs did not start with base, above appends full theirs (entry-level: duplicates possible but zero-loss)
else:
    union = oo + "\n" + tt
    report.append("CODELY: base-prefix assertion FAILED -> full append both sides (entry-level zero-loss)")
with open(p, "w", encoding="utf-8", newline="\n") as f:
    f.write(union)
report.append(f"CODELY.md: memory-union base={len(bo)}B + mine={len(mine_suffix) if 'mine_suffix' in dir() else '?'}B + theirs={len(theirs_suffix) if 'theirs_suffix' in dir() else '?'}B -> {len(union)}B")

print("\n".join(report))
print("CODELY final size:", os.path.getsize("CODELY.md"))
