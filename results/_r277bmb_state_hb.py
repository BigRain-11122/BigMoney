# -*- coding: utf-8 -*-
# r277 bm-b S7 wrap: state.json round bump + heartbeat + round report line + inbox move.
# Format-mirror laws: R255/R257 five-face probe (BOM/EOL/indent/ascii/trailing-newline).
# Timestamp law R271: all clock values from ONE now() instance. Epoch law R170/R178: JSON int.
import json, time, datetime, subprocess, os, shutil

now = datetime.datetime.now().astimezone()
clock_read = now.isoformat(timespec='seconds')   # T-separator law (R262)
epoch = int(time.time())
hhmm = now.strftime('%H:%M')

# ---------- 1) state.json (bm-b canon path) ----------
sp = 'logs/iteration-loop/state.json'
raw = open(sp, 'rb').read()
st_bom = raw.startswith(b'\xef\xbb\xbf')
st_crlf = b'\r\n' in raw
st_nl = raw.endswith(b'\n')
state = {
 "round_no": 277,
 "did": "r277: S0 stash-pop autofill_state 1-UU per skill recipe (launches union 49 identical cap50 asc; last_tick take-new local 22:50 face; resolver _r277bmb_resolve.py; stash dropped post-merge) + pull ff 855ad9b1 + orders 85/85 dual-scan empty + decisions.md absent-on-bm-b zero-action + smoke 25/25 + board 0 open (T-84=bm-a lane per O-2229) + S3 anti-dup honored (r276 verified town mandate alignment, no rebuild): delta = NEW v6-KPI data face daily-battle-report onboard (build_status _daily_report_state block + town.html office panel report row + token formatted row + mandate + footer note) + org_chart L116 stale 'to-build' three-building annotation corrected (ten buildings all onboard, r277 note) + S6 24 legs rc=0 weekend faces (no new bar -> paper family skipped)",
 "verdict": "green",
 "next": "09-28 Monday window (T-76 channels + new-bar chain + MF_IC panel self-heal bm-a lane); 10-01 month-first trio + REGIME_GUARD v3 date gate (governance-audit slot already discharged, no double-run); every round S0 first-probe root: new root present -> five-receipt assembly; absent -> journal tail + executor lock liveness (precheck waits on 3 Tuanjie editors, do NOT double-arm); window till 09-29 12:00",
 "last_round_ts": clock_read,
 "last_result": "ok",
 "current_task": "r277 done: town/panel v6 KPI face (daily battle report onboard) + org annotation sync; next: 09-28 Monday new-bar window + 10-01 month-first trio",
 "last_tick": hhmm,
 "updated_at": clock_read,
}
txt = json.dumps(state, ensure_ascii=False, indent=1)
data = txt.encode('utf-8')
if st_crlf:
    data = data.replace(b'\n', b'\r\n')
if st_nl and not data.endswith(b'\r\n' if st_crlf else b'\n'):
    data += b'\r\n' if st_crlf else b'\n'
open(sp, 'wb').write(data)

# ---------- 2) heartbeat fleet/machines/bm-b.json ----------
free_gb = None
try:
    out = subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         '[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,1)'],
        text=True)
    free_gb = float(out.strip())
except Exception:
    free_gb = None
gpu_free = None
try:
    out = subprocess.check_output(
        ['powershell', '-NoProfile', '-Command',
         "nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits"],
        text=True)
    gpu_free = int(out.strip().splitlines()[0])
except Exception:
    gpu_free = None

hp = 'fleet/machines/bm-b.json'
raw = open(hp, 'rb').read()
hb_bom = raw.startswith(b'\xef\xbb\xbf')
hb_crlf = b'\r\n' in raw
hb_nl = raw.endswith(b'\n')
hb = json.loads(raw.decode('utf-8-sig'))
hb.update({
    "last_seen": clock_read,
    "current_task": "r277 done: daily-battle-report panel face (v6 KPI) + org_chart viz-note sync + S6 green; migration executor v2.2 precheck-waiting (editor-gated)",
    "cores": 16,
    "cpu_cores": 16,
    "free_ram_gb": free_gb,
    "idle_ram_gb": free_gb,
    "gpu_free_vram_mb": gpu_free,
    "gpu_idle_vram_mb": gpu_free,
    "gpu_free_vram_gb": round(gpu_free / 1024, 1) if gpu_free else None,
    "gpu_idle_vram_gb": round(gpu_free / 1024, 1) if gpu_free else None,
    "round_no": 277,
    "verdict": "loaded_ok",
    "heartbeat_epoch_utc": epoch,
    "clock_read": clock_read,
})
txt = json.dumps(hb, ensure_ascii=False, indent=1)
data = txt.encode('utf-8')
if hb_crlf:
    data = data.replace(b'\n', b'\r\n')
if hb_nl and not data.endswith(b'\r\n' if hb_crlf else b'\n'):
    data += b'\r\n' if hb_crlf else b'\n'
open(hp, 'wb').write(data)

# ---------- 3) round report line (bm-b canon file) ----------
rp = 'logs/iteration-loop/round_reports.md'
raw = open(rp, 'rb').read()
rp_crlf = b'\r\n' in raw
eol = '\r\n' if rp_crlf else '\n'
if raw and not raw.endswith(b'\r\n' if rp_crlf else b'\n'):
    with open(rp, 'ab') as f:
        f.write(b'\r\n' if rp_crlf else b'\n')
line = (
 "2026-09-26T" + now.strftime('%H:%M:%S') + "+08:00 | r277 (bm-b) | dept:工程 | "
 "WM-VERDICT: GREEN py_low_board_clear (probe 22:54 py 1.1% window n=2; board 0 open / bandit 0 open / pool 49/49 done; "
 "next_pick=moneyflow IC reference batch parked=panel source-blocked bm-a lane; red=false; audit FLAG pool_starvation=weekend supply-gap legal idle per O-1137) | "
 "did: S0 stash-pop autofill_state 1-UU 按技能 mixed-dict 配方解（launches union 49 双侧恒等 cap50 asc 写回序 r245 律；last_tick 内部 ts 比较取新=本机 22:50>origin 22:40 整 dict；resolver _r277bmb_resolve.py parse-verify 零丢失后 stash drop）+pull fast-forward 855ad9b1；"
 "S0.5 orders 85/85 双扫零差集（轮首+S7 收尾）+decisions.md 本机缺席=零动作（r104/r107 先例）+P-32 零新行；S1 smoke 25/25；S2 board 0 open（T-84 四片 bm-a lane per O-2229+inbox 回执确认）；"
 "S3 反重复受尊（r276 已判 town mandate 对齐勿重建→本轮=纯增量新面非重建）：总经办 v6 KPI 数据面=每日战报上盘（monitor/build_status.py 新 _daily_report_state 块：REPORT-*.json 孪生 report_date/age/traders/equity/token_line 10 字段+wiring；town.html 总经办面板战报行+token 格式化行+mandate 补「每日战报」+footer 注记）+org_chart.md §AI 赋能原则5 过期「待建」三楼注记勘正（十楼全上盘·r277 勘注·含 v5 新楼）；"
 "验证=node --check JS OK+office 面板真数据 runtime check（2026-09-26 0d·6 员·¥5,996,645·18 持仓·token state 1995/report 460k est +1501）+build_status 再生 rc=0；"
 "S6 24 腿 rc=0 周末面（daily 0 行 cutoff 09-24 无新 bar→paper 族跳过/regime ORANGE d2 shadow/clock ORANGE_COOL 4/0 幂等/lhb 30min 节流/heat 周末/futures cutoff 覆盖/bm-a 车道 options+mf+sina_mf+ths+ah 与 bm-c fp 诚实 no-op/fundamental 0.6h 新鲜跳/blf 全门过/dsc 6 员/daily_report faces=4 token=1/token delta=-49 byte/3.5 粗估）；"
 "迁移面不变：executor v2.2 precheck 等待 3 Tuanjie 编辑器进程（journal 22:49 仍在推进·旧根唯一真身照跑·窗至 09-29 12:00·勿双 arm）；"
 "inbox 1 件处理：MSG-2245-bm-a T-84 s1 三证收讫回执（双机实证成立·四片仍 bm-a lane·CEO 三径裁决挂起）→移 processed/ 零动作面 | "
 "evidence: S6 逐腿 exit code in transcript + node --check/runtime check 输出 + resolver VERIFIED 零丢失 + orders diff 双扫脚本输出 + smoke 25/25 | "
 "next: 09-28 周一窗（T-76 channels run-6/10/4+新 bar 链+MF_IC 面板自愈后 bm-a 车道）；10-01 月首轮三件套+REGIME_GUARD v3 日期门（治理审视槽位已 discharge 勿双跑）；每轮 S0 首探新根（在位→五回执组装；缺席→journal 尾读+锁活性核勿双 arm）"
)
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(line + eol)

# ---------- 4) inbox: process bm-a receipt (zero action face) ----------
src = 'fleet/inbox/MSG-20260926-2245-bm-a-t84-s1-witness-receipt.md'
dst = 'fleet/inbox/processed/MSG-20260926-2245-bm-a-t84-s1-witness-receipt.md'
if os.path.exists(src):
    shutil.move(src, dst)
    print('inbox: receipt moved to processed/')

# ---------- self-verify (smoke F7 faces + parse) ----------
hb2 = json.load(open(hp, encoding='utf-8-sig'))
assert isinstance(hb2['heartbeat_epoch_utc'], int), 'epoch not int'
assert 'T' in hb2['clock_read'] and '+' in hb2['clock_read'], 'clock_read not T-sep ISO'
st2 = json.load(open(sp, encoding='utf-8-sig'))
assert st2['round_no'] == 277, 'round_no not bumped'
assert abs(int(time.time()) - hb2['heartbeat_epoch_utc']) < 120, 'epoch in future/past'
print('state 277 + heartbeat written; epoch int OK; clock', hb2['clock_read'],
      '| free_ram_gb', free_gb, '| gpu_free_mb', gpu_free)
