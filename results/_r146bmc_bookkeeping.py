# r146 bm-c bookkeeping: round-report append + state + heartbeat + orders 2nd scan
import io, json, os, time, datetime, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = datetime.datetime.now().astimezone()
ISO = NOW.isoformat(timespec="seconds")          # T-separated, +08:00
EPOCH = int(time.time())

def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()

def write_bytes(p, b):
    with open(p, "wb") as f:
        f.write(b)

def strip_bom(b):
    return (b[:3] == b"\xef\xbb\xbf", b[3:] if b[:3] == b"\xef\xbb\xbf" else b)

# ---------- 1. round report append (append-only, head bytes untouched) ----------
LINE = (
    NOW.isoformat(timespec="seconds")
    + "（钟读实测）｜R146｜bm-c (dept:工程 J12-线 W2-显示面 + 舰队维护链·周一盘前)｜WM verdict: green "
    "(red=false 07:40:01 lane healthy; probe 07:49:10 py_low_board_clear legal-idle Monday pre-market "
    "bars_present=false cutoff 09-24 n=3 span 25min avg py 0.1%; board 0 open + job_list 0 + pool 91 "
    "[83 done + 1 ready=V2-P1 lane=bm-b + 7 waiting 全 bm-b declare/RAM/cache 门 frozen sec.9.1 串行·census W2B 燃中 "
    "ETA ~10:30]=zero bm-c-claimable 七轮共识; audit v2.3 07:49:03 CLEAN flags=[] py 0.0% pool_ready=1 "
    "load_state=pool-supply-gap disclosed)｜did: S0-1 bm-c 锚定→S0 pull --rebase Already-up-to-date 零 UU 净树→"
    "S0.5 orders 99/99 差集零未回执（S7 双扫复验同）+decisions.md mtime 09-27 16:54 零 09-28 新行零动作"
    "（BigMoney 涉例 D-04/D-09 均已闭口·委员会 C-01 非本司席位）→S1 smoke 25/25→S2 双板零开"
    "（96 票 0 open·T-96 claimed bm-b 深进度 r365 禁撞·job_list 0）→S3 J12-线小闭环（r122 自有块延续·零重建）："
    "build_status _trial_labor_state wave-2 面扩展=TRIAL_LABOR_W2 漏斗诚实行（batch 3124=去重 2924+null 200→"
    "幸存 404·null p95 线 0.5116·ledger_total 297428·evidence_cutoff 09-22；judge_prep n_judge_cells=404="
    "judge_state.json prep 面如实·判决未跑零宣称；docstring 补 wave-2 溯源）——town.html wrows 消费面 r122 已泛化"
    "跨波零改动实读确认→探针 _trial_labor_state() 三 waves JSON 实读（W2 行数字与 w2_screen.json/w2_candidates.json "
    "恒等）+guard 跑 python -m monitor.build_status=lane_io 诚实 skip（bm-a 心跳 19min fresh·bm-a 下轮 derive 自动吃到 W2 行）"
    "→S6 23 腿 rc=0 周一盘前 no-op 家族零掩盖（audit CLEAN/probe py_low_board_clear/daily 0-new cutoff 09-24/"
    "regime ORANGE shadow hs300<MA200 #10+breadth 0.77/clock CALL-2026-09-24 ORANGE_COOL sleeves=4 activated=0 幂等/"
    "lhb <30min 节流/11 外车道守卫诚实 no-op=heat-futures-repo-options-moneyflow-sina_mf-astock-sigexp-ths-ah/"
    "fund_premium pre-15:30 no-op 本机车道首拍 ARMED/fundamental 22.4h fresh-skip/b_layer regen gates pass/"
    "paper 族 bars_present=false 合法跳/live-family x4 SKIP per trigger law/daily_scorecard derive=lane_io guard "
    "stale-takeover 放行（bm-a 心跳 21min 过阈=D-03 设计态·faces 6 员如实）/daily_report REPORT-2026-09-28 faces=4 "
    "token=1/token_meter delta=0 L2 0 today）→S7 自愈三查全在位（IterationLoop Running pin=5 no-op 实证/"
    "Watchdog Ready 08:10/Claw CR-normalized MATCH）｜evidence: smoke 25/25 复跑绿（build_status.py 编辑后）+"
    "_trial_labor_state probe 3-waves JSON（MASS_W1 975/166+TRIAL_W1 858/149+TRIAL_W2 3124/404+池面 W2-GENERATE done·"
    "W2-SCREEN done·W2-JUDGE waiting 实读）+S6 23 腿全 rc=0+state round_no=146+heartbeat epoch-int 写后自证｜"
    "next: ①15:30 fund_premium 首拍实弹（本机车道·S6 链自动发射·exit 2 即原样上报）②census W2B finalize watch"
    "（bm-b ETA ~10:30）→RAM 释放→W2-JUDGE flip（bm-b 域·twin-cache 物理门）→V2-P1 复跑（fuse 通道已解堵）→"
    "T-95 s3 verdict+s4 CEO 报告（negative also per O-2255·48h 钟 09-29 22:45）③T-19 G6 live-run proof=首新 bar 轮"
    "（15:30 后 bmc）④CEO 48h 呈报钟 09-29 22:45（bmb）⑤council C-01 窗 09-29 12:00·下轮 5x=bm-c r150 [via bm-c]\n"
)
rp_path = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp_path, "ab") as f:
    f.write(LINE.encode("utf-8"))
print("round-report appended ok")

# ---------- 2. state file ----------
st_path = os.path.join(ROOT, "state-bm-c.json")
b = read_bytes(st_path)
had_bom, body = strip_bom(b)
st = json.loads(body.decode("utf-8"))
st["round_no"] = 146
st["updated"] = ISO
st["updated_at"] = NOW.strftime("%Y-%m-%d %H:%M")
st["last_round_ts"] = ISO
st["note"] = ("r146: J12-line W2 funnel face wired into build_status _trial_labor_state "
              "(TRIAL_LABOR_W2 3124=2924+200nulls -> 404 survivors honest, judge-prep 404 cells "
              "prep-face only, ledger 297428; town consumer already wave-generic r122) + probe 3-waves "
              "readback + S6 23 legs rc=0 Monday pre-market no-op family + fund_premium 15:30 first-fire "
              "armed (bm-c lane) + orders 99/99 dual-scan + zero bm-c-claimable 7-round consensus "
              "(census W2B burning bm-b ETA ~10:30)")
out = json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8")
write_bytes(st_path, (b"\xef\xbb\xbf" if had_bom else b"") + out)

# ---------- 3. heartbeat ----------
hb_path = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
b = read_bytes(hb_path)
had_bom, body = strip_bom(b)
hb = json.loads(body.decode("utf-8"))
try:
    import psutil
    cpu = round(psutil.cpu_percent(interval=1), 1)
    vm = psutil.virtual_memory()
    free_ram = round(vm.available / (1024 ** 3), 1)
except Exception:
    cpu, free_ram = hb.get("cpu_util_pct"), hb.get("free_ram_gb")
hb["last_seen"] = ISO
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = ISO
hb["round_no"] = 146
hb["cpu_util_pct"] = cpu
hb["cpu_pct"] = cpu
hb["free_ram_gb"] = free_ram
hb["idle_ram_gb"] = free_ram
hb["current_task"] = ("r146 done: J12-line W2 funnel face in build_status trial_labor block "
                      "(3124->404 survivors honest, judge-prep 404 cells prep-face); S6 23 legs green; "
                      "fund_premium 15:30 first-fire armed lane bm-c")
hb["verdict"] = ("py_low_board_clear legal-idle (pool 1 ready=V2-P1 lane bm-b post-census; 7 waiting all "
                 "bm-b RAM/cache-gated serial; census W2B burning ETA ~10:30; zero bm-c-claimable 7-round consensus)")
hb["updated_at"] = NOW.strftime("%Y-%m-%d %H:%M")
hb["updated"] = ISO
hb["last_round_ts"] = ISO
out = json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8")
write_bytes(hb_path, (b"\xef\xbb\xbf" if had_bom else b"") + out)

# ---------- 4. self-verify ----------
chk = json.loads(read_bytes(hb_path).decode("utf-8-sig"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"] and chk["clock_read"].endswith("+08:00"), "clock not T-format"
chk2 = json.loads(read_bytes(st_path).decode("utf-8-sig"))
assert chk2["round_no"] == 146
print("heartbeat epoch int ok:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"], "| state round:", chk2["round_no"])

# ---------- 5. orders S7 second scan ----------
ack = set(chk.get("orders_ack") or [])
files = set(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "fleet", "orders", "O-*.md")))
unacked = sorted(files - ack)
print("orders files:", len(files), "unacked:", unacked if unacked else "NONE")
