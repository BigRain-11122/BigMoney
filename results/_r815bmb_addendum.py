"""r815 bm-b addendum: report line + heartbeat sync zero (post-push verified)."""
import json
import os
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(REPO, "logs", "iteration-loop", "round_reports.md")
HB = os.path.join(REPO, "fleet", "machines", "bm-b.json")

ts = time.strftime("%Y-%m-%dT%H:%M:%S+08:00",
                   time.gmtime(time.time() + 8 * 3600.0))

line = (
    "{ts} | r815 addendum bm-b | push LANDED tip=05d58b050 | rebase 集成：31 件同日再生产物风暴"
    "按 bigmoney-conflict-resolve 正典解（28 snapshot/twin 取 my 新侧〔deep-ts 探针 r100/R350 律·"
    "LIVE/daily twins 同侧原子·js-wrapper 整字节保壳〕+compute_audit history union 203 行"
    "+regime_state union 3+x2_watch_log union 1523 行·零丢失断言全过·收据 results/_r815bmb_resolve.json；"
    "UNKNOWN 1 件 _attrition_guard_scan 按 r813 snapshot 先例手工定性取新）| daemon 活面竞态一次"
    "add+continue 吸收（r813 律）| 本地未达 origin commit 数=0（push 后 fetch+rev-list ahead/behind=0/0"
    "+ls-remote tip=05d58b05032765b204d0bb34388f0382337f3ebf 自证）"
).format(ts=ts)

with open(REPORT, "a", encoding="utf-8") as f:
    with open(REPORT, "rb") as rb:
        rb.seek(-1, os.SEEK_END)
        if rb.read(1) != b"\n":
            f.write("\n")
    f.write(line + "\n")

hb = json.load(open(HB, encoding="utf-8"))
hb["sync"] = {"ahead": 0, "behind": 0, "last_push_ts": ts,
              "note": "r815 push landed 05d58b050 (rebase-integrated 6 incoming, "
                      "31-file storm resolved canonical); post-push "
                      "rev-list+ls-remote self-verified"}
hb["last_seen"] = ts
hb["updated"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = int(time.time())
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int)
assert "T" in hb2["clock_read"]
print(json.dumps({"addendum_ts": ts, "sync": hb2["sync"],
                  "epoch": hb2["heartbeat_epoch_utc"]}))
