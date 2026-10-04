"""r696 bm-b addendum closeout: CODELY pit + round-report addendum + HB refresh."""
import datetime
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().isoformat(timespec="seconds") + "+08:00"
EPOCH = int(time.time())

# 1) CODELY pit entry (bytes mode, EOL-detected, idem gate)
# NOTE: MARK must byte-match the ENTRY text (no space between tick and x).
MARK = "r696 bm-b] daemon tick\u00d7merge \u7a97\u53e3worktree\u9648\u65e7\u56de\u5199\u5751"
ENTRY = (
    "- [2026-10-04 21:5x r696 bm-b] daemon tick\u00d7merge \u7a97\u53e3worktree\u9648\u65e7\u56de\u5199\u5751"
    "\uff08r696 \u6536\u53e3\u53cc\u6ce2 push-race \u5b9e\u5f39\u00b7merge \u5f15\u64ce\u4ea7\u7269\u4e0e\u76d8\u9762\u5206\u88c2\u5f53\u573a\u5b9a\u8c23\u96f6\u4f24\u5bb3\uff09\uff1a"
    "treadmill \u673a\u7fa4\u4e0b autofill daemon tick\uff08~10min \u5468\u671f\uff09\u53ef\u4e0e `git merge` \u540c\u7a97\uff1adaemon \u4ee5 tick \u8d77\u70b9\u7684\u5185\u5b58\u9648\u65e7\u6c60\u89c6\u56fe\u56de\u5199 worktree"
    "\uff08\u8986\u76d6 merge \u5df2\u843d\u76d8\u7684\u6b63\u786e\u5408\u5e76\u4ea7\u7269\uff09\uff0c\u5176\u540e\u7eed\u90e8\u5206\u63d0\u4ea4\u5728\u51b2\u7a81\u672a\u89e3\u7a97\u88ab git \u62d2\uff08partial commit during merge\uff09"
    "\u2192\u51c0\u6001=\u7d22\u5f15 stage0=\u6b63\u786e\u5408\u5e76\u3001worktree=\u9648\u65e7 HEAD \u7248\uff08\u672c\u4f8b runnable_pool.json \u4e22 bm-a SHARD-3 done \u7ffb\u9762\u4e8e\u76d8\u9762\uff09\uff1b"
    "\u8bca\u65ad\u6cd5=\u4e09\u63a2\u9488\uff08merge-base/HEAD/MERGE_HEAD \u4e09\u9762 SHARD \u771f\u503c + stage0 `git show :0:<path>` \u89e3\u6790 + worktree==HEAD \u5b57\u8282\u6bd4\u5bf9\uff09\uff1b"
    "\u6b63\u6cd5=\u786e\u8ba4\u672c\u4fa7\u5bf9\u8be5\u9762\u96f6\u6539\u52a8\u540e `git checkout -- <path>` \u4ece\u7d22\u5f15\u6062\u590d worktree\uff0c\u518d\u8dd1\u65ad\u8a00\u4e0e\u63d0\u4ea4\uff1b"
    "\u7981\u6309 worktree \u76f4\u89c9\u5224\u300c\u4ed6\u673a\u7ffb\u9762\u4e22\u5931\u300d\u800c\u91cd\u505a\u624b\u672f\u3002How to apply\uff1a\u9a71\u52a8\u9762\u5408\u5e76\u7a97\u6536\u53e3\u524d\u5fc5\u8dd1"
    "\u300cstaged \u9762\u626b\u63cf\uff1aworktree==HEAD \u4e14\u975e UU \u9762=churn-race \u5acc\u7591\u300d\uff08_r696bmb_lost_scan.py \u8303\u5f0f\uff09\uff1b\u4e09\u8bc1\u5148\u4e8e\u91cd\u505a\uff08r661 \u65cf\uff09\u3002"
)
p = os.path.join(ROOT, "CODELY.md")
with open(p, "rb") as f:
    blob = f.read()
if blob.count(MARK.encode("utf-8")) == 1:
    print("CODELY pit already present (prior write OK) -- skip append")
else:
    assert blob.count(MARK.encode("utf-8")) == 0, "idem gate"
eol = b"\r\n" if blob.count(b"\r\n") * 2 > blob.count(b"\n") else b"\n"
if not blob.endswith(eol):
    blob += eol
    blob += ENTRY.encode("utf-8") + eol
    with open(p, "wb") as f:
        f.write(blob)
with open(p, "rb") as f:
    assert f.read().count(MARK.encode("utf-8")) == 1
print("CODELY pit verified")

# 2) round report addendum (append-only, marker idem gate)
rp = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
MARK2 = "round 696 addendum (bm-b)"
line = (
    NOW + " | round 696 addendum (bm-b) | S7 \u6536\u53e3\u53cc\u6ce2 push-race \u5b9e\u5f55\uff1a\u9996\u63a8\u88ab\u62d2"
    "\uff08origin \u524d\u8fdb 12 commit=bm-c r497/498 \u53cc\u6ce2\u96c6\u6210+bm-a r698 absorb+N2-W15 SHARD-3 bm-a done/SARD-4 bm-c claim\uff09"
    "\u2192 merge #1 17 UU\u2192resolver\uff08r694 \u8840\u7edf\u6539\u9020 _r696bmb_merge_resolve.py\uff09\uff1a\u9996\u8dd1\u4e24\u5751\u5f53\u573a\u62e6\u56de"
    "\uff08\u2460r453 \u884c\u9996\u5f8b\u81ea\u72af=\u5b50\u4e32 marker \u68c0\u67e5\u649e CODELY \u6b63\u6587\u5408\u6cd5\u5185\u5d4c '<<<<<<<' \u5b57\u9762\u91cf\u2192\u884c\u9996\u5224\u5b9a\u4fee\u6b63\uff1b"
    "\u2461base_idx \u5c3e\u90e8\u7a7a\u884c furniture \u8d8a\u8fc7\u65b0\u6761\u76ee\u2192\u5168\u91cf\u975e\u7a7a\u884c\u5dee\u96c6\u4fee\u6b63\uff09\u2192\u7b2c\u4e09\u8dd1\u649e\u6c60\u65ad\u8a00\u7ea2"
    "\uff08SHARD-3 done \u76d8\u9762\u4e22\u5931\uff09\u2192\u4e09\u63a2\u9488\u5b9a\u8c23=daemon tick\u00d7merge \u540c\u7a97\u9648\u65e7\u56de\u5199"
    "\uff08index stage0=\u6b63\u786e\u5408\u5e76/worktree=\u9648\u65e7 HEAD\u3001daemon \u90e8\u5206\u63d0\u4ea4\u88ab\u51b2\u7a81\u671f git \u62d2=\u96f6 commit \u6b8b\u7559\uff09"
    "\u2192`git checkout --` \u4ece\u7d22\u5f15\u6062\u590d\u2192\u5168\u90e8 17 UU \u5408\u6cd5\u89e3\u6bd5\u5168\u7eff\u2192merge #1 commit 2a6a8a39f\u2192\u4e8c\u63a8\u518d\u62d2"
    "\uff08origin \u524d\u8fdb 2=bm-c r498 \u6536\u53e3+SHARD-5 claim-by-file\uff09\u2192merge #2 14 UU"
    "\uff0810 \u9762 theirs ts-newer 21:4x/scorecard \u53cc\u9762 ours/twins \u9501\u4fa7/token per-key union\uff09\u2192commit f51dfb527"
    "\u2192\u4e09\u63a8 push_verify DELIVERED\uff08tip==remote\u00b7ahead=0\u00b7behind=0\uff09\u3002\u53cc\u722c\u96f6 --no-verify\u96f6\u5f3a\u63a8\uff1b"
    "\u65b0\u5751\u5f8b\u5165 CODELY\uff08daemon tick\u00d7merge worktree \u9648\u65e7\u56de\u5199\u5751\uff09\uff1b\u8bb0\u8d26\u589e\u8865\u5b9e\u5f55\u96f6\u4fe1\u606f\u635f\u5931\u3002"
    "\u672c\u5730\u672a\u8fbe origin commit \u65700\uff08push_verify DELIVERED \u5b9e\u8bc1\uff09\n"
)
with open(rp, "rb") as f:
    blob = f.read()
assert blob.count(MARK2.encode("utf-8")) == 0, "report idem gate"
eol = b"\r\n" if blob.count(b"\r\n") * 2 > blob.count(b"\n") else b"\n"
if not blob.endswith(eol):
    blob += eol
blob += line.encode("utf-8") + eol
with open(rp, "wb") as f:
    f.write(blob)
with open(rp, "rb") as f:
    assert f.read().count(MARK2.encode("utf-8")) == 1
print("report addendum appended")

# 3) heartbeat refresh (last_seen/epoch/clock only; fields preserved)
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = NOW
for k in ("ts", "updated", "updated_at"):
    hb[k] = NOW
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and chk["heartbeat_epoch_utc"] == EPOCH
print("HB refreshed epoch=", EPOCH)
print("ADDENDUM ALL OK @", NOW)
