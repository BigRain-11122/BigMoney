# r532 bm-b final surgical push: W40 closeout + S6 faces + bookkeeping.
# Same net path as _r532bmb_s0_surgical.py (in-flight nulls.jsonl blocks rebase).
import subprocess, os, sys

R = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(R)

def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")

# S4 memory line first (CODELY.md hot layer, one matter, lesson-first)
PIT = ("[2026-10-02 02:5x r532 bm-b] \u5728\u98de runner \u8ffd\u5199\u4ef6\u88ab\u63d0\u4ea4\u4e3a"
" checkpoint \u540e=\u8f6e\u4f1a\u8bdd rebase \u7ed3\u6784\u6027\u6b7b\u8def\u9762\uff08S0 \u6574\u5408\u65b0\u51c0\u8def\uff09"
"\uff1aLOWAMP-P3-NULLS \u70e7\u5f55\u5728\u98de\uff08append ~0.4s/\u884c\uff09\u65f6\u5176\u4ea7\u54c1 nulls.jsonl \u5df2\u6309 r310 "
"\u5165\u518c\u2192tracked \u6d3b\u5199\u4ef6\u4f7f git rebase \u6052\u62d2 unstaged changes\uff0cride/amend \u5faa\u73af=\u4e22\u884c\u9762"
"\uff08r299 autostash \u65cf\u540c\u56e0\uff09\u2192\u6b63\u89e3=S0 \u6574\u5408\u76f4\u63a5\u5916\u79d1 diff-based payload\uff08read-tree "
"origin/main+\u9010\u4ef6 hash-object+payload-count \u65ad\u8a00+deletion-set \u7a7a\u65ad\u8a00+\u9001\u8fbe ls-tree "
"\u81ea\u8bc1\uff09\uff0c\u5171\u4eab regen \u9762\u8ba9 origin \u4fa7\uff08\u672c\u8f6e S6 \u518d derive\uff09\uff1b\u5bf9\u9f50\u540e checkout "
"\u6062\u590d\u9648\u65e7\u9762\uff1b\u70e7\u6bd5\u524d\u7981\u624b\u5de5\u7ffb\u6c60\uff08\u5728\u98de\u2260ghost\uff0cr488 \u5224\u636e\u5148\u67e5\u8fdb\u7a0b"
"\u6d3b\u6027+\u884c\u6570\u589e\u957f\u7387\uff09\u3002How to apply\uff1a\u51e1 tracked \u6d3b\u5199\u4ef6\u5728\u573a=\u7981 rebase/amend/"
"autostash \u4e00\u5f8b\u5916\u79d1\uff1b\u300cready \u9762\u7591 ghost\u300d\u5148\u9a8c pid \u6d3b\u6027+\u4ea7\u7269\u589e\u957f\u7387\u518d\u5b9a\u6027\u3002\n")
p = "CODELY.md"
raw = open(p, "rb").read()
crlf = b"\r\n" in raw
sep = b"\r\n" if crlf else b"\n"
if raw and not raw.endswith(sep):
    raw += sep
open(p, "wb").write(raw + PIT.encode("utf-8"))
print("CODELY.md pit appended")

rc, out = git("fetch", "origin")
rc, parent = git("rev-parse", "origin/main")
assert rc == 0, parent
parent = parent.strip()
print("parent=", parent)

PAYLOAD = [
    "CODELY.md",
    "state.json",
    "fleet/machines/bm-b.json",
    "logs/iteration-loop/round_reports.md",
    "research/PERPETUAL_N1_W40_PREREG.md",
    "results/perpetual_faces/n1_w40_results.json",
    "docs/daily_report/REPORT-2026-10-02.json",
    "docs/daily_report/REPORT-2026-10-02.md",
    "docs/live_usage/LIVE-2026-10-02.json",
    "docs/live_usage/LIVE-2026-10-02.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/astock_daily_update_status.json",
    "results/autofill_state.bm-b.json",
    "results/compute_audit.bm-b.json",
    "results/compute_audit.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/etf_daily_pull_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.bm-b.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.bm-b.json",
    "results/lhb_update_status.json",
    "results/lowamp_p3/nulls.jsonl",
    "results/p1d_gates.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/pool_dualrun.bm-b.jsonl",
    "results/regime_state.bm-b.json",
    "results/regime_state.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/ledger_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.bm-b.json",
    "results/token_usage.json",
    "results/update_status.bm-b.json",
    "results/update_status.json",
    "results/_r532bmb_s0_surgical.py",
    "results/_r532bmb_align_fix.py",
    "results/_r532bmb_s78_backfill.py",
    "results/_r532bmb_closeout.py",
]
UNION = "results/x2_watch_log.jsonl"   # append-only shared: union leg

idx = os.path.join(os.environ["TEMP"], "fg-r532final-idx")
if os.path.exists(idx):
    os.remove(idx)
os.environ["GIT_INDEX_FILE"] = idx
rc, out = git("read-tree", parent)
assert rc == 0, out

n = 0
for f in PAYLOAD:
    if not os.path.exists(f):
        print("MISSING", f, "-- ABORT"); sys.exit(1)
    rc, out = git("hash-object", "-w", f)
    assert rc == 0, out
    rc, out = git("update-index", "--add", "--cacheinfo",
                  f"100644,{out.strip()},{f}")
    assert rc == 0, out
    n += 1
print("staged payload:", n, "of", len(PAYLOAD))

# union leg for x2_watch_log
org = subprocess.check_output(["git", "show", f"{parent}:{UNION}"]).decode(
    "utf-8", errors="replace").splitlines()
mine = open(UNION, encoding="utf-8", errors="replace").read().splitlines()
oset = set(org)
extra = [l for l in mine if l not in oset]
union = org + extra
print(f"x2 union: origin={len(org)} + mine-unique={len(extra)}")
tmp = os.path.join(os.environ["TEMP"], "r532-x2-union.jsonl")
open(tmp, "w", encoding="utf-8", newline="").write("\n".join(union) + "\n")
rc, out = git("hash-object", "-w", tmp)
assert rc == 0, out
rc, out = git("update-index", "--add", "--cacheinfo",
              f"100644,{out.strip()},{UNION}")
assert rc == 0, out
n += 1
payload = PAYLOAD + [UNION]
assert n == len(payload)

rc, tree = git("write-tree")
assert rc == 0, tree
tree = tree.strip()

msg_path = os.path.join(os.environ["TEMP"], "r532final-msg.txt")
open(msg_path, "w", encoding="utf-8", newline="\n").write(
    "round 532: r531-CRASH RECOVERY + W40 FULL CLOSEOUT (THIRTIETH wave "
    "finalized, bm-b thirteenth-owned): finalize one-pass prev 448,340 (W39 "
    "bm-c r343 head, origin-verified) + 2,200 = 450,540 CHAIN HEAD; K-lift "
    "-0.0002 (1.1571->1.1569 @n_eff_held 448,340); S5 4/4 PASS dual-anchor "
    "(W38 frozen + W39 rolled: mu d 0.0043/0.0048<0.02, sigma -0.43%/+1.85%"
    "<10%, A-p95 0.3057 d 0.0062/0.0063<0.05); ledger block persisted "
    "science_gates.ledger (r509 face); prereg s7/s8 mechanical backfill "
    "byte-safe + post-backfill default-wave selftest PASS (r522-2/r307 "
    "two-state) + S0 surgical db5110d55 earlier this round (W40 12/12 "
    "products first delivery + salvage superset; in-flight nulls.jsonl "
    "checkpoint = rebase-blocker new face -> surgical net path per r523/"
    "r512/r530 family; bm-a r549 bit-identical double-freeze yielded canon "
    "via their fixup ac9c9bad8) + engine ledger 12/12 flush 02:28:03 (r522 "
    "orphan self-heal) + S6 chain rc0 full (dualrun 1 DRIFT obs-phase streak "
    "reset honest, compute_audit CLEAN burning-healthy, WM loaded_ok, "
    "holiday no-ops honest, scorecard/clock/report/live_usage regenerated "
    "L3-takeover faces, monthly set skipped=Oct-1 ran) + S7 (attrition "
    "CLEAN, loop pin=2, watchdog S4U, claw, state 530->532 skip-531 "
    "per r529 law, heartbeat epoch int verified) + LOWAMP-P3-NULLS burn "
    "ACTIVE 683+/2000 daemon-managed no hand flip + CODELY r532 pit "
    "(in-flight tracked checkpoint = rebase blocker, surgical S0 net path) "
    "[bm-b]\n")
rc, sha = git("commit-tree", tree, "-p", parent, "-F", msg_path)
assert rc == 0, sha
sha = sha.strip()
print("newcommit=", sha)

rc, dels = git("diff", "--name-only", "--diff-filter=D", parent, sha)
if dels.strip():
    print("DELETION DETECTED -- ABORT (r519):"); print(dels); sys.exit(1)
print("deletion-set empty PASS")
present = 0
for f in payload:
    rc, out = git("ls-tree", sha, "--name-only", f)
    if out.strip() == f:
        present += 1
print("payload presence:", present, "of", len(payload))
assert present == len(payload)

rc, out = git("push", "origin", f"{sha}:refs/heads/main")
print("push rc=", rc, "|", out.strip()[-140:])
if rc != 0:
    print("REJECTED -- re-run (blob retry cheap r512)")
    sys.exit(2)
rc, out = git("fetch", "origin")
rc, out = git("rev-parse", "origin/main")
assert out.strip() == sha, ("origin not at sha", out.strip())
print("delivery self-verify PASS")
rc, out = git("update-ref", "refs/heads/main", sha)
rc, out = git("reset", "--mixed", "HEAD")
print("local aligned; HEAD:", sha[:10])
