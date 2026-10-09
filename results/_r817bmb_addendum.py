# -*- coding: utf-8 -*-
"""r817 bm-b addendum closeout: heartbeat sync block + addendum round-report line
(push-storm receipt, r816 addendum pattern; protocol-mandated S7 refusal annotation)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime('%Y-%m-%dT%H:%M:%S+08:00', time.localtime())

hb_path = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
with open(hb_path, encoding='utf-8') as f:
    hb = json.load(f)
hb['last_seen'] = now_iso
hb['updated'] = now_iso
hb['ts'] = now_iso
hb['clock_read'] = now_iso
hb['heartbeat_epoch_utc'] = int(time.time())
hb['sync'] = {
    "ahead": 0,
    "behind": 0,
    "last_push_ts": now_iso,
    "note": ("r817 push landed 575dd6b92 after canonical 18-UU two-wave rebase-storm resolve "
             "(pre-push claw first-blocked stale bm-b pool-mirror owner_since regression = designed "
             "protection per MSG-0612, zero --no-verify; recipes per bigmoney-conflict-resolve "
             "classifier: rolling-ledger union compute_audit 201+201->202 zero-loss / regime_state "
             "3-0-2 identical + snapshot take-new by ts both directions + same-day idempotent "
             "REPORT/LIVE take-new + tech.md append-union T9/T10 rows + records r816->r817->r828 "
             "ts order + saturation trio/p1d_gates live-absorbed ours; settle re-sync via "
             "merge_lane_views sync_face, mirror max owner_since 05:22:35 = origin-aligned; "
             "receipts results/_r817bmb_resolve.py + results/_r817bmb_classify.json; 4th redundant "
             "churn-retry pick dropped as empty, zero loss); post-push fetch+rev-list+ls-remote "
             "self-verified 0/0 tip=575dd6b92; idle_trigger --auto declared worked")
}
tmp = hb_path + '.tmp'
with open(tmp, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, hb_path)
chk = json.load(open(hb_path, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'

RR = os.path.join(ROOT, 'logs', 'iteration-loop', 'round_reports.md')
line = (
    now_iso + " | r817 addendum bm-b | push LANDED 575dd6b92 | "
    "首 push 撤 pre-push 爪拦（陈旧 bm-b 池镜 owner_since 回退族=MSG-0612 爪设计护池面·未用 --no-verify）"
    "→fetch 实核=bm-c r828 T10 shipped 同窗（tech 队列双机并行=T9 bm-b/T10 bm-c 零撞项·both done 双行并）"
    "→churn absorb+pool 镜 settle re-sync（merge_lane_views sync_face 幂等·镜像 max owner_since 05:22:35 对齐 origin 零回退）"
    "→二 rebase 撤 18 UU 两波四 pick（分类器 7 classified+8 UNKNOWN 手工定性：rolling-ledger union〔compute_audit 201+201→202 零丢失·regime_state history/transitions/triggers 3/0/2 恒等〕"
    "+snapshot take-new 双向按 ts〔本机 6 件 05:2x 新/bm-c attrition 05:24 新·tie 取 HEAD r140〕+REPORT/LIVE 同日幂等取新+tech.md append-union〔T9/T10 双 done 行并+r816→r817→r828 ts 序记录并〕"
    "+saturation 三 face+p1d_gates=活吸收新面 live-wins 取 ours=陈旧 pick 重放回退防护·p1d_gates 内容恒等取新 meta 戳 r816 律〕；"
    "resolver=results/_r817bmb_resolve.py+分类件 results/_r817bmb_classify.json；第 4 pick churn-retry 全冗余空提交自然摘除零丢失）"
    "→push 0c4cfc54d..575dd6b92 落地+fetch/rev-list 0/0+ls-remote tip 自证；idle_trigger --auto=declared worked（idle_rounds 0） | "
    "本地未达 origin commit 数：0（push 后 fetch+rev-list+ls-remote 自证）| [r817 addendum bm-b]\n")
with open(RR, 'a', encoding='utf-8') as f:
    f.write(line)
print('r817 addendum OK:', now_iso, '| epoch_int:', chk['heartbeat_epoch_utc'])
