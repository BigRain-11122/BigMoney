"""r366 bm-b push-storm canon resolver (skill bigmoney-conflict-resolve).

Latecomer yield (commit-time law: mine 07:39:23 > origin 21c691fd 07:33:07):
  - CODELY.md: base=ORIGIN + r366 entry kept hot + my dup 三十五批 pointer
    DROPPED (bm-c 三十五批/bm-a 三十六批 already archived the same 4 entries)
    + in-window fold #4 (r144 x3 + r390 -> archive 三十七批, union 复超线).
  - archive: ORIGIN verbatim + 三十七批 section; my 三十五批 section dropped
    as content-duplicate (zero-loss asserted: each of its 4 entry lines
    byte-present in origin archive).
  - rolling ledgers (compute_audit/regime_state): union list faces zero-loss
    + take-new state by ts.  x2_watch_log.jsonl: line-level union.
  - snapshots + unknown-classified (deterministic daily re-derive): take-new
    by embedded ts (mine is newer on every face, verified per-file).
  - parse-verify before write (r185); subprocess bytes only (r209).
"""
import io
import json
import re
import subprocess


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"],
                        capture_output=True)
    assert r.returncode == 0, (path, stage, r.stderr[:200])
    return r.stdout


def max_ts(b):
    hits = re.findall(rb"2026-09-2\d[T ]\d\d:\d\d:\d\d", b)
    return max(hits).decode() if hits else ""


def take_new(path):
    a, m = blob("2", path), blob("3", path)
    pick = m if max_ts(m) >= max_ts(a) else a
    if path.endswith(".json"):
        json.loads(pick.decode("utf-8"))          # r185 parse gate
    io.open(path, "wb").write(pick)
    return f"take-{'mine' if pick is m else 'origin'} ts={max_ts(pick)}"


def union_lines(path):
    a, m = blob("2", path), blob("3", path)
    la = [l for l in a.split(b"\n") if l.strip()]
    lm = [l for l in m.split(b"\n") if l.strip()]
    seen, out = set(la), list(la)
    for l in lm:
        if l not in seen:
            out.append(l)
            seen.add(l)
    body = b"\n".join(out) + (b"\n" if (a.endswith(b"\n") or
                                       m.endswith(b"\n")) else b"")
    assert len(out) >= max(len(la), len(lm)), "union lost lines"
    io.open(path, "wb").write(body)
    return f"union {len(la)}+{len(lm)}->{len(out)} lines"


def union_ledger(path, list_keys=("history", "transitions", "launches")):
    a, m = blob("2", path), blob("3", path)
    da, dm = (json.loads(x.decode("utf-8")) for x in (a, m))
    base = dm if max_ts(m) >= max_ts(a) else da
    other = da if base is dm else dm
    stats = []
    for k in list_keys:
        if isinstance(base.get(k), list) and isinstance(other.get(k), list):
            seen = {json.dumps(r, sort_keys=True, ensure_ascii=False)
                    for r in base[k]}
            add = [r for r in other[k]
                   if json.dumps(r, sort_keys=True, ensure_ascii=False)
                   not in seen]
            key = "ts"
            if add:
                allrows = base[k] + add
                allrows.sort(key=lambda r: str(r.get(key, "")))
                base[k] = allrows
            stats.append(f"{k}:{len(base[k])}")
    io.open(path, "wb").write(
        (json.dumps(base, ensure_ascii=False, indent=1) + "\n")
        .encode("utf-8"))
    return "union-ledger " + " ".join(stats)


log = []

# ---- 1. snapshots / js-wrapper / daily-derive faces: take-new by ts ------
TAKE_NEW = [
    "results/dashboard_status.json", "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/token_usage.json", "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-28.json",
    "docs/daily_report/REPORT-2026-09-28.md",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
for p in TAKE_NEW:
    log.append(f"{p}: {take_new(p)}")

# ---- 2. rolling ledgers + append log ----
log.append("results/compute_audit.json: " +
           union_ledger("results/compute_audit.json"))
log.append("results/regime_state.json: " +
           union_ledger("results/regime_state.json"))
log.append("results/x2_watch_log.jsonl: " + union_lines(
    "results/x2_watch_log.jsonl"))

# ---- 3. archive: origin verbatim + 三十七批; drop my dup section --------
A = "research/memory-archive/202609.md"
oa, mm = blob("2", A), blob("3", A)
oat, mmt = oa.decode("utf-8"), mm.decode("utf-8")

# my 三十五批 section content check: all 4 entry lines already in origin
sec35 = mmt[mmt.find("## 坑律归档 2026-09-28 三十五批"):]
mine_entries = [l for l in sec35.splitlines()
                if l.startswith("- [2026-09-28")]
assert len(mine_entries) == 4, len(mine_entries)
for l in mine_entries:
    assert l.encode("utf-8") in oa, "zero-loss fail: " + l[:50]

# fold #4: r144 x3 + r390 hot entries from origin CODELY -> 三十七批
oc = blob("2", "CODELY.md").decode("utf-8")
FOLD_PREFIX = "- [2026-09-28 07:"
fold_ids = ["r144 bm-c] 坑律：**rebase 冲突批的 UU 面清点禁经截断管道",
            "r144 bm-c] 坑律：**PowerShell 文本面追加=BOM 静默剥除面",
            "r144 bm-c] 坑律：**写层/控制台层内容失真双型",
            "r390 bm-a] 坑律：**行插入类 replace 的 old_string"]
oc_lines = oc.splitlines(keepends=True)
kept, folded = [], []
for l in oc_lines:
    if l.startswith(FOLD_PREFIX) and any(i in l for i in fold_ids):
        folded.append(l.rstrip("\n"))
    else:
        kept.append(l)
assert len(folded) == 4, f"expected 4 fold entries, got {len(folded)}"
for l in folded:
    assert any(l in kept_line for kept_line in oc.splitlines()), \
        "fold entry not from origin CODELY hot face"

my_r366 = [l for l in blob("3", "CODELY.md").decode("utf-8").splitlines()
           if l.startswith("- [2026-09-28 07:4x r366 bm-b]")]
assert len(my_r366) == 1, "r366 entry not found on my side"
r366 = my_r366[0]

ptr37 = ("冷层指针：坑律正典 2026-09-28 三十七批（r366 bm-b 窗·撞号让路重编"
         "〔origin 三十五批=r144 bm-c 先落同 4 条、本窗 bm-b 三十五批让路删〕+"
         "水位律当窗整编〔r366 新坑律 append 后 union 复超 ≤10KB 硬线〕）："
         "r144 UU 面截断管道清点 / r144 PS BOM 剥除 / r144 格式串失真 / "
         "r390 行插入锚定 四条全文 verbatim=archive 202609.md"
         "『坑律归档 2026-09-28 三十七批』节（行级零丢失校验）。")

new_codely = "".join(kept)
if not new_codely.endswith("\n"):
    new_codely += "\n"
new_codely += ptr37 + "\n" + r366 + "\n"
b = new_codely.encode("utf-8")
assert b"\r" not in b
size_c = len(b)
assert size_c <= 10240, f"CODELY still over line: {size_c}B"

sec37 = ("\n## 坑律归档 2026-09-28 三十七批（r366 bm-b 窗·撞号让路重编"
         "〔origin 三十五批先落·本窗三十五批让路〕+水位律当窗整编"
         "〔CODELY union 复超 ≤10KB 硬线〕）\n\n")
body37 = "".join(l + "\n\n" for l in folded)
new_arch = oa + sec37.encode("utf-8") + body37.encode("utf-8")

# zero-loss gate: folded lines verbatim in new archive; hot file keeps r366
for l in folded:
    assert l.encode("utf-8") in new_arch, "fold loss"
assert r366.encode("utf-8") in b, "r366 lost"
assert "三十五批（r366 bm-b" not in new_codely, "dup pointer survived"
for l in folded:
    assert l.encode("utf-8") not in b, "folded entry still hot"

io.open("CODELY.md", "wb").write(b)
io.open(A, "wb").write(new_arch)
log.append(f"CODELY.md: union base=origin + r366 hot + fold#4 三十七批 "
           f"({size_c}B)")
log.append(f"archive: origin verbatim + 三十七批 4 entries "
           f"({len(new_arch)}B); my dup 三十五批 dropped (zero-loss "
           f"asserted 4/4)")

for l in log:
    print(l)
