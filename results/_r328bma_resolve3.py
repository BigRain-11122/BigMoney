# r328 bm-a: completing rebase UU resolver (r329 session inherits dead r328 mid-rebase)
# 16-UU batch: bm-a r328 (de4cff16) replay vs origin/main f3afd952 (bm-c r85 closeout).
# CODELY.md already resolved in tree by dead session (memory-union + 十六批 archival) -> verify byte-exact here.
# 15 files with markers resolved per SKILL canon: mixed-dict+ledger / rolling-ledger / js-wrapper / snapshot.
# REBASE side semantics (inverted, r84): :2: = ours = HEAD = origin/main (bm-c face);
# :3: = theirs = replayed commit (bm-a r328 face). r140 tie -> :2:.
# 4 classifier-UNKNOWNs manually classified (fail-closed): daily_report json+md and scorecard_v1 +
# strategy_scorecard = deterministic same-day re-derive products (R216 snapshot class); md twin takes the
# SAME side as its json twin (twin consistency); all four re-derived in place by S6 chain post-rebase anyway.
import io, json, re, subprocess, sys

def sh(*args):
    r = subprocess.run(list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%d: %s" % (args, r.returncode, r.stderr[:300]))
    return r.stdout

def blob(stage, path):
    return sh("git", "show", stage + path)

def unmerged():
    out = sh("git", "diff", "--name-only", "--diff-filter=U").decode("utf-8")
    return [l for l in out.splitlines() if l.strip()]

R = []

# ---------------------------------------------------------------- ts probing
TS_KEYS = ("ts", "generated", "generated_at", "updated_at", "updated",
           "last_attempt", "last_seen", "asof", "time", "epoch", "date")

def deep_ts(obj, depth=0):
    if depth > 6 or not isinstance(obj, dict):
        return None
    for k in TS_KEYS:
        v = obj.get(k)
        if isinstance(v, bool):
            continue
        if isinstance(v, (int, float)):
            return (k, v)
        if isinstance(v, str) and len(v) >= 8 and re.match(r"^\d{4}-\d{2}-\d{2}", v):
            return (k, v)
    for v in obj.values():
        if isinstance(v, dict):
            r = deep_ts(v, depth + 1)
            if r:
                return r
    return None

def cmp_ts(a, b):
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return (a > b) - (a < b)
    return (str(a) > str(b)) - (str(a) < str(b))

# ---------------------------------------------------------------- writers
def write_bytes(path, data):
    with io.open(path, "wb") as f:
        f.write(data)

def write_json_mirror(path, data, base_bytes):
    # r85 law: mirror EOL + indent from BASE blob (never the marker-laden worktree)
    crlf = b"\r\n" in base_bytes[:4000]
    indent = 1
    for line in base_bytes.decode("utf-8", "replace").splitlines():
        if line.startswith(" {"):
            indent = len(line) - len(line.lstrip(" "))
            break
    out = json.dumps(data, ensure_ascii=False, indent=indent) + "\n"
    if crlf:
        out = out.replace("\n", "\r\n")
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(out)

def parse_ok(path):
    if path.endswith(".json"):
        json.loads(io.open(path, encoding="utf-8").read())
        return True
    return True  # md/js handled as byte-faithful takes

# ------------------------------------------------- CODELY.md verification (memory-union + archival)
STAMPS = ["- [2026-09-27 13:3x r83 bm-c]",
          "- [2026-09-27 13:5x r327 bm-b]",
          "- [2026-09-27 13:4x r326 bm-a]"]
OLD_TAIL = "（r85 勘注：两机同窗各编一批『十五批』——bm-a r327 面=四~十四批索引折叠归档、r84 bm-c 面=r321/r323/r82/r325 条目外迁，归档侧两『十五批』节并存零覆盖；后续新批自十六批起编。）"
NEW_TAIL = OLD_TAIL + "十六批外迁（r328 bm-a·rebase 撞窗水位律当窗整编）：r83 配方表覆盖面核对/r327bmb town.html 面板同步/r326bma pandas asi8 单位坑=归档十六批节·行级零丢失。"

def archival_transform(union_bytes):
    # replicate results/_r328bma_codely_archival.py exactly (universal-newline read -> LF write)
    live = union_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    removed, kept = [], []
    for ln in live.split("\n"):
        if any(ln.startswith(s) for s in STAMPS):
            removed.append(ln)
        else:
            kept.append(ln)
    assert len(removed) == 3, "archival expected 3 removals, got %d" % len(removed)
    live2 = "\n".join(kept) + ("\n" if live.endswith("\n") else "")
    assert OLD_TAIL in live2, "pointer tail missing in reconstructed union"
    live2 = live2.replace(OLD_TAIL, NEW_TAIL)
    return live2.encode("utf-8"), removed

def verify_codely():
    # Manual-class verification (skill: in-place edit -> manual review), done programmatically:
    # :3: pure-append; :2: in-place pointer-line extension + appends. Verify the dead session's
    # tree union+archival by bidirectional ENTRY-LEVEL coverage (r327 phantom/loss law):
    #   every ours/theirs entry line present in tree OR archive (archived 3);
    #   every tree entry line traceable to base/ours/theirs (zero phantoms);
    #   pointer line carries BOTH sides' batch notes; archive holds the 十六批 section verbatim.
    path = "CODELY.md"
    base = blob(":1:", path)
    ours = blob(":2:", path)
    theirs = blob(":3:", path)
    assert theirs.startswith(base), "r328 face must be pure append to base"
    tree = io.open(path, "rb").read().decode("utf-8")
    arch = io.open("research/memory-archive/202609.md", encoding="utf-8").read()
    def entries(text):
        return [ln for ln in text.replace("\r\n", "\n").split("\n") if ln.startswith("- [")]
    e_base, e_ours, e_theirs = entries(base.decode("utf-8")), entries(ours.decode("utf-8")), entries(theirs.decode("utf-8"))
    e_tree, e_arch = entries(tree), entries(arch)
    missing = [ln for ln in (e_ours + e_theirs)
               if ln not in e_tree and ln not in e_arch]
    assert not missing, "entries lost from both tree and archive: %s" % [m[:80] for m in missing]
    known = set(e_base) | set(e_ours) | set(e_theirs)
    phantom = [ln for ln in e_tree if ln not in known]
    assert not phantom, "phantom tree entries with no blob source: %s" % [p[:80] for p in phantom]
    for s in STAMPS:
        assert any(ln.startswith(s) for ln in e_arch), "archived stamp absent from archive: %s" % s
    assert "十六批外迁（r328 bm-a" in arch and "## 坑律归档 2026-09-27——十六批外迁" in arch, "archive 十六批 section missing"
    for probe in ("十五批外迁（r84 bm-c", "（r85 勘注：", "十六批外迁（r328 bm-a"):
        assert probe in tree, "pointer merge missing: %s" % probe
    assert b"<<<<<<<" not in tree.encode("utf-8")
    assert len(tree.encode("utf-8")) <= 10240, "CODELY.md over 10KB hard line"
    R.append((path, "memory-union+十六批archival (manual-class verified)",
              "entries base=%d ours=%d theirs=%d -> tree=%d archive-十六批=3" %
              (len(e_base), len(e_ours), len(e_theirs), len(e_tree)),
              "bidirectional zero-loss + zero-phantom + pointer-merge ok", "tree=%dB" % len(tree.encode("utf-8"))))
    return True

# ---------------------------------------------------------------- snapshot take-new (whole side, byte-faithful)
def take_side(path, label="snapshot"):
    a = json.loads(blob(":2:", path).decode("utf-8"))
    b = json.loads(blob(":3:", path).decode("utf-8"))
    ta, tb = deep_ts(a), deep_ts(b)
    c = cmp_ts(ta[1] if ta else None, tb[1] if tb else None)
    side = ":2:" if c >= 0 else ":3:"
    write_bytes(path, blob(side, path))
    parse_ok(path)
    R.append((path, label, "ts%s" % (ta,), "ts%s" % (tb,), "took %s (%s)" % (side, "origin/bm-c" if side == ":2:" else "replayed/bm-a")))

# ---------------------------------------------------------------- mixed-dict+ledger (autofill_state)
def resolve_autofill(path):
    a = json.loads(blob(":2:", path).decode("utf-8"))
    b = json.loads(blob(":3:", path).decode("utf-8"))
    CK = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    un = {}
    divergent = []
    for tag, side in (("A", a), ("B", b)):
        for e in side.get("launches", []):
            k = tuple(e.get(c) for c in CK)
            if k in un:
                prev = un[k]
                sp, se = set(prev), set(e)
                same = all(prev.get(c) == e.get(c) for c in (sp & se))
                if same and (sp <= se or se <= sp):
                    m = dict(prev); m.update(e); un[k] = m
                else:
                    divergent.append(k)
                    un[k] = prev if len(sp) >= len(se) else e
            else:
                un[k] = e
    ent = sorted(un.values(), key=lambda e: str(e.get("ts", "")))
    ent = ent[-50:]
    ent.sort(key=lambda e: str(e.get("ts", "")))  # ascending producer order before write-back (r245)
    lt_a, lt_b = a.get("last_tick"), b.get("last_tick")
    ta = deep_ts(lt_a); tb = deep_ts(lt_b)
    last_tick = lt_a if cmp_ts(ta[1] if ta else None, tb[1] if tb else None) >= 0 else lt_b
    assert isinstance(last_tick, dict), "last_tick must be dict"
    merged = dict(a)
    for k, v in b.items():
        if k not in merged:
            merged[k] = v
    merged["launches"] = ent
    merged["last_tick"] = last_tick
    write_json_mirror(path, merged, blob(":1:", path))
    v = json.loads(io.open(path, encoding="utf-8").read())
    assert isinstance(v["last_tick"], dict)
    keys = [tuple(e.get(c) for c in CK) for e in v["launches"]]
    assert len(keys) == len(set(map(str, keys))), "composite-key uniqueness"
    tss = [str(e.get("ts", "")) for e in v["launches"]]
    assert tss == sorted(tss), "launches ts-ascending"
    assert len(v["launches"]) <= 50
    R.append((path, "mixed-dict+ledger", "launches %d|%d -> %d" % (len(a.get("launches", [])), len(b.get("launches", [])), len(ent)),
             "last_tick took %s" % ("origin" if last_tick is lt_a else "replayed"), "divergent=%d" % len(divergent)))
    if divergent:
        print("DIVERGENT composite keys:", divergent)

# ---------------------------------------------------------------- rolling-ledger (compute_audit)
def resolve_compute_audit(path):
    a = json.loads(blob(":2:", path).decode("utf-8"))
    b = json.loads(blob(":3:", path).decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    keyf = lambda e: str(e.get("ts", ""))
    union = {}
    conflicts = []
    for e in ha + hb:
        k = keyf(e)
        if k in union:
            if json.dumps(union[k], sort_keys=True, ensure_ascii=False) != json.dumps(e, sort_keys=True, ensure_ascii=False):
                conflicts.append(k)  # same-ts divergent content: keep first = :2: face (r140 tie->HEAD)
        else:
            union[k] = e
    # survival proof (r85 law): every in-window key of both faces present in union
    ka = set(keyf(e) for e in ha)
    kb = set(keyf(e) for e in hb)
    assert ka <= set(union) and kb <= set(union), "history keyset survival FAILED"
    ent = sorted(union.values(), key=lambda e: str(e.get("ts", "")))
    la, lb = a.get("latest"), b.get("latest")
    ta, tb = deep_ts(la), deep_ts(lb)
    latest = la if cmp_ts(ta[1] if ta else None, tb[1] if tb else None) >= 0 else lb
    merged = dict(a)
    for k, v in b.items():
        if k not in merged:
            merged[k] = v
    merged["history"] = ent
    merged["latest"] = latest
    write_json_mirror(path, merged, blob(":1:", path))
    v = json.loads(io.open(path, encoding="utf-8").read())
    assert len(v["history"]) == len(union)
    R.append((path, "rolling-ledger", "history %d|%d -> %d (overlap-identical=%d, conflicts=%d)"
             % (len(ha), len(hb), len(ent), len(ka & kb) - len(conflicts), len(conflicts)),
             "latest took %s (ts %s vs %s)" % ("origin" if latest is la else "replayed", ta, tb), "survival-proof ok"))

# ---------------------------------------------------------------- rolling-ledger (regime_state)
def resolve_regime(path):
    a = json.loads(blob(":2:", path).decode("utf-8"))
    b = json.loads(blob(":3:", path).decode("utf-8"))
    def union_list(la, lb, keyf):
        un = {}
        conflicts = []
        for e in la + lb:
            k = keyf(e)
            if k in un:
                if json.dumps(un[k], sort_keys=True, ensure_ascii=False) != json.dumps(e, sort_keys=True, ensure_ascii=False):
                    conflicts.append(k)
            else:
                un[k] = e
        return sorted(un.values(), key=keyf), conflicts
    hist, hc = union_list(a.get("history", []), b.get("history", []), lambda e: str(e.get("asof", "")))
    trans, tc = union_list(a.get("transitions", []), b.get("transitions", []),
                           lambda e: json.dumps(e, sort_keys=True, ensure_ascii=False))
    ta, tb = deep_ts(a), deep_ts(b)
    base = a if cmp_ts(ta[1] if ta else None, tb[1] if tb else None) >= 0 else b
    merged = dict(base)
    merged["history"] = hist
    merged["transitions"] = trans
    write_json_mirror(path, merged, blob(":1:", path))
    json.loads(io.open(path, encoding="utf-8").read())
    R.append((path, "rolling-ledger", "history %d|%d -> %d, transitions -> %d" %
             (len(a.get("history", [])), len(b.get("history", [])), len(hist), len(trans)),
             "state took %s (updated %s vs %s)" % ("origin" if base is a else "replayed", ta, tb),
             "conflicts=%d/%d" % (len(hc), len(tc))))

# ---------------------------------------------------------------- js-wrapper-snapshot (dashboard_status.js)
def resolve_js(path):
    a = blob(":2:", path).decode("utf-8")
    b = blob(":3:", path).decode("utf-8")
    ts_in = lambda t: (re.findall(r'"generated"[:\s]*"([^"]+)"', t) or re.findall(r'"ts"[:\s]*"([^"]+)"', t) or [None])[0]
    ta, tb = ts_in(a), ts_in(b)
    c = cmp_ts(ta, tb)
    pick = a if c >= 0 else b
    write_bytes(path, pick.encode("utf-8"))
    json.loads(re.search(r"=\s*(\{.*\})\s*;?\s*$", pick, re.S).group(1))  # wrapper payload parses
    R.append((path, "js-wrapper-snapshot", ta, tb, "took %s" % (":2: origin" if c >= 0 else ":3: replayed")))

# ================================================================ main
FILES = unmerged()
print("unmerged count:", len(FILES))

ok_codely = verify_codely()
if not ok_codely:
    print("FATAL: CODELY.md tree state not reproducible from blobs -- manual review required")
    sys.exit(2)

DAILY_JSON = "docs/daily_report/REPORT-2026-09-27.json"
DAILY_MD = "docs/daily_report/REPORT-2026-09-27.md"

for p in FILES:
    if p == "CODELY.md":
        continue
    if p == "results/autofill_state.json":
        resolve_autofill(p)
    elif p == "results/compute_audit.json":
        resolve_compute_audit(p)
    elif p == "results/regime_state.json":
        resolve_regime(p)
    elif p == "results/dashboard_status.js":
        resolve_js(p)
    elif p == DAILY_JSON:
        # resolve json first, remember winning side, md twin follows the same side
        a = json.loads(blob(":2:", p).decode("utf-8"))
        b = json.loads(blob(":3:", p).decode("utf-8"))
        ta, tb = deep_ts(a), deep_ts(b)
        c = cmp_ts(ta[1] if ta else None, tb[1] if tb else None)
        side = ":2:" if c >= 0 else ":3:"
        write_bytes(p, blob(side, p))
        parse_ok(p)
        write_bytes(DAILY_MD, blob(side, DAILY_MD))  # twin-side coupling
        R.append((p + " + md-twin", "snapshot(manual-class: re-derive product)",
                  "generated_at %s|%s" % (ta, tb), "took %s" % side, "twin md byte-faithful same side"))
    elif p == DAILY_MD:
        continue  # handled with the json twin
    else:
        # snapshots incl. manual-classified re-derive products:
        # scorecard_v1 / strategy_scorecard / fundamental_b_layer_filter / futures|heat|lhb_update_status
        # / token_usage / update_status / dashboard_status.json
        take_side(p)

# post-write marker scan (nothing may keep conflict markers)
bad = [p for p in FILES if p != DAILY_MD and
       (b"<<<<<<<" in io.open(p, "rb").read() or b">>>>>>>" in io.open(p, "rb").read())]
assert not bad, "markers remain: %s" % bad

print("== resolve3 report ==")
for r in R:
    print(" ", r)
print("RESOLVE3 DONE")
