# -*- coding: utf-8 -*-
# r852 bm-c pre3: rebase-race closeout books (round report addendum + state sync refresh)
import json
import datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

line = (
    "2026-10-11T05:1x+08:00 | r852 bm-c pre3 addendum | rebase-race closeout record（r851 pre3 同款·收口后补账）"
    "：r852 close 首推被拒（bm-b r861 三连同窗落 origin·71a0e3aea）→fetch 后直接 rebase origin/main（r784 多分支 FETCH_HEAD 坑正法）"
    "→31-UU S6 同窗并发面（与 r851 同集同族）=_r852bmc_rebase_resolver.py（r851 血统 verbatim clone·面数 31）逐面归一"
    "（26 ts-audited ours-newer 主导+attrition theirs-newer 1 面+paper_export no-ts-both→ours 2 面+双 UNION 面：compute_audit history ts-key union 201/201→201〔cap 201〕"
    "+x2_watch_log 行 union 1697/1697→1703）→r758/r863 已知面命中（零 UU 仍拒）按 r858 定谳疗法执行（commit -F rebase-message+rebase --quit+分支重挂+cherry-pick 补拾）"
    "→close 33804aea9 重放+addendum c7839c6f3 补拾+pre2 旧拾因 daemon 活面恒动内容过期改现态新吸收 3feb3debe→push DELIVERED 71a0e3aea..3feb3debe"
    "·fetch 自证 ahead=0/behind=0·零强推零 --no-verify（pre-push 爪零拦截）｜另：S7 收尾双扫 ORD f90233c7/DEC 68d13893 双零增量。\r\n"
)
b = open("round_reports-bm-c.md", "rb").read()
assert b.endswith(b"\r\n")
open("round_reports-bm-c.md", "wb").write(b + line.encode("utf-8"))

# state sync face refresh (r851 pre3 precedent)
sb = open("state-bm-c.json", "rb").read()
st = json.loads(sb.decode("utf-8"))
st["sync"] = {
    "ahead_behind": "0/0 post-rebase-race",
    "origin_tip": "3feb3debe",
    "ts": NOW,
    "note": "r852 close push race vs bm-b r861 trio (71a0e3aea); 31-UU rebase resolved "
            "(_r852bmc_rebase_resolver.py r851 bloodline, ts-audited + union duo), r758/r863 "
            "codified remedy applied (commit -F rebase-message + rebase --quit + reattach + "
            "cherry-pick carryover), push DELIVERED 71a0e3aea..3feb3debe, delivery 0/0 verified",
}
st["head_sha"] = "3feb3debe"
st["last_pulled_at"] = NOW
out = json.dumps(st, ensure_ascii=False, indent=1) + "\n"
open("state-bm-c.json", "wb").write(out.encode("utf-8"))
chk = json.loads(open("state-bm-c.json", "rb").read().decode("utf-8"))
assert chk["round_no"] == 853 and isinstance(chk["heartbeat_epoch_utc"], int)
print("pre3 books written: report addendum + state sync face (origin_tip 3feb3debe, 0/0)")
