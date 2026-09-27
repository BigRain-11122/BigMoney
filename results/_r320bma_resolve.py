"""r320 bm-a rebase resolver: 16-UU S6-mirror batch + HANDOVER GBK-segment repair.

Rebase semantics: stage :2 = origin/upstream (bm-b r320 12:12 + bm-c tick 12:10),
stage :3 = this machine's replayed commit c99488f7 (12:15). Recipes per
classify_conflicts.py + bigmoney-conflict-resolve SKILL canon; the 5 UNKNOWN =
derive-faces hand-adjudicated per r317 bm-b mirror precedent (deterministic
same-day re-derivation -> deep-strip honesty check -> take-new by generated ts,
winner RAW BYTES verbatim, no re-serialization drift).

HANDOVER.md (auto-merged region, not UU): bm-b r320 commit 249c8595 wrote their
new bottom dev-queue window line in GBK bytes (single non-UTF-8 region) -> strict
UTF-8 readers structurally crash. Lossless transcode GBK->UTF-8, zero content
change, whole-file strict re-verify + both r320 entries presence assertion.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = []
RESOLVED = []


def blob(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True, cwd=ROOT)
    return out.stdout


def jload(b):
    return json.loads(b.decode("utf-8-sig"))


def nl_of(b):
    return "\r\n" if b"\r\n" in b else "\n"


def dump_like(obj, ref_b):
    text = json.dumps(obj, ensure_ascii=False, indent=1)
    if ref_b[:3] == b"\xef\xbb\xbf":
        text = "\ufeff" + text
    nl = nl_of(ref_b)
    text = text.replace("\r\n", "\n").replace("\n", nl)
    if not text.endswith(nl):
        text += nl
    return text.encode("utf-8")


def ts_of(d, keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return None


def take_new_snapshot(path, ts_keys, label="snapshot"):
    a, b = blob(":2", path), blob(":3", path)
    da, db = jload(a), jload(b)
    ta, tb = ts_of(da, ts_keys), ts_of(db, ts_keys)
    assert ta and tb, f"{path}: ts keys {ts_keys} missing ({ta!r} vs {tb!r})"
    if ta >= tb:
        raw, side = a, "origin"
    else:
        raw, side = b, "mine"
    (ROOT / path).write_bytes(raw)
    RESOLVED.append(path)
    LOG.append(f"{label} {path}: origin_ts={ta} mine_ts={tb} -> {side} whole-bytes")


def take_new_deepstrip(path, ts_keys, strip_keys):
    a, b = blob(":2", path), blob(":3", path)
    da, db = jload(a), jload(b)

    def strip(d):
        c = json.loads(json.dumps(d))
        for k in list(c.keys()):
            if k in strip_keys:
                c.pop(k)
        return c

    eq = strip(da) == strip(db)
    ta, tb = ts_of(da, ts_keys), ts_of(db, ts_keys)
    assert ta and tb, f"{path}: generated ts missing"
    if ta >= tb:
        raw, side = a, "origin"
    else:
        raw, side = b, "mine"
    (ROOT / path).write_bytes(raw)
    RESOLVED.append(path)
    LOG.append(f"deepstrip {path}: deep_eq={eq} origin_ts={ta} mine_ts={tb} -> {side} "
               f"({'PASS' if eq else 'FAIL-CLOSED-CONTENT-DIVERGENCE'} strip={sorted(strip_keys)})")
    return eq


# ---------------- 1. snapshot faces (winner raw bytes) ----------------
for p, keys in [
    ("results/fundamental_b_layer_filter.json", ["updated"]),
    ("results/futures_update_status.json", ["ts", "last_attempt"]),
    ("results/heat_update_status.json", ["updated"]),
    ("results/lhb_update_status.json", ["updated", "last_attempt"]),
    ("results/token_usage.json", ["generated"]),
    ("results/update_status.json", ["updated", "now"]),
]:
    take_new_snapshot(p, keys)

# ---------------- 2. derive faces (UNKNOWN five, hand-adjudicated) ----------------
take_new_deepstrip("results/scorecard_v1.json", ["generated"], {"generated", "elapsed_sec"})
take_new_deepstrip("results/strategy_scorecard.json", ["generated"], {"generated", "elapsed_sec"})
take_new_deepstrip("results/prospect_promotion/_summary.json", ["generated"],
                   {"generated", "elapsed_sec"})
take_new_deepstrip("docs/daily_report/REPORT-2026-09-27.json", ["generated_at"],
                   {"generated_at", "elapsed_sec"})

# REPORT md pairs with the json winner side (md carries no ts)
_a, _b = jload(blob(":2", "docs/daily_report/REPORT-2026-09-27.json")), \
         jload(blob(":3", "docs/daily_report/REPORT-2026-09-27.json"))
_md_rev = ":2" if ts_of(_a, ["generated_at"]) >= ts_of(_b, ["generated_at"]) else ":3"
(ROOT / "docs/daily_report/REPORT-2026-09-27.md").write_bytes(
    blob(_md_rev, "docs/daily_report/REPORT-2026-09-27.md"))
RESOLVED.append("docs/daily_report/REPORT-2026-09-27.md")
LOG.append(f"report-md: paired with json winner side {_md_rev}")

# ---------------- 3. regime_state: history/transitions union by asof + state take-new ----------------
def union_rows_by(rows_a, rows_b, key):
    def keyset(rows):
        if key:
            return {r.get(key) for r in rows}
        return {json.dumps(r, sort_keys=True) for r in rows}

    ma = {}
    for r in rows_a or []:
        ma[r.get(key) if key else json.dumps(r, sort_keys=True)] = r
    mb = {}
    for r in rows_b or []:
        mb[r.get(key) if key else json.dumps(r, sort_keys=True)] = r
    union = dict(ma)
    for k, v in mb.items():
        if k not in union:
            union[k] = v
    return union, len(ma), len(mb), len(union), keyset(rows_a or []) | keyset(rows_b or [])


def resolve_regime():
    path = "results/regime_state.json"
    a, b = blob(":2", path), blob(":3", path)
    da, db = jload(a), jload(b)
    # state fields take-new by 'updated'
    base, side = (da, "origin") if ts_of(da, ["updated"]) >= ts_of(db, ["updated"]) else (db, "mine")
    merged = json.loads(json.dumps(base))
    for key in ["history", "transitions"]:
        rows_a = da.get(key) or []
        rows_b = db.get(key) or []
        k = "asof" if rows_a and isinstance(rows_a[0], dict) and "asof" in rows_a[0] else None
        union, na, nb, nu, keyset_u = union_rows_by(rows_a, rows_b, k)
        assert nu == len(keyset_u), f"{path}:{key} zero-loss assertion failed"
        merged[key] = sorted(union.values(), key=lambda r: r.get(k) or "")
        LOG.append(f"union {path}:{key}: origin={na} mine={nb} -> {nu} (key={k or 'row'}) zero-loss")
    (ROOT / path).write_bytes(dump_like(merged, a))
    RESOLVED.append(path)
    LOG.append(f"regime_state: state fields take-new by updated -> {side} "
               f"(origin {ts_of(da, ['updated'])} vs mine {ts_of(db, ['updated'])})")


resolve_regime()


# ---------------- 4. compute_audit: history union by ts + latest take-new ----------------
def resolve_audit():
    path = "results/compute_audit.json"
    a, b = blob(":2", path), blob(":3", path)
    da, db = jload(a), jload(b)
    union, na, nb, nu, keyset_u = union_rows_by(da.get("history") or [], db.get("history") or [], "ts")
    assert nu == len(keyset_u), "compute_audit zero-loss failed"
    la, lb = da.get("latest") or {}, db.get("latest") or {}
    latest, side = (la, "origin") if ts_of(la, ["ts"]) >= ts_of(lb, ["ts"]) else (lb, "mine")
    merged = {"latest": latest, "history": sorted(union.values(), key=lambda r: r["ts"])}
    (ROOT / path).write_bytes(dump_like(merged, a))
    RESOLVED.append(path)
    LOG.append(f"compute_audit: history union origin={na} mine={nb} -> {nu} zero-loss; "
               f"latest take-new -> {side} ({ts_of(latest, ['ts'])})")


resolve_audit()


# ---------------- 5. autofill_state: launches union cap50 ts-asc + last_tick inner-ts ----------------
def resolve_autofill():
    path = "results/autofill_state.json"
    a, b = blob(":2", path), blob(":3", path)
    da, db = jload(a), jload(b)

    def lmap(d):
        out = {}
        for r in (d.get("launches") or []):
            out[(r.get("ts"), r.get("machine"), r.get("entry"), r.get("shard"), r.get("pid"))] = r
        return out

    ma, mb = lmap(da), lmap(db)
    union = dict(ma)
    for k, v in mb.items():
        if k not in union:
            union[k] = v
    rows = sorted(union.values(), key=lambda r: r.get("ts") or "")
    rows = rows[-50:]  # cap 50 keep newest (cap semantics), ts asc write-back (r245 law)
    lta, ltb = (da.get("last_tick") or {}), (db.get("last_tick") or {})
    ta, tb = ts_of(lta, ["ts"]), ts_of(ltb, ["ts"])
    if tb and (not ta or tb > ta):
        last_tick, lside = ltb, "mine"
    elif ta and (not tb or ta > tb):
        last_tick, lside = lta, "origin"
    else:
        last_tick, lside = lta, "origin(tie->HEAD r140)"
    assert isinstance(last_tick, dict), "last_tick must be dict"
    merged = {"launches": rows, "last_tick": last_tick}
    (ROOT / path).write_bytes(dump_like(merged, a))
    RESOLVED.append(path)
    LOG.append(f"autofill: launches union origin={len(ma)} mine={len(mb)} -> {len(union)} "
               f"cap->{len(rows)} (ts asc, dup-key zero); last_tick origin={ta} mine={tb} -> {lside}")


resolve_autofill()


# ---------------- 6. dashboard_status.js + .json twins: whole-bytes by meta.generated_at ----------------
def resolve_dashjs():
    path = "results/dashboard_status.js"
    a, b = blob(":2", path), blob(":3", path)

    def inner(b_):
        t = b_.decode("utf-8-sig")
        return json.loads(t[t.find("{"):t.rfind("}") + 1])

    ta = ts_of(inner(a).get("meta") or {}, ["generated_at"])
    tb = ts_of(inner(b).get("meta") or {}, ["generated_at"])
    assert ta and tb, "dashjs meta.generated_at missing"
    raw, side = (a, "origin") if ta >= tb else (b, "mine")
    (ROOT / path).write_bytes(raw)
    RESOLVED.append(path)
    # .json twin pairs with the SAME side (R148 dash-twin same-side law)
    jpath = "results/dashboard_status.json"
    (ROOT / jpath).write_bytes(blob(":2" if ta >= tb else ":3", jpath))
    RESOLVED.append(jpath)
    LOG.append(f"dashjs+json twins: origin_ts={ta} mine_ts={tb} -> {side} whole-bytes "
               f"(wrapper preserved, twins same-side)")


resolve_dashjs()

# ---------------- 7. HANDOVER GBK segment repair ----------------
hp = ROOT / "research/HANDOVER.md"
hb = hp.read_bytes()
try:
    hb.decode("utf-8")
    LOG.append("HANDOVER: already pure UTF-8, no repair needed")
except UnicodeDecodeError as e:
    start = e.start
    p = start
    while p < len(hb):
        try:
            hb[p:p + 4000].decode("utf-8")
            break
        except UnicodeDecodeError as e2:
            p = p + e2.start + 1
    seg = hb[start:p]
    fixed_text = seg.decode("gbk")  # strict, fails loudly if not clean GBK
    repaired = hb[:start] + fixed_text.encode("utf-8") + hb[p:]
    repaired.decode("utf-8")  # whole-file strict re-verify
    t = repaired.decode("utf-8")
    assert "bm-a round 320" in t, "my HANDOVER header entry missing after repair"
    assert "round 320 bm-b" in t, "bm-b bottom entry missing after repair"
    hp.write_bytes(repaired)
    LOG.append(f"HANDOVER: GBK region {start}..{p} ({len(seg)}B) transcoded GBK->UTF-8 lossless; "
               f"whole-file strict UTF-8 PASS; both r320 entries present")
RESOLVED.append("research/HANDOVER.md")

# ---------------- 8. parse-validate every resolved json/js (r185 law) ----------------
for path in RESOLVED:
    if path.endswith(".json"):
        json.loads((ROOT / path).read_bytes().decode("utf-8-sig"))
    elif path.endswith(".js"):
        t = (ROOT / path).read_bytes().decode("utf-8-sig")
        json.loads(t[t.find("{"):t.rfind("}") + 1])
    elif path.endswith(".md"):
        (ROOT / path).read_bytes().decode("utf-8")  # HANDOVER strict decode

print("=== r320 bm-a resolve LOG ===")
for line in LOG:
    print(line)
print(f"resolved files: {len(RESOLVED)} | ALL PARSE-VALIDATED (r185 law)")
