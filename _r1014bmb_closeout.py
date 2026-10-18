# -*- coding: utf-8 -*-
# r1014 bm-b closeout: state.json + round report line + heartbeat, one-shot.
import io, json, time, datetime, subprocess, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec='seconds')
epoch = int(time.time())

# ---- machine probes ----
ram_gb, cpu_pct, vram_free, codely_live = 0.0, 0.0, 0, 0
try:
    import psutil
    ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    for p in psutil.process_iter(['name']):
        if 'codely' in (p.info.get('name') or '').lower():
            codely_live += 1
except Exception:
    pass
try:
    r = subprocess.run(['nvidia-smi', '--query-gpu=memory.free',
                        '--format=csv,noheader,nounits'],
                       capture_output=True, timeout=30, creationflags=_NO_WINDOW)
    vram_free = int(float(r.stdout.decode().strip().splitlines()[0]))
except Exception:
    pass

# ---- state.json (logs/iteration-loop/, bm-b canonical round state) ----
sp = io.open(r'logs\iteration-loop\state.json', encoding='utf-8').read()
st = json.loads(sp)
st['round_no'] = 1014
st['did'] = ('r1014: ST-001 集团收口（drama-dept-v1 LEDGER J-D0-1R 回填行 CAS 上链 ae59395d6b 一次过·'
             'blob 恒等+行落位双验·≤r1015 死线提前一轮清）+ CONTENT-LOOP v0.2 runners 建成并同轮执行'
             '（content_loop_step.py +st003/+st004 双 runner+adopt-runners 维护命令+全 subprocess '
             'CREATE_NO_WINDOW 零窗化；clone 三路回退链 direct→gh-proxy→ssh·首跳 schannel 被掐后 '
             'gh-proxy 中标）→ ST-003 声库车道首批（GPT-SoVITS 1d9fe63d2875 + OpenVoice 74a1d147b17a '
             '双 --depth 1 克隆入 media/drama-tools/ + outbox 评估面 VOICE-LIBRARY-EVAL-20261019.md + '
             '骨架 VOICE-PIPELINE-SKELETON-v1.md·MIT 双证/中文支持/GPT-SoVITS 主选+OpenVoice 备选定谳）'
             '→ ST-004 锚清洗纪律入产线（anchor_precheck.py=三元组校验+银行入行门+跨帧行零漂移检+'
             '视觉席位工单面·版本化源 content/drama/runner_assets/ 部署 MiniGame/Tools/comfy/ + '
             'drama_ep_burn.py 5 锚补发色钉（RED/MANCANG/XIONGWEI/FATHER/BOY）+启动硬闸 anchor_gate '
             'ANCHOR_TRIPLE_FAIL exit2 + selftest 断言 PASS + 补丁后探针 7/7 + py_compile 双绿）+'
             'S0 双面核验（decisions 8706acd8 零变·orders e695556b→04050fda 一行 V5.9 出片回执零新义务·'
             'bm-a r1070 双件 FF 吸收+autostash 干净落回）+S1 smoke 49/49+S3 SatEngine alive（idle·'
             'queue_depth 0）+S6 43 腿 rc0 2.5min（ZERO-DRIFT streak 51·compute_audit '
             'pool_starvation/supply_floor 诚实旗·LIVE-2026-10-19 ORANGE cap50% 重生·stale-takeover '
             '四面 scorecard/paper_export/daily_scorecard/dashboard）+S7 三任务（IterationLoop/'
             'LoopWatchdog/ContentLoop）+双爪全绿')
st['verdict'] = ('GREEN: r1014 CONTENT-LOOP v0.2 双 runner 同轮建成+执行——ST-001 集团 LEDGER J-D0-1R '
                 '上链（ae59395d6b·≤r1015 死线提前清）+ ST-003 声库首批完成（双仓克隆+评估面+骨架件·'
                 'P1 主里程碑落地）+ ST-004 锚清洗入产线（工具+补丁+硬闸+selftest 双绿·CSA v1.1 item 2 '
                 '闭环）；四站态=ST-001 done/ST-002 候 CEO 门/ST-003 done/ST-004 done；S6 43 rc0；'
                 'orders 水位推进 04050fda；leftovers=O-0948 窗口判决 10-19 ~10:2x + PT02 夜班 poke '
                 '03:07 值守 + ST-002 候 CEO 方向门回执 + pool_starvation 诚实旗（研究池空=试用劳动力'
                 '常设线候下轮起草或候秘书处补货）')
st['next'] = ('r1015: 1) O-0948 窗口关闭判决（10-19 ~10:2x·O-20261014-0948-bm-b）2) PT02 poke 值守'
              '（夜班 03:07）3) ST-002 观察 CEO direction-gate 回执（IndexTTS-2 门后）4) '
              'pool_starvation 面：试用劳动力常设线起草或候委员会派工 5) W273+/W274 席位观察（bm-c '
              '在飞）6) BigMoney 席位自动化案=bm-a r1069 3762f3dafa 消费勿重建')
st['last_round_ts'] = ts
st['last_result'] = 'ok'
st['current_task'] = 'r1014: 三站收口（ST-001 LEDGER/ST-003 声库/ST-004 锚清洗）+S6+S7'
st['updated_at'] = ts
st['last_seen'] = ts
st['ts'] = ts
with io.open(r'logs\iteration-loop\state.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- round report line ----
line = ('%s | r1014 bm-b | dept:舰队+工程 | WM verdict: GREEN (red=False @02:39 S6 链内'
        'py_watermark insufficient_history 夜间合法低载) | 当前活=r1014 CONTENT-LOOP v0.2 双 runner '
        '同轮建成+三站收口（ST-001 LEDGER/ST-003 声库/ST-004 锚清洗）+S6 43+S7 | 最近实物=①集团 '
        'drama-dept-v1 LEDGER J-D0-1R 回填行上链 CAS ae59395d6b（02:29·一次过·blob 恒等+行落位双验）'
        '②VOICE-LIBRARY-EVAL-20261019.md+VOICE-PIPELINE-SKELETON-v1.md（02:37·GPT-SoVITS/OpenVoice '
        '双克隆 1d9fe63d2875/74a1d147b17a）③anchor_precheck.py 部署+drama_ep_burn.py 三元组钉锚补丁+'
        '启动硬闸（selftest PASS+探针 7/7+py_compile 双绿）+ST-004-ANCHOR-PRECHECK-RECEIPT.md | '
        '下个里程碑=CONTENT-LOOP 连续运行证据窗 10-28 判据（72h≥3 站/日）+O-0948 判决 10-19 ~10:2x+'
        'ST-002 候 CEO 门 | 孤儿面=0 | orders 水位 e695556b→04050fda（V5.9 出片回执·零新义务）| '
        'decisions 8706acd8 零变 | S6 43 rc0 2.5min | 本地未达 origin commit 数=0（push 后核验）' % ts)
rpt = r'logs\iteration-loop\round_reports.md'
lines = io.open(rpt, encoding='utf-8').read().splitlines()
lines = [l for l in lines if '| r1014 bm-b |' not in l]  # idempotent re-run: drop failed-run row
lines.append(line)
with io.open(rpt, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

# ---- heartbeat fleet/machines/bm-b.json ----
hp = os.path.join(ROOT, 'fleet', 'machines', 'bm-b.json')
hb = json.loads(io.open(hp, encoding='utf-8').read())
hb['machine_id'] = 'bm-b'
hb['last_seen'] = ts
hb['task'] = 'r1014: CONTENT-LOOP v0.2 runners (ST-001 LEDGER + ST-003 voice + ST-004 anchor) + S6 43 + closeout'
hb['did'] = ('r1014: ST-001 group LEDGER J-D0-1R backfill row CAS-landed (ae59395d6b one-shot, blob-equality '
             '+ row-landing double-verified, <=r1015 deadline cleared one round early) + CONTENT-LOOP v0.2 '
             'RUNNERS BUILT AND EXECUTED SAME ROUND (st003 + st004 + adopt-runners maintenance op + '
             'CREATE_NO_WINDOW zero-flash pass over all subprocess calls; clone fallback chain direct->gh-proxy'
             '->ssh, gh-proxy won after schannel cut) + ST-003 voice first batch COMPLETE (GPT-SoVITS '
             '1d9fe63d2875 + OpenVoice 74a1d147b17a cloned into media/drama-tools/, eval face + pipeline '
             'skeleton in outbox, MIT both, primary/fallback verdict) + ST-004 anchor-clean INTO PRODUCTION '
             '(anchor_precheck.py util triple-validate + bank admission gate + cross-frame zero-drift + '
             'vision-seat workorder face, versioned source in runner_assets, deployed to MiniGame/Tools/comfy; '
             'drama_ep_burn.py five anchors hair-pinned + startup hard gate ANCHOR_TRIPLE_FAIL exit2; '
             'selftest PASS + probe 7/7 + py_compile both) + S0 dual-face (decisions 8706acd8 unchanged / '
             'orders e695556b->04050fda one V5.9 receipt row zero new obligation; bm-a r1070 FF absorb + '
             'clean autostash) + S1 smoke 49/49 + S3 satengine alive + S6 43 rc0 2.5min (ZERO-DRIFT 51, '
             'pool_starvation/supply_floor honest flag, LIVE-2026-10-19 ORANGE cap50% regenerated, '
             'stale-takeover x4) + S7 three tasks + two claws all green')
hb['cpu_cores'] = 16
hb['free_ram_gb'] = ram_gb
hb['gpu_free_vram_mb'] = vram_free
hb['cpu_load_pct'] = cpu_pct
hb['verdict'] = st['verdict']
hb['idle_rounds'] = 0
hb['agenda_starved'] = False
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = ts
hb['ts'] = ts
hb['round_no'] = 1014
hb['round'] = 1014
hb['current_task'] = st['current_task']
hb['next'] = st['next']
hb['last_action'] = ('r1014: CONTENT-LOOP v0.2 two runners built+executed same round (ST-001 LEDGER CAS push '
                     '+ ST-003 voice first batch + ST-004 anchor-clean patch) + S6 43 + watermark advance 04050fda')
hb['last_action_at'] = ts
hb['orders_ack_last'] = hb.get('orders_ack_last')
hb['last_orders_sha'] = '04050fdab14983da6af0c900e1d27a83bc7e39aaa48743d7964ea54478f26b98'
hb['last_decisions_sha'] = '8706acd8a7b65441f23c9813f62a25fdecbd9da0df10994e5915b5742a40a3fd'
hb['last_orders_read_at'] = ts
hb['last_decisions_read_at'] = ts
hb['last_orders_at'] = '2026-10-19T02:18:00+08:00'
hb['last_decisions_at'] = hb.get('last_decisions_at')
hb['current'] = st['verdict']
hb['next_milestone'] = ('CONTENT-LOOP continuous-run evidence window (10-28 judgment: 72h >=3 stations/day) '
                        '+ O-0948 window judgment 10-19 ~10:2x + ST-002 gated on CEO direction receipt')
hb['latest_artifact'] = ('content/drama/outbox/VOICE-LIBRARY-EVAL-20261019.md + VOICE-PIPELINE-SKELETON-v1.md '
                         '+ ST-004-ANCHOR-PRECHECK-RECEIPT.md (02:37) + group LEDGER row J-D0-1R @ae59395d6b '
                         '(02:29) + Tools/content_loop_step.py v0.2 runners')
hb['last_artifact'] = hb['latest_artifact']
hb['now_active'] = 'r1014 closing'
hb['orphan_face'] = 0
hb['codely_live_count'] = codely_live
hb['note'] = ('r1014: CONTENT-LOOP all four stations resolved same round (001/003/004 done, 002 CEO-gated); '
              'voice lane P1 first batch landed 3 days before 10-22 deadline; ST-001 group face cleared')
with io.open(hp, 'w', encoding='utf-8') as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write('\n')

# ---- self-verify ----
chk = json.loads(io.open(hp, encoding='utf-8').read())
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in chk['clock_read'] and '+' in chk['clock_read'], 'clock_read format'
assert chk['round_no'] == 1014
st2 = json.loads(io.open(r'logs\iteration-loop\state.json', encoding='utf-8').read())
assert st2['round_no'] == 1014
print('CLOSEOUT_OK ts=%s ram=%sG vram=%sMB cpu=%s%% codely=%d epoch=%d' % (
    ts, ram_gb, vram_free, cpu_pct, codely_live, epoch))
