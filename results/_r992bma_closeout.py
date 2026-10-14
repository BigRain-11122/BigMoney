"""r992 bm-a closeout: METHODOLOGY E67 append + state round 992 + D-19 watermarks
+ heartbeat + idle --worked clear. Fresh read-modify-write per multi-writer law."""
import json, time, datetime, subprocess

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
now_short = now[:19]

# --- S4: methodology append (E67) ---
mfile = 'knowledge/METHODOLOGY_ASSETS.md'
with open(mfile, encoding='utf-8', errors='replace') as f:
    m = f.read()
if 'E67' not in m:
    entry = (
        '\n- **E67 中断轮 estate 吸收三坑速记（陈旧 unmerged index 判性 + daemon-dirty pick rescheduled 环 + stash-blob union tick 回捞）**：proven，工程面。'
        '①轮首 pull 拒「unmerged files」而 .git/MERGE_HEAD/rebase-merge/rebase-apply 三件全缺 = 中断操作残尸（非活冲突）——repo 全提交面被堵；判性=ls-files -u 三 stage 全量列出+逐 stage ts 探针，snapshot 形态（attrition scan 等 per-run 证据件）取 stage∪worktree 最新 ts 侧，append-only 形态走 merge_lane_views resolve 禁手写 union。'
        '②常驻 daemon（satengine/autofill）在 rebase 窗内秒级回写 face 文件→pick 应用报 rescheduled 循环堵死；正法链=path 限定 git stash push→rebase --continue；continue 报零 UU 仍拒=r863 坑族第二实例（正解=add -A 索引归一+$env:GIT_EDITOR=\'true\' 一发即过·r933 remedy 复验）。'
        '③多 stash 持有 daemon tick 追加行时禁逐层 pop（pop 3-way 在 append-only 尾部必炸）——正法=**stash-blob 直接读回捞**：git show stash@{N}:<path> 取各 stash blob→jsonl 行级 unique union 落回+face/snapshot 按 ts 取最新→drop stash；零 pop 冲突面、append-only 零丢失可验（live：35 history 行回捞+155 行全量 parse-verify 0 fail）。'
        'live 实证：r992 bm-a（16:18 死窗 W240 splice estate 吸收+19 UU shared-regen 批+r986 坑族 continue 双拒+三 stash 回捞全链）。\n'
    )
    with open(mfile, 'a', encoding='utf-8') as f:
        f.write(entry)

# --- S7: state-bm-a.json ---
sfile = 'state-bm-a.json'
s = json.load(open(sfile, encoding='utf-8-sig'))
s['round_no'] = 992
s['last_round'] = 992
s['loop_round'] = 992
s['clock_read'] = now
s['last_round_at'] = now
s['last_round_closed'] = now
s['last_round_ts'] = now
s['last_run'] = now
s['last_seen'] = now
s['current'] = ('r992: dead 16:18-fire W240 splice estate ABSORBED+LANDED origin dc27f5217 (five-face freeze + pf/n1 band edits + 12/12 N1 shards + receipts; sole-executor census self=PID51772); '
                'stale-UU repo blockage healed (19-file shared-regen batch canonical resolve: 6 ALL_FACES merge_lane_views union + 3 twins take-newer + snapshots deep-ts + host faces take-local); '
                'W240 finalize = next-round standing product (shards complete, runner perpetual_faces_n1.py --wave 240)')
s['current_task'] = s['current']
s['did'] = ('r992: S0 orphan 0/58 + git-rescue full chain (stale unmerged index diagnosed=no-op-state leftover -> attrition scan take-newest resolve -> estate commit -> 2x pull --rebase with bm-b r1000 race '
            '(stash-race rescheduled pick + 13/19-UU canonical resolver _r992bma_resolve.py) -> push dc27f5217 BEHIND=0) + 3-stash daemon-tick union recovery (35 history lines zero-loss) '
            '+ r376 reconcile 6 faces zero-drift + S0.5 D19 dual-delta consumed (ORD 542f99a9 / DEC c61d7884 zero BigMoney directives; DEC side co-adopted bm-b r1000 adjudication) '
            '+ S1 smoke 49/49 + S2 boards empty (queue probe CLEAR T22/E14) + S3 satengine ALIVE idle queue0 (pool_starvation flag = W241 supply standing) + S6 chain detached PID 36992 running '
            '+ METHODOLOGY E67 appended')
s['last_action'] = 'r992 W240 splice estate absorb+land'
s['last_artifact'] = 'scripts/perpetual_faces_n1.py W240 bands LANDED on origin dc27f5217 (16:4x) + results/p2cal_ext/n1_w240/ 12 shards'
s['latest_artifact'] = s['last_artifact']
s['last_orders_seen'] = 'r992: ORD 542f99a9 consumed (tail rows MV/committee/software-copyright/CEO-PROXY lanes; 10-13 CPU 常开令+云端放开令 already in law; zero new BigMoney directives; watermark advanced)'
s['last_orders_sha'] = '542f99a90d06a0f64d1d681e9bb4ed4bcf74d7ae89490b5aaeae29bf630f4ada'
s['last_orders_at'] = now
s['last_decisions_seen'] = 'r992: DEC c61d7884 consumed (delta rows = 10-14 batch D-20261014-01..08 group-domain lanes; bm-b r1000 same-hash adjudication co-adopted dual-source; zero BigMoney directives; watermark advanced)'
s['last_decisions_sha'] = 'c61d7884b347e7e706ed98546aadc304f7f3afddd9071a5110152a860a064bb'
s['last_decisions_at'] = now
json.dump(s, open(sfile, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# --- S7: heartbeat fleet/machines/bm-a.json ---
hfile = 'fleet/machines/bm-a.json'
h = json.load(open(hfile, encoding='utf-8-sig'))
h['last_seen'] = now
epoch = int(time.time())
h['heartbeat_epoch_utc'] = epoch
h['last_heartbeat_epoch_utc'] = epoch
h['heartbeat_epoch_utc_type_int'] = True
h['clock_read'] = now
h['ts'] = now
h['idle_rounds'] = 0
h['agenda_starved'] = False
h['verdict'] = 'green (wm-red=false; satengine ALIVE rc0 idle queue0 pool_starvation=W241 supply standing; orphan 0/58; r992 estate landed)'
json.dump(h, open(hfile, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert isinstance(h['heartbeat_epoch_utc'], int)
print('closeout writes done; epoch int verified:', epoch)
