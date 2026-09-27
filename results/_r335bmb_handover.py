# -*- coding: utf-8 -*-
"""r335 bm-b: HANDOVER 5x reconciliation section append (round 335 = 5x checkpoint)."""
import io

SECTION = (
    "- 开发队列增量窗（续接版）*round 335 bm-b（5x 核对本轮）*，2026-09-27 17:4x 补核；对账区间增量 bm-b r331-335 "
    "并读 bm-a R336-338/bm-c r86-91（基线=round 330 bm-b/bm-a 行已收讫窗），统一链 286,541→286,551 实读"
    "（_r295bmb_ledger_scan 复跑 N=80 件 INTERNAL_BALANCE_FAIL=0·DUP_BATCH_CONFLICTS=0·"
    "HEAD=sina_construct_p1 286,551；本窗增量 +10=bm-a r338 SINA-CONSTRUCT-P1 判定批 gate_attrition+census rows）；"
    "① r331-334 已录前行（r331/r332 tick 竞态窗律族；r333 SINA_CONSTRUCT_P1 点火面+W2-A burn 监控；"
    "r334=S0 死局救援+27-UU 正典解+20 批当窗整编+push#4 拒→machine/bm-b-r334 逃生阀）；"
    "② **r335（本轮）=S0 fold 承继使命窗**——r334 addendum 既定 fold 落地：全链重放 onto 72bea1dd（bm-c r91）"
    "两停点 30-UU+29-UU 正典解（CODELY oa-filter/archive 直拼/autofill 多面 tick 竞态恢复/compute_audit union 223/"
    "regime asof-union 2/x2 852/21 件 deep-ts 取新）；tick mid-rebase 三连击定谳+零丢失恢复（17:13 blind-add 标记件"
    "→pre-commit claw 拦截幸免；~17:27 stash-pop 造 autofill UU+daily_scorecard stage 灭失→HEAD:/REBASE_HEAD: 直读恢复；"
    "~17:30 再 add→动态 resolver v2+add→continue→push 原子链）；push 两拒（origin 同窗三动：bm-a r338 17:06/"
    "bm-c r91 17:2x/+1）→逃生阀 machine/bm-b-r335 承全量折链（下轮 S0 收折）；"
    "③ 窗口维护面：smoke 25/25·orders 96/96 双扫零未回执·水位 red=false healthy·S6 29/29 rc=0（周日 no-op 族；"
    "live.paper/t35v/t24 腿=无新 bar 诚实跳过）·post_review 现行零 NO·CODELY 二十三批当窗整编 9447B≤10KB 硬线；"
    "④ 坑律入册=r335 tick add/stash 腿不受 r201 mid-rebase 护栏管辖律（指针=results/_r335bmb_resolve.py+round_reports r335）；"
    "⑤ 指针：**r336 S0=收折 machine/bm-b-r335 onto main（一次 pull --rebase+resolver v2 就绪）+落地后 GC "
    "machine/bm-b-r334**；09-28 周一开市窗=新 bar 全链接力（update_daily→live.paper REGIME_GUARD v3 enforce 首跑→"
    "t35v→t24×2→aggr 20 账→grid 5 账首拍→marks→export→scorecard→daily_report）；T-91 s3 自动点火 09:15"
    "（SIG/BARS-2026-09-28 到位即确定性 replay）；**RAM 低水位警示=本轮实测空闲 0.4GB（双机纪律 <4GB 禁重活，"
    "r336 遵守禁令面）**；迁移 v2.2 armed 窗至 09-29 12:00 不变；R340 下次 5x 核对。"
)
P = "research/HANDOVER.md"
b = open(P, "rb").read()
eol = "\r\n" if b.count(b"\r\n") >= (b.count(b"\n") - b.count(b"\r\n")) and b.count(b"\r\n") > 0 else "\n"
with io.open(P, "a", encoding="utf-8", newline="") as f:
    f.write(SECTION + eol)
chk = io.open(P, encoding="utf-8").read()
assert SECTION in chk, "HANDOVER append verify FAIL"
print(f"HANDOVER r335 5x section appended (+{len(SECTION.encode('utf-8'))}B, eol={eol!r})")
