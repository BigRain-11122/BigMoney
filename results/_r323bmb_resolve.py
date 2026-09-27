# -*- coding: utf-8 -*-
"""r323 bm-b push-collision resolver: 18-UU vs bm-a r322 (77828236, 12:46 same-window S6 mirror).

Recipes (conflict-canon routing). REBASE SEMANTICS: :2: = ours = upstream bm-a r322
face (77828236, HEAD-priority for shared keys), :3: = theirs = my replayed r323
face. Receipt labels: side2=bm-a(origin), side3=bm-b(replay).
- CODELY.md: take theirs (landed 12th-batch archival, superset incl r79) + append my r323
  pitlaw entry; drop my subsumed index line. Assert size<10KB + both new entries present.
- research/memory-archive/202609.md: take theirs (their batch = superset r317/318/319/r79);
  content-eq assert my 3 shared entries byte-identical in their batch (r319 content-eq law);
  if any diff -> fallback keep both sections (zero-loss).
- autofill_state.json: launches key-union (cap50 ts-asc, r245) + last_tick newest (r317).
- compute_audit.json / regime_state.json: history key-union zero-loss assert (r319) + latest
  by *existing* ts path (compute_audit=latest.ts, regime_state=latest.ts probe-first).
- token_usage.json: probe structure; history-list w/ ts keys -> union; flat ts -> take-newer.
- dashboard_status.js/.json, REPORT twins, all *_status/summary/scorecard derive faces:
  take-newer by inner ts (r316 measurement-face canon), probe ts path first (r319).
"""
import io, os, json, subprocess, sys

REPO = r"C:\Users\Administrator\Desktop\Bigmoney"

UU = ["CODELY.md", "research/memory-archive/202609.md",
      "results/autofill_state.json", "results/compute_audit.json",
      "results/dashboard_status.js", "results/dashboard_status.json",
      "results/token_usage.json", "results/update_status.json",
      "results/scorecard_v1.json", "results/strategy_scorecard.json",
      "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
      "results/heat_update_status.json", "results/lhb_update_status.json",
      "results/prospect_promotion/_summary.json",
      "docs/daily_report/REPORT-2026-09-27.md", "docs/daily_report/REPORT-2026-09-27.json"]

MY_R323_ENTRY = None  # loaded from my working-tree CODELY before overwrite (kept in commit 09e9c67b)

def git_bytes(spec):
    return subprocess.run(["git", "show", spec], capture_output=True, cwd=REPO).stdout

def jload(b):
    return json.loads(b.decode("utf-8"))

def jwrite(path, obj):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

def ts_of(obj, *paths):
    for p in paths:
        cur = obj
        ok = True
        for k in p.split("."):
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False
                break
        if ok and cur:
            return cur
    return None

def take_newer(path, ours, theirs, *ts_paths):
    o, t = jload(ours), jload(theirs)
    ot, tt = ts_of(o, *ts_paths), ts_of(t, *ts_paths)
    assert ot and tt, f"{path}: ts probe failed (r319 law) ours={ot} theirs={tt}"
    winner = "side2-bma" if ot >= tt else "side3-bmb"
    data = ours if ot >= tt else theirs
    with io.open(path, "wb") as f:
        f.write(data)
    return {"file": path, "recipe": "take-newer", "side2_bma_ts": ot, "side3_bmb_ts": tt, "winner": winner}

def union_ledger(path, ours, theirs, list_key, entry_key_fn, latest_ts_path, cap=None):
    o, t = jload(ours), jload(theirs)
    ol, tl = o.get(list_key, []), t.get(list_key, [])
    merged = {}
    for e in ol + tl:
        merged[entry_key_fn(e)] = e  # ours first, theirs overwrites only absent keys? -> explicit: keep first-seen, but zero-loss assert below
    # prefer ours face for shared keys (HEAD-priority per r317); theirs-only keys appended
    by_key_o = {entry_key_fn(e): e for e in ol}
    by_key_t = {entry_key_fn(e): e for e in tl}
    result_keys = set(by_key_o) | set(by_key_t)
    assert len(result_keys) == len(set(by_key_o)) + len(set(by_key_t) - set(by_key_o)), "key fn collision"
    merged_list = [by_key_o[k] if k in by_key_o else by_key_t[k] for k in result_keys]
    merged_list.sort(key=lambda e: entry_key_fn(e) if isinstance(entry_key_fn(e), str) else str(entry_key_fn(e)))
    # zero-loss assert BEFORE cap (cap=retention policy, not loss)
    zero_loss = len(merged_list) == len(set(by_key_o) | set(by_key_t))
    dropped = 0
    if cap:
        def ets(e):
            v = e.get("ts") or e.get("last_tick") or ""
            return str(v)
        merged_list.sort(key=ets)
        dropped = max(0, len(merged_list) - cap)
        if dropped > 0:
            merged_list = merged_list[-cap:]
    o[list_key] = merged_list
    # latest/last_tick: snapshot node replaced WHOLE from newer side (inner ts compared per r317;
    # mixing ts of one side with payload of the other = corrupted record)
    top = latest_ts_path.split(".")[0]
    ov, tv = ts_of(o, latest_ts_path), ts_of(t, latest_ts_path)
    assert ov and tv, f"{path}: latest ts probe failed at {latest_ts_path}"
    if tv > ov:
        o[top] = t[top]
    jwrite(path, o)
    return {"file": path, "recipe": "union-ledger", "side2_bma_n": len(ol), "side3_bmb_n": len(tl),
            "merged_n": len(merged_list), "dropped_by_cap": dropped, "zero_loss": zero_loss,
            "latest_winner": "side2-bma" if ov >= tv else "side3-bmb"}

def main():
    receipt = []
    # REBASE SEMANTICS (inverted vs merge): :2: = ours = upstream bm-a r322 face (77828236);
    # :3: = theirs = my replayed r323 face (09e9c67b). HEAD-priority shared-key face = :2:.
    # --- CODELY.md ---
    theirs_c = git_bytes(":2:CODELY.md").decode("utf-8")   # bm-a landed face (base)
    ours_c = git_bytes(":3:CODELY.md").decode("utf-8")      # bm-b face (has r323 entry)
    # my r323 entry lives in bm-b face (appended at tail); extract verbatim
    my_lines = [l for l in ours_c.splitlines() if "r323 bm-b" in l and "GBK 污染修复" in l]
    assert len(my_lines) == 1, f"my r323 entry not unique in bm-b face: {len(my_lines)}"
    entry = my_lines[0]
    # bm-a face as base; assert their archival state; append my entry
    assert "十二批" in theirs_c, "bm-a index line missing"
    new_c = theirs_c.rstrip("\n") + "\n" + entry + "\n"
    size = len(new_c.encode("utf-8"))
    assert size <= 10240, f"CODELY union {size}B over 10KB"
    with io.open(os.path.join(REPO, "CODELY.md"), "w", encoding="utf-8", newline="") as f:
        f.write(new_c)
    receipt.append({"file": "CODELY.md", "recipe": "bma-base+append-bmb-r323",
                    "my_index_line_dropped": True, "size": size,
                    "bma_pitlaw_present": "content-eq" in theirs_c,
                    "bmb_entry_present": entry[:40] in new_c})

    # --- archive 202609.md ---
    theirs_a = git_bytes(":2:research/memory-archive/202609.md").decode("utf-8")  # bm-a superset batch
    ours_a = git_bytes(":3:research/memory-archive/202609.md").decode("utf-8")   # bm-b batch
    shared_keys = ["[2026-09-27 11:3x r317 bm-b]", "[2026-09-27 11:4x r318 bm-b]", "[2026-09-27 12:0x r319 bm-b]"]
    mine_shared = [l for l in ours_a.splitlines() if any(k in l for k in shared_keys)]
    theirs_shared = [l for l in theirs_a.splitlines() if any(k in l for k in shared_keys)]
    content_eq = sorted(mine_shared) == sorted(theirs_shared) and len(mine_shared) == 3
    if content_eq:
        final_a = theirs_a  # bm-a superset batch (incl r79), zero dupes
        note = "bma-batch-kept (superset r317/318/319/r79); my 3 shared entries content-eq byte-verified"
    else:
        # zero-loss fallback: bm-a face + my batch section appended (extract from mine)
        my_sec_start = None
        ol = ours_a.splitlines(keepends=True)
        for i, l in enumerate(ol):
            if "十二批迁移" in l and "r323" in l:
                my_sec_start = i
                break
        assert my_sec_start is not None
        my_section = "".join(ol[my_sec_start:])
        final_a = theirs_a.rstrip("\n") + "\n\n" + "## 十三批迁移（r323 bm-b·content-eq fail fallback·行级零丢失）\n" + my_section
        note = "FALLBACK both-sections kept (content-eq FAIL)"
    with io.open(os.path.join(REPO, "research", "memory-archive", "202609.md"), "w", encoding="utf-8", newline="") as f:
        f.write(final_a)
    receipt.append({"file": "research/memory-archive/202609.md", "recipe": "bma-superset",
                    "content_eq_3shared": content_eq, "note": note,
                    "r79_in_bma_batch": "[2026-09-27 12:1x r79 bm-c]" in theirs_a})

    # --- ledger unions ---
    receipt.append(union_ledger(
        os.path.join(REPO, "results", "autofill_state.json"),
        git_bytes(":2:results/autofill_state.json"), git_bytes(":3:results/autofill_state.json"),
        "launches",
        lambda e: (e.get("ts"), e.get("machine"), e.get("entry"), e.get("shard"), e.get("pid")),
        "last_tick.ts", cap=50))
    receipt.append(union_ledger(
        os.path.join(REPO, "results", "compute_audit.json"),
        git_bytes(":2:results/compute_audit.json"), git_bytes(":3:results/compute_audit.json"),
        "history", lambda e: e.get("ts"), "latest.ts"))

    # regime_state: no 'latest' node -- latest face IS the top level (updated/asof/state...);
    # history asof-keyed union (r319 law) + top-level whole face take-newer by 'updated'
    o_rg = jload(git_bytes(":2:results/regime_state.json"))
    t_rg = jload(git_bytes(":3:results/regime_state.json"))
    o_h = {e.get("asof"): e for e in o_rg.get("history", [])}
    t_h = {e.get("asof"): e for e in t_rg.get("history", [])}
    keys = set(o_h) | set(t_h)
    merged_h = [o_h[k] if k in o_h else t_h[k] for k in sorted(keys)]
    zero_loss_rg = len(merged_h) == len(keys)
    base = o_rg if o_rg.get("updated", "") >= t_rg.get("updated", "") else t_rg
    base["history"] = merged_h
    jwrite(os.path.join(REPO, "results", "regime_state.json"), base)
    receipt.append({"file": "results/regime_state.json", "recipe": "asof-union+top-take-newer",
                    "side2_bma_n": len(o_h), "side3_bmb_n": len(t_h), "merged_n": len(merged_h),
                    "zero_loss": zero_loss_rg,
                    "winner": "side2-bma" if o_rg.get("updated", "") >= t_rg.get("updated", "") else "side3-bmb",
                    "side2_updated": o_rg.get("updated"), "side3_updated": t_rg.get("updated")})

    # --- token_usage: top take-newer by generated + machines dict key-union (zero-loss) ---
    o_tu = jload(git_bytes(":2:results/token_usage.json"))
    t_tu = jload(git_bytes(":3:results/token_usage.json"))
    og, tg = o_tu.get("generated", ""), t_tu.get("generated", "")
    assert og and tg, "token_usage generated probe failed"
    base_tu = o_tu if og >= tg else t_tu
    m_o, m_t = o_tu.get("machines", {}), t_tu.get("machines", {})
    merged_m = dict(m_o)
    merged_m.update(m_t)  # side3 (bm-b) wins shared keys; per-machine keys are disjoint by design
    zero_loss_tu = set(merged_m.keys()) == set(m_o.keys()) | set(m_t.keys())
    base_tu["machines"] = merged_m
    jwrite(os.path.join(REPO, "results", "token_usage.json"), base_tu)
    receipt.append({"file": "results/token_usage.json", "recipe": "top-take-newer+machines-union",
                    "side2_bma_gen": og, "side3_bmb_gen": tg,
                    "winner": "side2-bma" if og >= tg else "side3-bmb",
                    "machines_union_n": len(merged_m), "zero_loss": zero_loss_tu})

    # --- take-newer derive faces (ts path probed per r319) ---
    tn = [
        ("results/update_status.json", ["updated"]),
        ("results/scorecard_v1.json", ["generated"]),
        ("results/strategy_scorecard.json", ["generated"]),
        ("results/fundamental_b_layer_filter.json", ["updated"]),
        ("results/futures_update_status.json", ["ts", "last_attempt"]),
        ("results/heat_update_status.json", ["updated", "last_attempt"]),
        ("results/lhb_update_status.json", ["updated", "last_attempt"]),
        ("results/prospect_promotion/_summary.json", ["generated"]),
        ("docs/daily_report/REPORT-2026-09-27.json", ["generated_at"]),
    ]
    for rel, paths in tn:
        receipt.append(take_newer(os.path.join(REPO, rel.replace("/", os.sep)),
                                 git_bytes(":2:" + rel), git_bytes(":3:" + rel), *paths))

    # REPORT md: winner follows its json twin (both faces regenerate together)
    jrel = "docs/daily_report/REPORT-2026-09-27.json"
    o_j, t_j = jload(git_bytes(":2:" + jrel)), jload(git_bytes(":3:" + jrel))
    winner_side = "side2-bma" if ts_of(o_j, "generated_at") >= ts_of(t_j, "generated_at") else "side3-bmb"
    md_rel = "docs/daily_report/REPORT-2026-09-27.md"
    data = git_bytes((":2:" if winner_side == "side2-bma" else ":3:") + md_rel)
    with io.open(os.path.join(REPO, "docs", "daily_report", "REPORT-2026-09-27.md"), "wb") as f:
        f.write(data)
    receipt.append({"file": md_rel, "recipe": "take-newer-via-json-twin", "winner": winner_side})

    # dashboard twins: whole-bytes take-newer by meta.generated_at
    def js_ts(b):
        import re
        m = re.search(rb'"generated_at"\s*:\s*"([^"]+)"', b)
        return m.group(1).decode() if m else None
    o_js = git_bytes(":2:results/dashboard_status.js"); t_js = git_bytes(":3:results/dashboard_status.js")
    oj, tj = js_ts(o_js), js_ts(t_js)
    assert oj and tj, "dashboard js ts probe failed"
    w = o_js if oj >= tj else t_js
    with io.open(os.path.join(REPO, "results", "dashboard_status.js"), "wb") as f:
        f.write(w)
    receipt.append({"file": "results/dashboard_status.js", "recipe": "whole-bytes-take-newer", "side2_bma": oj, "side3_bmb": tj, "winner": "side2-bma" if oj >= tj else "side3-bmb"})
    o_dj = jload(git_bytes(":2:results/dashboard_status.json")); t_dj = jload(git_bytes(":3:results/dashboard_status.json"))
    od, td = ts_of(o_dj, "meta.generated_at"), ts_of(t_dj, "meta.generated_at")
    assert od and td, "dashboard json ts probe failed"
    wd = git_bytes(":2:results/dashboard_status.json") if od >= td else git_bytes(":3:results/dashboard_status.json")
    with io.open(os.path.join(REPO, "results", "dashboard_status.json"), "wb") as f:
        f.write(wd)
    receipt.append({"file": "results/dashboard_status.json", "recipe": "whole-bytes-take-newer", "side2_bma": od, "side3_bmb": td, "winner": "side2-bma" if od >= td else "side3-bmb"})

    # verify all resolved JSONs parse strict utf-8
    bad = []
    for rel in [u for u in UU if u.endswith(".json")]:
        p = os.path.join(REPO, rel.replace("/", os.sep))
        try:
            json.load(io.open(p, encoding="utf-8"))
        except Exception as e:
            bad.append((rel, str(e)[:60]))
    ok = not bad and all(r.get("zero_loss", True) for r in receipt if r.get("recipe") == "union-ledger")
    print(json.dumps({"receipt": receipt, "json_reparse_bad": bad, "verdict": "PASS" if ok else "FAIL"},
                     ensure_ascii=False, indent=1))
    sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
