# r426 bm-b rebase-replay conflict resolver (22 UU, single-commit replay: r425 4185a8534 onto bm-a r428 501f77290)
# Canon: .codely-cli/skills/bigmoney-conflict-resolve/SKILL.md + classify_conflicts.py output
#   17 classified (snapshot/twin/rolling-ledger/js-wrapper/memory-union) + 5 UNKNOWN manual-classified:
#   live_usage x4 = same-day idempotent regen twin family (snapshot law, twins same side);
#   research/memory-archive/202609.md = pure-append union (prefix identity asserted on both sides).
# Rebase side law (pit-72): :2: = ours = HEAD = onto (bm-a r428 origin side); :3: = theirs = replayed
#   local commit (bm-b r425 crashed-round side). Tie -> :2: (r140 same-second law).
# Reused verbatim from results/_r427bma_pushstorm2_resolve.py (deep_ts probe + take-new + twin + laws)
# and results/_r94bmc_resolve_compute_audit.py (r341 whole-entry canonical dedup union law).
import subprocess, json, re, sys

TS_RX = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None

def deep_ts(obj, best=("", "")):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and TS_RX.match(v):
                if v > best[0]:
                    best = (v, str(k))
            else:
                best = deep_ts(v, best)
    elif isinstance(obj, list):
        for it in obj:
            best = deep_ts(it, best)
    return best

def resolve_json_take_new(path):
    b2, b3 = blob(2, path), blob(3, path)
    if b2 is None and b3 is None:
        print(f"[FAIL] {path}"); return None
    p2 = deep_ts(json.loads(b2))[0] if b2 else ""
    p3 = deep_ts(json.loads(b3))[0] if b3 else ""
    stage = 2 if (not p3 or p2 >= p3) else 3   # tie -> :2: ours/origin (r140)
    json.loads(blob(stage, path))              # parse-verify staged bytes before write
    with open(path, "wb") as f:
        f.write(blob(stage, path))
    print(f"[take-new] {path}: :{stage}: ours_ts={p2} theirs_ts={p3}")
    return stage

def resolve_twin(jp, bp):
    s = resolve_json_take_new(jp)
    if s is None:
        print(f"[SKIP-twin] {bp}"); return
    b = blob(s, bp)
    if b is None:
        print(f"[FAIL-twin] {bp}"); return
    with open(bp, "wb") as f:
        f.write(b)
    print(f"[twin-copy] {bp}: whole-bytes :{s}: same-side law")

# ---------- compute_audit.json rolling-ledger union (r188/R208/r341 law) ----------
def resolve_compute_audit(path):
    ha = json.loads(blob(2, path))
    ta = json.loads(blob(3, path))
    key_h = [k for k in ha.keys() if isinstance(ha[k], list)]
    assert key_h, 'no list key in HEAD compute_audit'
    hist_key = key_h[0] if len(key_h) == 1 else max(key_h, key=lambda k: len(ha[k]))
    hl, tl = ha.get(hist_key, []), ta.get(hist_key, [])
    def canon(e): return json.dumps(e, sort_keys=True, ensure_ascii=False)
    seen, union = set(), []
    for e in hl + tl:
        k = canon(e)
        if k not in seen:
            seen.add(k); union.append(e)
    union.sort(key=lambda e: str(e.get('ts', '')))
    # dedup keys must exist inside entries (r319 probe per-face before union)
    missing = sum(1 for e in union if 'ts' not in e)
    out = dict(ha)                    # top-level schema from ours/HEAD side
    out[hist_key] = union
    if 'latest' in ha and union:
        out['latest'] = union[-1]    # latest = newest entry by ts
    # mirror producer serialization: probe indent + trailing newline from :2: blob
    raw2 = blob(2, path)
    indent = 2 if re.search(rb'\n  "', raw2[:400]) else 4
    trail_nl = raw2.endswith(b'\n')
    s = json.dumps(out, ensure_ascii=False, indent=indent)
    if trail_nl: s += '\n'
    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(s)
    chk = json.load(open(path, encoding='utf-8'))
    n = len(chk[hist_key])
    print(f"[union] {path}: ours={len(hl)} theirs={len(tl)} -> union={len(union)} "
          f"(dedup={len(hl)+len(tl)-len(union)}, no-ts-entries={missing}) hist_key={hist_key} "
          f"latest_ts={union[-1].get('ts') if union else 'EMPTY'}")
    assert n == len(union)

# ---------- CODELY.md memory-union: conflict-block splice ----------
# Working tree = cleanly-merged both-sides changes + ONE conflict block where HEAD-side is
# empty (bm-a deleted 102/103 hot lines; bm-b deleted same + inserted own cold-layer pointer).
# Resolution = keep theirs block content (the only non-empty side). Both machines' entries preserved.
def resolve_codely(path):
    raw = open(path, 'rb').read()
    # line-based block parser (regex ^-anchor after non-DOTALL group cannot cross \n - live-fire fix)
    lines = raw.split(b'\n')
    starts = [i for i, l in enumerate(lines) if l.rstrip(b'\r') == b'<<<<<<< HEAD']
    assert len(starts) == 1, f'CODELY.md expected 1 conflict block, got {len(starts)}'
    i = starts[0]
    j = next(i2 for i2 in range(i + 1, len(lines)) if lines[i2].rstrip(b'\r') == b'=======')
    k = next(i2 for i2 in range(j + 1, len(lines)) if lines[i2].startswith(b'>>>>>>> '))
    head_side, theirs_side = lines[i + 1:j], lines[j + 1:k]
    assert all(l.strip() == b'' for l in head_side), f'CODELY.md HEAD side not empty: {head_side[:2]!r}'
    assert any(l.strip() for l in theirs_side), 'CODELY.md theirs side empty - manual review'
    out_lines = lines[:i] + theirs_side + lines[k + 1:]
    out = b'\n'.join(out_lines)
    assert b'<<<<<<< ' not in out and b'>>>>>>> ' not in out, 'markers remain'
    open(path, 'wb').write(out)
    txt = out.decode('utf-8')
    for probe in ['一百零四批', 'r427 bm-a] 坑律一百零五批', 'r425 bm-b] 坑律一百零五批',
                  '冷层指针：坑律正典 2026-09-29 一百零二批', 'W8 泊位起草与预测重校律']:
        assert probe in txt, f'CODELY.md lost entry: {probe}'
    for gone in ['坑律一百零二批（S0 rebase 队列构成诊断律', '坑律一百零三批（池条目 lane_owner']:
        assert gone not in txt.split('### Reference')[0], f'CODELY.md hot 102/103 not archived: {gone}'
    print(f"[memory-union] {path}: 1 block spliced (HEAD empty -> theirs kept), "
          f"probes 5/5 OK, bytes={len(out)}")

# ---------- archive 202609.md pure-append direct-concat union ----------
# base=4185a8534^, ours=+6 lines (r427 bm-a 窗批), theirs=+14 lines (r425 bm-b 窗批+流水整编).
# Both sides appended verbatim sections -> resolved = base + ours_suffix + theirs_suffix.
def resolve_archive(path):
    b = subprocess.run(['git', 'show', '4185a8534^:' + path], capture_output=True).stdout
    o, t = blob(2, path), blob(3, path)
    assert o.startswith(b), 'archive ours prefix-identity FAIL (in-place edit? manual review)'
    assert t.startswith(b), 'archive theirs prefix-identity FAIL (in-place edit? manual review)'
    out = o + t[len(b):]                     # ours whole (base+ours_suffix) + theirs_suffix
    open(path, 'wb').write(out)
    txt = out.decode('utf-8')
    assert '<<<<<<< ' not in txt, 'archive markers remain'
    for probe in ['坑律归档 2026-09-29 r427 bm-a 窗批', '坑律归档 2026-09-29 r425 bm-b 窗批',
                  '流水整编 2026-09-29 r425 bm-b 窗批']:
        assert probe in txt, f'archive lost section: {probe}'
    nb, no, nt = b.count(b'\n'), o.count(b'\n'), t.count(b'\n')
    print(f"[append-union] {path}: base={nb} ours={no} theirs={nt} -> union={out.count(chr(10).encode())} "
          f"(expect {no + (nt-nb)}) sections 3/3 OK")

if __name__ == '__main__':
    ONLY_MEMORY = len(sys.argv) > 1 and sys.argv[1] == 'memory'
    PAIRS = [
        ("results/dashboard_status.json", "results/dashboard_status.js"),
        ("docs/daily_report/REPORT-2026-09-29.json", "docs/daily_report/REPORT-2026-09-29.md"),
        ("docs/live_usage/LIVE-2026-09-29.json", "docs/live_usage/LIVE-2026-09-29.md"),
        ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
    ]
    SNAPS = [
        "results/futures_update_status.json", "results/lhb_update_status.json",
        "results/update_status.json", "results/scorecard_v1.json",
        "results/strategy_scorecard.json", "results/fundamental_b_layer_filter.json",
        "results/t35_open_fill_verify.json", "results/token_usage.json",
        "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
        "results/regime_state.json",
    ]
    if not ONLY_MEMORY:
        for jp, bp in PAIRS:
            resolve_twin(jp, bp)
        for p in SNAPS:
            resolve_json_take_new(p)
        resolve_compute_audit("results/compute_audit.json")
    resolve_codely("CODELY.md")
    resolve_archive("research/memory-archive/202609.md")
    ok = True
    for p in [x for pair in PAIRS for x in pair] + SNAPS + ["results/compute_audit.json"]:
        if p.endswith(".json"):
            try: json.load(open(p, encoding="utf-8"))
            except Exception as e: ok = False; print(f"[VERIFY-FAIL] {p}: {e}")
    for p in ["CODELY.md", "research/memory-archive/202609.md", "results/dashboard_status.js"]:
        s = open(p, 'rb').read()
        # line-anchored marker check: verbatim historical law text may QUOTE marker
        # strings mid-line (live-fire: archive pos 54259 `}` 在 >>>>>>> 后公共区) - legal
        if re.search(rb'(?m)^<<<<<<< |^>>>>>>> ', s):
            ok = False; print(f"[VERIFY-FAIL markers] {p}")
    print("ALL-PARSE-OK" if ok else "VERIFY-FAILURES")
    sys.exit(0 if ok else 2)
