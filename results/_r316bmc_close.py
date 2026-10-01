# _r316bmc_close.py -- r316 round close writes (state/heartbeat/report/CODELY/MSG) + json verify (r504 law)
import json, time, os, glob
from datetime import datetime, timezone, timedelta

REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
iso = now.strftime('%Y-%m-%dT%H:%M:%S+08:00')
epoch = int(time.time())

def read_raw(p): return open(p, 'rb').read()
def write_verified_json(p, obj):
    raw = read_raw(p)
    crlf = b'\r\n' in raw
    trail_nl = raw.endswith(b'\n')
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    if crlf: s = s.replace('\n', '\r\n')
    data = s.encode('utf-8')
    if trail_nl and not data.endswith(b'\n'): data += b'\r\n' if crlf else b'\n'
    if not trail_nl and data.endswith(b'\n'): data = data[:-2] if crlf else data[:-1]
    open(p, 'wb').write(data)
    json.loads(read_raw(p).decode('utf-8'))  # r504 same-round json.loads verification
    print('JSON_OK', p)

# --- 1) MSG to bm-b: LAT3-DEEP-X2 crash forensics ---
msg = """# MSG-20261001-1331-bmc-bmb -- LAT3-DEEP-X2 (P2) crash forensics + ignition preconditions

From: bm-c r316 round session
To: bm-b (owner of LOWAMP-P2-CELL-LAT3-DEEP-X2, claim 10831456f @ 2026-10-01 13:20:16)

1. bm-c's 12:59:15 X2 run (and 12:58:01 BASE run) both died in seconds with:
   FileNotFoundError: Money02\\data\\cache\\t18_deep_panel\\ohlcv\\159915.parquet
   (lowamp_p2.py cmd_run -> load_axis("deep") -> t22_virtual_timepoints._load_axis_prices L139)
2. Root cause class: DATA, not code. bm-c never built the t18 deep panel locally
   (scripts/t18_deep_axis.py build, idempotent, sha gate; docstring: "Caller must have run build locally").
   bm-c's Money02\\...\\t18_deep_panel\\ohlcv cache is EMPTY. Before your ignition verify locally:
   - scripts/t18_deep_axis.py build completed (manifest verdict PASS)
   - adjusted_view 19/19 hard gate (data/consolidation/adjusted_view)
   - per-member ohlcv parquets present for all manifest members not in adjusted_view
3. bm-c yield status: ZERO products / checkpoint rows from bm-c's X2 attempt (died pre-ignition);
   no partial-resume hazard on your side. bm-c crash-fuse holds the sig (23+ refusals) -- no double-burn from bm-c.
4. If your run crashes the same way: the fuse (O-0947) clears only on runner code change -- data fixes
   alone do NOT clear it. Legitimate code touch = probe axis-inventory leg (per-file existence check in
   cmd_probe): bm-c's probe.json PASSED while the axis price file was missing = in-runner gate blind spot.
5. Pool truth 13:26: P2 = 14/16 done. Your X2 + bm-a's NULLS are the only remaining. LAEDGE-LEGACY-X2
   double-burn adjudicated per r481 (envelope-only diff, payload byte-identical 1254/1254, origin side
   = your r505 products kept; bm-c claim/close landed as provenance alongside). No action needed on 5.
-- bm-c r316 (auto round session, unattended)
"""
msgp = os.path.join(REPO, 'fleet', 'inbox', 'MSG-20261001-1331-bmc-bmb.md')
open(msgp, 'w', encoding='utf-8', newline='\n').write(msg)
print('MSG_WRITTEN', msgp)

# --- 2) CODELY.md append (S4 memory entry, r316 pit law) ---
entry = "- [2026-10-01 13:3x r316 bm-c] 数据面缺件过闸坑（host_gates 登记态×probe 文件盲区×fuse 代码触面·LAT3-DEEP P2 双胞实弹）：bm-c 12:58/12:59 BASE+X2 双点火双秒死（FileNotFoundError：Money02\\t18_deep_panel\\ohlcv\\159915.parquet——本机从未跑 scripts\\t18_deep_axis.py build·deep 轴价格消费面全空）——池 host_gates dir_nonempty=登记时门（登记机面过）非认领时本机复检、probe.json 无 axis 价格文件在场清点腿→数据面缺件批合法点火；O-0947 fuse=code_sha 变更才清→数据根因批修数据不清闸、合法代码触=probe 文件清点腿（堵闸类正解）。How to apply：跨机池登记带本机数据前置的批，认领机点火前必本机复验前置（登记态≠本机态）；probe 腿必含 axis 消费面文件清点；数据根因 fuse 滞留=如实留闸+MSG 通知接管机，勿为清闸盲改 runner。"
cp = os.path.join(REPO, 'CODELY.md')
raw = read_raw(cp); crlf = b'\r\n' in raw
nl = '\r\n' if crlf else '\n'
txt = raw.decode('utf-8')
if entry[:60] not in txt:  # dedupe guard
    if not txt.endswith(('\n', '\r')): txt += nl
    txt += nl + entry + nl
    open(cp, 'w', encoding='utf-8', newline='').write(txt)
    print('CODELY_APPENDED len', len(txt.encode('utf-8')))
else:
    print('CODELY_DEDUPE_SKIP')
assert entry[:60] in open(cp, encoding='utf-8').read()
print('CODELY_SIZE', os.path.getsize(cp))

# --- 3) state-bm-c.json ---
sp = os.path.join(REPO, 'state-bm-c.json')
st = json.loads(read_raw(sp).decode('utf-8'))
st['round_no'] = 316
st['last_round_at'] = iso; st['last_round_ts'] = iso; st['updated'] = iso
st['cpu_pct'] = 19.0; st['idle_ram_gb'] = 5.2; st['gpu_free_vram_mib'] = 12382
st['verify'] = ("S1 smoke 47/47; S6 37 legs rc0 (1 gated skip); D-19 753F99E8 MATCH-unchanged; "
    "orders double-scan EMPTY; attrition CLEAN; dualrun ZERO-DRIFT streak 1/3; S0 delivery pushed "
    "8f1a2fb55 (AHEAD=0 BEHIND=0 at verify); X2 AA adjudicated r481 exact 1254/1254 take-origin; "
    "LAT3-DEEP-X2 crash root-caused = data gap (t18 deep panel absent on bm-c), forensics MSG-1331 to bm-b, fuse held + yielded")
st['did'] = ("r316: S0 3-commit delivery (LAEDGE-LEGACY-BASE products + W8 finalize n1_w8_results.json + "
    "MSG-1310 landed origin 8f1a2fb55) + X2 AA adjudication (r481 exact, origin side kept, resolver "
    "_r316bmc_s0_resolver.py) + LAT3-DEEP-X2 crash forensics MSG to bm-b (t18 deep panel data gap, not code) + S6 37 legs rc0")
st['current_task'] = ("r317 first item: CODELY.md 51.5KB>50KB hot-cold recompile (zero-loss verify); "
    "W9 supply mint (floor breach 2<3 lit); LAT3-DEEP-X2 bm-b in-flight watch; T-134 s2 5th conversion")
st['next'] = ("(r317-first) CODELY recompile; (a) W9 mint per law sec.4 tail + r307 disjoint machine-gate; "
    "(b) X2/NULLS fleet watch -> T-140 P2 finalize at 16/16; (c) T-134 s2 5th candidate; "
    "(d) bm-c t18 deep panel data-gap repair path (Money02 untouched per ironclad -> TRANSFER.md lane)")
st['heartbeat_epoch_utc'] = epoch
st['clock_read'] = iso
st['note'] = ("r316 clean single-session round; X2 double-burn adjudicated per r481 (bm-b re-burn legal per "
    "r297 claim-invisibility -- r315 ended with unpushed claim commits, delivery self-proof must run after "
    "the round's LAST push); LAT3-DEEP-X2 legally lost to bm-b (bm-c deep panel absent)")
st['last_ts'] = iso
st['last_round'] = ("2026-10-01 r316 bm-c: S0 delivery landed (BASE products + W8 finalize on origin) + "
    "X2 r481 adjudication + crash forensics MSG to bm-b + S6 37 legs rc0")
write_verified_json(sp, st)

# --- 4) heartbeat fleet/machines/bm-c.json ---
hp = os.path.join(REPO, 'fleet', 'machines', 'bm-c.json')
hb = json.loads(read_raw(hp).decode('utf-8'))
hb['round_no'] = 316
hb['updated_at'] = iso; hb['last_seen'] = iso; hb['last_seen_at'] = iso
hb['cpu_pct'] = 19.0; hb['cpu_util_pct'] = 19.0; hb['cpu_idle_pct'] = 81.0
hb['idle_ram_gb'] = 5.2; hb['free_ram_gb'] = 5.2; hb['ram_free_gb'] = 5.2
hb['gpu_free_vram_mb'] = 12382; hb['gpu_idle_vram_mib'] = 12382; hb['gpu_free_vram_mib'] = 12382
hb['prod_lanes'] = ("r316: S0 3-commit delivery landed (LAEDGE-LEGACY-BASE products + W8 finalize on origin "
    "8f1a2fb55) + X2 AA r481 adjudication + LAT3-DEEP-X2 crash forensics to bm-b")
hb['verdict'] = ("WM py_low_with_work_cands 13:26 = legal idle whitelist (only open ticket = T-131 GM-gate "
    "standing; pool ready 2 both other-machine in-flight X2/NULLS, unclaimed 0; no local burnable; "
    "supply_floor breach 2<3 -> W9 mint next round); S0 delivery N=0 verified")
hb['current_task'] = ("r317 first: CODELY >50KB recompile; W9 supply mint watch; X2 bm-b in-flight + NULLS bm-a "
    "watch -> T-140 P2 finalize at 16/16; T-134 s2 5th conversion")
hb['activity_now'] = ("S0 delivery landed (X2 AA adjudicated + BASE products + W8 finalize on origin); "
    "LAT3-DEEP-X2 crash forensics sent to bm-b (t18 deep panel data gap, not code)")
hb['latest_artifact'] = ("origin 8f1a2fb55: results/lowamp_p2/cells_LA-EDGE_legacy_base.jsonl + cont_LA-EDGE_legacy_base.json "
    "+ results/perpetual_faces/n1_w8_results.json (13:24)")
hb['next_milestone'] = ("P2 16/16 (X2 bm-b + NULLS bm-a in-flight) -> T-140 P2 finalize + W9 supply mint; window <=48h")
hb['heartbeat_epoch_utc'] = epoch
hb['clock_read'] = iso
hb['health'] = 'ok'
assert isinstance(hb['heartbeat_epoch_utc'], int)
write_verified_json(hp, hb)

# --- 5) round report append ---
rp = os.path.join(REPO, 'round_reports-bm-c.md')
raw = read_raw(rp); crlf = b'\r\n' in raw
nl = '\r\n' if crlf else '\n'
line = (iso + "｜r316｜dept:工程（S0 整合送达+崩溃取证）+dept:研究（P2 收敛推进）｜watermark verdict="
    "py_low_with_work_cands（合法 idle 白名单：板 open=1=T-131 GM 署名门 standing·bandit 0·池 ready 2 全员他机在飞"
    "（X2 bm-b 13:20:16+NULLS bm-a 13:09:43）·unclaimed 0·bars_present false·local_batch_running false——本机无合法可烧批）"
    "｜本轮主产出=①S0 三 commit 送达落地（CAS cherry-pick 净路：8d2b7235c+02c7ea63c+8f1a2fb55→push 10831456f..8f1a2fb55·"
    "AHEAD=0 BEHIND=0 终验·LAEDGE-LEGACY-BASE 双产物+W8 finalize n1_w8_results.json+MSG-1310 落 origin）"
    "②X2 AA 双烧裁定（r481 律：1254/1254 payload 逐位恒等·仅 machine/elapsed/workers 信封差·取 origin 侧=bm-b r505 基·"
    "resolver _r316bmc_s0_resolver.py 留档·r297 认领不可见律再犯面：r315 以未推 claim 收轮=送证面，送达自证必须在轮末最后 "
    "push 之后）③LAT3-DEEP-X2 崩溃取证+MSG-1331 送 bm-b（根因=本机 Money02 t18_deep_panel 全缺·从未跑 t18_deep_axis.py "
    "build·数据面非代码面·host_gates=登记态非认领态+probe 无文件清点腿=闸类盲区·fuse 23+ refusals 留闸让路·bm-b 13:20:16 "
    "合法接管）④S6 37 腿 rc0（dualrun ZERO-DRIFT streak 1/3·REGIME ORANGE〔hs300<MA200 #10+breadth 0.79〕·clock "
    "ORANGE_COOL sleeves=4·scorecard 46.1s·daily_report 5 faces·车道守卫 12 腿诚实 no-op）｜验证证据=S1 smoke 47/47；"
    "attrition CLEAN（4 ledgers·2 healed 注记）；precommit claw IDENTICAL；schtasks 双任务在场（IterationLoop 13:35+"
    "Watchdog 13:50·pin :X5 intact·silent query 零窗）；orders 轮首+S7 双扫差集 EMPTY；D-19 753F99E8 MATCH-unchanged"
    "（raw-blob python 法）；inbox 无本机件（MSG-1310=本机致 bm-a 在途）；CODELY.md 51,554B>50KB 水线亮（bm-b r504 刚 "
    "consolidation·残余=在役法典面·整编=r317 首件如实登记勿等周轮）｜实况三行（CEO 过程可见面）：当前活=S0 送达+X2 裁定+"
    "崩溃取证毕｜最近实物=origin 8f1a2fb55（LAEDGE-LEGACY-BASE cells+cont+W8 finalize n1_w8_results.json·13:24）｜下个里程碑="
    "P2 16/16（余 X2 bm-b 烧制中+NULLS bm-a 烧制中）→T-140 P2 finalize 窗≤48h｜产品分=2（origin 实物交付）+1（取证 MSG+"
    "簿记实改）｜本地未达 origin commit 数=0（收尾 push 后 fetch+rev-list 自证·若被拒走 fallback 分支照实改写此行）｜next: "
    "(r317 首件) CODELY.md 热冷整编（行级零丢失校验·D-20260924-01 范式）；(a) W9 供给 mint（supply_floor breach 2<3 亮·"
    "r307 disjoint 机验先行·法典 §4 尾律）；(b) LAT3-DEEP-X2 bm-b 烧制跟踪+本机 t18 deep panel 数据面修复评估（Money02 不动"
    "铁律下走 TRANSFER.md 车道）；(c) T-134 s2 第五候选证据序转换")
with open(rp, 'a', encoding='utf-8', newline='') as f:
    f.write(nl + line + nl)
print('REPORT_APPENDED')

# --- 6) open ticket locate (watermark said T-2026-09-30-131 open; verify real filename) ---
for p in glob.glob(os.path.join(REPO, 'fleet', 'tasks', '*.json')):
    try:
        t = json.loads(read_raw(p).decode('utf-8'))
        if str(t.get('status')) == 'open':
            print('OPEN_TICKET', os.path.basename(p), t.get('title', '')[:60])
    except Exception as e:
        print('TICKET_READ_ERR', os.path.basename(p), str(e)[:80])
print('CLOSE_WRITES_DONE epoch_int=%d type=%s' % (epoch, type(epoch).__name__))
