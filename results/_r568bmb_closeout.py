# -*- coding: utf-8 -*-
"""r568 bm-b closeout: state.json + heartbeat + round report append (bytes-safe)."""
import json, time, datetime, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now = int(time.time())
iso = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

# --- state.json ---
sp = os.path.join(REPO, 'state.json')
st = json.load(open(sp, encoding='utf-8'))
st['round_no'] = 568
st['note'] = ("r568: W67 FINALIZE one-pass landed (prev 509,748 live-head derive + 2,200 "
              "= 511,948 NET CHAIN HEAD, K=145,320 == prereg bitwise; S5 4/4 PASS, se_mu "
              "0.000642 narrowing chain; prereg s7/s8 mechanical backfill; pre-rebase "
              "commit 77fd35e87) + W70 FREEZE delivered 34a0c2780 (FIFTY-NINTH engine wave, "
              "bm-b 22nd owned; seat MSG-20261002-1040-bmb published=reserved; A "
              "183_004..185_003 arithmetic continuation + B 51_001..51_200 PAST-HIT RESTART "
              "= FORK FACE #3 disclosed [reading 2 window-step chain 51_101..51_300 NOT "
              "taken; single-mid-hit precedent family W26-A/W68-B; pin pending "
              "HQ-FEEDBACK F-20261002-03 per the W69 row mandate derive+disclose]; band "
              "gate ADMIT + MSG-0640 FIX-A/B/C five-face + banned gate ADMIT + full-chain "
              "selftest W2..W70 PASS) + ignition verified (shards 0/1/2 landed = 3/12, tick "
              "self-start r535 law, queue self-continuing) + S6 chain all-green (bm-a "
              "heartbeat stale 63-65min -> lane_io stale-takeover legal derives on "
              "scorecard/paper_export/daily_scorecard/dashboard_status); W69 seat taken "
              "same-window by bm-c r360 per r565 law (honored, zero-cost); next = W70 burn "
              "watch 12/12 (engine self-continuing) + W70 finalize one-pass AFTER W68 bm-a "
              "+ W69 bm-c both land (chain order, r538 one-pass law, FAIL-CLOSED r307)")
st['last_round_at'] = now
st['last_round_ts'] = iso
st['ts'] = iso
st['updated'] = ("r568 bm-b: W67 finalize one-pass landed (chain head 511,948) + W70 freeze "
                 "delivered (fork face #3 disclosed) + ignition 3/12; W70 finalize watch "
                 "on W68+W69")
st['updated_at'] = iso
raw = json.dumps(st, ensure_ascii=False, indent=1)
open(sp, 'wb').write((raw + '\n').encode('utf-8'))
print('state.json written, round_no =', st['round_no'])

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-b.json')
hb = json.load(open(hp, encoding='utf-8'))
hb['last_seen'] = iso
hb['heartbeat_epoch_utc'] = int(now)          # smoke F7: JSON int type mandatory
hb['clock_read'] = iso                        # smoke F7: T-separator ISO 8601
hb['current_task'] = ("W70 burn in flight via engine tick (3/12 shards landed, "
                      "self-continuing); r568 W67 finalize one-pass landed (chain head "
                      "511,948) + W70 freeze delivered (fork face #3 disclosed); W70 "
                      "finalize watch on W68 bm-a + W69 bm-c")
hb['round_no'] = 568
hb['verdict'] = 'loaded_ok'
hb['cpu_util_pct'] = 4.3
hb['free_ram_gb'] = 6.5
hb['idle_ram_gb'] = 6.5
hb['ram_free_gb'] = 6.5
raw = json.dumps(hb, ensure_ascii=False, indent=1)
open(hp, 'wb').write((raw + '\n').encode('utf-8'))
chk = json.load(open(hp, encoding='utf-8'))
assert isinstance(chk['heartbeat_epoch_utc'], int), 'epoch must be JSON int (R170/R178)'
assert 'T' in chk['clock_read'], 'clock_read must be T-separated (R262)'
print('heartbeat written; epoch int + T-clock self-checked OK')

# --- round report append (EOL-probe, bytes-safe r530 law) ---
rp = os.path.join(REPO, 'logs', 'iteration-loop', 'round_reports.md')
b = open(rp, 'rb').read()
eol = '\r\n' if b.count(b'\r\n') * 2 > b.count(b'\n') else '\n'
line = (
 "2026-10-02T10:12+08:00 | r568 | dept:研究/工程 | watermark verdict=绿（py_low_board_clear"
 "=合法闲〔板全闭环+bandit 空+无可跑批·探测窗=W70 点火前静默段〕；supply_floor 旗=池饿引擎车道已知"
 "面·W70 冻结同窗即治）: 当前活=W70 烧录在飞（引擎 tick 自续·点火实证 shard-0/1/2 落盘=3/12·队列 9 "
 "自续）；最近实物=results/perpetual_faces/n1_w67_results.json（W67 FINALIZE one-pass @10:0x·ledger "
 "509,748→511,948 净链头·K=145,320==prereg 投影逐位·S5 4/4 PASS·se_mu 0.000642 收窄链）+ W70 FREEZE "
 "commit 34a0c2780（canon W70 行+N1_BANDS[70]+WAVE_CONFIGS[70]+prereg PERPETUAL_N1_W70_PREREG.md"
 "+selftest 全链 W2..W70 PASS+ADMIT 回执 results/_r568bmb_w70_band_gate.py·席位公示 "
 "MSG-20261002-1040-bmb）；下个里程碑=W70 12/12 烧毕→finalize（链序前置 W68 bm-a+W69 bm-c 双席落账"
 "·FAIL-CLOSED r307·窗≤48h 随双席进度）+W71 冻结（never-dry 常设·W71+ 投影 A 185_004..187_003/B "
 "51_201..51_400 双 CLEAN 已机证）。实况=W69 席被 bm-c r360 同窗再占（r565 律合法·本机转 W70）；W70 B "
 "侧=分叉面第三例（51_000 中位拒点·读法一越hit起窗 51_001..51_200 采此〔W26-A/W68-B 单点中位期例族〕"
 "vs 读法二连锁 51_101..51_300 披露不采〔W63-B=双点期〕·F-20261002-03 钉死行待裁定·W69 行「裁定前"
 "=机闸 derive+分叉披露强制」三面满足）；D-19 水位 MATCH-unchanged（4FD501…零动作）；orders 差集空 "
 "143/143；smoke 47/47；S6 36 腿全绿（假期 no-op 族诚实·dualrun streak 13/3 零漂移·WM rc0·audit "
 "supply_floor 如实·bm-a 心跳停摆 63-65min→三共享面 lane_io stale-takeover 合法接管 derive·"
 "REPORT/LIVE-2026-10-02 regen·token delta=0）；attrition CLEAN；推送窗撞机队高峰五拒→r341/r541 "
 "restore+rebase 净路+S6 再生面 20 件取墙钟新侧（bm-a r568 closeout 后跑=新侧）+pool_core_samples "
 "冲突区 union（704 基+716 origin 新+1 本机新=1421·r294 域限并集律）一次收敛；loop pin=2 no-op"
 "·watchdog S4U 重注册·claw 装·pre-commit 钳过。验证=commit 34a0c2780/40b0f7e9b/bfd33bbff 三连推 "
 "origin 送达+selftest W2..W70 全链 PASS+带闸 ADMIT+禁向闸 ADMIT。本地未达 origin commit 数=0（收尾 "
 "push 后复核）。")
open(rp, 'ab').write((eol + line).encode('utf-8'))
print('round report appended, EOL =', 'CRLF' if eol == '\r\n' else 'LF')
