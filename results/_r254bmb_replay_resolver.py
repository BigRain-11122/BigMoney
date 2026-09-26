"""_r254bmb_replay_resolver -- S7 push-collision replay batch resolver (bm-b r254).

Window: bm-a r250 x2 commits (83ecffbb 14:13:30 / 2b7bac34 14:21:50) landed inside
my r254 S7 push window -> pull --rebase 14-UU replay batch. Rebase semantics NOTE:
during rebase OURS (:2) = the new base = bm-a origin side; THEIRS (:3) = my replayed
commit side (inverse of merge -- r245 stash law family).

Recipes per classifier (tools/skills/bigmoney-conflict-resolve):
  memory-union       CODELY.md            line union both machines' new entries
  mixed-dict+ledger  autofill_state.json  launches union->ts desc->cap50->re-sort ASC
                                           write-back; last_tick inner-ts whole-dict
  rolling-ledger     compute_audit/regime_state  history union zero-loss + newest snap
  js-wrapper         dashboard_status.js  take-side whole bytes (wrapper preserved)
  snapshot           *_status.json / b_layer / token_usage  ts-probe -> newer whole doc
  UNKNOWN pair       daily_report REPORT pair (r242 precedent: json generated_at picks
                     side, md takes SAME side whole-byte)
Laws: r242 probe-first (real ts keys, no None>=None silent-ours), r140 same-second
tie->HEAD, r185 parse-verify before add, R208/R209/R216 zero-loss + byte mirror.
"""
import json
import subprocess
import sys

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
TS_KEYS = ("ts", "updated", "generated", "generated_at", "as_of", "last_attempt",
           "updated_at", "time")


def blob(side, path):
    """side 1/2/3 = base/ours(bm-a origin)/theirs(my replayed)."""
    r = subprocess.run(["git", "show", ":%d:%s" % (side, path)],
                       capture_output=True, cwd=ROOT)
    return r.stdout if r.returncode == 0 else None


def wtree(path):
    with open(ROOT + "\\" + path.replace("/", "\\"), "rb") as f:
        return f.read()


def put(path, data):
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(data)


def jload(b):
    try:
        return json.loads(b.decode("utf-8-sig"))
    except Exception:
        return None


def probe_ts(obj):
    """(key, value) of first real (non-None) ts candidate, top level only."""
    if not isinstance(obj, dict):
        return None, None
    for k in TS_KEYS:
        v = obj.get(k)
        if v is not None:
            return k, str(v)
    return None, None


def side_pick(path, log):
    """Snapshot pick: ts-probe both sides, newer wins; equal -> ours(bm-a, HEAD);
    keys absent on either side -> UNKNOWN -> fail-closed manual note."""
    a, t = jload(blob(2, path)), jload(blob(3, path))
    ka, va = probe_ts(a)
    kt, vt = probe_ts(t)
    if ka is None or kt is None or va is None or vt is None:
        log.append("  UNKNOWN-ts %s: ours[%s]=%s theirs[%s]=%s -> MANUAL"
                   % (path, ka, va, kt, vt))
        return None
    if va == vt:
        log.append("  tie %s: %s=%s -> ours (r140 HEAD)" % (path, ka, va))
        return blob(2, path)
    win = 2 if va > vt else 3
    log.append("  %s: ours[%s]=%s vs theirs[%s]=%s -> side %d (%s)"
               % (path, ka, va, kt, vt, win, "bm-a origin" if win == 2 else "bm-b mine"))
    return blob(win, path)


def main():
    log = []
    # —————— snapshots (take-new by real ts probe) ——————
    snaps = ["results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
             "results/futures_update_status.json", "results/heat_update_status.json",
             "results/lhb_update_status.json", "results/token_usage.json",
             "results/update_status.json"]
    for p in snaps:
        b = side_pick(p, log)
        if b is not None:
            put(p, b)
            assert jload(b) is not None, "parse fail " + p
    # —————— rolling ledgers ——————
    for p, key in (("results/compute_audit.json", "history"),
                   ("results/regime_state.json", "history")):
        a, t = jload(blob(2, p)), jload(blob(3, p))
        ha, ht = (a or {}).get(key) or [], (t or {}).get(key) or []
        seen, union = set(), []
        for row in ha + ht:                       # ts-ASC union, zero loss, dedupe
            sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if sig not in seen:
                seen.add(sig)
                union.append(row)
        union.sort(key=lambda r: str(r.get("ts") or ""))
        base = a if (probe_ts(a)[1] or "") >= (probe_ts(t)[1] or "") else t
        merged = dict(base)
        merged[key] = union
        if p == "results/regime_state.json" and isinstance(merged.get("transitions"), list):
            tr_a = (a or {}).get("transitions") or []
            tr_t = (t or {}).get("transitions") or []
            seen2, un2 = set(), []
            for row in tr_a + tr_t:
                sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
                if sig not in seen2:
                    seen2.add(sig)
                    un2.append(row)
            un2.sort(key=lambda r: str(r.get("ts") or r.get("date") or ""))
            merged["transitions"] = un2
        out = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8")
        put(p, out)
        assert jload(out) is not None
        log.append("  %s: %s union %d+%d->%d zero-loss, snap ts ours=%s theirs=%s"
                   % (p, key, len(ha), len(ht), len(union), probe_ts(a)[1], probe_ts(t)[1]))
    # —————— mixed-dict+ledger autofill_state ——————
    p = "results/autofill_state.json"
    a, t = jload(blob(2, p)), jload(blob(3, p))
    la, lt = (a or {}).get("launches") or [], (t or {}).get("launches") or []
    seen, union = set(), []
    for row in la + lt:
        sig = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if sig not in seen:
            seen.add(sig)
            union.append(row)
    union.sort(key=lambda r: str(r.get("ts") or ""), reverse=True)   # cap 语义=保最新
    union = union[:50]
    union.sort(key=lambda r: str(r.get("ts") or ""))                 # 写回序=生产者 append 序 ASC
    ta, tt = (a or {}).get("last_tick") or {}, (t or {}).get("last_tick") or {}
    tsa, tst = str(ta.get("ts") or ""), str(tt.get("ts") or "")
    tick = ta if (not tst or (tsa and tsa >= tst)) else tt           # 同秒 tie -> ours(bm-a HEAD)
    merged = dict(a or {})
    merged["launches"] = union
    merged["last_tick"] = tick
    assert isinstance(merged.get("last_tick"), dict), "last_tick must stay dict"
    out = json.dumps(merged, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8")
    put(p, out)
    assert jload(out) is not None
    log.append("  %s: launches union %d+%d->cap%d ASC write-back; last_tick ts ours=%s vs theirs=%s -> %s"
               % (p, len(la), len(lt), len(union), tsa or None, tst or None,
                  "ours" if merged["last_tick"] is ta else "theirs"))
    # —————— js-wrapper dashboard_status.js ——————
    p = "results/dashboard_status.js"
    a, t = jload(blob(2, p)), jload(blob(3, p))
    ka, va, kt, vt = *probe_ts(a), *probe_ts(t)
    win = 2 if (va or "") >= (vt or "") else 3
    data = blob(win, p)
    put(p, data)
    assert data.strip().startswith(b"window.DASH_DATA"), "wrapper stripped R209"
    log.append("  %s: ts ours[%s]=%s vs theirs[%s]=%s -> side %d whole-byte wrapper-asserted"
               % (p, ka, va, kt, vt, win))
    # —————— UNKNOWN pair: daily_report (r242 precedent) ——————
    pj = "docs/daily_report/REPORT-2026-09-26.json"
    pm = "docs/daily_report/REPORT-2026-09-26.md"
    a, t = jload(blob(2, pj)), jload(blob(3, pj))
    ka, va, kt, vt = *probe_ts(a), *probe_ts(t)
    if ka is None or kt is None:
        log.append("  UNKNOWN daily_report json ts absent -> MANUAL REQUIRED")
        print("\n".join(log))
        return 2
    win = 2 if va > vt else 3 if vt > va else 2
    put(pj, blob(win, pj))
    put(pm, blob(win, pm))                       # md 同侧整字节
    assert jload(blob(win, pj)) is not None
    log.append("  daily_report pair: json generated_at ours=%s vs theirs=%s -> side %d; md same-side whole-byte"
               % (va, vt, win))
    # —————— memory-union CODELY.md ——————
    p = "CODELY.md"
    a, t = blob(2, p), blob(3, p)
    la = a.decode("utf-8-sig").splitlines()
    lt = t.decode("utf-8-sig").splitlines()
    # 行级 union：bm-a(origin) 侧全量序保留 + bm-b 独有行追加（各机条目原字面零丢失）
    seen = set(la)
    out_lines = list(la)
    for line in lt:
        if line not in seen:
            out_lines.append(line)
            seen.add(line)
    crlf = b"\r\n" in a or b"\r\n" in t
    body = ("\r\n" if crlf else "\n").join(out_lines) + ("\r\n" if crlf else "\n")
    put(p, body.encode("utf-8"))
    log.append("  CODELY.md: line union ours=%d theirs=%d -> %d (both machines' entries kept)"
               % (len(la), len(lt), len(out_lines)))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    sys.exit(main())
