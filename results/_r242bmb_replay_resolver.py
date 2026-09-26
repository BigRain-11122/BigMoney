"""r242 addendum: push-replay resolver provenance (bm-b).

Origin: %TEMP%_r242bmb_replay_resolver.py ran EXTERNAL to the repo per
r231 law during the S7 push-rejection rebase replay (13-UU batch vs
bm-a mid-round push b8114b9e). Copied here for provenance after rebase
completed (r225 pattern).

Correction note (run-time deviation from this script as written): the
snapshot take-new ts-key probes missed the real field names for 4
status files (heat/lhb_update_status use "updated", token_usage uses
"generated", update_status uses "updated" -- not top-level "ts"), so
the first pass silently defaulted to ours on ties; a targeted stage-3
byte rewrite fixed those 4 to the newer side (mine 10:58-10:59 vs
bm-a 10:48) before `git add`. Verified by field probe: expected values
written. Everything else ran as scripted (classifier-routed recipes;
js-wrapper take-side by twin meta.generated_at 10:59:45>10:49:21 with
wrapper bytes preserved; autofill_state mixed-dict+ledger; compute_audit
history union 201+201->202 zero-loss; regime history union; daily
report pair = same-day regen snapshot take-side by json generated_at
10:59:38>10:49:18).

Post-replay poison scan: HEAD commit 20 files, zero line-start
conflict markers, all JSON parse-clean (r231 law 4).

Wiring commit hash drift: f95adf89 -> d65f2d4a after replay;
provenance references re-anchored same round.
"""
import json
import os
import subprocess
import sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"


def sh(*args):
    r = subprocess.run(args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(args[-1] + ": " + r.stderr.decode("utf-8", "replace"))
    return r.stdout


def stage_blobs():
    out = {}
    for line in sh("git", "ls-files", "-u").decode("utf-8").splitlines():
        parts = line.split("\t")
        meta = parts[0].split()
        sha, stage, path = meta[1], int(meta[2]), parts[1]
        out[(path, stage)] = sha
    return out


def blob_json(shas, path, stage):
    return json.loads(sh("git", "cat-file", "-p", shas[(path, stage)]))


def blob_bytes(shas, path, stage):
    return sh("git", "cat-file", "-p", shas[(path, stage)])


def eol_of(raw: bytes) -> str:
    return "\r\n" if b"\r\n" in raw else "\n"


def write_out(path: str, obj, indent=1, eol="\r\n", raw=None):
    full = os.path.join(REPO, path)
    body = raw if raw is not None else json.dumps(obj, ensure_ascii=False,
                                                  indent=indent)
    with open(full, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
        if not body.endswith(eol):
            fh.write(eol)


def resolve():
    shas = stage_blobs()
    paths = sorted({p for (p, s) in shas})
    log = []

    # ---- mixed-dict+ledger: autofill_state.json ----------------------
    p = "results/autofill_state.json"
    a = blob_json(shas, p, 2)
    b = blob_json(shas, p, 3)
    lt_a = (a.get("last_tick") or {}).get("ts", "")
    lt_b = (b.get("last_tick") or {}).get("ts", "")
    last_tick = dict(a["last_tick"]) if lt_a >= lt_b else dict(b["last_tick"])
    assert isinstance(last_tick, dict)
    seen, merged = set(), []
    for row in (a.get("launches") or []) + (b.get("launches") or []):
        k = (row.get("ts"), row.get("entry"), row.get("machine"),
             row.get("pid"))
        if k in seen:
            continue
        seen.add(k)
        merged.append(dict(row))
    merged.sort(key=lambda r: r.get("ts", ""))
    out = {"last_tick": last_tick, "launches": merged[-50:]}
    write_out(p, out, indent=1, eol=eol_of(blob_bytes(shas, p, 2)))
    log.append(f"{p}: mixed-dict+ledger last_tick={last_tick['ts']} "
               f"launches={len(out['launches'])} (union "
               f"{len(a.get('launches') or [])}+{len(b.get('launches') or [])})")

    # ---- rolling-ledger: compute_audit.json ---------------------------
    p = "results/compute_audit.json"
    a = blob_json(shas, p, 2)
    b = blob_json(shas, p, 3)
    hist_key = [k for k in a if isinstance(a[k], list)]
    out = dict(b if (b.get("ts", "") >= a.get("ts", "")) else a)
    for k in hist_key:
        ua = {json.dumps(r, sort_keys=True): r for r in a.get(k, [])}
        ub = {json.dumps(r, sort_keys=True): r for r in b.get(k, [])}
        merged_k = list(ua.values()) + [r for kk, r in ub.items() if kk not in ua]
        merged_k.sort(key=lambda r: json.dumps(r, sort_keys=True))
        out[k] = merged_k
    write_out(p, out, indent=2, eol=eol_of(blob_bytes(shas, p, 2)))
    log.append(f"{p}: ledger union {len(a.get('history', []))}"
               f"+{len(b.get('history', []))} -> {len(out['history'])} "
               f"(zero-loss), snapshot fields take-new ts={out.get('ts')}")

    # ---- rolling-ledger: regime_state.json ----------------------------
    p = "results/regime_state.json"
    a = blob_json(shas, p, 2)
    b = blob_json(shas, p, 3)
    out = dict(b if (b.get("asof", "") >= a.get("asof", "")) else a)
    for k in ("history", "transitions"):
        if k in a or k in b:
            ka = {json.dumps(r, sort_keys=True): r for r in a.get(k, [])}
            kb = {json.dumps(r, sort_keys=True): r for r in b.get(k, [])}
            mk = list(ka.values()) + [r for kk, r in kb.items() if kk not in ka]
            mk.sort(key=lambda r: json.dumps(r, sort_keys=True))
            out[k] = mk
    write_out(p, out, indent=2, eol=eol_of(blob_bytes(shas, p, 2)))
    log.append(f"{p}: history/transitions union "
               f"{len(a.get('history', []))}+{len(b.get('history', []))}"
               f" -> {len(out.get('history', []))}, asof={out.get('asof')}")

    # ---- js-wrapper + twin: dashboard_status.{js,json} -----------------
    pjs, pjson = "results/dashboard_status.js", "results/dashboard_status.json"
    ja = blob_json(shas, pjson, 2)
    jb = blob_json(shas, pjson, 3)
    ta = (ja.get("meta") or {}).get("generated_at", "")
    tb = (jb.get("meta") or {}).get("generated_at", "")
    winner_stage = 2 if ta >= tb else 3
    js_raw = blob_bytes(shas, pjs, winner_stage)
    json_raw = blob_bytes(shas, pjson, winner_stage)
    for path, raw in ((pjs, js_raw), (pjson, json_raw)):
        full = os.path.join(REPO, path)
        with open(full, "wb") as fh:
            fh.write(raw)
    log.append(f"{pjs}+{pjson}: take-side stage{winner_stage} by twin "
               f"meta.generated_at ours={ta} theirs={tb} (wrapper bytes "
               f"preserved)")

    # ---- snapshots take-new by ts (field names per header note) --------
    snaps = {
        "results/fundamental_b_layer_filter.json": "updated",
        "results/futures_update_status.json": "ts",
        "results/heat_update_status.json": "updated",
        "results/lhb_update_status.json": "updated",
        "results/token_usage.json": "generated",
        "results/update_status.json": "updated",
    }
    for p, key in snaps.items():
        a = blob_json(shas, p, 2)
        b = blob_json(shas, p, 3)
        ta = str(a.get(key) or "")
        tb = str(b.get(key) or "")
        out, side = (a, "ours") if ta >= tb else (b, "theirs")
        write_out(p, out, indent=1, eol=eol_of(blob_bytes(shas, p, 2)))
        log.append(f"{p}: take-new {side} {key}={out.get(key)}")

    # ---- daily report pair (manual: same-day regen snapshot) ----------
    pj = "docs/daily_report/REPORT-2026-09-26.json"
    pm = "docs/daily_report/REPORT-2026-09-26.md"
    ja = blob_json(shas, pj, 2)
    jb = blob_json(shas, pj, 3)
    ta = str(ja.get("generated_at") or ja.get("ts") or "")
    tb = str(jb.get("generated_at") or jb.get("ts") or "")
    wstage = 2 if ta >= tb else 3
    for path in (pj, pm):
        raw = blob_bytes(shas, path, wstage)
        full = os.path.join(REPO, path)
        with open(full, "wb") as fh:
            fh.write(raw)
    log.append(f"{pj}+{pm}: take-side stage{wstage} same-day regen "
                f"(json ts ours={ta} theirs={tb}, md same side)")

    # ---- fail-closed verification --------------------------------------
    bad = []
    for p in paths:
        full = os.path.join(REPO, p)
        raw = open(full, "rb").read()
        for marker in (b"<<<<<<<", b">>>>>>>"):
            if any(line.startswith(marker) for line in raw.splitlines()):
                bad.append((p, marker.decode()))
        if p.endswith(".json"):
            try:
                json.loads(raw.decode("utf-8-sig"))
            except Exception as exc:
                bad.append((p, f"PARSE {exc}"))
    if bad:
        for x in bad:
            print("BAD", x)
        print("RESOLVE-FAIL: markers/unparseable remain")
        return 2

    for line in log:
        print(line)
    print(f"RESOLVED {len(paths)} files, all parse-clean, zero markers")
    return 0


if __name__ == "__main__":
    sys.exit(resolve())
