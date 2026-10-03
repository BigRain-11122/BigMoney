# -*- coding: utf-8 -*-
# r650 bm-b closeout: HANDOVER 5x line + state.json + round report + heartbeat
import json, datetime, time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

now = datetime.datetime.now()
stamp = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())
clock = stamp

# ---------- 1. HANDOVER.md 5x line (bytes-mode append, newline='' no CRLF translation) ----------
handover_line = (
    "> bm-b round 650 五倍数核对（2026-10-04 06:0x·增量窗 r641-r650 十轮）：增量窗 r641-r650=bm-b 面"
    "（**FUND 三族 NULLS 烧录值守主线+S7 push-race 连环窗+town.html 对齐收口线**——"
    "r641 死会话收养交付轮〔r640 延期 HANDOVER 5x 行 r631-r640 收编+三族 finalize 预演 ALL-GREEN x3 收编+MSG-20261004-0135 双面定谳〔decisions.md 回退=瞬态自愈·post_review ✗7 已闭〕+D-19 水位更至 EB14B510+钟串格式串笔误三坑当场抓回〕；"
    "r642 维护值守〔streak 34〕；r643 迭代轮 tick 重叠活会话探测三证律〔reflog/文件闪变/进程数三证·活并发期共享簿记面零写退避〕+S7 push-race 承接；"
    "r644 merge 收口守卫假阳性坑〔--check CRLF trailing whitespace≠冲突标记残留·判别=输出含 conflict marker 才真拦〕；"
    "r645 state.json 尾逗号崩律〔写回一律 json.dump+写后 json.loads 自证〕+D-19 假 CHANGED 证伪〔UTF-16 转码面〕+theme_persist_p1 bm-a 属主面 push-race 让路〔r630 净路三步〕；"
    "r646 orders 双扫计数口径坑〔跨口径计数比对假新令警报·正法=双侧同口径 ls-tree 集合比对〕+bm-c r443 wave 后到 Already-up-to-date 拓扑核验；"
    "r647/r648 维护值守〔moneyflow IC parked 一行声明不重扫〕；"
    "r649 push-race 环实录〔pre-push 爪正拦 w115 bm-c 属主删除集→r642 配方 fetch+re-merge 2 UU 分类解→DELIVERED〕+readiness probe 05:25+S6 34 legs rc0；"
    "r650=本核对轮 **town.html 楼名/详情 org_chart §5 全表对齐验收收口**〔r639 起指针悬置小活清账：唯一漂移=office 楼名「总经办」→org_chart §5 正典「总经理办公室」归正（画布字+BUILDINGS label 两处+footer 版本行）；验收探针 _r650bmb_town_accept.py=11/11 楼名全命中正典集+11 dept+11 mandate+node --check rc0·TOWN-ALIGN-ACCEPT VERDICT PASS〕+readiness probe 05:47〔Q443/V590/D310 dup_k=0·ETA Q~10-07/V~10-06/D~10-08 全在 finalize 窗 10-05..10-09·D 未触 10-09 12:00 提速线〕+S6 34 legs rc0〔dualrun ZERO-DRIFT streak 42·黄金周 no-op 族·新 bar 三件套按 r637 先例门跳〕+post_review 44/0/5+attrition CLEAN〕"
    "）产物清单漂移=town.html〔r650 楼名两处+footer 行〕+results/_r650bmb_{town_probe,town_accept,s6_runner,handover_facts}.py+_r650bmb_s6_evidence.txt〔r650〕"
    "+results/_r649bmb_{merge_resolve,merge_resolve2,s6_runner}.py+_r649bmb_s6_evidence.txt〔r649〕"
    "+results/_r641bmb_{wt_resolve,treesync}.py〔r641〕+CODELY.md 坑律行〔r641/r643/r644/r645/r646 窗批〕"
    "+docs/daily_report/REPORT-2026-10-04.*+docs/live_usage/LIVE-2026-10-04.*〔S6 维护链再生件〕；"
    "池态=FUND 三族 NULLS bm-b canonical burner 在飞〔Q443/V590/D310 of 2000 @05:47·dup_k=0·G1=F G2/G3=T G4=PENDING〕+W14-GENERATE 治理 park 维持+moneyflow IC next_pick claimed（parked 源阻断 30min 自愈域）；"
    "orders 152/152 双扫零未回执；smoke 47/47 全窗维持；D-19 EB14B510 MATCH 零消费全窗维持；"
    "指针：**三族烧毕 mechanical_ready=true 且窗开即执行 finalize+E1（G-SEG 无裁决走 r638 fallback）·V 最早 ~10-06·全族 ≤10-08·窗尾 10-09·D 速率 0.29-0.31/min 波动盯防线〔ETA>10-09 12:00 即评估合规提速面〕+W14-GENERATE 治理冻结待 GM 裁定不重提+D-06 全线收口窗 10-07〔bm-c 主导〕+月界首考 10-31**；下一 5x=bm-b r655。\n"
)
with open(r'research/HANDOVER.md', 'ab') as f:
    f.write(handover_line.encode('utf-8'))
print('HANDOVER line appended bytes:', len(handover_line.encode('utf-8')))

# ---------- 2. state.json (programmatic write + json.loads self-verify per r645 law) ----------
state = json.load(open(r'state.json', encoding='utf-8'))
state['round_no'] = 650
state['note'] = ("r650: watch/readiness + town-align closeout round -- S0 zero-intersection merge origin/main (behind 4, f890e9ade); "
 "S0.5 orders 152/152 zero-diff + D-19 sparse-clone fallback MATCH EB14B510 zero-consume + inbox 0; S1 47/47; S2 board 0 open (46 claimed); "
 "S3 gates green (WM red=false; engine alive rc0 idle; trio burns healthy in-flight = standing trial-labor line satisfied; "
 "moneyflow IC parked one-line declared; W14-GENERATE governance-parked one-line declared); "
 "S3 product = town.html building-name/details org_chart v2 full-table alignment ACCEPT closed (r639-pending small item): sole drift office label "
 "restored to canonical 总经理办公室 (canvas text + BUILDINGS label + footer version line), accept probe _r650bmb_town_accept.py 11/11 names "
 "+ 11 dept + 11 mandate + node --check rc0, VERDICT PASS; readiness probe 05:47 Q443/V590/D310 dup_k=0 G1=F G2/G3=T G4=PENDING, "
 "ETAs Q~10-07/V~10-06/D~10-08 all in finalize window 10-05..10-09, D under 10-09 12:00 speedup line; S6 34 legs rc0 (streak 42; Golden-Week "
 "no-op family, new-bar trio gated off per r637); post_review run YES=44 NO=0; attrition CLEAN; HANDOVER 5x line r641-r650 delivered.")
state['last_round_at'] = stamp
state['ts'] = stamp
state['updated'] = stamp
state['last_seen'] = stamp
state['round_no_label'] = 'round 650 (bm-b)'
state['clock_read'] = stamp
state['last_decisions_read_at'] = stamp
with open(r'state.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(state, f, ensure_ascii=False, indent=1)
    f.write('\n')
chk = json.load(open(r'state.json', encoding='utf-8'))
assert chk['round_no'] == 650 and isinstance(chk['round_no'], int)
print('state.json round_no:', chk['round_no'], 'self-verify OK')

# ---------- 3. round report line (bytes-mode append per r641 mixed-encoding law) ----------
report_line = (
    stamp + " | round 650 (bm-b, dept:工程/数据+研究): watermark verdict=GREEN (red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 42; py 61-93% 三族烧批占用合法)\n"
    "当前活: FUND trio NULLS burn watch + readiness 复跑（05:47 探针 Q443/V590/D310 of 2000 dup_k=0·G1=F G2/G3=T G4=PENDING·ETA Q~10-07/V~10-06/D~10-08 全在 finalize 窗 10-05..10-09·D 未触 10-09 12:00 提速线·G-SEG GM 裁决未至 r638 fallback armed）\n"
    "最近实物: town.html 楼名/详情 org_chart §5 全表对齐验收收口（11/11 PASS·总经理办公室归正·node rc0·05:5x）——r639 起悬置小活清账，验收件 results/_r650bmb_town_accept.py\n"
    "下个里程碑: 三族 NULLS 烧毕→finalize+E1 判决（V 最早 ~10-06·全族 ≤10-08·窗尾 10-09）\n"
    f"验证证据: smoke 47/47；town-accept 11/11 PASS（node --check rc0）；readiness probe JSON 实跑（elapsed 60.0s）；S6 per-leg 探针清单 34/34 rc=0（evidence results/_r650bmb_s6_evidence.txt）；post_review YES=44 NO=0；attrition scan CLEAN（evidence results/_attrition_guard_scan.json）；心跳/state json.loads 双自证（epoch={epoch} int·clock T 分隔）\n"
    "下轮指针: r651 = 烧录进位 watch+readiness 复跑；mechanical_ready=true 且窗开即执行三族 finalize+E1（G-SEG 无裁决走 r638 fallback）；D 速率波动盯防线：ETA>10-09 12:00 即评估合规提速面（禁池面整文件重放陷阱 r630 律·redo-k-lo/hi 分片序 r611）；W14-GENERATE 治理冻结待 GM 裁定不重提\n"
    "本地未达 origin commit 数=0（以收轮 push_verify 输出为准·失败则 addendum 补记）\n"
)
with open(r'logs/iteration-loop/round_reports.md', 'ab') as f:
    f.write(report_line.encode('utf-8'))
print('round report line appended')

# ---------- 4. heartbeat fleet/machines/bm-b.json (int epoch + T-clock + CEO 3 lines) ----------
hb = json.load(open(r'fleet/machines/bm-b.json', encoding='utf-8'))
hb['last_seen'] = stamp
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock
hb['round_no'] = 650
hb['round_no_label'] = 'round 650 (bm-b)'
hb['current_task'] = ("FUND trio NULLS burn watch (Q443/V590/D304->310 of 2000 dup_k=0; ETA V~10-06/Q~10-07/D~10-08 all in-window 10-05..10-09; "
 "finalize fires on mechanical_ready w/ r638 fallback; G-SEG GM ruling G4 PENDING one-line; D speedup line 10-09 12:00 not tripped) "
 "+ r650: town.html org_chart full-table align ACCEPT closed (11/11), readiness probe 05:47 refresh, S6 34 legs rc0, HANDOVER 5x r641-r650 line")
hb['verdict'] = ("GREEN (smoke 47/47; D-19 MATCH EB14B510 zero-consume; orders 152/152; WM red=false; engine alive rc0 idle; dualrun ZERO-DRIFT streak 42; "
 "S6 34 legs rc0; attrition CLEAN; post_review 44/0/0 pending-5-known; W14-GENERATE governance-parked (GM pending) one-line; trio burns healthy dup_k=0)")
hb['ts'] = stamp
hb['updated'] = stamp
hb['updated_at'] = stamp
with open(r'fleet/machines/bm-b.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')
chk2 = json.load(open(r'fleet/machines/bm-b.json', encoding='utf-8'))
assert isinstance(chk2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in chk2['clock_read'] and '+' in chk2['clock_read'], 'clock must be ISO-8601 T-separated'
print('heartbeat epoch:', chk2['heartbeat_epoch_utc'], 'clock:', chk2['clock_read'], 'int+T self-verify OK')
