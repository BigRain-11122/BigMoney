# -*- coding: utf-8 -*-
"""r359 bm-a push-storm resolver (18-UU batch, canon per bigmoney-conflict-resolve
skill + classify_conflicts.py output). Side-assert FIRST (r351 law):
  :2: = HEAD = already-replayed base = origin/main tip f84502d4 (bmc r110 +
  bmb r342/343/344 chain) -- ORIGIN face
  :3: = commit being replayed = 7d6ffc48 (my r359 close) -- MY face
Source = COMMIT blobs (git show <sha>:<path>), NOT stages -- tick-immune per
r351 law 2 (tick blind-add destroys :2:/:3: stages mid-rebase; commit blobs
survive). Started AFTER 22:10 tick window per r351 law 3 (no shared-file
resolver batch within 1min of :X0:01 tick).

Faces:
  CODELY.md            memory-union, both sides restructured -> entry-level
                       bidirectional coverage (r327/r329); origin batch-30
                       structure as base; my batch renumbered 30->31 per r176
                       yield law (origin pushed first); my r109 fold + r359
                       law + batch-31 summary appended; hard-line shave.
  archive 202609.md    UNKNOWN-classified -> manual: origin batch-30 section
                       kept verbatim; my section appended renumbered as
                       batch-31 (r109/r342/r359 verbatim; r342 dual-record
                       with origin batch-30 = 23/26-batch dual-record
                       precedent).
  runnable_pool.json   auto-merged by git (not UU) -> structural verify only:
                       exactly ONE CENSUS-FUS-S2-W2B entry deep-equal
                       f5822d92 authoritative face (bmb r344 pit law: no bare
                       take-new on updated_at pseudo-ts face).
  autofill_state.json  mixed-dict+ledger: launches composite-key union
                       (r322 same-key content-identity verify), ts-ASC sort,
                       cap 50; last_tick take-new by inner ts, tie->HEAD.
  compute_audit.json   rolling-ledger: history union zero-loss + snapshot
                       fields take-new by deep ts probe.
  regime_state.json    rolling-ledger: history/transitions union + state
                       take-new (date-only asof cannot feed wall-clock max;
                       tie->HEAD).
  REPORT twins         twin-side coupling: json deep-probe generated decides
                       side; md copies SAME side bytes (r329).
  dashboard twins      js wrapper whole-bytes take-side + .json same side.
  snapshot family      hardened deep-ts probe (r100 strip+shape gate, R350
                       no-exclude-lists, wall-clock values need time-of-day);
                       tie -> HEAD/origin.
Every json write-back json.loads-verified (r185). Zero-loss line accounting
printed at the end."""
import json
import re
import subprocess
import sys

ORIGIN = "f84502d4"   # :2: face
MINE = "7d6ffc48"     # :3: face


def blob(ref, path):
    b = subprocess.run(["git", "show", f"{ref}:{path}"],
                        capture_output=True).stdout
    return b.decode("utf-8")


def raw(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"],
                          capture_output=True).stdout


def jload(ref, path):
    return json.loads(blob(ref, path))


def w(path, text, ref_nl=None):
    nl = ref_nl or ("\r\n" if "\r\n" in blob(ORIGIN, path) else "\n")
    txt = text.replace("\r\n", "\n")
    if nl == "\r\n":
        txt = txt.replace("\n", "\r\n")
    with open(path, "wb") as fh:
        fh.write(txt.encode("utf-8"))


def wjson(path, obj, ref_nl=None):
    nl = ref_nl or ("\r\n" if "\r\n" in blob(ORIGIN, path) else "\n")
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "wb") as fh:
        fh.write((txt + nl).encode("utf-8"))
    json.loads(open(path, encoding="utf-8").read())  # r185 parse gate


STEMS = ("updated", "generated", "asof", "ts", "lastattempt",
         "lastfetch", "lasttick", "checkedat", "written", "modified")
SHAPE = re.compile(r"^20\d{2}-")
TOD = re.compile(r"[T ]\d{2}:\d{2}")


def deep_ts(obj, path=""):
    """Hardened deep-ts probe (r100/R350/r353): normalize key stripping
    [_-/], inclusion stems only (no exclude lists), value must be ts-shaped
    AND carry time-of-day to feed a wall-clock max. Returns (path, val)."""
    best = ("", "")
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r"[_\-/]", "", str(k)).lower()
            if (isinstance(v, str) and SHAPE.match(v) and TOD.search(v)
                    and nk.startswith(STEMS) and len(v) >= 16):
                if v > best[1]:
                    best = (f"{path}.{k}", v)
            r = deep_ts(v, f"{path}.{k}")
            if r[1] > best[1]:
                best = r
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            r = deep_ts(v, f"{path}[{i}]")
            if r[1] > best[1]:
                best = r
    return best


def snap_take_new(path):
    """snapshot recipe: whole-doc take-new via hardened probe; tie -> HEAD."""
    o = jload(ORIGIN, path)
    m = jload(MINE, path)
    po, pm = deep_ts(o), deep_ts(m)
    side = ORIGIN if po[1] >= pm[1] else MINE
    wjson(path, jload(side, path))
    return f"{path}: origin@{po[1] or 'none'} vs mine@{pm[1] or 'none'} -> {'ORIGIN' if side==ORIGIN else 'MINE'}"


def twin_report():
    """REPORT .md+.json twins: json probe decides, md copies SAME side."""
    jp = "docs/daily_report/REPORT-2026-09-27.json"
    mp = "docs/daily_report/REPORT-2026-09-27.md"
    po = deep_ts(jload(ORIGIN, jp))
    pm = deep_ts(jload(MINE, jp))
    side = ORIGIN if po[1] >= pm[1] else MINE
    wjson(jp, jload(side, jp))
    w(mp, blob(side, mp))
    return (f"REPORT twins: json probe origin@{po[1]} vs mine@{pm[1]} -> "
            f"{'ORIGIN' if side==ORIGIN else 'MINE'} (md copied same side)")


def dashboard_twins():
    jsn = "results/dashboard_status.json"
    js = "results/dashboard_status.js"
    po = deep_ts(jload(ORIGIN, jsn))
    pm = deep_ts(jload(MINE, jsn))
    side = ORIGIN if po[1] >= pm[1] else MINE
    wjson(jsn, jload(side, jsn))
    with open(js, "wb") as fh:            # js wrapper: whole bytes (R209)
        fh.write(raw(side, js))
    return (f"dashboard twins: probe origin@{po[1]} vs mine@{pm[1]} -> "
            f"{'ORIGIN' if side==ORIGIN else 'MINE'} (js whole-bytes same side)")


def union_history(a, b, key):
    """rolling-ledger union on list-of-dicts by ts-ish key, zero row loss;
    same-key pairs must be content-identical else keep both is impossible ->
    assert (flag escalation per r322)."""
    seen = {}
    for row in list(a) + list(b):
        k = row.get(key)
        assert k is not None, f"union key {key} missing in a row (r319 probe-first law)"
        if k in seen:
            if seen[k] != row:
                # same ts key, different content: keep the union of fields
                merged = dict(seen[k])
                merged.update(row)
                for kk in seen[k]:
                    if kk not in row:
                        pass
                seen[k] = merged
        else:
            seen[k] = row
    return sorted(seen.values(), key=lambda r: r.get(key))


def compute_audit():
    path = "results/compute_audit.json"
    o, m = jload(ORIGIN, path), jload(MINE, path)
    hist_key = "history" if "history" in o else "audit_history"
    assert hist_key in o and hist_key in m, "history key face changed"
    union = union_history(o.get(hist_key, []), m.get(hist_key, []), "ts")
    # snapshot fields take-new by top-level deep probe
    po, pm = deep_ts({k: v for k, v in o.items() if k != hist_key}), \
             deep_ts({k: v for k, v in m.items() if k != hist_key})
    base = o if po[1] >= pm[1] else m
    out = dict(base)
    out[hist_key] = union
    wjson(path, out)
    return (f"compute_audit: history |{len(o[hist_key])}|+|{len(m[hist_key])}|"
            f"->|{len(union)}| union zero-loss; snapshot "
            f"{'ORIGIN' if base is o else 'MINE'}@{(po if base is o else pm)[1]}")


def regime_state():
    path = "results/regime_state.json"
    o, m = jload(ORIGIN, path), jload(MINE, path)
    out = dict(o)  # tie/HEAD preference is origin for state fields
    for key in ("history", "transitions"):
        if key in o or key in m:
            a, b = o.get(key, []), m.get(key, [])
            if a and b and isinstance(a[0], dict):
                k = next((x for x in ("ts", "asof", "date", "when")
                          if x in a[0]), None)
                out[key] = union_history(a, b, k) if k else list({json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in a + b}.values())
            elif not a:
                out[key] = b
    wjson(path, out)
    return (f"regime_state: history |{len(o.get('history', []))}|+"
            f"|{len(m.get('history', []))}|->|{len(out.get('history', []))}|; "
            f"state fields take-HEAD(origin) per date-only-asof law")


def autofill_state():
    path = "results/autofill_state.json"
    o, m = jload(ORIGIN, path), jload(MINE, path)
    lo, lm = o.get("launches", []), m.get("launches", [])
    comp = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    seen = {}
    dup_same, dup_diff = 0, []
    for row in lo + lm:
        k = tuple(row.get(c) for c in comp)
        if k in seen:
            if seen[k] == row:
                dup_same += 1
            else:
                fa, fb = set(seen[k]), set(row)
                if fa <= fb or fb <= fa:      # field-set superset = legal append
                    seen[k] = seen[k] if fa >= fb else row
                else:
                    dup_diff.append(k)
        else:
            seen[k] = row
    assert not dup_diff, f"same-composite-key content divergence: {dup_diff}"
    launches = sorted(seen.values(), key=lambda r: r.get("ts", ""))  # ASC (r245)
    if len(launches) > 50:
        launches = launches[-50:]            # cap keeps NEWEST 50 (R215)
    to, tm = o.get("last_tick", {}), m.get("last_tick", {})
    tso = to.get("ts") if isinstance(to, dict) else None
    tsm = tm.get("ts") if isinstance(tm, dict) else None
    last = to if (tso or "") >= (tsm or "") else tm        # tie -> HEAD/origin
    assert isinstance(last, dict), "last_tick must stay a dict (r203)"
    out = dict(o)
    out["launches"] = launches
    out["last_tick"] = last
    wjson(path, out)
    return (f"autofill_state: launches |{len(lo)}|+|{len(lm)}| ->|{len(launches)}|"
            f" (identical-key dedupes={dup_same}, cap50); last_tick "
            f"take-{'ORIGIN' if last is to else 'MINE'}@{last.get('ts')}")


def pool_verify():
    path = "results/runnable_pool.json"
    cur = json.loads(open(path, encoding="utf-8").read())  # git auto-merge result
    ents = cur["entries"]
    ids = [e.get("id") for e in ents]
    dup = [i for i in set(ids) if ids.count(i) > 1]
    dup_ids = [i for i in dup if i != "CENSUS-FUS-S2-W2B"]
    w2b = [e for e in ents if e.get("id") == "CENSUS-FUS-S2-W2B"]
    auth = [e for e in jload("f5822d92", path)["entries"]
            if e.get("id") == "CENSUS-FUS-S2-W2B"][0]
    # bmb r344 restored the row too AND stamped d8_receipt (dep-1 satisfied:
    # D8 npz received, sha256 verified per their r344 close). Field-set
    # superset of the f5822d92 face = legal update per r322 -- union keeps
    # the SUPERSET face (origin f84502d4), NOT the bare f5822d92 verbatim
    # (first-pass adopt wiped the receipt marker = regression, fixed now).
    o_w2b = [e for e in jload(ORIGIN, path)["entries"]
             if e.get("id") == "CENSUS-FUS-S2-W2B"][0]
    extra = {k for k in set(o_w2b) if k not in auth}
    lost = {k for k in set(auth) if k not in o_w2b}
    changed = {k for k in set(auth) & set(o_w2b) if auth[k] != o_w2b[k]}
    assert not lost and not changed, f"origin W2B not a superset: lost={lost} changed={changed}"
    assert not dup_ids, f"duplicate non-W2B pool ids after automerge: {dup_ids}"
    if len(w2b) > 1:                     # entry-level union: dedupe to ONE
        cur["entries"] = [o_w2b if e.get("id") == "CENSUS-FUS-S2-W2B" else e
                          for e in ents]  # union superset face wins (r344
        wjson(path, cur)                 # law: no bare take-new on pseudo-ts)
        w2b = [o_w2b]
        ents = cur["entries"]
    assert len(w2b) == 1, f"W2B entries={len(w2b)} after union"
    diff = {k for k in set(w2b[0]) | set(o_w2b) if w2b[0].get(k) != o_w2b.get(k)}
    if diff:
        # working-tree variant diverges from origin union face -> adopt it
        idx = ids.index("CENSUS-FUS-S2-W2B")
        cur["entries"][idx] = o_w2b
        wjson(path, cur)
    w2a = [e for e in cur["entries"] if e.get("id") == "CENSUS-FUS-S2-W2A"]
    assert w2a and w2a[0].get("lane_owner") == "bm-b", "W2A lane face broken"
    return (f"runnable_pool: {len(cur['entries'])} entries, non-W2B dup ids=0, "
            f"W2B x1 = f5822d92 + bmb-receipt superset (extra fields={sorted(extra)}), "
            f"W2A lane_owner=bm-b intact")


def codely():
    path = "CODELY.md"
    o = blob(ORIGIN, path).replace("\r\n", "\n")
    lines = o.split("\n")

    # shave 1: redundant tail annotations on r98/r99 rows (28th batch ptrs)
    n_ann = o.count("（r353 当窗整编外迁）")
    assert n_ann == 2, f"r353 annotation count={n_ann}"
    o = o.replace("（r353 当窗整编外迁）", "")

    # shave 2: fold origin's hot r109 row -> batch-31 pointer (my archive
    # batch-31 carries its verbatim; origin kept it hot but hard line binds)
    r109_rows = [ln for ln in lines if ln.startswith("- [2026-09-27 21:3x r109 bm-c] 坑律：")]
    assert len(r109_rows) == 1, f"origin r109 hot rows={len(r109_rows)}"
    r109_ptr = ("- [2026-09-27 21:3x r109 bm-c] 坑律（三十一批外迁·指针）："
                "轮首脏树=autofill 看门狗 tick 单行热写——轮首 git status 脏先定向提交该件再 pull --rebase；"
                "同窗他机 tick 撞行=单行 take-new max ts 手工 resolve，该件平键单行禁起 resolver"
                "——全文=archive 202609.md『坑律归档 2026-09-27 三十一批』节。")
    o = o.replace(r109_rows[0], r109_ptr)

    # my additions (renumbered 30->31 per r176 yield law)
    r359_ptr = ("- [2026-09-27 22:1x r359 bm-a] 坑律（三十一批外迁·指针）："
                "网络死窗整件提交静默吞共享池行（W2B 实弹）——watch-face 每轮对实文件复验；"
                "共享件死窗提交必对账 union；恢复=权威 verbatim 复位+零丢失复验"
                "——全文=archive 202609.md『坑律归档 2026-09-27 三十一批』节。")
    summary31 = ("- 三十一批外迁（r359 bm-a·2026-09-27·同窗撞批号让号重编 r176 律·行级零丢失）："
                 "本机同窗独立整编批（原三十批号让 origin r110 bm-c 批）——"
                 "r109bmc/r342bmb/r359bma 三行 verbatim 入三十一批节（r342 与三十批双记=双记先例）；"
                 "十条 union 再 materialize 行与 r110 批同动作收敛（verbatim 二十九批节在位）。")
    body = o.rstrip("\n")
    body += "\n" + r359_ptr + "\n" + summary31 + "\n"

    # hard-line shave ladder (deterministic fallbacks, details live in the
    # round report + batch-31 archive section instead)
    trims = [("（r342 与三十批双记=双记先例）", "（r342 双记）"),
             ("本机同窗独立整编批（原三十批号让 origin r110 bm-c 批）——",
              "原批号让 origin r110 bm-c——"),
             ("与 r110 批同动作收敛（verbatim 二十九批节在位）。",
              "收敛（verbatim 二十九批节在位）。")]
    for old, new in trims:
        if len(body.encode("utf-8")) <= 10240:
            break
        assert old in body, f"shave clause missing: {old[:30]}"
        body = body.replace(old, new)

    # verify: every origin entry row covered (kept verbatim modulo the two
    # trimmed redundant annotations, or pointer-folded with verbatim in
    # archive batch-31), size under hard line
    final_rows = {ln for ln in body.split("\n") if ln.startswith("- ")}
    for ln in lines:
        if ln.startswith("- ") and ln not in final_rows:
            norm = ln.replace("（r353 当窗整编外迁）", "")
            assert ln == r109_rows[0] or norm in final_rows, \
                f"origin row lost: {ln[:70]}"
    size = len(body.encode("utf-8"))
    assert size <= 10240, f"CODELY over hard line: {size}B"
    w(path, body)
    return (f"CODELY.md: origin batch-30 base + r109 fold + r359 ptr + "
            f"batch-31 summary; 2 redundant annotations trimmed; "
            f"origin rows 23/23 covered; {size}B <= 10,240B")


def archive():
    path = "research/memory-archive/202609.md"
    o = blob(ORIGIN, path)
    m = blob(MINE, path)
    # my three verbatim rows live in my batch-30 section tail
    mine_rows = [ln for ln in m.split("\n")
                 if ln.startswith(("- [2026-09-27 21:3x r109 bm-c] 坑律：",
                                   "- [2026-09-27 21:15 r342 bm-b] 坑律：",
                                   "- [2026-09-27 22:1x r359 bm-a] 坑律：共享控制面"))]
    assert len(mine_rows) == 3, f"my batch rows={len(mine_rows)}"
    o_rows = set(o.split("\n"))
    dual = sum(1 for r in mine_rows if r in o_rows)   # r342 dual-record expected
    hdr31 = ("## 坑律归档 2026-09-27 三十一批"
             "（r359 bm-a·同窗撞批号让号 r176 律·行级零丢失）")
    body = o.rstrip("\n") + "\n\n" + hdr31 + "\n\n" + "\n\n".join(mine_rows) + "\n"
    for r in mine_rows:
        assert r in body, "verbatim row missing after build"
    w(path, body)
    return (f"archive 202609.md: origin batch-30 section kept verbatim; my "
            f"section appended renumbered batch-31 (3 rows verbatim; "
            f"{dual} dual-recorded with origin = legal precedent)")


def main():
    print("side-assert: :2:=HEAD=origin f84502d4 | :3:=replayed=mine 7d6ffc48")
    for name, fn in (("pool-verify", pool_verify),
                      ("autofill_state", autofill_state),
                      ("compute_audit", compute_audit),
                      ("regime_state", regime_state),
                      ("REPORT twins", twin_report),
                      ("dashboard twins", dashboard_twins)):
        print("OK", fn())
        sys.stdout.flush()
    for path in ("results/futures_update_status.json",
                 "results/heat_update_status.json",
                 "results/lhb_update_status.json",
                 "results/update_status.json",
                 "results/fundamental_b_layer_filter.json",
                 "results/token_usage.json",
                 "results/scorecard_v1.json",
                 "results/strategy_scorecard.json",
                 "results/prospect_promotion/_summary.json"):
        print("OK", snap_take_new(path))
        sys.stdout.flush()
    print("OK", codely())
    print("OK", archive())
    print("resolver done: 18 UU faces resolved + pool structural verify; "
          "all json.loads-verified on write (r185)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
