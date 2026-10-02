# r585 bm-b round close: S4 memory line + S5 round report + state round_no 585
# + heartbeat dynamic fields (r583 law: orders_ack carried verbatim from file).
import json, time, datetime, sys, os, subprocess
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

now = datetime.datetime.now().astimezone()
ts = now.strftime('%Y-%m-%dT%H:%M:%S') + now.strftime('%z')[:3] + ':' + now.strftime('%z')[3:]
epoch = int(time.time())

# 1. S4: CODELY.md one-line lesson (memory entry gate: single lesson, <1.5KB)
lesson = ("- [2026-10-02 18:0x r585 bm-b] 术后工作树陈旧面伪装成本轮新增行（S0 定性探针序定谳）：r584 外科的 commit 树取了 origin 版"
          "CODELY（引擎域拆件后 79 行）但工作树文件被排除在术后 checkout 清单外=pre-split 110 行版原地滞留→本轮轮首 diff +33/-1 乍看像 33 条新教训行；"
          "正法=①blob 空间行集双向差集探针（working vs origin：only_local=33/only_origin=2）②逐行在场审计（pit-engine/pit-git 在场性=零丢失证）"
          "③origin-verbatim 收口禁 union 回灌（union 会撤销他机域拆件）。连带：merge-base==自己 HEAD 时 S0=纯 FF+分面 checkout 免 payload 手术"
          "（probe=rev-list 计数+merge-base 身份先验）；外科 payload 取 MY COMMIT 的 ls-tree blob（工作树活写件留后续 ride 禁 hash-object 现盘）。"
          "How to apply：S0 见 CODELY 大额本地 diff 先疑「术后滞留」非「新增」；行集探针+域文件在场审计定 union 方向；纯 FF 窗直接 update-ref+reset --mixed+分面 checkout。\n")
with open('CODELY.md', 'r', encoding='utf-8') as f:
    codely = f.read()
assert lesson.strip() not in codely
with open('CODELY.md', 'a', encoding='utf-8', newline='') as f:
    f.write(lesson)
print('CODELY.md lesson appended (%d bytes)' % len(lesson.encode('utf-8')))

# 2. S5: round report line (bm-b file)
report_line = ("%s | r585 | WM=py_low_with_work_cands(work-cand=never-dry 供给线·本轮 W106 席位+冻结+自燃点火闭环回应非违令) | "
               "当前活=W106 12 分片引擎自燃烧录在飞(shard-0/1 落盘 pid 实证 r325 律) | 最近实物=results/perpetual_faces/n1_w100_results.json"
               "(W100 finalize 17:29·head 584,548)+W106 五面冻结 commit d6b2952e3(17:57 推 origin) | 下个里程碑=W101 bm-a finalize 落地后链序推进"
               "W102/W103 finalize(他机前置·~24h 窗)+W106 烧毕 12/12 下轮 ride+finalize 待 W105 前置 | 做了什么=S0 纯 FF 集成(5 他机 commit)"
               "+CODELY 域拆件零丢失审计收口+pool/history union+orders 143/143 双扫空+smoke 47/47+W100 finalize one-pass(prev 582,348+2,200=584,548"
               "·skill_line 1.1692→1.1687)+W103 烧毕 12/12 shards 8-11 ride+席位 MSG-1733 r565 律+band gate ADMIT+禁向闸 ADMIT+五面冻结纯插入"
               "+n1/pf selftest 双绿+外科 payload 推送(fe191d370·r374 分叉伪影 r523 律正解)+S6 31 legs rc0(dualrun ZERO-DRIFT 29/3·报告/CEO 页新)"
               "+S7 自愈(loop pin=2 no-op·watchdog 在跑·双爪实弹验证·attrition CLEAN 4-healed) | 验证证据=W100 finalize 输出+W106 ADMIT 回执"
               "+selftest PASS+ignition shard 落盘+origin 双 commit 送达 rev-list 0 | 本地未达 origin commit 数=0 | 下轮指针=W106 烧毕产品 ride+"
               "W101 落地后视链序 finalize W102/W103+收 W107 席位窗(bm-a/bm-c 去节流连续系列)\n") % ts
with open(os.path.join('logs', 'iteration-loop', 'round_reports.md'), 'a', encoding='utf-8') as f:
    f.write(report_line)
print('round report line appended')

# 3. state.json round_no 585 (dynamic fields only)
sp = os.path.join('state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 585
st['note'] = ('r585: W100 FINALIZE landed one-pass (prev 582,348 + 2,200 = 584,548, skill_line 1.1692->1.1687 K-lift -0.0005, '
              'voids LOWAMP-P1/P2; chain W98->W99->W100 verified) + W103 burn COMPLETE 12/12 (shards 8-11 ridden) + '
              'W106 FREEZE five-face delivered (seat MSG-20261002-1733-bmb -> gate ADMIT A 255_004..257_003 / B 60_201..60_400 '
              'hops 0/0 single state -> banned ADMIT 0 -> pure-insertion + AST -> n1 selftest PASS W106 leg live + pf 9/9 -> '
              'commit d6b295e3 pushed -> tick engine SELF-IGNITED n1w106 shards landing pid-verified, 96th engine wave, '
              'bm-b 36th owned) + S0 pure-FF (merge-base==HEAD, 5 origin commits adopted; CODELY origin-verbatim post '
              'engine-domain-split zero-loss audited; pool union +4; history_bm-a union +14 heal) + surgical push fe191d370 '
              '(r374 fork artifact via r523 law, 13 shared derive faces origin-side) + S6 31 legs rc0 (ZERO-DRIFT 29/3; '
              'WM py_low_with_work_cands answered by W106 supply duty; ORANGE_COOL; daily report + CEO page fresh) + '
              'orders 143/143 + S7 5/5 + next: W106 burn ride + W102/W103 finalize when W101 upstream lands')
st['last_round_at'] = epoch
st['last_round_ts'] = ts
st['ts'] = ts
st['updated'] = 'r585 bm-b: W100 finalize landed + W103 12/12 complete + W106 frozen+ignited (96th wave) + S6/S7 green'
st['updated_at'] = ts
st['last_decisions_sha'] = '937A373DA4339EDC70E95D2EC3E2AC5B1B62E298C834AC84B5FD2955EC5FD4E1'
st['last_decisions_at'] = ts
with open(sp, 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print('state.json round_no -> 585')

# 4. heartbeat: dynamic fields only, orders_ack carried verbatim (r583 law)
hp = os.path.join('fleet', 'machines', 'bm-b.json')
h = json.load(open(hp, encoding='utf-8'))
ack = h['orders_ack']  # carried verbatim
h['last_seen'] = ts
h['heartbeat_epoch_utc'] = epoch
assert isinstance(h['heartbeat_epoch_utc'], int)
h['clock_read'] = ts
h['current_task'] = 'W106 engine burn in flight (12 shards, self-ignited post-freeze d6b2952e3)'
h['round_no'] = 585
h['verdict'] = ('W100 finalize landed 584,548 + W103 12/12 + W106 frozen+ignited; WM py_low_with_work_cands = never-dry '
                'supply duty answered same-window')
try:
    import psutil
    vm = psutil.virtual_memory()
    h['ram_free_gb'] = round(vm.available / 1024**3, 1)
    h['cpu_util_pct'] = psutil.cpu_percent(interval=None)
except Exception:
    pass
h['orders_ack'] = ack
with open(hp, 'w', encoding='utf-8') as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178 law)'
assert len(chk['orders_ack']) == 143, 'orders_ack must carry 143 verbatim (r583 law)'
assert 'T' in chk['clock_read'], 'clock_read must be ISO 8601 T-separated (R262 law)'
print('heartbeat written: epoch=%d (int) clock=%s ack=143' % (chk['heartbeat_epoch_utc'], chk['clock_read']))
