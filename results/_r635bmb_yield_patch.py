import io, sys

def patch(path, pairs):
    raw = open(path, 'rb').read()
    for old, new in pairs:
        ob, nb = old.encode('utf-8'), new.encode('utf-8')
        n = raw.count(ob)
        assert n == 1, (path, old[:40], n)
        raw = raw.replace(ob, nb)
    open(path, 'wb').write(raw)
    print('patched', path)

patch('logs/iteration-loop/round_reports.md', [
    ("轮中入站·首 ack 机=bm-b)", "轮中入站·首 ack 机=bm-c·bm-b 让位焊面)"),
    ("①ack 本轮完成 (bm-b.json orders_ack 152·两他机 21:2x 心跳均无此令=首 ack 机归我)",
     "①ack 本轮完成 (bm-b.json orders_ack 152；bm-c r431 S7-supplement 先 ack 858791cf7 已达 origin=首 ack 机=bm-c·我=后到 ack)"),
    ("④余片派工 T-2026-10-03-161-P1 claimed (三类脚本改造 r624 族清扫/S0 restore/retention·五类收口步入册焊点·清扫面零命中断言行·里程碑 git tag·验收 10-08 治理日并窗)",
     "④焊面让位: bm-c r431 已认领 r432+ 开焊 (撞认领 commit 时间序 bm-c 858791cf7 先达 origin·我码在暂存未达=后到让路·anti-dup 律)·引擎+T-161 转 yielded 贡献 bm-c r432 焊面采纳或替换·MSG-2215 bmb→bmc 已发 (验收 10-08 治理日并窗)"),
])

patch('CODELY.md', [
    ("执行回执：bm-b 首 ack 机；守门引擎 Tools/treasure_guard.py 落地",
     "执行回执：首 ack 机=bm-c r431（858791cf7 先达 origin）·bm-b 后到 ack 并按撞认领 commit 时间序让位焊面；守门引擎 Tools/treasure_guard.py 落地为贡献件"),
    ("余片接线 T-2026-10-03-161-P1 claimed（三类脚本改造+五焊点+里程碑 tag·验收 10-08）；指针=轮报告 R635 addendum + orders_ack 152。",
     "焊面归 bm-c r432+（其 858791cf7 认领在先）·T-161 转 yielded=贡献件（selftest 21/21·live 硬拒 rc3·引擎供采纳或替换）·MSG-2215 bmb→bmc 已发；指针=轮报告 R635 addendum + orders_ack 152。"),
])

patch('state.json', [
    ("first acker bm-b: ack + wiring slice 1 delivered this round",
     "first acker = bm-c r431 (858791cf7 on origin, claimed weld r432+); bm-b secondary ack same round with contribution engine delivered"),
    ("remaining wiring claimed as T-2026-10-03-161-P1 (acceptance 10-08)",
     "weld yielded to bm-c r432+ per anti-dup commit-order (my claim staged-undelivered when bm-c's landed); T-161 status=yielded contribution; MSG-2215 bmb->bmc sent (acceptance 10-08)"),
])
print('ALL PATCHED')
