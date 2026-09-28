# -*- coding: utf-8 -*-
# r383 bm-b closeout: storm addendum line + heartbeat refresh
import json, time, datetime, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
epoch = int(time.time())
assert clock.endswith("+08:00")

line = ("2026-09-28T" + now.strftime("%H:%M:%S") + "+08:00 | round 383 addendum bm-b | dept:工程 | "
        "S7 push-storm 撞头留痕（fleet/README §4 后到让路·commit 时间序：bm-c r163+addendum 先落 12:39-12:40，本机后到 rebase 让路）——"
        "pull --rebase 重放 70c9a245 撞 24-UU：分类器 24 分类 0 UNKNOWN 全正典解（bm-c r163 resolver 强化探针核 verbatim 复用扩面："
        "REPORT 双件耦合 take-:3:（12:53:45>12:39:59 双件同侧 r327 律）+ 17 snapshot 深探针 take-:3: all-newer（12:50-12:54>12:38-12:40·staged blob :2:/:3: 探测 r351 律）"
        "+ dashboard_status.js js-wrapper 整字节 take-:3:（R209 禁 json.dumps 剥包装）+ compute_audit history union 102+102->103 零丢失（r188/R208）"
        "+ regime_state transitions 0+0 态字段 take-:3: + x2_watch_log 行级 union 1224+1224->1230 零丢失（r188/r217）；"
        "全 24 件写后 json.loads/包装断言过闸（r185 律）零冲突标记；auto-merge 面复核：CODELY 10,066B（batch-49 指针+r383 条在位·bm-c r163 未加坑律条=零撞）·"
        "bm-b 心跳 round 383 epoch int T 钟在位·round_reports r383 行在位（bm-c 行在其自管 round_reports-bm-c.md）·archive 四十九批单份零重——"
        "push landed a1d089e6..c05e1b47 禁 force-push 全程；resolver 留痕=results/_r383bmb_resolve_storm.py\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)

hb = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["verdict"] = (hb["verdict"] + "; r383 S7 push-storm 24-UU canon-resolved zero-loss (bm-c r163 first-land, bm-b rebase yield), push c05e1b47 landed")
with open("fleet/machines/bm-b.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
v = json.load(open("fleet/machines/bm-b.json", encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int) and v["clock_read"].endswith("+08:00")
print("addendum line + heartbeat refresh OK", clock)
