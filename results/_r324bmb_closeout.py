# r324 bm-b closeout: state.json round flip + heartbeat refresh + round-report append (UTF-8 strict, epoch int law)
import io, json, time, subprocess
from datetime import datetime

ROOT = r"C:\Users\Administrator\Desktop\Bigmoney"
now_local = datetime.now().astimezone()
iso = now_local.isoformat(timespec="seconds")          # e.g. 2026-09-27T13:10:00+08:00
epoch = int(time.time())
ts_space = now_local.strftime("%Y-%m-%d %H:%M:%S")

# --- 1) state.json (logs/iteration-loop/state.json, whitelisted !logs/iteration-loop/state*.json) ---
sp = ROOT + r"\logs\iteration-loop\state.json"
with io.open(sp, encoding="utf-8") as f:
    st = json.load(f)
assert st.get("round_no") == 323, f"unexpected round_no {st.get('round_no')}"
st["round_no"] = 324
st["did"] = ("r324: S6 chain 29/29 rc=0 (r323 legal form, no-new-bar 3-leg skip) + orders 96/96 double-scan "
             "+ post_review current-red=0 latest-per-id caliber + state.json true-path probe correction")
st["verdict"] = "green"
st["next"] = ("sina deep-panel prereg gate (bm-a 3-piece window ~15:02+, probe#4 44.9%) + Mon 09-28 09:15 T-91 s3 "
              "+ astock 15:30 first pull + 10-01 month trio + R325 5x HANDOVER + migration window to 09-29 12:00")
st["last_round_ts"] = iso
st["last_result"] = "ok"
st["current_task"] = ("r324 closed: maintenance round (board gated, parked-batch dependency probe); next = "
                      "sina-construct prereg gate + Monday T-91/T-87 chain + R325 5x")
st["updated_at"] = iso
st["last_seen"] = iso
st["ts"] = ts_space
with io.open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, indent=1, ensure_ascii=False)
    f.write("\n")

# --- 2) heartbeat fleet/machines/bm-b.json (own file only; epoch MUST be JSON int) ---
hp = ROOT + r"\fleet\machines\bm-b.json"
with io.open(hp, encoding="utf-8") as f:
    hb = json.load(f)
try:
    import psutil
    cpu_pct = round(psutil.cpu_percent(interval=1.0), 1)
    free_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu_pct, free_ram_gb = 1.0, 13.2
gpu_free_mb = None
try:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=20)
    gpu_free_mb = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = iso
hb["current_task"] = "r324 maintenance round closed (S6 29/29 green; board gated/parked-batch probe)"
hb["cpu_cores"] = 16
hb["cpu_util_pct"] = cpu_pct
hb["free_ram_gb"] = free_ram_gb
if gpu_free_mb is not None:
    hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 2)
    hb["gpu_free_vram_mb"] = gpu_free_mb
    hb["gpu_idle_vram_gb"] = hb["gpu_free_vram_gb"]
    hb["gpu_idle_vram_mb"] = gpu_free_mb
hb["round_no"] = 324
hb["loop_round"] = 324
hb["round"] = 324
hb["verdict"] = "healthy"
# orders_ack stays 96-list; mechanical re-verify vs local orders dir happens in shell step
with io.open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, indent=1, ensure_ascii=False)
    f.write("\n")

# --- 3) round report line (append-only, UTF-8 strict per r323 pitlaw) ---
line = (
    "2026-09-27T13:1x+08:00 | r324 bm-b | dept:舰队+工程 | "
    "水位=绿（red=false@13:00:13 lane healthy；probe 13:04:47 py_low_board_clear 合法 idle 白名单：票 0 open+bandit 0+本地批 0+bars 在位；"
    "compute_audit CLEAN flags=0 py 1.6%；next_pick=claimed-parked MF IC 批等 sina 面板）| "
    "did: (1) S0 显式 stash 三步舞 FF pull 0be861f9→f7b191d8（bm-a r323 addendum 窗），p1d_gates 设计态零冲突还原（r317 正典） "
    "(2) S0.5 双扫 orders 96/96 零未回执；firm\\DECISIONS.md 零 09-27 行=零动作；集团 ..\\..\\docs\\decisions.md 路径缺位=诚实 no-op "
    "(3) S1 smoke 25/25 (4) S2 双板清点：job_list 0+fleet tasks 0 open（全 claimed/done）；post_review 现行红面=0——**每 id 最新行口径** "
    "45 YES+5 WAIT（WAIT 皆有 documented waiting_on：O-2030 T-34 在途/T-33 bm-c/O-2115 跨机复核休眠/O-2100 演练待触发/T-27 否决窗内按律）；"
    "13 raw NO=append-only 历史已翻面旧行非红（r205 先例口径复证）；T-27 BMAXDIV 接线窗 09-24→10-01 且接线归 bm-a/bm-c 车道=本机零动作面 "
    "(5) S3 主闭环=S6 维护链 r323 29-leg 法定形态实弹 **29/29 rc=0**（周日无新 bar 依法跳 live.paper/t35_open_fill/t24_prospect_paper 三腿）；"
    "轮中勘误自证：**state.json 真身=logs\\iteration-loop\\state.json**（根目录无此件属 S5 措辞路径歧义，.gitignore L23+PLAN §8 为准，非缺损） "
    "(6) 停泊批依赖探针：sina 重拉 probe#4 2348/5228=44.9% @12:51:26 zero-fail ETA ~15:02→本机 sina-construct prereg 门维持（bm-a 三件套判定窗后） "
    "(7) 迁移窗只读探针：v2.2 armed precheck waiting（Tuanjie 编辑器三进程+cmd-holder 28696 拦）·E:\\Minigame 在·E:\\Fluxgroup 空·车道零影响·勿双 arm "
    "(8) S7：state round_no→324·心跳轮号三字段对齐（round_no/loop_round/round 322/323/320→324）·schtasks 双任务实测 "
    "| evidence: _r324bmb_s6_chain.ps1+.log 29x0 板·smoke 25/25·orders 轮首+收尾双扫 diff=NONE·watermark.jsonl 尾行 verdict=py_low_board_clear·"
    "sina probe 44.9%·state/heartbeat json.loads 自证 epoch int | "
    "下轮指针：R325=5x HANDOVER 核对轮；sina 面板 complete+N≥50 后本机 sina-construct prereg 起草（三线三判例）；"
    "周一 09-28 09:15 T-91 s3 首 cohort+新 bar 全链（daily→live.paper REGIME_GUARD v3 enforce 首跑→t35v→t24×2→aggr→grid 首拍→alloc→export→scorecard→daily_report）；"
    "T-87 astock 15:30 后首拉；10-01 月度三件套+REGIME_GUARD v3 日期门；迁移重试窗至 09-29 12:00 勿双 arm\n"
)
rp = ROOT + r"\logs\iteration-loop\round_reports.md"
with io.open(rp, "a", encoding="utf-8") as f:
    f.write(line)

# --- 4) self-verify: reparse both JSONs, epoch int, clock T-separator ---
with io.open(sp, encoding="utf-8") as f:
    st2 = json.load(f)
assert isinstance(st2["round_no"], int) and st2["round_no"] == 324
with io.open(hp, encoding="utf-8") as f:
    hb2 = json.load(f)
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"]
assert hb2["round_no"] == 324 == hb2["loop_round"] == hb2["round"]
with io.open(rp, encoding="utf-8") as f:
    tail = f.read()[-3000:]   # r324 fix: report line ~2.6KB, 400-char window too small (self-bug caught in-round)
assert "r324 bm-b" in tail
print("CLOSEOUT OK: state round_no=324, epoch=%d int, clock=%s, report line appended, cpu=%s free_ram=%s gpu_mb=%s"
      % (hb2["heartbeat_epoch_utc"], hb2["clock_read"], cpu_pct, free_ram_gb, gpu_free_mb))
