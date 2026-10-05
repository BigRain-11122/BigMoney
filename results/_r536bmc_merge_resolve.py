"""r536 bm-c merge resolver (merge-mode canon, r725/r715/r511 lineage).

6 UU faces, diff-filter=U census (r713 law):
- 5 snapshot faces -> take-ours verbatim bytes (OURS-NEW by ts: our S6 regen
  11:49-51 vs bm-b r725 wave 11:32-11:36; all deterministic same-panel regen)
- compute_audit.json -> rolling union on history key (r188/R208, r522 values()
  + type gate): dynamic |A u B| zero loss, ts-sorted; latest = ours (newer)
Laws applied: r710-A/B (subprocess bytes capture, stage-empty gate), r185
(parse-verify before write+add), r522 (union=dict.values, type gate), r704
(post-write readback assert), r515 (sides from index stages, merge-mode :2:=ours)."""
import subprocess, json, hashlib, re, sys, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
TAKE_OURS = [
    "results/regime_state.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/update_status.json",
]
UNION_LEDGER = "results/compute_audit.json"
RECEIPT = "results/_r536bmc_merge_resolve.json"


def stage(n, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f":{n}:{path}"], capture_output=True)
    # r710-B gate: empty stdout = stage-absent signal, never "empty file"
    assert r.returncode == 0 and len(r.stdout) > 100, f"stage {n} {path} rc={r.returncode} len={len(r.stdout)}"
    return r.stdout


def wpath(rel):
    return os.path.join(ROOT, rel.replace("/", "\\"))


def no_markers(b):
    return not any(m in b for m in (b"<<<<<<<", b">>>>>>>", b"|||||||"))


receipt = {"round": "r536 bm-c merge (bm-b r725 wave, push-race recovery)",
           "faces": {}, "laws": "r188/R208/r185/r522/r704/r710/r715/r713"}

# --- leg 1: take-ours verbatim (byte-exact, zero reserialization drift) ---
for p in TAKE_OURS:
    ob, tb = stage(2, p), stage(3, p)
    assert no_markers(ob) and no_markers(tb), f"marker in stage blob {p}"
    o, t = json.loads(ob), json.loads(tb)
    with open(wpath(p), "wb") as f:
        f.write(ob)
    back = open(wpath(p), "rb").read()
    assert back == ob, f"readback byte mismatch {p}"
    json.loads(back)  # r185 parse gate
    receipt["faces"][p] = {
        "recipe": "take-ours-verbatim",
        "ours_bytes": len(ob), "theirs_bytes": len(tb),
        "ours_updated": o.get("updated") or o.get("ts") or o.get("last_attempt"),
        "theirs_updated": t.get("updated") or t.get("ts") or t.get("last_attempt"),
        "md5": hashlib.md5(back).hexdigest(),
    }
    print(f"TAKE-OURS {p} ({len(ob)}B) ok")

# --- leg 2: compute_audit rolling union (dynamic, no hardcoded counts) ---
ob, tb = stage(2, UNION_LEDGER), stage(3, UNION_LEDGER)
assert no_markers(ob) and no_markers(tb)
o, t = json.loads(ob), json.loads(tb)
oh, th = o["history"], t["history"]
oid = {}
for row in oh:
    oid[json.dumps(row, sort_keys=True)] = row          # key=dedup id, value=row object (r522)
for row in th:
    oid.setdefault(json.dumps(row, sort_keys=True), row)
union = list(oid.values())                               # r522: values(), never list(dict)
assert all(isinstance(r, dict) for r in union), "r522 type gate"
ours_ids = set(json.dumps(r, sort_keys=True) for r in oh)
theirs_ids = set(json.dumps(r, sort_keys=True) for r in th)
assert ours_ids | theirs_ids == set(oid.keys()), "union != |A u B| zero-loss gate"
overlap = len(ours_ids & theirs_ids)
tss = [r.get("ts", "") for r in union]
uniform = all(re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", x) for x in tss)
if uniform:
    union.sort(key=lambda r: r["ts"])                    # chronological; stable for ties
merged = {"latest": o["latest"], "history": union}       # latest=ours (11:49+ > theirs)
# format detection (r223/r234 EOL law): reproduce ours blob byte-exactly
fmt = None
eol = "\r\n" if b"\r\n" in ob else "\n"
for indent in (1, 2, 3, 4):
    for ea in (True, False):
        for tail in ("", eol):
            ref = (json.dumps(o, indent=indent, ensure_ascii=ea) + tail).replace("\n", eol)
            if ref.encode("utf-8") == ob:
                fmt = (indent, ea, tail)
                break
        if fmt: break
    if fmt: break
assert fmt, "cannot reproduce producer format from ours blob"
indent, ea, tail = fmt
out = (json.dumps(merged, indent=indent, ensure_ascii=ea) + tail).replace("\n", eol).encode("utf-8")
with open(wpath(UNION_LEDGER), "wb") as f:
    f.write(out)
back = json.loads(open(wpath(UNION_LEDGER), "rb").read())
assert len(back["history"]) == len(oid) == (len(ours_ids) + len(theirs_ids) - overlap), \
    f"union rowcount {len(oid)} != |A u B|"
assert back["latest"]["ts"] == o["latest"]["ts"], "r704 readback: latest.ts != ours"
assert all(isinstance(r, dict) for r in back["history"]), "r522 readback type gate"
receipt["faces"][UNION_LEDGER] = {
    "recipe": "rolling-union-zero-loss (r188/R208)",
    "ours_rows": len(oh), "theirs_rows": len(th), "union_rows": len(oid),
    "ours_only": len(ours_ids - theirs_ids), "theirs_only": len(theirs_ids - ours_ids),
    "overlap": overlap, "ts_sorted": uniform,
    "latest_side": "ours", "latest_ts": o["latest"]["ts"], "theirs_latest_ts": t["latest"]["ts"],
    "format": f"indent={indent} ensure_ascii={ea} eol={repr(eol)} tail={repr(tail)}",
}
print(f"UNION {UNION_LEDGER}: {len(oh)}+{len(th)} -> {len(oid)} rows "
      f"(ours_only={len(ours_ids - theirs_ids)} theirs_only={len(theirs_ids - ours_ids)} "
      f"overlap={overlap}), ts_sorted={uniform}, fmt={fmt}")

with open(wpath(RECEIPT), "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print("RECEIPT " + RECEIPT)
print("RESOLVE-OK")
