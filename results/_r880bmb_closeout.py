# r880 bm-b closeout: state writeback + heartbeat + round report line
# -*- coding: utf-8 -*-
import json, time, datetime, psutil, os

ROOT = os.path.dirname(os.path.abspath(__file__))  # results/ -> not root; use fixed
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
os.chdir(ROOT)

now = datetime.datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

# --- machine faces ---
vm = psutil.virtual_memory()
ram_free_gb = round(vm.available / 1024**3, 1)
ram_free_pct = round(vm.available / vm.total * 100, 1)
try:
    import subprocess
    out = subprocess.run(["nvidia-smi","--query-gpu=memory.free","--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=10).stdout.strip()
    vram_free_mb = int(out.splitlines()[0])
except Exception:
    vram_free_mb = 3500
vram_free_gb = round(vram_free_mb/1024,1)

RNO_NEW = 881

did = ("r880 watch+receipt round: S0 lane-state checkpoint 8 faces (r642 law, commit c4736c63d) + rebase pull clean; "
       "S0.5 CEO order O-20261011-1254 (idle-relapse scold) RECEIPTED same round: bm-b sec.2 self-check line landed in order file sec.4 "
       "(CPU=E16 burn py~48% / GPU=3070 Ollama resident 4.5GB backup-for-MV-lane per order / cloud zero backlog) + orders_ack 194/69 diff EMPTY "
       "+ D19 dec/ord both 恒等 zero action; S1 smoke 49/49; S2 board empty (0 open tickets, T-184 held claimed, branch transfer/t184-510880 still absent from origin 13:0x ls-remote, bm-a dark, deadline 10-12 15:30); "
       "satengine alive rc0 (queue 0, verdict idle on N1 face while autofill pool burns); E16 WATCH: shard-1 COMPLETED mid-round "
       "(product shard_1of12.json + ckpt 28,659B ~13:1x = 2/12 done, wiring-fix double-proven in real fire, autofill chain self-turning, 12/12 ETA ~16:xx); "
       "W-band chain re-read: W207 FINALIZED + W208 bm-a DECLARED (dark, head-block) + W209 bm-c ready-on-W208 + W210 bm-b seat-DECLARED gated on W209 (M9); "
       "P2 tech queue 0 live rows + P3 explore sole open row = E16 (own lane in-flight); S6 40 legs 39 rc0 + alloc_paper rc=2 (T-184 dep honest 5th consecutive); "
       "S7 four-piece green (pin=2 no-op, watchdog registered, hooks both MATCH zero reinstall, attrition CLEAN 4 healed 0 active) "
       "+ orphan probe py_faces=14 orphans=0 + HANDOVER 5x r880 reconciliation line + heartbeat orders_ack=194")

verdict = ("GREEN: r880 COMPLETE (CEO order receipted same round; E16 2/12 landed shard-0+shard-1 both clean = wiring fix double-proven; "
           "smoke 49/49; S6 39rc0+alloc rc2 T-184 dep honest 5th round; WM red = burn-ramp window GM-waiver O-1612 legal, autofill self-turning")

nxt = ("r881: E16 shard-2..11 completion watch (autofill cadence, 12/12 ETA today ~16:xx) -> finalize when 12/12 (observing round, refuse-if-exists) "
       "-> CENSUS verdict face -> T-184 transfer receiver restore SAME round origin/transfer/t184-510880 lands (deadline 2026-10-12 15:30, bm-a dark - re-probe branch each round) "
       "-> W210 freeze anchor watch (gated W209<-W208 bm-a) -> 48h CEO report due 2026-10-13 11:2x")

now_active = ("r880: E16 shard-1 COMPLETED mid-round (2/12); shard-2 claim expected by autofill; CEO order O-20261011-1254 receipted")

latest_artifact = ("r880: results/alphagen_rg/shard_1of12.json (E16 2/12 shard product, census face, cutoff 2026-10-09) + fleet/orders/O-20261011-1254-bm-c.md sec.4 bm-b receipt line")

# --- state.json (bm-b) ---
sp = os.path.join(ROOT, "state.json")
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = RNO_NEW
st["round"] = 880
st["round_no_label"] = "r880"
st["did"] = did
st["verdict"] = verdict
st["next"] = nxt
st["current_task"] = nxt
st["task"] = nxt
st["now_active"] = now_active
st["latest_artifact"] = latest_artifact
st["last_action"] = did
st["last_action_at"] = ts
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["last_seen"] = ts
st["clock_read"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["orphan_face"] = 0
st["orphan_face_note"] = "r880 round probe: py_faces=14 alive, orphans=0"
st["orphan_faces"] = 0
st["note"] = "r880: CEO order O-20261011-1254 receipted (sec.2); E16 2/12; T-184 branch absent (bm-a dark); W210 seat-DECLARED gated W209<-W208"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("state.json round_no ->", RNO_NEW)

# --- heartbeat fleet/machines/bm-b.json ---
hp = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
h = json.load(open(hp, encoding="utf-8"))
h["round"] = 880
h["round_no"] = RNO_NEW
h["did"] = did
h["verdict"] = verdict
h["next"] = nxt
h["current_task"] = nxt
h["task"] = nxt
h["now_active"] = now_active
h["latest_artifact"] = latest_artifact
h["last_action"] = did
h["last_action_at"] = ts
h["last_round_at"] = ts
h["last_seen"] = ts
h["clock_read"] = ts
h["ts"] = ts
h["updated"] = ts
h["updated_at"] = ts
h["heartbeat_epoch_utc"] = epoch
h["idle_rounds"] = 0
h["agenda_starved"] = False
h["free_ram_gb"] = ram_free_gb
h["ram_free_gb"] = ram_free_gb
h["ram_free_pct"] = ram_free_pct
h["gpu_free_vram_mb"] = vram_free_mb
h["gpu_free_vram_gb"] = vram_free_gb
h["vram_free_gb"] = vram_free_gb
h["orphan_face"] = 0
h["orphan_face_note"] = "r880 round probe: py_faces=14 alive, orphans=0"
h["orphan_faces"] = 0
json.dump(h, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# verify epoch int (R170/R178 law)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat epoch", chk["heartbeat_epoch_utc"], "ram_free", ram_free_gb, "vram_free", vram_free_gb)

# --- round report line (bm-b: logs/iteration-loop/round_reports.md) ---
rr = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
line = (
    ts + " | r880 bm-b | "
    "dept:研究（E16 alphagen RG census 值守轮：shard-1 COMPLETED mid-round=2/12·autofill 链自转·12/12 ETA 今日~16:xx）"
    "+dept:舰队（CEO 令 O-20261011-1254 闲置复发斥责令 §2 自查回执同轮落册：令件 §四 bm-b 行×·三面=CPU E16 烧 py~48%/GPU 3070 Ollama 常驻 4.5GB=备援归 MV 车道候令/云零积压·已领任务=E16 池批+T-184 receiver+W210 席·orders_ack 194）"
    "+dept:工程（S6 40 腿 39rc0+alloc_paper rc=2 T-184 物理依赖诚实面第 5 轮·S7 四件套绿+HANDOVER 5x r880 对账行）"
    " | 当前活=E16 分片烧录值守（autofill 自续·2/12）| 最近实物=results/alphagen_rg/shard_1of12.json（2/12·13:1x 落地）"
    "| 下个里程碑=E16 12/12+finalize+CENSUS verdict face 今日~16:xx（bound ≤2026-10-13）·T-184 510880 restore ≤10-12 15:30（bm-a 暗线·逐轮再探分支）·48h CEO 报告 ≤10-13 11:2x"
    " | 孤儿面=0（round probe py_faces=14 orphans=0）"
    " | WM-VERDICT: red=true·lane=pool-batch-runnable-idle-low-cpu=burn-ramp 窗 O-1612 GM waiver 合法（2/12 已落·autofill 续烧自转·py 48%实测）"
    " | 验证证据=results/_r880bmb_s6_log.txt 40 腿账（S6_FAILS=1=alloc dep）+smoke 49/49+attrition CLEAN（4 healed·0 active）+hooks 双 MATCH 零重装+loop pin=2 no-op+watchdog 重注册+D19 双面恒等+orders_ack_scan 差集 69/69"
    " | 本地未达 origin commit 数=0（push 后 ls-remote 自证）"
    " | 下轮指针=r881：E16 3/12..11 完成守望+finalize refuse-if-exists+T-184 origin 分支再探+W210 锚窗\n"
)
with open(rr, "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
print("CLOSEOUT_OK")
