# r517 bm-b closeout writes: round-report line + CODELY lesson + state/heartbeat
# (byte-format-preserving JSON rewrite: probe indent/EOL first, r289/r500 law)
import json, os, time, subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# --- live machine faces ------------------------------------------------------
n19 = 0
p = os.path.join(ROOT, "results", "p2cal_ext", "n1_w19")
if os.path.isdir(p):
    n19 = len([f for f in os.listdir(p) if f.endswith(".json")])
free_ram = None
try:
    import psutil
    free_ram = round(psutil.virtual_memory().available / 1e9, 1)
except Exception:
    pass
gpu_free = None
try:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"], timeout=10)
    gpu_free = round(int(out.decode().strip().splitlines()[0]) / 1024.0, 1)
except Exception:
    pass

def load_json(path):
    with open(path, "rb") as f:
        raw = f.read()
    obj = json.loads(raw.decode("utf-8"))
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n") - crlf
    indent = 1
    for line in raw.decode("utf-8").splitlines():
        if line.startswith(" ") and line.strip():
            indent = len(line) - len(line.lstrip(" "))
            break
    return obj, ("crlf" if crlf >= lf else "lf"), indent, raw.endswith(b"\n")

def save_json(path, obj, eol, indent, trailing):
    text = json.dumps(obj, ensure_ascii=False, indent=indent)
    if eol == "crlf":
        text = text.replace("\n", "\r\n")
    if trailing:
        text += ("\r\n" if eol == "crlf" else "\n")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

# --- 1) state.json ------------------------------------------------------------
sp = os.path.join(ROOT, "state.json")
st, eol, ind, trail = load_json(sp)
st["round_no"] = 517
st["note"] = ("r517: N1-W19 engine wave FROZEN five-face full chain (7th engine "
              "wave, bm-b 5th own wave, sovereignty rotation F-20261001-01 slot "
              "W19=bm-b via 16+3; A=76_001..78_000 arithmetic continuation clean, "
              "B=38_100..38_299 FORCED skip-over past lfc actual 30_000..30_099 + "
              "SEED_REGISTRY point 30_000 -- ADMIT receipt "
              "results/_r517bmb_w19_band_gate.py, W16 row W17+ WARNING honored, "
              "NOT a re-pick R250; law sec.4 row + N1_BANDS/WAVE_CONFIGS mirrors + "
              "per-wave prereg + selftest W19 materializer legs all green + "
              "banned_direction_gate ADMIT; wave numbers 17/18 unfrozen -- gap "
              "notes, r516 derive law). Engine ignited W19 12-shard burn same "
              "round (queue picked up <=1 tick, products growing; finalize next "
              "round). S6 37 legs rc0 (dualrun ZERO-DRIFT streak 6/3).")
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["ts"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
save_json(sp, st, eol, ind, trail)
chk = json.load(open(sp, encoding="utf-8"))
assert chk["round_no"] == 517

# --- 2) heartbeat fleet/machines/bm-b.json -----------------------------------
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
hb, eol, ind, trail = load_json(hp)
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["current_task"] = ("W19 12-shard engine burn in flight (" + str(n19) +
                      "/12 on disk @close); next: W19 finalize + ledger "
                      "(+2,200 -> 401,948) + prereg S5/S7/S8 backfill; "
                      "W17=bm-c / W18=bm-a sovereignty watch (bands continue "
                      "from W19 table tail)")
if free_ram is not None:
    hb["free_ram_gb"] = free_ram
    hb["idle_ram_gb"] = free_ram
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
    hb["gpu_idle_vram_gb"] = gpu_free
    hb["gpu_idle_vram_mb"] = int(gpu_free * 1024)
hb["round_no"] = 517
hb["verdict"] = ("W19 frozen+ignited same round (never-dry standing step = "
                 "supply root-fix for the idle-family flags; T-141 acceptance "
                 "face in flight); fresh probe cands EMPTY; py_low_board_clear "
                 "(r528 claim-lock fix consumed -- no claimed-ticket false red)")
save_json(hp, hb, eol, ind, trail)
chk2 = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("state.json round_no=517 OK | heartbeat epoch(int)=%d clock=%s"
      % (chk2["heartbeat_epoch_utc"], chk2["clock_read"]))
print("live faces: w19_shards=%d free_ram=%s gpu_free=%s" % (n19, free_ram, gpu_free))

# --- 3) round report line -----------------------------------------------------
rr = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
with open(rr, "rb") as f:
    raw = f.read()
eol_rn = "\r\n" if raw.count(b"\r\n") * 2 > raw.count(b"\n") else "\n"
need_nl = not raw.endswith(b"\n")
line = (
    now_iso + " | r517 bm-b | dept:研究/工程 | "
    "[watermark verdict: GREEN（watermark_red red=false·lane healthy·18:23 probe=py_low_board_clear"
    "＝板空合法 idle〔open_tickets 0——r528 claim-lock 修复已消费·claimed 票假红归零〕·bars_present·daily_panel true；"
    "audit 旗 idle_with_work/pool_starvation/supply_floor＝standing r513-family 轮换空窗供给面——本轮 W19 冻结即根治步："
    "引擎 queue 0→W19 12 分片入队点火）] | "
    "本轮主产出（实物）：(1) **N1-W19 引擎波冻结五面全链落地**（本机第五枚自有波·第七枚引擎波·"
    "主权轮值律 F-20261001-01 槽位 W19=bm-b〔16+3 模 3 续行·fetch-first 复核 ORIGIN_AHEAD=0·表尾无 17/18/19 行=r483 让票律过〕；"
    "never-dry 常设步+T-141 验收面 3 工作日 py≥70% 在测的反空转步）：带位机闸 **ADMIT**"
    "（results/_r517bmb_w19_band_gate.py——A=76_001..78_000 算术续带免跳〔leg1 CLEAN+leg2 首净窗==算术位〕；"
    "**B=38_100..38_299 被迫跳位**〔+200 算术位 29_900..30_099 撞 lfc 实际流 30_000..30_099+SEED_REGISTRY lfc_p1_screen 点 30_000"
    "——leg1b 必红机证=W16 行 W17+ 警示窗兑现·首自由 200 窗机闸定·非重挑 R250〕）；"
    "五面=N1_BANDS[19]+WAVE_CONFIGS[19] 镜像行+法典 §4 W19 展行（波号 17/18 间隙注记·r516 波集 derive 律承接）"
    "+research/PERPETUAL_N1_W19_PREREG.md（累计池预期 K=35,320·§5 四预测锚=W16 finalize 实测·出场轴③声明）"
    "+selftest W19 materializer 腿全绿（含 prior-wave set derive 断言〔2..14,16·无 15/17/18〕）；"
    "banned_direction_gate ADMIT（no banned direction claimed）·compile 0；"
    "(2) **引擎点火实证**（产物增长面 r325 律）：W19 入队 queue_depth 10·active n1w19-1of12 pid=51856·"
    "shard 逐片落盘（收轮时 " + str(n19) + "/12 在途）·台账批量落账待烧毕；"
    "(3) S6 37 腿全 rc0（dualrun ZERO-DRIFT streak 6/3·flip 门数据继续累积 GM 面；节假日诚实 no-op 面；"
    "REPORT-2026-10-01+LIVE-2026-10-01 当日再生；t35_open_fill_verify/daily_scorecard stale-takeover derive"
    "〔bm-a 心跳龄 23-24min>r378 20min 阈=合法接管〕） | "
    "验证：S1 smoke 47/47；n1 selftest PASS（W19 腿含）；attrition scan CLEAN（4 台账·bm-a 历史缩行 healed 注记照录）；"
    "三任务健康（Loop pin=2 no-op next 18:32/Watchdog 就绪/pre-commit claw OK）；"
    "orders 轮首+收尾双扫 EMPTY（139 令全回执）；D-19 决策水位 753F99E8 MATCH-unchanged"
    "（python raw-bytes·temp partial clone·大小写归一）；engine status rc0（W19 烧录中） | "
    "坑例（已入 CODELY 一条）：bm-b 引擎 per-tick 短命架构注记（新波登记无需重启·r325 驻留冻结面不适用本机实例） | "
    "inbox：2 件均本机 r516 自发票据（MSG-175x→bma/GM·MSG-176x→bmc/ALL）等收件方消费·零本机动作 | "
    "executive 三行实况：当前活=W19 12 分片引擎烧录在途（" + str(n19) + "/12）+finalize 待烧毕窗；"
    "最近实物=results/_r517bmb_w19_band_gate.py+research/PERPETUAL_N1_W19_PREREG.md+N1_BANDS/WAVE_CONFIGS W19 行"
    "（18:2x 落地）+results/p2cal_ext/n1_w19/shard-*.json 烧录产物；"
    "下个里程碑=W19 12/12 烧毕→finalize 判决面+账本落账（ledger 399,748+2,200=401,948·预期 ≤2h 窗） | "
    "下轮指针：①W19 烧毕核验（12/12 产物+engine ledger 行）→finalize --wave 19（prev=活链头 derive 禁手抄）"
    "+§5 四判定+§7/§8 回填 ②W17=bm-c/W18=bm-a 主权观察（其带位自 W19 表尾续行·机闸落位）"
    "③GM 双裁观察（W14 293 候选存量/N2-W15 重带裁定/LOWAMP-P2 E1）④dualrun flip 门 streak 6/3 GM 决策面 "
    "⑤MSG-175x/176x 对侧消费观察 | 本地未达 origin commit 数=0（收尾 push+fetch 自证） | [via bm-b]"
)
with open(rr, "a", encoding="utf-8", newline="") as f:
    if need_nl:
        f.write(eol_rn)
    f.write(line + eol_rn)
print("round report appended (r517)")

# --- 4) CODELY.md lesson ------------------------------------------------------
cl = os.path.join(ROOT, "CODELY.md")
lesson = (
    "- [2026-10-01 18:3x r517 bm-b] bm-b 引擎面=per-tick 短命进程架构注记（W19 冻结窗实探·r325 模块冻结面的本机变体）："
    "bm-b 实例（scripts/saturation_engine.py＋60s schtasks）无常驻 python 进程——每 tick 短命执行＋烧录子体分离存活"
    "（r317 close_fds 面），模块视图每 tick 自然刷新→新波登记后**无需重启引擎**（r325「常驻实例冻结→停旧起新」律"
    "只适用 bm-c 驻留式实例），W19 行落地后下一 tick（≤60s）自动入队点火（实证：75s 窗内 shard-1 ignite+shard-0 落盘）。"
    "How to apply：bm-b 新波冻结后点火验证=等 ≤2 tick 读**产物增长面**（r325 律验证面不变），勿做驻留实例重启手术；"
    "诊断引擎死活以 schtasks last-result＋status exit 码为准，勿以「无 python 进程」误判引擎死（每 tick 间歇态=正常）。"
)
with open(cl, "rb") as f:
    rawc = f.read()
eol_c = "\r\n" if rawc.count(b"\r\n") * 2 > rawc.count(b"\n") else "\n"
with open(cl, "a", encoding="utf-8", newline="") as f:
    if rawc and not rawc.endswith(b"\n"):
        f.write(eol_c)
    f.write(lesson + eol_c)
print("CODELY lesson appended (r517)")
print("CLOSEOUT WRITES DONE")
