# -*- coding: utf-8 -*-
"""R262 bm-b: push-collision resolver (19 conflicts, skill recipes + manual
adjudication of 7 UNKNOWN files). YIELD law: bm-a R258/R259 landed first ->
duplicate slice-D deliverables yield; unique deliverables (T-82 sender leg,
identity lessons, forensics probes) survive. Stage semantics in rebase:
:1 = ancestor, :2 = origin/bm-a side, :3 = replayed/mine."""
import io
import json
import subprocess

TS_KEYS = ("ts", "updated", "generated", "as_of", "last_attempt", "time",
           "generated_at")


def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout


def jload(n, path):
    return json.loads(stage(n, path).decode("utf-8-sig"))


def wfile(path, data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    io.open(path, "wb").write(data)


def probe_face(raw):
    return {"bom": raw.startswith(b"\xef\xbb\xbf"),
            "crlf": b"\r\n" in raw,
            "trailing_nl": raw.endswith(b"\n")}


def ts_of(d):
    for k in TS_KEYS:
        v = d.get(k) if isinstance(d, None | dict) else None
        if isinstance(v, str) and v:
            return k, v
    return None, None


def dump_face(d, face):
    """serialize mirroring the :2 face (indent 1 compact used by producers
    probed at write time; here mirror actual :2 face params)."""
    txt = json.dumps(d, ensure_ascii=False, indent=1)
    if not face["trailing_nl"]:
        txt = txt.rstrip("\n")
    out = txt.encode("utf-8")
    if face["bom"]:
        out = b"\xef\xbb\xbf" + out
    if face["crlf"]:
        out = out.replace(b"\n", b"\r\n")
    return out


log = []


def note(m):
    log.append(m)
    print(m, flush=True)

# ============ 1. UNKNOWN: daily_report pair -> take :3 (mine newer) ============
for n in (2, 3):
    pass
d2 = jload(2, "docs/daily_report/REPORT-2026-09-26.json")
d3 = jload(3, "docs/daily_report/REPORT-2026-09-26.json")
_, t2 = ts_of(d2)
_, t3 = ts_of(d3)
assert t3 > t2, f"expected mine newer: {t3} vs {t2}"
wfile("docs/daily_report/REPORT-2026-09-26.json", stage(3, "docs/daily_report/REPORT-2026-09-26.json"))
wfile("docs/daily_report/REPORT-2026-09-26.md", stage(3, "docs/daily_report/REPORT-2026-09-26.md"))
note(f"daily_report pair: take :3 (mine {t3} > {t2}) whole-side both files")

# ============ 2. UNKNOWN: AA duplicate slice-D deliverables -> yield to bm-a ============
# canonical script + artifact = :2 (bm-a); mine archived; my script discarded
# (its prereg block lives on inside the archived artifact)
wfile("scripts/t73_s2_factor_history.py", stage(2, "scripts/t73_s2_factor_history.py"))
mine_art = stage(3, "results/t73_s2/factor_history.json")
wfile("results/t73_s2/factor_history.json", stage(2, "results/t73_s2/factor_history.json"))
wfile("results/t73_s2/factor_history_bmb_r262_duplicate_yield.json", mine_art)
note("slice-D yield: canonical script+artifact = bm-a's (:2); my artifact "
     "archived results/t73_s2/factor_history_bmb_r262_duplicate_yield.json; "
     "my script discarded (prereg preserved inside archived artifact)")

# digest: unconflicted mine in tree -> rename with YIELD marker + banner
old_dg = "research/digests/DIGEST-20260926-t73-s2-sliceD-factor-history.md"
new_dg = ("research/digests/"
          "DIGEST-20260926-t73-s2-sliceD-factor-history-BMB-R262-YIELD.md")
dg = io.open(old_dg, encoding="utf-8").read()
dg = dg.replace("# DIGEST-20260926-t73-s2-sliceD", "# [BMB-R262 YIELD ARCHIVE "
               "-- duplicate batch yielded to bm-a R258 per commit-time "
               "order; canonical slice-D = bm-a's artifact; this file "
               "documents the ARCHIVED duplicate for cross-machine "
               "replication evidence] DIGEST-20260926-t73-s2-sliceD", 1)
wfile(new_dg, dg.encode("utf-8"))
subprocess.run(["git", "rm", "-q", "--cached", old_dg], check=False)
import os
os.remove(old_dg)
note(f"digest renamed {old_dg} -> {new_dg} with YIELD banner")

# ============ 3. UNKNOWN: T-73 ticket = :2 + progress_r262 yield note ============
tk = jload(2, "fleet/tasks/T-2026-09-26-73-P1.json")
tk["progress_r262"] = (
    "r262 bm-b YIELD NOTE (same-window duplicate; fleet/README s4 "
    "commit-time order: bm-a R258 98a54985 < bm-b r262 push 17:3x -> bm-b "
    "yields). Identity-incident session (started by misreading PULLED "
    "TRACKED state-bm-a.json as local state, executed the R257 next-slice "
    "pointer under the bm-a lens; four-source probe re-established bm-b "
    "mid-round) independently built slice-D in the same window as bm-a "
    "R258. Duplicate deliverables yielded in rebase: canonical "
    "script+artifact = bm-a's (mktcap sidecar, exchange-exact raw_close "
    "lineage); my batch ARCHIVED at results/t73_s2/"
    "factor_history_bmb_r262_duplicate_yield.json (+ digest renamed "
    "-BMB-R262-YIELD). REPLICATION EVIDENCE (independent same-window "
    "implementations, dA row-multiset family value): both agree on the "
    "overlapping law verdicts -- LOWVOL alive ALL eras negative (mine: "
    "pre2005 -0.034 .. 2021-2024 -0.088 .. 2025+ -0.048 never flipped; "
    "theirs: all-era-uniform), SIZE 2017-2020 sign inversion (mine era IC "
    "+0.0075; theirs regime-map sign-flip crown), both OOS-alive. "
    "COMPLEMENTARY faces (not consumed, future prereg may cite): my "
    "dividend style-history era table (510880vs510300: 2021-2024 "
    "+12.39%/yr, 2025+ reversal -8.63% in case, price-face bias-against "
    "disclosed) vs their dividend defensive maxDD-halved face -- different "
    "faces of the same law family. Unit forensics kept (true regardless "
    "of artifact winner): 688 volume-unit doc-lore vs operative-cache "
    "split (amount/volume~close anchors x1.0007/x1.0014; probe "
    "results/_r258bma_688_probe.py + CODELY 17:2x entry) + identity "
    "pit law (CODELY 17:3x entry). NOT part of yield (unique deliverables "
    "same round): T-82 deep-bcd SENDER LEG (branch "
    "transfer/t80-deep-bcd-basis 2ef23068 pushed + 6/6 blob byte-verified "
    "vs MSG-1556 + manifest + receipt MSG-20260926-172x, see T-82 "
    "progress_r262). Helper-name note: my wrong-identity-era "
    "_r258bma_ticket_{probe,update}.py renamed _r262bmb_* (bm-a owns the "
    "_r258bma prefix by right: their R258 + their machine suffix).")
wfile("fleet/tasks/T-2026-09-26-73-P1.json",
      dump_face(tk, {"bom": False, "crlf": False, "trailing_nl": False}))
json.loads(io.open("fleet/tasks/T-2026-09-26-73-P1.json", encoding="utf-8").read())
note("T-73 ticket: :2 fields + progress_r262 rewritten as YIELD note "
     "(parse-verified)")

# ============ 4. UNKNOWN: AA misnamed helpers -> bm-a keeps path, mine renamed ============
for src, dst in [
    ("results/_r258bma_ticket_probe.py", "results/_r262bmb_ticket_probe.py"),
    ("results/_r258bma_ticket_update.py", "results/_r262bmb_ticket_update.py"),
]:
    mine = stage(3, src)
    wfile(src, stage(2, src))
    wfile(dst, mine)
    note(f"AA helper {src}: bm-a's keeps path; mine -> {dst}")

# ============ 5. memory-union: CODELY.md = :2 + my 4 new lines ============
base_lines = stage(1, "CODELY.md").decode("utf-8").splitlines()
mine_lines = stage(3, "CODELY.md").decode("utf-8").splitlines()
new_mine = mine_lines[len(base_lines):]
out = stage(2, "CODELY.md").decode("utf-8").splitlines() + new_mine
wfile("CODELY.md", ("\n".join(out) + "\n").encode("utf-8"))
note(f"CODELY union: :2 ({len(stage(2, 'CODELY.md').decode('utf-8').splitlines())} "
     f"lines) + my {len(new_mine)} new lines; dedupe none needed "
     f"(verified disjoint by probe)")

# ============ 6. mixed-dict+ledger: autofill_state.json ============
a2 = jload(2, "results/autofill_state.json")
a3 = jload(3, "results/autofill_state.json")
face2 = probe_face(stage(2, "results/autofill_state.json"))
l2, l3 = a2.get("launches", []), a3.get("launches", [])
k2, _ = ts_of(l2[0]) if l2 else (None, None)
assert k2, "launches ts key not found"
seen = {}
for row in l2 + l3:
    key = row.get(k2)
    if key is not None and (key not in seen or True):
        seen[key] = row          # later same-ts overwrite = same-second tie
union = sorted(seen.values(), key=lambda r: r[k2])[-50:]
union = sorted(union, key=lambda r: r[k2])   # r245 law: write-back ts ASC
lt2, lt3 = a2.get("last_tick", {}), a3.get("last_tick", {})
_, lts2 = ts_of(lt2) if isinstance(lt2, dict) else (None, None)
_, lts3 = ts_of(lt3) if isinstance(lt3, dict) else (None, None)
if (lts3 or "") >= (lts2 or ""):
    a2["last_tick"] = lt3
a2["launches"] = union
wfile("results/autofill_state.json", dump_face(a2, face2))
chk = json.loads(io.open("results/autofill_state.json", encoding="utf-8-sig").read())
assert isinstance(chk.get("last_tick"), dict), "last_tick must be dict"
assert len(chk["launches"]) == len(union)
note(f"autofill_state: launches union |{len(l2)}+{len(l3)}| -> {len(union)} "
     f"ts-asc cap50; last_tick whole-dict by inner ts ({lts3} >= {lts2}); "
     f"face {face2}; isinstance(last_tick, dict) OK")

# ============ 7. rolling-ledger: compute_audit.json ============
c2 = jload(2, "results/compute_audit.json")
c3 = jload(3, "results/compute_audit.json")
face2 = probe_face(stage(2, "results/compute_audit.json"))
h2 = c2.get("history", [])
h3 = c3.get("history", [])
k2, _ = ts_of(h2[0]) if h2 else (None, None)
seen = {}
for row in h2 + h3:
    t = row.get(k2)
    key = (t, json.dumps(row, sort_keys=True, ensure_ascii=False))
    seen[key] = row
union = sorted(seen.values(), key=lambda r: r[k2])
_, ct2 = ts_of(c2)
_, ct3 = ts_of(c3)
winner = c2 if (ct2 or "") >= (ct3 or "") else c3
out = dict(winner)
out["history"] = union
wfile("results/compute_audit.json", dump_face(out, face2))
json.loads(io.open("results/compute_audit.json", encoding="utf-8-sig").read())
note(f"compute_audit: history union |{len(h2)}+{len(h3)}| -> {len(union)} "
     f"ts-asc zero-loss; snapshot take-new by {ct3} vs {ct2}")

# ============ 8. rolling-ledger + dedupe: regime_state.json ============
r2 = jload(2, "results/regime_state.json")
r3 = jload(3, "results/regime_state.json")
face2 = probe_face(stage(2, "results/regime_state.json"))
t2l = r2.get("transitions", [])
t3l = r3.get("transitions", [])
seen = {}
for row in t2l + t3l:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    seen[key] = row
k2, _ = ts_of(t2l[0]) if t2l else (None, None)
union = sorted(seen.values(), key=lambda r: r.get(k2, "")) if k2 else list(seen.values())
_, rt2 = ts_of(r2)
_, rt3 = ts_of(r3)
winner = r2 if (rt2 or "") >= (rt3 or "") else r3
out = dict(winner)
out["transitions"] = union
wfile("results/regime_state.json", dump_face(out, face2))
json.loads(io.open("results/regime_state.json", encoding="utf-8-sig").read())
note(f"regime_state: transitions identity-dedupe union |{len(t2l)}+{len(t3l)}| "
     f"-> {len(union)}; state take-new ({rt3} vs {rt2})")

# ============ 9. js-wrapper + snapshots: take-new whole bytes ============
# js wrapper: compare meta.generated_at inside both stages
import re
def js_gen(raw):
    m = re.search(rb'"generated_at"\s*:\s*"([^"]+)"', raw)
    return m.group(1).decode() if m else ""
js2 = stage(2, "results/dashboard_status.js")
js3 = stage(3, "results/dashboard_status.js")
g2, g3 = js_gen(js2), js_gen(js3)
win = js3 if g3 >= g2 else js2
wfile("results/dashboard_status.js", win)
note(f"dashboard_status.js: whole-byte take-side by generated_at "
     f"({g3} vs {g2}) -> {'mine' if g3 >= g2 else 'bm-a'}")

SNAPS = ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
         "results/futures_update_status.json", "results/heat_update_status.json",
         "results/lhb_update_status.json", "results/token_usage.json",
         "results/update_status.json"]
for p in SNAPS:
    d2 = jload(2, p)
    d3 = jload(3, p)
    _, s2 = ts_of(d2)
    _, s3 = ts_of(d3)
    assert s2 and s3, f"ts key not found for {p}"
    win = 3 if s3 >= s2 else 2
    wfile(p, stage(win, p))
    json.loads(io.open(p, encoding="utf-8-sig").read())
    note(f"{p}: take :{win} ({'mine ' + s3 if win == 3 else 'bm-a ' + s2})")

io.open("results/_r262bmb_resolve_log.json", "w", encoding="utf-8",
        newline="\n").write(json.dumps(log, ensure_ascii=False, indent=1) + "\n")
print("RESOLVER DONE:", len(log), "resolutions")
