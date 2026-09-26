"""r243 addendum: S7 push-replay resolver provenance (bm-b).

Origin: %TEMP% r243_replay_resolver.py (+ r243_stash_resolver.py for
the post-rebase stash-pop tick) ran EXTERNAL per r231 law during the
S7 push-rejection rebase replay vs bm-a 3ddd741f+89740a29. Replay:
step1 99a3043c autofill UU mixed-dict+ledger (CRLF translation write =
r234 fix; r242 archived resolver had append-only-final-EOL bug leaving
LF body = the flip my S0 commit converged); step2 bd42a609 freeze
applied clean; step3 75ca9a7f 12-UU batch: CODELY line-union 62+62->63,
compute_audit history union 203+201->204 zero-loss (indent=2), regime
history union, dashboard pair stage3 by meta.generated_at 11:18:24>
11:09:22 raw bytes (r226 twin law), daily-report pair stage3 by
generated_at 11:18:22>11:09:21 (classifier UNKNOWN -> r242 manual
precedent), 6 snapshots field-probed take-side (updated/ts/generated
real keys per r242 lesson). Poison scan 22 files zero line-start
markers, 14 JSON parse-clean. Freeze hash drift db8ac757->bd42a609
re-anchored same round (r242 drift law).

--- resolver body as-run (step-3 batch) ---
"""r243 S7 push-replay resolver step-3 batch (bm-b, EXTERNAL per r231 law).

12 UU at replay step 3/3 (bookkeeping commit 324e7456) vs bm-a
ff5811cb..89740a29 same-window S6 face. Classifier: 11 classified + 2
UNKNOWN (daily report pair -> r242 precedent: same-day regen snapshot
pair, take-side by json twin timestamp, md same side whole bytes).

Design laws applied:
  - R209: snapshot files = take-side WHOLE BYTES of the winning blob
    (no re-serialization => zero indent/EOL/format drift)
  - r242: ts-key FIELD PROBE per file (ts/updated/generated/generated_at/
    as_of/last_attempt/derived_at) with non-null values compared; all
    keys absent -> UNKNOWN fail-closed, never None-tie default
  - r226: dashboard_status.js has no top-level ts -> winner decided by
    .json twin, js written as winner raw bytes (wrapper preserved)
  - r188/R208: compute_audit/regime_state = ledger union zero-loss
  - R208/r212: CODELY.md = line-level union (both machines' entries)
"""
import json
import os
import subprocess

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"
TS_KEYS = ("ts", "updated", "generated", "generated_at", "as_of",
           "last_attempt", "derived_at", "written_at")


def sh(*args):
    r = subprocess.run(args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(args[-1] + ": " + r.stderr.decode("utf-8", "replace"))
    return r.stdout


def blobs():
    out = {}
    for line in sh("git", "ls-files", "-u").decode("utf-8").splitlines():
        parts = line.split("\t")
        meta = parts[0].split()
        sha, stage, path = meta[1], int(meta[2]), parts[1]
        out[(path, stage)] = sha
    return out


def raw(shas, path, stage):
    return sh("git", "cat-file", "-p", shas[(path, stage)])


def jload(shas, path, stage):
    return json.loads(raw(shas, path, stage))


def probe_ts(obj):
    for k in TS_KEYS:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and v.strip():
            return k, v
    return None, None


def pick_newer(shas, path, log):
    a, b = jload(shas, path, 2), jload(shas, path, 3)
    ka, va = probe_ts(a)
    kb, vb = probe_ts(b)
    if ka is None and kb is None:
        raise SystemExit(f"UNKNOWN ts-face {path}: no candidate key in either"
                         f" blob -> manual adjudication (fail-closed)")
    side = 2 if (va or "") >= (vb or "") else 3
    data = raw(shas, path, side)
    with open(os.path.join(REPO, path), "wb") as fh:
        fh.write(data)
    log.append(f"{path}: snapshot take-side stage{side} "
                f"(keys {ka}={va} vs {kb}={vb})")


def union_ledger(shas, path, list_keys, ts_key, indent, log):
    a, b = jload(shas, path, 2), jload(shas, path, 3)
    out = dict(b if (b.get(ts_key, "") >= a.get(ts_key, "")) else a)
    for k in list_keys:
        if k not in a and k not in b:
            continue
        ua = {json.dumps(r, sort_keys=True): r for r in a.get(k, [])}
        ub = {json.dumps(r, sort_keys=True): r for r in b.get(k, [])}
        merged = list(ua.values()) + [r for kk, r in ub.items() if kk not in ua]
        merged.sort(key=lambda r: json.dumps(r, sort_keys=True))
        out[k] = merged
        log.append(f"{path}: {k} union {len(a.get(k, []))}+{len(b.get(k, []))}"
                   f" -> {len(merged)} (zero-loss)")
    base_eol = b"\r\n" if b"\r\n" in raw(shas, path, 1) else b"\n"
    body = json.dumps(out, ensure_ascii=False, indent=indent)
    with open(os.path.join(REPO, path), "w", encoding="utf-8",
              newline=("\r\n" if base_eol == b"\r\n" else "\n")) as fh:
        fh.write(body + "\n")
    log.append(f"{path}: snapshot fields take-new {ts_key}={out.get(ts_key)}")


def main():
    shas = blobs()
    log = []

    # CODELY.md: line-level union, both machines' appended entries kept
    p = "CODELY.md"
    la = raw(shas, p, 2).decode("utf-8").splitlines()
    lb = raw(shas, p, 3).decode("utf-8").splitlines()
    seen, merged = set(), []
    for ln in la + lb:
        if ln in seen:
            continue
        seen.add(ln)
        merged.append(ln)
    eol = "\r\n" if b"\r\n" in raw(shas, p, 1) else "\n"
    with open(os.path.join(REPO, p), "w", encoding="utf-8",
              newline=("\r\n" if eol == "\r\n" else "\n")) as fh:
        fh.write("\n".join(merged) + "\n")
    log.append(f"{p}: line-union {len(la)}+{len(lb)} -> {len(merged)} lines")

    # rolling ledgers
    union_ledger(shas, "results/compute_audit.json", ["history"], "ts", 2, log)
    union_ledger(shas, "results/regime_state.json",
                 ["history", "transitions"], "asof", 2, log)

    # dashboard pair: winner by .json twin meta.generated_at (r226 law:
    # no top-level ts; nested meta face), both as raw bytes
    pj, pjs = "results/dashboard_status.json", "results/dashboard_status.js"
    a, b = jload(shas, pj, 2), jload(shas, pj, 3)
    va = (a.get("meta") or {}).get("generated_at") or ""
    vb = (b.get("meta") or {}).get("generated_at") or ""
    if not va and not vb:
        raise SystemExit(f"UNKNOWN ts-face {pj} (dashboard twin)")
    side = 2 if va >= vb else 3
    for pp in (pj, pjs):
        data = raw(shas, pp, side)
        with open(os.path.join(REPO, pp), "wb") as fh:
            fh.write(data)
        log.append(f"{pp}: js-wrapper/json take-side stage{side} raw bytes "
                    f"(meta.generated_at {va} vs {vb})")

    # daily report pair (UNKNOWN -> r242 manual precedent: same-day regen
    # snapshot pair; winner by json twin timestamp, md same side bytes)
    rj = "docs/daily_report/REPORT-2026-09-26.json"
    rm = "docs/daily_report/REPORT-2026-09-26.md"
    a, b = jload(shas, rj, 2), jload(shas, rj, 3)
    ka, va = probe_ts(a)
    kb, vb = probe_ts(b)
    if ka is None and kb is None:
        # fall back to embedded any-depth 'generated'/'ts' probe
        def deep_ts(o):
            if isinstance(o, dict):
                k, v = probe_ts(o)
                if k:
                    return k, v
                for vv in o.values():
                    r = deep_ts(vv)
                    if r:
                        return r
            return None
        ka, va = deep_ts(a) or (None, None)
        kb, vb = deep_ts(b) or (None, None)
    if ka is None and kb is None:
        raise SystemExit("UNKNOWN ts-face daily report json twin (fail-closed)")
    side = 2 if (va or "") >= (vb or "") else 3
    for pp in (rj, rm):
        data = raw(shas, pp, side)
        with open(os.path.join(REPO, pp), "wb") as fh:
            fh.write(data)
        log.append(f"{pp}: daily-report pair take-side stage{side} "
                   f"({ka}={va} vs {kb}={vb})")

    # plain snapshots: take-new whole bytes by field-probed ts
    for p in ("results/dashboard_status.json"  # already done above; skip
              ,):  # placeholder guard
        pass
    for p in ("results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json",
              "results/token_usage.json",
              "results/update_status.json"):
        pick_newer(shas, p, log)

    print("\n".join(log))
    # parse-verify every resolved JSON (r185 law)
    for p in ("results/compute_audit.json", "results/regime_state.json",
              "results/dashboard_status.json",
              "results/fundamental_b_layer_filter.json",
              "results/futures_update_status.json",
              "results/heat_update_status.json",
              "results/lhb_update_status.json", "results/token_usage.json",
              "results/update_status.json", rj):
        json.loads(open(os.path.join(REPO, p), encoding="utf-8").read())
    js = open(os.path.join(REPO, pjs), encoding="utf-8").read()
    assert js.startswith("window.DASH_DATA") and js.rstrip().endswith(";")
    print("PARSE-VERIFY: all JSON parse-clean; js wrapper intact")


if __name__ == "__main__":
    main()


--- stash-pop resolver body as-run ---
"""r243 stash-pop resolver: autofill_state.json mixed-dict+ledger (canon)."""
import json
import os
import subprocess

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"


def sh(*args):
    r = subprocess.run(args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise RuntimeError(args[-1] + ": " + r.stderr.decode("utf-8", "replace"))
    return r.stdout


def main():
    shas = {}
    for line in sh("git", "ls-files", "-u").decode().splitlines():
        parts = line.split("\t")
        meta = parts[0].split()
        shas[(parts[1], int(meta[2]))] = meta[1]
    p = "results/autofill_state.json"
    a = json.loads(sh("git", "cat-file", "-p", shas[(p, 2)]))   # HEAD side
    b = json.loads(sh("git", "cat-file", "-p", shas[(p, 3)]))   # stash side
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
    body = json.dumps(out, ensure_ascii=False, indent=1)
    with open(os.path.join(REPO, p), "w", encoding="utf-8",
              newline="\r\n") as fh:
        fh.write(body + "\n")
    chk = json.loads(open(os.path.join(REPO, p), encoding="utf-8").read())
    assert isinstance(chk["last_tick"], dict)
    raw = open(os.path.join(REPO, p), "rb").read()
    assert raw.count(b"\r\n") == raw.count(b"\n")
    print(f"stash-pop resolved: last_tick={last_tick['ts']} launches="
          f"{len(out['launches'])} (union {len(a.get('launches') or [])}+"
          f"{len(b.get('launches') or [])}) CRLF-verified")


if __name__ == "__main__":
    main()
