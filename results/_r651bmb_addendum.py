# -*- coding: utf-8 -*-
# r651 bm-b addendum: push-race closeout receipt (r650 lineage recipe)
import time, datetime

NOW_EPOCH = int(time.time())
now = datetime.datetime.fromtimestamp(NOW_EPOCH).astimezone()
ISO = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')

block = f"""{ISO} | round 651 addendum (bm-b): S7 push-race 净路实录——首推 push_verify NOT-DELIVERED（rc1）→fetch 实证 behind 6（bm-a r661 波 06:00-06:06 同窗 S6 再生面）→merge origin/main 14 UU 全 S6 再生面；分类解=5 面 merge_lane_views 单源 resolve（compute_audit/regime_state/lhb/futures/token_usage·rolling-ledger union+parse-verified）+9 面 take-new-by-ts（双侧 ts 实比全 ours 胜：06:08:50-06:09:33 vs bm-a 05:52:17-05:58:55·REPORT/LIVE 双 md 孪生随 json 同侧·resolver=results/_r651bmb_merge_resolve.py 留痕·staged JSON 全 parse 自证零失败）→pre-commit 爪过（staged 零 conflict marker）→merge commit e3741fd24→push_verify DELIVERED（tip==remote·ahead=0 behind=0）。零 --no-verify。本地未达 origin commit 数=0
"""
p = 'logs/iteration-loop/round_reports.md'
with open(p, 'a', encoding='utf-8', newline='') as f:
    f.write(block)
print('addendum appended:', ISO)
