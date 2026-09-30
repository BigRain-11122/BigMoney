# r498 bm-a bookkeeping: round report line + state-bm-a.json + heartbeat (mirror formats: CRLF, state/heartbeat indent=1 no trailing NL, report trailing NL)
import json, time, datetime, psutil

NOW = datetime.datetime.now().astimezone().isoformat(timespec='seconds')  # T-sep ISO8601 with offset

REPORT = ("2026-10-01T02:58+08:00 | r498（猝死续作收口窗：前 r498 会话 ~02:30 猝死于 push 被拒后的 rebase 中途，"
"4 commit〔r497+2 runtime sync+r498 本体〕已 commit 未 push 逐件验后沿用零重做 r471）| dept:工程 | "
"WM=py_low_with_work_cands 如实解释非违令：2 ready 分片（EXCLUSION-MARGINAL-P1-RUN/CROSS-START-ROBUSTNESS-P1-FACEB）"
"owner=bm-b 01:56/01:58 在飞=反重复正确让道；supply_floor ready2<floor3=LOWAMP 判负关线后供给面自然回缩"
"（W14-GENERATE waiting=板空后下一波原料）| "
"实物1=LOWAMP-P1 judged 批全收敛判决落地：18/18 面齐（16 cells 各 1254/1506 starts+nulls 2000/2000+sens 500/500"
"·SENS 尾片=本机 autofill daemon 02:48:16 认领 12w ~90s 烧完=r496 多核机实弹）→ finalize verdict=judged-negative"
"（DSR 0.0%·n_trials=2008·sr_ann=-1.4475 vs sr_star=0.0816·trials ledger 366789→368797·evidence_cutoff 2026-09-22）"
"→ results/lowamp_p1/lowamp_p1_results.json+cells.csv+T-132 票 done+result_ref 齐；判负=诚实关线禁续烧（O-1901 四闸）| "
"实物2=撞车 rebase 四批冲突正典解完推送：分类器 18 分类+12 UNKNOWN 逐件定性（ALL_FACES merge_lane_views resolve 全 "
"parse-verified·twin/LIVE/dashboard 孪生同侧 md/js 字节直拷·pool_core_samples 行级 union 17+29→36 零丢失"
"·10 AA 分片 science-payload 恒等断言后取 origin·快照族 ts 探针取新）→ rebase Successfully×2+reconcile 7/8 零漂移"
"（compute_audit drift=观察相）+push 50995ca69..490c7f821；池 NULLS/SENS entry 面 ready→done 手术 2+/2-"
"（r488 族 entry-lag·shard 面先被 daemon harvest 02:48/02:50 翻）| "
"坑律新条=AA 双烧产品信封分歧裁定律（CODELY 已固化·resolver 留痕 results/_r498_resolve.py）| "
"orders 差集 139/139 零·D-19 sha ED4E0EAB 匹配零动作·inbox 1 件=bmb→bmc 双烧劝阻（涉本机面=知悉勿再领 nulls"
"·bm-c lane 不代处理）·T-131 GM 署名门继续守候（P1 新方向未署名不启动）·post_review 无新 ✗（T-78-WINNER-WIRING 红仍归 bm-c P0）| "
"S6 28 腿 rc0（国庆休市无新 bar·live.paper 触发组合法跳过·host=bm-a 执笔面 scorecard/daily_report/LIVE/build_status 02:52-02:5x 刷新）| "
"verify: smoke 47/47+attrition CLEAN(healed-4 历史)+自愈三件套（pin=8 no-op·watchdog 重注册首跳 02:56·claw in sync）"
"+dualrun ZERO-DRIFT streak1/3+token L2 今日 0 | "
"当前活=EXCLUSION-MARGINAL/CROSS-START-FACEB bm-b lane 烧批看守；最近实物=lowamp_p1_results.json"
"（judged-negative 判决面·02:51）+池 LOWAMP 18/18 done；下里程碑=板空后 W14 供给波 prereg 起草（TRIAL_LABOR 常设线）"
"+三机核分布行 10-02 晨报汇入（窗 ≤24h）| next: r499 W14 波起草判据（板空触发）+T-131 GM 署名守候+自主扩展 [via bm-a]")

# 1. round report append (CRLF, trailing newline preserved)
p = 'round_reports-bm-a.md'
raw = open(p, 'rb').read()
if not raw.endswith(b'\r\n'):
    raw += b'\r\n'
raw += REPORT.encode('utf-8') + b'\r\n'
open(p, 'wb').write(raw)

# 2. state-bm-a.json (indent=1, CRLF, no trailing NL)
p = 'state-bm-a.json'
s = json.load(open(p, encoding='utf-8'))
s['round_no'] = 498
s['did'] = ("r498 (dead-session rebase crash continuation + judged-batch closure): LOWAMP-P1 judged batch CLOSED "
"judged-negative per frozen prereg (18/18 faces: 16 cells + nulls 2000/2000 + sens 500/500 -- sens tail burned "
"locally by autofill daemon 02:48:16 claim 12w ~90s per r496 multicore machinery; finalize DSR 0.0% n_trials=2008 "
"sr_ann=-1.4475 sr_star=0.0816, trials ledger 366789->368797; verdict face results/lowamp_p1/lowamp_p1_results.json "
"+ cells.csv + T-132 done with result_ref; honest line-closure per O-1901, no further LOWAMP-P1 burns) + "
"rebase push-rejection collision resolved across 4 conflict batches canonical (classifier 18 classified + 12 UNKNOWN "
"adjudicated; ALL_FACES merge_lane_views resolve; twins same-side byte-copy; pool_core_samples 17+29->36 line-union; "
"10 AA shards science-payload-equal -> take-origin) + reconcile 7/8 zero-drift + push 50995ca69..490c7f821 + pool "
"NULLS/SENS entry-face heal 2+/2- surgical (r488 family; daemon harvested shard faces 02:48/02:50) + AA-envelope "
"adjudication law memorized (CODELY) + WM py_low_with_work_cands explained (2 ready shards owned by bm-b in-flight, "
"anti-duplicate yield, no violation) + orders 139/139 zero diff + D-19 ED4E0EAB unchanged zero-action + inbox "
"bmb->bmc double-burn advisory informational (nulls = bm-b lane, no re-claim) + T-131 GM-gate standing wait + "
"S6 28 legs rc0 (holiday no-new-bar group legal skip)")
s['verify'] = ("smoke 47/47 + finalize completeness gate 18/18 + attrition CLEAN(healed-4 hist) + dualrun ZERO-DRIFT "
"streak1/3 + pool entry flip surgical 2+/2- (diff --stat verified) + reconcile 7/8 zero-drift + self-heal trio "
"(pin=8 no-op, watchdog registered, claw in sync) + resolver script results/_r498_resolve.py committed as receipt")
s['next'] = ("r499: W14 supply-wave prereg drafting when board empties (TRIAL_LABOR standing law) + T-131 GM-signature "
"standing wait + 3-machine core-spread row accrual for 10-02 morning report + EXCLUSION-MARGINAL/CROSS-START-FACEB "
"burns on bm-b lane watch")
s['last_round_at'] = NOW
s['current_task'] = 'r498 closed: LOWAMP-P1 judged-negative delivered; next = board-empty-triggered W14 wave drafting'
s['updated'] = NOW
s['last_round'] = ('2026-10-01 r498: rebase crash recovered + 4 commits pushed (50995ca69..490c7f821) + '
'LOWAMP-P1 judged batch CLOSED judged-negative (18/18, DSR 0.0%, 2008 trials) + S6 28 legs rc0')
s['last_decisions_at'] = '2026-10-01T02:46:30+08:00'
s['last_round_ts'] = NOW
out = json.dumps(s, ensure_ascii=False, indent=1).replace('\n', '\r\n')
open(p, 'w', encoding='utf-8', newline='').write(out)

# 3. heartbeat fleet/machines/bm-a.json (indent=1, CRLF, no trailing NL; epoch must be JSON int)
p = 'fleet/machines/bm-a.json'
h = json.load(open(p, encoding='utf-8'))
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
h['last_seen'] = NOW
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = NOW
h['cpu_pct'] = round(cpu, 1)
h['cpu_util_pct'] = round(cpu, 1)
h['free_ram_gb'] = round(vm.available / (1024**3), 1)
h['idle_ram_gb'] = round(vm.available / (1024**3), 1)
h['current_task'] = 'r498 closed: LOWAMP-P1 judged-negative verdict delivered (18/18), rebase crash recovered + pushed; W14 wave drafting on board-empty trigger'
h['round_no'] = 498
h['verdict'] = ('r498 closed (dead-session continuation): LOWAMP-P1 judged batch CLOSED judged-negative (finalize 18/18 '
'faces, DSR 0.0%, 2008 trials, T-132 done) + rebase push-rejection collision resolved 4 batches canonical + push '
'490c7f821 + pool entry heal NULLS/SENS + S6 28 legs rc0')
out = json.dumps(h, ensure_ascii=False, indent=1).replace('\n', '\r\n')
open(p, 'w', encoding='utf-8', newline='').write(out)

# self-assertions per law
hh = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(hh['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in hh['clock_read'], 'clock_read must be T-separated'
ss = json.load(open('state-bm-a.json', encoding='utf-8'))
assert ss['round_no'] == 498
print('bookkeeping done; epoch int ok; clock T-sep ok; report line appended; now =', NOW)
