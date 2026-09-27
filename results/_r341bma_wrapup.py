import json, io, time, datetime, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

now = datetime.datetime.now()
ts_hm = now.strftime('%H:%M')
ts_hms = now.strftime('%H:%M:%S')
clock_read = now.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'
epoch = int(time.time())

# 1) round report append (match file EOL)
rp_path = r'logs\iteration-loop\round_reports-bm-a.md'
raw = open(rp_path, 'rb').read()
crlf = b'\r\n' in raw
line = ("2026-09-27T" + ts_hms + "+08:00 | R341 bm-a (dept:舰队+engineering) | WM first-line verdict: green (red=false lane healthy @17:20:02; 17:50 probe py_low_board_clear=法定idle白名单: board 0 open 96 claimed + 池 ready=1 CENSUS-FUS-S2-W2A lane_owner=bm-b R31护栏非本机可烧 + bandit claimed-await-panel; audit v2.3 CLEAN flags=[] py 0.3% load_state=pool-supply-gap) | did: (A) S0 pull--rebase up-to-date 4837c841 零冲突; (B) S0.5 orders 96/96 双扫零未回执 + decisions 无新行(D-01~10 前轮已毕零动作); (C) S1 smoke 25/25; (D) 板/池巡检: 0 open票, post_review 15 NO 行全被后行翻案覆盖=零P0, inbox 零未读; (E) bm-b 心跳71min stale 但16:56:15 pool commit(owner_since勘正16:32->16:42)+W2-A燃烧在途15:10起est 3-6h=忙非死, 本轮不接管防同checkpoint双写, 下轮git静默+心跳续滞才按stale>20min正典接管(新坑律已入CODELY 10141B<10KB); (F) T-91 launch-eve ALL GREEN保持, 周一09-28 09:15自动点火; (G) S6 33/33 rc=0 周日no-op家族(无新bar cutoff 09-24中秋周末; moneyflow rank 17:26 spawn=源阻断fetch_failed, 30min self-heal驻留IC批等面板); (H) schtasks双任务在位(schtasks /query实证)+claw CR归一一致; (I) token API delta=0 | next: (1) 监W2-A finalize窗~18:10-21:10+UNC后续批sec.9.3路由; (2) bm-b双证盯守; (3) 周一T-91首标记链+新bar家族恢复; (4) next 5x=round 345; (5) C-01 council窗09-29 12:00")
nl = b'\r\n' if crlf else b'\n'
with open(rp_path, 'ab') as f:
    if not raw.endswith(nl):
        f.write(nl)
    f.write(line.encode('utf-8') + nl)
print('round report appended, crlf=', crlf)

# 2) state-bm-a.json (preserve: indent=1, LF, no trailing newline, ensure_ascii=False)
sp = r'state-bm-a.json'
st = json.load(io.open(sp, encoding='utf-8'))
st['round_no'] = 341
st['did'] = ("R341: S0 up-to-date 4837c841 zero-collision + orders 96/96 double-scan zero-unacked + decisions no-new-past-D-10 + smoke 25/25 + board/pool patrol (0 open; post_review 15 NO all superseded by later rows; inbox clear) + bm-b stale-takeover dual-evidence judgment (71min stale heartbeat BUT 16:56:15 pool commit + W2-A burn in-flight 15:10 est 3-6h = busy-not-dead, no takeover this round; new pitlaw appended CODELY 10141B<10KB) + S6 33/33 rc=0 Sunday no-op family (no new bar cutoff 09-24) + token API delta=0")
st['verify'] = ("smoke 25/25 + S6 33 legs rc=0 all + watermark 17:50 probe py_low_board_clear legal-idle (board 0 open, pool ready=1 lane_owner=bm-b R31, bandit claimed-await-panel) + audit v2.3 CLEAN flags=[] + schtasks /query both tasks present + claw CR-normalized byte match")
st['next'] = ("(1) T-91 s3 auto-fires Mon 09-28 09:15 first-marks chain (preflight ALL GREEN armed); (2) Monday new-bar family (next trading bar Mon 09-28); (3) W2-A bm-b finalize window ~18:10-21:10 + UNC follow-up batch per sec.9.3; (4) bm-b dual-evidence watch: git-silent + heartbeat still stale next round -> takeover per stale>20min canon; (5) next 5x = round 345; (6) C-01 council window 09-29 12:00")
st['last_round_at'] = "2026-09-27 " + ts_hm
st['current_task'] = "r341 done: maintenance round (S6 33/33 + dual-scan + no-takeover judgment + pitlaw); T-91 armed Mon 09:15"
with open(sp, 'wb') as f:
    f.write(json.dumps(st, ensure_ascii=False, indent=1).encode('utf-8'))
print('state r341 written')

# 3) heartbeat fleet\machines\bm-a.json
hp = r'fleet\machines\bm-a.json'
hb = json.load(io.open(hp, encoding='utf-8'))
hb['last_seen'] = "2026-09-27 " + ts_hms
hb['current_task'] = "r341: maintenance S6 33/33 + bm-b dual-evidence no-takeover judgment + takeover pitlaw; T-91 armed Mon 09-28 09:15"
hb['cpu_pct'] = 3.2
hb['free_ram_gb'] = 48.53
hb['gpu_free_vram_gb'] = 5.52
hb['gpu_free_vram_mb'] = 5656
hb['verdict'] = "healthy"
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = clock_read
hb['round_no'] = 341
hb['task'] = "idle-legal post-r341 (board 0 open; pool ready=1 lane_owner=bm-b R31; T-91 fires Mon)"
with open(hp, 'wb') as f:
    f.write(json.dumps(hb, ensure_ascii=False, indent=1).encode('utf-8'))
# self-verify epoch int type
chk = json.load(io.open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in chk['clock_read'][:11], 'clock_read not T-separated'
print('heartbeat r341 written; epoch int ok;', chk['clock_read'])
