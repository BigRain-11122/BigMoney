# r246 bm-c closeout: heartbeat/state update (values from PS side collected fresh) + round report append + verification
import io, sys, json, re, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

vals = json.load(open(r'results\_r246bmc_vals.json', encoding='utf-8-sig'))
now_iso = datetime.datetime.now().astimezone().strftime('%Y-%m-%dT%H:%M:%S+08:00')

# 1) state round_no 245 -> 246
sp = 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8-sig'))
prev = st.get('round_no')
st['round_no'] = 246
json.dump(st, open(sp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
open(sp, 'a', encoding='utf-8', newline='\n').write('\n')

# 2) heartbeat
hp = r'fleet\machines\bm-c.json'
hb = json.load(open(hp, encoding='utf-8-sig'))
hb['last_seen'] = now_iso
hb['updated_at'] = now_iso
hb['round_no'] = 246
hb['current_task'] = ('r246 closed: W4 VOLREGIME-TIMING-P1 verdict adopted (0/3 judged-negative, zoo #96 volume-native '
                      'timing family closed per law s5, ledger 352,021, prereg s7/s8 backfilled + pool SLOT-4 done flipped); '
                      'next = W5 berth draft (supply floor ready=1<3) + 10-01 monthly trio')
hb['heartbeat_epoch_utc'] = int(vals['epoch'])
hb['clock_read'] = vals['clock']
hb['cpu_util_pct'] = vals['cpu']
hb['cpu_pct'] = vals['cpu']
hb['free_ram_gb'] = vals['ram']
hb['ram_free_gb'] = vals['ram']
hb['idle_ram_gb'] = vals['ram']
hb['gpu_free_vram_mb'] = vals['gpu']
hb['gpu_vram_free_mb'] = vals['gpu']
hb['gpu_free_vram_mib'] = vals['gpu']
hb['verdict'] = 'healthy'
json.dump(hb, open(hp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
open(hp, 'a', encoding='utf-8', newline='\n').write('\n')

# 3) round report line
line = (now_iso + ' | r246 bm-c (dept:研究+舰队·W4 判决收编轮) | WM-VERDICT: 绿 (watermark_red red=false lane=healthy; '
        'py 尾窗 0-3.1%=SLOT-4 在飞有据烧批非空转; 烧毕 ready=1(仅 bm-b 车道 W11-JUDGE)+supply_floor 旗如实披露) | '
        'CEO 可见面: 当前活=W4 VOLREGIME-TIMING-P1 判决 adopt-verify-close 收编; '
        '最近实物=results/innovation_quota/VOLREGIME-TIMING-P1.json（判决件 01:50:57·0/3 全负判·账本 352,021）'
        '+research/INNOVATION_QUOTA_W4_PREREG.md §7/§8 回填+results/runnable_pool.json SLOT-4 done 翻面; '
        '下个里程碑=10-01 月首轮三件套（science_audit/monthly_briefing/self_review·≤48h 窗）'
        '+W11 JUDGE verdict（bm-b 车道）+W5 泊位起草（supply_floor ready=1<3 供给缺口修复面） | '
        'did: S0-1 锚 bm-c→fetch 双向 0/0 零 rebase→S0.5 令差集 122/122+decisions 尾 09-28 批零新行→S1 smoke 26/26→'
        'S2 双板零 open 票→S3 试用劳动力常设线=在飞判决批收编：三步锚验（①进程链 01:50:01→01:50:57 pid 37072 已退零僵尸'
        '②工件全 face+seed 20322000/runner 869c1097ce0091b8 点火记录/在树件三方哈希一致+prereg 判据零触碰'
        '③账本线性 350,018→352,021+attrition 双面 01:50:57 已落）→adopt 四件=prereg §7 跑后实证+§8 批后复盘'
        '（预测 1 部分对/2 对且强化/3 错/4 错/5 对·族关单+重开注记三通道=非HMA量能矩/UPPER独立新prereg/日内高频面）'
        '+池 SLOT-4 行级手术翻面 done+result_ref（json 全量重排首试即撤改 R32 行级手术·resolver=results/_r246bmc_pool_flip.py·'
        'json.loads 复验过）+CODELY 热冷整编（9,731→9,603B 硬线下·r236 GBK 坑律 750B verbatim 迁 archive 202609.md '
        'r246 窗批节+W4 判决指针行·零丢失 PASS·resolver=results/_r246bmc_codely_hotcold.py）→S6 38 腿 37 绿'
        '+update_lhb rc=3（EM 源改史旗标·本地零改写·r229 判例·bm-a 车道对账）·audit 旗=supply_gap+supply_floor'
        '（ready 1<3·W4 收编后池饿=W5 泊位起草窗下轮开）·scorecard/paper/t35/export/dashboard 守卫 stale-takeover'
        '（bm-a 心跳 51min 陈旧·O-2100 s2.4 STALE_MIN 律合法接管·如实披露）→S7: loop pin5 no-op+watchdog Ready'
        '+pre-commit claw 在位+attrition guard CLEAN（4 账本·bm-a 车道历史 shrink 2 处 healed 注记照录）+state '
        + str(prev) + '→246 +心跳 epoch int 自证 | verify: smoke 26/26; orders 122/122 双扫; S6 37/38 绿+1 rc3 诚实隔离; '
        'W4 判据面三证同窗（prereg §7/§8+attrition 行+池 result_ref）; attrition CLEAN; 心跳 epoch int+clock_read T 分隔自证 | '
        'next: (a) 10-01 月首轮三件套+REGIME_GUARD v3 日期门 hands-off (b) W5 泊位起草（填充阶梯·先扫 zoo 后备族谱防重） '
        '(c) W11 JUDGE verdict 观察（bm-b 车道禁碰） (d) update_lhb rc3=bm-a 车道对账 [via bm-c]')
rp = r'logs\iteration-loop\round_reports-bm-c.md'
with open(rp, 'ab') as f:
    f.write(('\r\n' + line + '\r\n').encode('utf-8'))

# 4) verification (R170/R178/R262 law)
hb2 = json.load(open(hp, encoding='utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$', hb2['clock_read']), 'clock_read T-format'
assert hb2['round_no'] == 246 and len(hb2['orders_ack']) == 122
st2 = json.load(open(sp, encoding='utf-8-sig'))
assert st2['round_no'] == 246
print('closeout PASS: state %s->246; heartbeat epoch int=%d clock=%s; report line appended'
      % (prev, hb2['heartbeat_epoch_utc'], hb2['clock_read']))
