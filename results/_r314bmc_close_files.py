# r314 bm-c S7 close -- file writes (python, UTF-8) + targeted commit + push + delivery verify
import json, time, sys, datetime, io

repo = 'K:/Fluxgroup/FluxGroup/quant/bigmoney/'
now = datetime.datetime.now().astimezone()
now_iso = now.isoformat(timespec='seconds')
epoch = int(time.time())
cpu_pct = float(sys.argv[1]); ram_free = float(sys.argv[2]); gpu_mib = int(sys.argv[3])

# ---------- state-bm-c.json ----------
sp = repo + 'state-bm-c.json'
st = json.load(open(sp, encoding='utf-8'))
st['machine_id'] = 'bm-c'
st['round_no'] = 314
st['last_round_at'] = now_iso
st['last_round_ts'] = now_iso
st['updated'] = now_iso
st['cpu_pct'] = cpu_pct
st['idle_ram_gb'] = ram_free
st['gpu_free_vram_mib'] = gpu_mib
st['verify'] = ('S1 smoke 47/47; S6 35 legs rc0 NON-GREEN=NONE (dualrun ZERO-DRIFT streak 3/3; '
                'WM red=runnable-work-idle-low-cpu 12:20 -- origin-truth recheck: 5 ready ALL STOCKFURN bm-b-lane '
                '(data-gated, bm-c takeable=0) + W8 12/12 done -> lane-blind stale signal, GM waiver O-1612, probe '
                'verdict insufficient_history n=2; monthly trio re-run idempotent: self_review P1 supply-gap v2.4 '
                'never-CLEAN 1 miss + P2 moneyflow source-blocked 106min both reported); D-19 753F99E8 CONSUMED '
                '(D-20261001-01..08 + C-01/02/03 all pre-wired via O-1058/prompt = zero new action rows; watermark '
                'key updated, raw-blob method); orders double-scan diff EMPTY; attrition CLEAN (4 healed); '
                'wild_route r312 conversion adoption-verified (real-path smoke 393-cell byte-identity ALL PASS)')
st['did'] = ('r314: triple-crash adoption (r311/r312/r313 dead sessions + HQ unpushed 936da95cb) + fleet git '
             'integration via CAS cherry-pick (0-behind deadlock window closed, pushed 3305af3ca..6cdaadba9, '
             'delivery-verified N=0) + W8 shard products 8-11 landed on origin (5/12) + monthly trio refreshed on '
             'fresh base + O-1058 union resolve (bm-b ack x HQ sec.6)')
st['current_task'] = ('W8 finalize blocked on peer product hygiene (origin 5/12: bm-a owes 1-7, bm-b owes 6; '
                      '12/12 ls-tree assertion before finalize per r310 law) + T-134 s2 next-candidate evidence-order '
                      'rescan of remaining banned runners')
st['next'] = ('(a) W8 12/12 products on origin -> finalize --wave 8 + entry/shard dual flip (r489) + s7/s8 backfill '
              '+ predictions 4-check; (b) T-134 s2: rescan remaining banned runners by evidence-order law, convert '
              'next candidate (wild_route done+verified, census 34); (c) r319 = HANDOVER 5x; (d) WM lane-blind '
              'red-flag improvement item = backlog candidate (per-lane takeable counting in py_watermark)'
              )
st['heartbeat_epoch_utc'] = epoch
st['clock_read'] = now_iso
st['note'] = ('r314 round-number rebuild note: state was rolled back to r310 close-face by the r312 rebase-recovery '
              'surgery (r313 disclosed); r312 (wild_route + W7 finalize + orders acks, committed/pushed pre-crash) + '
              'r313 (W7 s7/s8 backfill, adopted+committed this round) reconstructed via commit-log x round-report x '
              'heartbeat three-source cross-check per r471 adoption law; this session = r314')
st['last_ts'] = now_iso
st['last_decisions_sha'] = '753f99e81a27db3e1b4f2c76cd991ca50d52b80aa7faa63d6412cc2da1f5fb01'
st['last_decisions_read_at'] = now_iso
st['last_decisions_sha_method'] = 'python subprocess.check_output raw-blob bytes SHA-256 (PS-pipeline join method = transcoding false-drift, see CODELY r292 pit)'
st['last_round'] = ('2026-10-01 r314 bm-c: triple-crash adoption + CAS cherry-pick integration + W8 products 5/12 '
                    'on origin + monthly trio refresh + S6 35 legs rc0')
json.dump(st, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- heartbeat fleet/machines/bm-c.json ----------
hp = repo + 'fleet/machines/bm-c.json'
hb = json.load(open(hp, encoding='utf-8'))
ack = hb.get('orders_ack', [])
hb['machine_id'] = 'bm-c'
hb['cores'] = 32
hb['orders_ack'] = ack
hb['cpu_util_pct'] = cpu_pct
hb['free_ram_gb'] = ram_free
hb['total_ram_gb'] = 25.7
hb['gpu_free_vram_mb'] = str(gpu_mib)
hb['gpu_model'] = 'NVIDIA GeForce RTX 3070 16384MiB (nvidia-smi real read)'
hb['prod_lanes'] = ('r314: triple-crash adoption closed (r312 wild_route conversion verified byte-identical; '
                    'r313 W7 s7/s8 backfill committed); fleet integration deadlock cleared (16-behind/1-ahead -> 0/0); '
                    'W8 products 5/12 on origin (bm-c leg complete)')
hb['cpu_pct'] = cpu_pct
hb['round_no'] = 314
hb['updated_at'] = now_iso
hb['ram_free_gb'] = ram_free
hb['gpu_vram_free_mb'] = gpu_mib
hb['last_seen'] = now_iso
hb['current_task'] = ('W8 finalize blocked on peer product commits (bm-a owes 1-7, bm-b owes 6); T-139 stock '
                      'furnaces = GM/bm-b/bm-a lanes (bm-c no claim per data gate); bm-c = T-134 s2 next-candidate '
                      'rescan + lane-free compute')
hb['cpu_cores'] = 32
hb['idle_ram_gb'] = ram_free
hb['gpu_free_vram_mib'] = gpu_mib
hb['verdict'] = ('WM red runnable-work-idle-low-cpu = lane-blind stale signal (origin truth: 5 ready ALL '
                 'bm-b-lane STOCKFURN, bm-c takeable=0, W8 12/12 done, GM waiver O-1612); integration N=0')
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = now_iso
hb['health'] = 'ok'
hb['gpu_idle_vram_mb'] = gpu_mib
hb['gpu_idle_vram_mib'] = gpu_mib
hb['cpu_idle_pct'] = round(100.0 - cpu_pct, 1)
hb['last_seen_at'] = now_iso
hb['activity_now'] = 'triple-crash adoption + fleet integration closed, W8 product delivery leg complete'
hb['latest_artifact'] = ('origin results/p2cal_ext/n1_w8/shard-8..11-of-12.json + results/briefings/BRIEF-202609.md '
                         '+ results/self_review/SELF-REVIEW-202609.md @ ' + now_iso)
hb['next_milestone'] = ('W8 12/12 products -> finalize --wave 8 + T-134 s2 next conversion; window <=48h')
json.dump(hb, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---------- round_reports-bm-c.md append ----------
rp = repo + 'round_reports-bm-c.md'
line = (
 now_iso + '｜r314｜dept:工程（机队 git 整合+死会话收编核验）+dept:研究（常供面 W8 产品交付）｜'
 'watermark verdict=红（runnable-work-idle-low-cpu 12:20 旗·origin 真值复核=5 ready 全 STOCKFURN bm-b lane 独占'
 '〔数据门本机诚实 exit3 不可领〕+W8 12/12 done+本机可领=0+probe insufficient_history n=2+GM waiver O-1612'
 '→定性=lane 盲伪信号非怠工·r513 stale-view 法实履）｜'
 '本轮主产出=四件：①**三连猝死收编+全机 git 整合**（r311 心跳后死/r312 finalize 后 rebase 劫持死/r313 回填后未 commit 死'
 '+HQ 未推 936da95cb）：liveness 三查定无活会话→真携带集 carry commit〔CODELY 坑律/W7 §7/§8 回填/W8 产物件/append jsonl/lane 态〕'
 '→纯派生共享面 restore-to-HEAD〔r296 ③〕→checkout --detach origin/main+逐 cherry-pick〔O-1058=bm-b ack×HQ §六 union 解'
 '+CODELY=基块+两侧独有行防重 union 解+pool_core_samples=行集 union 解〕+commit -C〔r305 净路避 rebase --continue 三拒面〕'
 '+update-ref CAS 原子移 ref〔daemon 抢道=败非吞〕→push 3305af3ca..6cdaadba9→fetch+ls-tree 送达核验〔16-behind/1-ahead 死锁窗收口·N=0〕'
 '②**W8 产物件 4 件入 origin**〔shard-8/9/10/11·r310 harvest-不含产物系统面本机腿清偿·origin n1_w8 5/12'
 '〔bm-a 1-7+bm-b 6 待各自 S0 hygiene·shard-8 双烧 AA 面照 r481 律裁定·12/12 ls-tree 断言前 finalize 禁跑〕'
 '③**r312 wild_route 转换收编核验**（real-path smoke 393 cell byte-identity ALL PASS 本轮实跑复核+S-mp 43/43 死会话自证'
 '·census 34·T-134 s2 第四件闭环）④**月度三件 fresh-base 再履**〔BRIEF-202609.md+SELF-REVIEW-202609.md+science_audit 刷新'
 '·r311 05:42 首履后 stale-base 幂等再生合法·self_review 新发现如实呈报=P1 supply-gap CLEAN 判据 v2.4 never-CLEAN 违例 1'
 '+P2 moneyflow 源阻断 106min·只报不阻断〕｜'
 '验证证据=S1 47/47；S6 35 腿 rc0〔dualrun ZERO-DRIFT streak3/3·compute_audit pool-supply-gap ready5 全 bm-b lane'
 '·REGIME ORANGE〔trigger hs300<MA200 #10+breadth 0.79〕·clockcall ORANGE_COOL sleeves=4·scorecard/daily/build/paper 面 '
 'host 守卫放行写〔bm-a 心跳 17min 新鲜〕·LIVE/REPORT 2026-10-01 再生·token 0 today·fund_premium 15:30 前 no-op·B 层掩码再生〕；'
 'orders 轮首+S7 双扫差集 EMPTY；D-19 753F99E8 CONSUMED〔新行 D-20261001-01..08+C-01/02/03 全经 O-1058/prompt 承接=零新动作行·水位键已更新〕；'
 'attrition CLEAN〔4 healed〕；claw byte-equal 免重装；schtasks loop 12:25 实火实证在册〔zh-CN 输出面英滤空勘正照录〕；'
 'inbox 2 件消费入 processed/〔bm-b T-139 akshare 面认领=本机不碰注记·r312 N2-W15 让位头信=已送达件归档〕·余 2 件 GM 收件留置｜'
 '实况三行（CEO 过程可见面）：当前活=三死会话遗产收编+全机整合收口毕｜'
 '最近实物=origin n1_w8 shard-8..11 4 件+BRIEF-202609.md+SELF-REVIEW-202609.md（' + now_iso + '）｜'
 '下个里程碑=W8 产物 12/12→finalize --wave 8+T-134 s2 第五候选证据序重扫（窗≤48h·待 peers 产品 hygiene）｜'
 '产品分=2（W8 产品交付+月度三件实物）+1（整合手术实改）｜'
 'next: (a) W8 finalize 待 12/12 产物〔peers hygiene〕+entry 双翻+s7/s8 回填；(b) T-134 s2 余 34 禁面证据序重扫定下一件；'
 '(c) r319=HANDOVER 5x；(d) WM lane 盲红牌→py_watermark per-lane takeable 计数=backlog 候选'
)
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write('\n' + line + '\n')

# ---------- CODELY.md append (one pit entry, <=1.5KB) ----------
cp_ = repo + 'CODELY.md'
entry = (
'\n- [2026-10-01 12:3x r314 bm-c] 三连猝死会话收编+CAS 整合法（r471 收养律×r305/r501 净路族合订·单窗实弹）：'
'单日三死会话（r311 心跳后/r312 finalize 后 rebase 劫持/r313 回填未 commit）+HQ 未推 commit 的收编正序='
'①liveness 三查（进程扫描排自匹配+tick 锁龄+6min 新鲜写面）定无活会话才动手；'
'②真携带集〔坑律/prereg 回填/产物件/append jsonl/lane 态〕定向 add 成 carry commit、纯派生共享面 restore-to-HEAD 让 origin 落地（r296 ③）；'
'③集成禁 rebase --continue 全家（git 2.55 三拒面）=checkout --detach origin/main+逐 cherry-pick+commit -C，'
'冲突 union 三式〔md 追加块=公共基块+两侧独有行防重复·jsonl=行集 union 去重·orders 尾=双方节并存〕；'
'④update-ref refs/heads/main <新sha> <预期旧sha> CAS 原子移 ref（daemon 抢道=CAS 败非 orphan 吞）+checkout main+push+fetch ls-tree 送达核验；'
'⑤daemon 每分钟重写 lane 态件（autofill/dispatcher state）与 checkout/pick 构成秒窗竞态=同窗 restore-then-pick 打包，事后被 daemon 重写属正常态勿追。'
'How to apply：多死会话遗产按「已 commit=已保·未 commit=核验后收编」分流；daemon 活跃机整合一律走 CAS cherry-pick 净路勿 rebase --continue；'
'cherry-pick 祖先 commit（已在 HEAD 历史内）=恒 empty pick，先 detach 再按拓扑序逐个 pick。'
)
with open(cp_, 'a', encoding='utf-8', newline='') as f:
    f.write(entry)
print('FILES-WRITTEN-OK', now_iso, 'epoch', epoch)
