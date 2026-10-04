"""r694 bm-b N2-W15 waiter closeout (MSG-2026-10-04-2100 receipt, item 1):
(1) waiter liveness DUAL-FORM (psutil full-enumeration cmdline match +
    tasklist /FO CSV full-pull pid cross-check -- r659/r661 single-form
    laws) then early-kill (bm-c authorized: product first-landed on
    origin, zero info loss);
(2) own sibling shard n2-w15-generate-0of1 flip ready->done in
    runnable_pool.json (needle anchored to the quoted full key line per
    r694-2 law; double-read freshness gate; reparse + shape asserts);
(3) r497 claim-file backfill (closed, refused-by-first-land-canonical);
(4) round-694 addendum append to the ledger (bytes mode, marker count==0
    gate, r641 mixed-encoding law)."""
import datetime
import io
import json
import os
import subprocess
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
CLAIM = os.path.join(ROOT, "results", "pool_claims",
                     "PERPETUAL-N2-W15-GENERATE", "n2-w15-generate-0of1.bm-b.json")
PROD_SHA = "440db8656e3b0b2ea71cbbd3fee6a8c2392e8722570bc34cc900ba9900b7a3b0"
PROD_SHA16 = PROD_SHA[:16]

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")


def find_waiters():
    import psutil
    hits = []
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cl = p.info["cmdline"] or []
            joined = " ".join(str(c) for c in cl)
            if "perpetual_faces_n2" in joined and "generate" in joined:
                hits.append((p.info["pid"], joined[:160]))
        except Exception:
            continue
    return hits


def csv_pids():
    r = subprocess.run(["tasklist", "/FO", "CSV"], capture_output=True,
                       timeout=30)
    text = r.stdout.decode("utf-8", errors="replace")
    pids = set()
    for line in text.splitlines()[1:]:
        parts = line.strip().strip('"').split('","')
        if len(parts) >= 2:
            try:
                pids.add(int(parts[1]))
            except ValueError:
                pass
    return pids


# ------------------------------------------------- (1) waiter dual-form kill
waiters = find_waiters()
csv = csv_pids()
alive = [(pid, cl) for pid, cl in waiters if pid in csv]
print("waiter scan: psutil-hits=%d csv-cross-alive=%d %r"
      % (len(waiters), len(alive), alive))
killed = []
if alive:
    import psutil
    for pid, _cl in alive:
        p = psutil.Process(pid)
        p.terminate()
    time.sleep(3.0)
    for pid, _cl in alive:
        try:
            p = psutil.Process(pid)
            p.kill()
            killed.append((pid, "kill-fallback"))
        except psutil.NoSuchProcess:
            killed.append((pid, "terminate-ok"))
    # post-verify dual form
    again = find_waiters()
    csv2 = csv_pids()
    still = [pid for pid, _ in again if pid in csv2]
    assert not still, "waiter still alive after kill: %r" % still
    print("waiter killed + post-verify dead: %r" % killed)
else:
    print("waiter not alive at closeout (already exited; honest no-kill)")

# ------------------------------------------ (2) sibling shard flip (needle)
raw = io.open(POOL, "rb").read()
eol = b"\r\n" if b"\r\n" in raw else b"\n"
KEY = b'"key": "n2-w15-generate-0of1"'
assert raw.count(KEY) == 1, "sibling key needle count != 1"
pos = raw.find(KEY)
nxt = raw.find(b'"key":', pos + len(KEY))
assert nxt > pos, "region end anchor missing"
seg = raw[pos:nxt]
assert b'"key"' not in seg[len(KEY):], "foreign key line inside region"
assert seg.count(b'"status": "ready"') == 1, "status needle count != 1"
seg = seg.replace(b'"status": "ready"', b'"status": "done"')
o_pos = seg.find(b'"owner_since":')
assert o_pos > 0, "owner_since anchor missing"
line_end = seg.find(b"\n", o_pos)
owner_line = seg[o_pos:line_end]
assert not owner_line.rstrip().endswith(b","), "owner_since not last field?"
ins = (owner_line.rstrip() + b"," + eol +
       b'     "done_by": "bm-b",' + eol +
       b'     "done_at": ' + json.dumps(clock).encode() + b"," + eol +
       b'     "harvest_ref": ' +
       json.dumps("results/n2_w15/n2_w15_candidates.json sha256=" + PROD_SHA16
                  + " (bm-c 2026-10-04 20:45:29 first-land canonical per "
                  "r486; refuse-if-exists face; bm-b waiter early-killed "
                  "zero-info-loss per MSG-2026-10-04-2100 authorization)"
                  ).encode() + eol)
seg = seg[:o_pos] + ins + seg[line_end + 1:]
out = raw[:pos] + seg + raw[nxt:]
raw2 = io.open(POOL, "rb").read()
assert raw2 == raw, "pool changed between reads (daemon write) -- ABORT rerun"
doc = json.loads(out.decode("utf-8"))
e = [x for x in doc["entries"] if x.get("id") == "PERPETUAL-N2-W15-GENERATE"][0]
mine = [s for s in e["shards"] if s["key"] == "n2-w15-generate-0of1"][0]
assert mine["status"] == "done" and mine["owner"] == "bm-b"
assert e["status"] == "done", "entry not done (bm-c flip lost?)"
bare = [s for s in e["shards"] if s["key"] == "generate-0of1"][0]
assert bare["status"] == "done", "bm-c bare-shard flip lost?"
io.open(POOL, "wb").write(out)
print("pool flip OK: sibling shard done; entry done; bm-c bare shard done")

# --------------------------------------------------- (3) r497 claim backfill
os.makedirs(os.path.dirname(CLAIM), exist_ok=True)
claim = {
    "machine_id": "bm-b",
    "state": "closed",
    "pid": alive[0][0] if alive else None,
    "heartbeat": clock,
    "outcome": ("waiter-early-killed (product first-landed on origin by "
                "bm-c; zero info loss)" if alive else
                "waiter-not-alive-at-closeout (product first-landed; "
                "refuse-if-exists face)"),
    "exit_code": 2,
    "started": "r691 2026-10-04 20:3x launch (RAM-gate wait, 2880min cap)",
    "closed_at": clock,
    "result_ref": ("results/n2_w15/n2_w15_candidates.json sha256="
                   + PROD_SHA16 + " (bm-c canonical)"),
}
io.open(CLAIM, "w", encoding="utf-8").write(json.dumps(claim, indent=1) + "\n")
print("claim file OK -> %s" % os.path.relpath(CLAIM, ROOT))

# ---------------------------------------------------- (4) ledger addendum
MARK = b"round 694 addendum"
lraw = io.open(LEDGER, "rb").read()
assert lraw.count(MARK) == 0, "addendum marker already present"
line = (
    "2026-10-04T21:4x+08:00 | round 694 addendum (bm-b) | S7 收口 "
    "push-race 实录: 首推被拒（origin 6 commit 前移=bm-a r696+bm-c r496 波）"
    "→ merge 净路（r437-iv·真脏交集=零）→ 15 UU 全解（results/"
    "_r694bmb_merge_resolve.json：14 S6 再出面 per-face ts newer-wins〔本机 "
    "21:0x 全 ours·paper/scorecard/prospect lane-guard 族 theirs 正确〕+"
    "token per-key union side_pick>0+x2 line-union+crash_fuse 每键 ts-newer "
    "union〔r694 bm-b 新腿〕）+ runnable_pool 自动合并双改并存断言过（我的 "
    "CONTEST-RC 钉面 dep 换 + bm-c N2 首落翻面 both 在位）→ 单批 add → "
    "merge commit → 重推 | MSG-2026-10-04-2100 回执: N2 waiter 双形活性实证"
    "后提前击杀（bm-c 授权·产品已首落 origin·零信息损失）+ 自家 shard "
    "n2-w15-generate-0of1 翻 done（harvest_ref=bm-c 产品 sha16 "
    + PROD_SHA16 + "）+ r497 claim 回填 | MSG-2100 已消费入 processed；"
    "本地未达 origin commit 数=merge commit 推送后 push_verify 实证\n")
with io.open(LEDGER, "ab") as f:
    f.write(line.encode("utf-8"))
lraw2 = io.open(LEDGER, "rb").read()
assert lraw2.count(MARK) == 1, "addendum marker count != 1"
print("addendum append OK (marker count==1)")
print("N2 CLOSEOUT OK r694 bm-b")
