"""r511 bm-b W12-yield rebase resolver (bigmoney-conflict-resolve canon).

Collision verdict: bm-a r523 delivered the W12 freeze suite on origin
(A=63_050..65_049, engine_owner=bm-a, 12/12 burned per their closeout)
while bm-b drafted the same wave locally (A=63_001..65_000). r239
commit-order law: bm-b's commit is unsent on a local replay -> late ->
YIELD. Origin's W12 stands; local W12 suite + shards + claims discarded.

Resolution classes:
  yield      -> git show :2: (origin side verbatim): prereg/law/mirrors/
                runner/shard products 0..5
  host       -> :2: wholesale (r378 D-03 C-family single-writer host=bm-a):
                strategy_scorecard/scorecard_v1/dashboard_status.{js,json}
  newer      -> wall-clock newer of :2:/:3: (idempotent same-day derive
                faces, tie -> :3: mine): docs REPORT/LIVE twins,
                token_usage, update_status, lhb/futures status,
                fundamental_b_layer_filter, _attrition_guard_scan
  union      -> compute_audit.json (history union + latest newer-wins,
                r504 canon), regime_state.json (history/transitions union
                + scalars newer-wins, r510 canon), pool_core_samples.jsonl
                (binary line union, r503/r510 canon)
  codely     -> :2: base + amended bm-b entry appended (yield-facts
                included)
  discard    -> bm-b W12 claim dirs (SHARD-0..5) removed
  annotate   -> _r511bmb_w12_band_gate.py yield addendum
"""
import subprocess, json, io, os, shutil

def blob(stage, path):
    return subprocess.check_output(["git", "show", stage + ":" + path])

def write_bytes(path, data):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with io.open(path, "wb") as f:
        f.write(data)

def probe_ts(obj):
    for k in ("generated", "ts", "updated", "updated_at", "asof"):
        if isinstance(obj, dict) and k in obj:
            return str(obj[k])
    return ""

# ---- 1. yield + host files: take :2: verbatim ----
yield_files = [
    "research/PERPETUAL_N1_W12_PREREG.md",
    "research/PERPETUAL_FACES.md",
    "scripts/perpetual_faces.py",
    "scripts/perpetual_faces_n1.py",
] + [f"results/p2cal_ext/n1_w12/shard-{k}-of-12.json" for k in range(6)]
host_files = [
    "results/strategy_scorecard.json", "results/scorecard_v1.json",
    "results/dashboard_status.json", "results/dashboard_status.js",
]
for p in yield_files + host_files:
    write_bytes(p, blob(":2", p))
    print("take-origin:", p)

# ---- 2. wall-clock-newer idempotent derive faces ----
newer_files = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/token_usage.json", "results/update_status.json",
    "results/lhb_update_status.json", "results/futures_update_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/_attrition_guard_scan.json",
]
for p in newer_files:
    try:
        t2 = probe_ts(json.loads(blob(":2", p)))
        t3 = probe_ts(json.loads(blob(":3", p)))
        side = ":2" if t2 > t3 else ":3"
        why = f"ts {t2} vs {t3}"
    except Exception:
        side, why = ":3", "probe-fail-default-mine"
    write_bytes(p, blob(side, p))
    print(f"take-{side[1:]}-newer: {p} ({why})")

# ---- 3. compute_audit.json: history union + latest newer-wins ----
a2 = json.loads(blob(":2", "results/compute_audit.json"))
a3 = json.loads(blob(":3", "results/compute_audit.json"))
seen, hist = set(), []
for e in a2.get("history", []) + a3.get("history", []):
    key = json.dumps(e, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); hist.append(e)
hist.sort(key=lambda e: str(e.get("ts", "")))
latest = a2["latest"] if probe_ts(a2.get("latest", {})) > probe_ts(a3.get("latest", {})) else a3["latest"]
merged_audit = {"history": hist, "latest": latest}
write_bytes("results/compute_audit.json",
            (json.dumps(merged_audit, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
print(f"union: results/compute_audit.json history {len(a2.get('history',[]))}+{len(a3.get('history',[]))}->{len(hist)}")

# ---- 4. regime_state.json: history/transitions union + scalars newer-wins ----
r2 = json.loads(blob(":2", "results/regime_state.json"))
r3 = json.loads(blob(":3", "results/regime_state.json"))
def union_list(x2, x3):
    seen, out = set(), []
    for e in x2 + x3:
        key = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key); out.append(e)
    return out
base = r2 if probe_ts(r2) > probe_ts(r3) else r3
base = dict(base)
base["history"] = union_list(r2.get("history", []), r3.get("history", []))
base["transitions"] = union_list(r2.get("transitions", []), r3.get("transitions", []))
write_bytes("results/regime_state.json",
            (json.dumps(base, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
print(f"union: results/regime_state.json hist {len(base['history'])} trans {len(base['transitions'])}")

# ---- 5. pool_core_samples.jsonl: binary line union ----
s2 = blob(":2", "results/pool_core_samples.jsonl")
s3 = blob(":3", "results/pool_core_samples.jsonl")
crlf = b"\r\n" in s2
nl = b"\r\n" if crlf else b"\n"
lines2 = [l for l in s2.splitlines() if l.strip()]
lines3 = [l for l in s3.splitlines() if l.strip()]
seen, out = set(), []
for l in lines2 + lines3:
    if l not in seen:
        seen.add(l); out.append(l)
write_bytes("results/pool_core_samples.jsonl", nl.join(out) + nl)
print(f"union: pool_core_samples.jsonl {len(lines2)}+{len(lines3)}->{len(out)} (crlf={crlf})")

# ---- 6. CODELY.md: origin base + amended bm-b entry ----
codely_base = blob(":2", "CODELY.md").decode("utf-8")
entry = ("- [2026-10-01 16:2x r511 bm-b] 引擎波跨机双冻结撞车+让票律（W12 实弹·r239/r483 承用·r297 认领可见性族"
         "新变体）：never-dry 常设步对引擎波无跨机认领可见面（不入池=零 claim 心跳）→ bm-a r523 与本机 r511 同窗"
         "各自冻结 W12（本机 A=63_001..65_000·bm-a A=63_050..65_049·同 63_000..66_000 间隙窗重叠 1,951 值+B 带"
         "全同 29_100..29_299）双烧撞车；裁定=commit 时间序后到让路（本机 commit 未达 origin=让），五步正解="
         "①截断本机在飞烧录（本例 rebase 冲突标记破坏 runner import=自然截断属幸运遏制非可依赖机制）②yield 件全取"
         " origin 侧（prereg/法典/N1_BANDS/WAVE_CONFIGS/分片产物）③本机已烧分片与 claim 件全弃（finalize 从未跑="
         "科学账本零双计污染）④回执 MSG+轮报告 yield_record ⑤观察项=引擎波供给线跨机锁设计（wave-freeze 行展"
         "前 fetch+查表尾=唯一现役锁）。姊妹课：带位「首自由窗」必须穷尽扫描全预留面（预告面只列硬撞点——本机机闸"
         "二层抓真撞 40_050/41_000+41_001..42_999 净空 1,999 差一窗；本机扫描起点 63_001 vs bm-a 落位 63_050="
         "两机扫描序分歧待法典面澄清，穷尽扫描律本身成立）；枚举快照腿禁硬编码须 derive（pf engine-wave 白名单 "
         "(10,11) 腿被 W12 打红当场 derive 化修）。How to apply：never-dry 续波动作前必 fetch+查法典 §4 表尾行"
         "是否已被他机展行（引擎波无 claim 面=表格行就是唯一锁）；一切带位跳位先跑穷尽扫描机闸再落行。")
sep = "\r\n" if "\r\n" in codely_base else "\n"
if not codely_base.endswith(sep):
    codely_base += sep
codely_base += entry + sep
write_bytes("CODELY.md", codely_base.encode("utf-8"))
print("codely: origin base + amended bm-b entry")

# ---- 7. discard bm-b W12 claim dirs (yielded burn) ----
for k in range(6):
    d = f"results/pool_claims/PERPETUAL-N1-W12-SHARD-{k}"
    if os.path.isdir(d):
        shutil.rmtree(d)
        print("discard-claim-dir:", d)

# ---- 8. annotate band gate receipt with yield addendum ----
p = "results/_r511bmb_w12_band_gate.py"
t = io.open(p, encoding="utf-8").read()
addendum = ('''\n"""YIELD ADDENDUM (r511 bm-b, post-freeze): this receipt documented the
bm-b draft-window ADMIT for A=63_001..65_000. bm-a r523 delivered the W12
freeze suite on origin FIRST (A=63_050..65_049, engine_owner=bm-a); per
r239 commit-order law bm-b yielded -- the frozen W12 law row is bm-a's,
and this window was never burned into any finalize. Kept as collision
evidence + exhaustive-scan pattern reference (the scan law itself stands).
"""\n''')
if "YIELD ADDENDUM" not in t:
    io.open(p, "w", encoding="utf-8", newline="").write(t + addendum)
print("annotate: band gate receipt yield addendum")

print("RESOLVER DONE")
