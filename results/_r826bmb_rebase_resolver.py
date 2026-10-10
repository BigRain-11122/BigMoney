# r826 bm-b rebase resolver — pick1 = local r825 replay vs onto = bm-a r948 (landed first).
# Same-window dual-dev collision on E4 (OMO probe) + S6 regen storm (21 UU/AA faces).
# Skill: bigmoney-conflict-resolve. Machine laws: r648 sha channel, r782 rebase stage
# semantics (stage2=onto=origin/bm-a, stage3=replay=local r825), r140 tie->HEAD(stage2),
# r100/R350 deep-ts probe (value-shape only, wall-clock required), r188/R208 ledgers
# union zero-loss, r185 parse-verify before write, r808-bm-c marker guard.
# E4 shared-path yield: scripts/omo_liquidity_probe.py -> origin side (bm-a r948 primary
# by land order); bm-b findings preserved at distinct-path evidence + survey doc.
import io, json, re, subprocess

R = lambda a: subprocess.run(a, capture_output=True).stdout

uu = {}
for ln in R(["git", "ls-files", "-u"]).decode("utf-8", "replace").splitlines():
    meta, path = ln.split("\t")
    _, sha, stage = meta.split()
    uu.setdefault(path, {})[int(stage)] = sha

def blob(sha):
    b = subprocess.run(["git", "cat-file", "-p", sha], capture_output=True).stdout
    assert b, "EMPTY BLOB READ r648: " + sha
    return b

TS = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")
def deep_ts(o):
    best, st = "", [o]
    while st:
        x = st.pop()
        if isinstance(x, dict):
            for v in x.values():
                if isinstance(v, (dict, list)): st.append(v)
                elif isinstance(v, str) and TS.match(v) and v > best: best = v
        elif isinstance(x, list):
            for v in x:
                if isinstance(v, (dict, list)): st.append(v)
                elif isinstance(v, str) and TS.match(v) and v > best: best = v
        elif isinstance(x, str) and TS.match(x) and x > best: best = x
    return best

receipt = {"round": "r826-pick1", "stage_semantics": "rebase r782: s2=onto(origin/bm-a r948) s3=replay(local r825)",
           "faces": {}, "law": "skill bigmoney-conflict-resolve; r648/r782/r140/r100/R350/r188/R208/r185"}
def jload(path, side):
    return json.loads(blob(uu[path][side]).decode("utf-8"))
def wbytes(path, b):
    assert b"<<<<<<<" not in b and b">>>>>>>" not in b, "marker in " + path
    io.open(path, "wb").write(b)
def snap(path, note=""):
    d2, d3 = jload(path, 2), jload(path, 3)
    t2, t3 = deep_ts(d2), deep_ts(d3)
    side = 2 if t2 >= t3 else 3                      # r140 tie -> HEAD(onto=s2)
    wbytes(path, blob(uu[path][side]))
    receipt["faces"][path] = {"recipe": "snapshot take-newer " + note, "ts_s2": t2, "ts_s3": t3, "side": side}
    return side

# --- twins families: probe one member, apply SAME side to all members (r98/r99/r100)
fam_rep = ["docs/daily_report/REPORT-2026-10-10.json", "docs/daily_report/REPORT-2026-10-10.md"]
fam_live = ["docs/live_usage/LIVE-2026-10-10.json", "docs/live_usage/LIVE-2026-10-10.md",
            "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"]
for fam, probe in ((fam_rep, fam_rep[0]), (fam_live, fam_live[0])):
    d2, d3 = jload(probe, 2), jload(probe, 3)
    t2, t3 = deep_ts(d2), deep_ts(d3)
    side = 2 if t2 >= t3 else 3
    for p in fam:
        wbytes(p, blob(uu[p][side]))
        receipt["faces"][p] = {"recipe": "twin-family take-newer same side", "probe": probe, "ts_s2": t2, "ts_s3": t3, "side": side}

# --- single snapshots (hardened probe; wins by in-doc wall-clock ts)
for p in ["results/daily_scorecard.json", "results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/dashboard_status.json", "results/fundamental_b_layer_filter.json",
          "results/futures_update_status.json", "results/lhb_update_status.json",
          "results/update_status.json", "results/token_usage.json", "results/_attrition_guard_scan.json"]:
    snap(p)

# --- rolling ledgers: union rows zero-loss, scalars from newer side (r188/R208, r824 template)
def rowkey(r): return json.dumps(r, sort_keys=True, ensure_ascii=False)
for p, keys in [("results/compute_audit.json", ["history"]),
                ("results/regime_state.json", ["triggers", "transitions", "history"])]:
    d2, d3 = jload(p, 2), jload(p, 3)
    t2, t3 = deep_ts(d2), deep_ts(d3)
    doc = dict(d2 if t2 >= t3 else d3)
    counts = {}
    for k in keys:
        seen, out = set(), []
        for src in (d2, d3):
            for r in (src.get(k) or []):
                kk = rowkey(r)
                if kk not in seen:
                    seen.add(kk); out.append(r)
        if out and all(isinstance(r, dict) and "ts" in r for r in out):
            out.sort(key=lambda r: str(r.get("ts")))
        doc[k] = out
        counts[k] = {"s2": len(d2.get(k) or []), "s3": len(d3.get(k) or []), "union": len(out)}
        assert len(out) >= max(counts[k]["s2"], counts[k]["s3"]), "UNION LOSS " + p + "/" + k
    txt = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    json.loads(txt)
    assert "<<<" not in txt and ">>>" not in txt
    io.open(p, "w", encoding="utf-8", newline="\n").write(txt)
    receipt["faces"][p] = {"recipe": "ledger union zero-loss + scalars newer", "ts_s2": t2, "ts_s3": t3, "scalar_side": 2 if t2 >= t3 else 3, "counts": counts}

# --- js-wrapper snapshot: whole bytes of newer side, wrapper preserved (R209)
p = "results/dashboard_status.js"
b2, b3 = blob(uu[p][2]), blob(uu[p][3])
m2 = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?", b2.decode("utf-8", "replace"), re.S)
m3 = re.search(r"window\.DASH_DATA\s*=\s*(\{.*\})\s*;?", b3.decode("utf-8", "replace"), re.S)
t2 = deep_ts(json.loads(m2.group(1))) if m2 else ""
t3 = deep_ts(json.loads(m3.group(1))) if m3 else ""
side = 2 if t2 >= t3 else 3
wbytes(p, b2 if side == 2 else b3)
receipt["faces"][p] = {"recipe": "js-wrapper take-newer whole bytes (R209)", "ts_s2": t2, "ts_s3": t3, "side": side}

# --- AA probe script: yield shared path to origin (bm-a r948 landed-first primary)
p = "scripts/omo_liquidity_probe.py"
wbytes(p, blob(uu[p][2]))
compile(blob(uu[p][2]), p, "exec")                     # syntax-verify origin side
receipt["faces"][p] = {"recipe": "AA yield-to-origin: land-order primary=bm-a r948; bm-b 641-line variant superseded (findings preserved at results/omo_liquidity_probe.json + survey doc)", "s2_bytes": len(blob(uu[p][2])), "s3_bytes": len(blob(uu[p][3]))}

# --- queue md: origin base + E4 row dual annotation + r825 yield record (r947-E3 precedent)
p = "state/queue/explore.md"
t2 = blob(uu[p][2]).decode("utf-8")
t3 = blob(uu[p][3]).decode("utf-8")
eol = "\r\n" if "\r\n" in t2 else "\n"
anchor = "状态翻转） | research/digests/DIGEST-20261010-omo-liquidity-face.md | done |"
ext = ("状态翻转）＋r825 bm-b 同窗收敛判读（akshare 全库 1141 函数名×17 关键词零净投放命中·"
       "月度存量面 356 月·FR007×GC007 同日 r=0.869/728 重叠日） | "
       "research/digests/DIGEST-20261010-omo-liquidity-face.md+research/shortline/OMO_LIQUIDITY_DATA_FEASIBILITY.md | done |")
assert t2.count(anchor) == 1, "E4 row anchor not unique in origin blob"
merged = t2.replace(anchor, ext)
i3 = t3.find("> r825 消耗记录")
assert i3 >= 0, "r825 record missing in replay blob"
rec3 = t3[i3:].rstrip("\r\n")
prefix_old = "> r825 消耗记录（bm-b）：E4 本轮完成出列（"
prefix_new = ("> r825 消耗记录（bm-b）：E4 同窗撞头后到让路注记（bm-a r948 先落 origin=primary"
              "〔探针共享名 scripts/omo_liquidity_probe.py 让路取 origin 侧 384 行版·判负判词与数据债/复活通道以 bm-a r948 调研件为准〕"
              "·r825 bm-b 同窗独立完成=convergent secondary·独立路径证据保全）——原消耗记录：E4 本轮完成出列（")
assert rec3.count(prefix_old) == 1
rec3 = rec3.replace(prefix_old, prefix_new)
out = merged + eol + rec3 + eol
assert "<<<<<<<" not in out and ">>>>>>>" not in out
assert "> r948 消耗记录" in out and "r825 消耗记录" in out
io.open(p, "w", encoding="utf-8", newline="").write(out)
receipt["faces"][p] = {"recipe": "queue md: origin base + E4 row dual annotation + r825 yield record (r947-E3 yield precedent)", "eol": repr(eol)}

# --- final marker sweep over every face written
bad = []
for p in list(receipt["faces"]):
    b = io.open(p, "rb").read()
    if b"<<<<<<<" in b or b">>>>>>>" in b: bad.append(p)
assert not bad, "MARKERS REMAIN: " + repr(bad)
with io.open("results/_r826bmb_rebase_resolver.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print("RESOLVED", len(receipt["faces"]), "faces; zero markers; receipt results/_r826bmb_rebase_resolver.json")
for k, v in receipt["faces"].items():
    print(" ", k, "->", v.get("recipe", "")[:80], "side:", v.get("side", v.get("scalar_side", "")), "ts2:", v.get("ts_s2", ""), "ts3:", v.get("ts_s3", ""))
