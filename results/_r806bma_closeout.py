"""r806 bm-a closeout: state increment (804->806, dead-r805 absorbed per r804
precedent), round report line, heartbeat update (fresh-read-modify-write,
r575 multi-writer law for append-only faces)."""
import io, json, time, datetime, platform, subprocess

NOW = datetime.datetime.now(datetime.timezone.utc).astimezone()
TS = NOW.isoformat(timespec="seconds")          # T-separated ISO8601 with offset
EPOCH = int(time.time())                        # int epoch seconds

# --- 1) state-bm-a.json: round_no 804 -> 806 --------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
assert st.get("round_no") == 804, f"unexpected state round_no {st.get('round_no')}"
st["round_no"] = 806
st["last_round_ts"] = TS
json.dump(st, open(sp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("state round_no: 804 -> 806 (dead r805 absorbed)")

# --- 2) round report line ----------------------------------------------------
RR = ("2026-10-07T03:1x+08:00 | r806 bm-a (dept:工程+研究·W167 收口窗·dead-r805 吸收) | "
"watermark verdict: 绿(red=false lane=healthy; probe py 低位=假期合法 idle 白名单:板全闭环 0 open 票+引擎 idle verdict+W167 烧录完毕队列空) | "
"当前活: W167 全生命周期收口+W168 席位链首发 | "
"最近实物: results/perpetual_faces/n1_w167_results.json @2026-10-07T02:5x(origin 65e2df06e·ledger 772,812/K=365,320) | "
"下个里程碑: W168 prereg build+freeze edits(窗≤24h·never-dry 律·席位 MSG-0259+带闸 ADMIT 已备) | "
"did: S0 churn-absorb 8 面(rebase 干净 3/3)+MSG-2026-10-07-0250 处理(bm-c 揭 r804 两面带冲突标记推 origin·已继承治愈面+双钳进程内重装+两面 PARSE-OK 验证+坑入 CODELY)+W167 烧录产物吸收窗(r752 三恒等门 PASS:totals 2000/200+seed 连续性全等+12/12 分片)+W167 finalize one-pass(ledger 770,612→772,812 双投影精确命中·K 365,320·skill_line K-lift +0.0000·r776 三步绿·r518/r708 pre-flight 零活进程零同头)+W168 席位链(pre-seat probe rc0 ADMIT·A 384_404..386_403/B 386_404..386_603·阶梯第 27 例 E36·席位 MSG-2026-10-07-0259 推 origin ceaf58908+带闸 ADMIT 双窗 parity·W169+ 投影 A 386_404..388_403/B 386_604..386_803)+S0.5 零未回执令+decisions 水位 635c3024 匹配零动作+S1 smoke 48/48+S6 全链 rc0(38 项·对账 ZERO-DRIFT streak 51·audit supply_gap/supply_floor 持续态旗 ready=2·watermark insufficient_history·scorecard 36.4s·ORANGE_COOL 时钟·token L2 0)+attrition CLEAN+S7 四件绿(双任务 pin=8/看门狗/双钳/账本) | "
"验证证据: ledger_head 772,812 file=n1_w167_results.json 机读+三恒等门 results/_r806bma_w167_three_gate.json+带闸 results/_r806bma_w168_band_gate.json+git push 2dd265a70 送达核验 | "
"下轮指针: ①W168 prereg build(xform W167→W168·src 19,388B·席位 ceaf58908+gate 2dd265a70 事实源)②freeze edits 5-face(N1_BANDS[168]+WAVE_CONFIGS[168]+materializer 138..167 刷新+@CLMS@ 归属)③freeze_verify 8 腿④finalize(r806 两段会话律) | 本地未达 origin commit 数=见收尾 push 后核验 | [r806 bm-a]\n")

p = "logs/iteration-loop/round_reports-bm-a.md"
s = io.open(p, encoding="utf-8", newline="").read()
if not s.endswith("\n"):
    s += "\n"
s += RR
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("round report appended")

# --- 3) heartbeat fleet/machines/bm-a.json -----------------------------------
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
free_gb = round(__import__("psutil").virtual_memory().available / (1 << 30), 1)
gpu_free_vram = "n/a (CEO 同机办公·O-20261006-2110 pause 态执行面)"
hb["last_seen"] = TS
hb["current_task"] = "W167 finalize landed + W168 seat chain published; next: W168 prereg+freeze"
hb["cpu_cores"] = 32
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram"] = gpu_free_vram
hb["verdict"] = "healthy: W167 finalize landed (ledger 772,812 / K 365,320); W168 seat+gate published; prereg+freeze next session"
hb["heartbeat_epoch_utc"] = EPOCH
hb["clock_read"] = TS
hb["ts"] = TS
json.dump(hb, open(hp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
# self-verify: epoch must be JSON int
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in chk["clock_read"], "clock_read not T-separated"
print("heartbeat updated; epoch int verified:", chk["heartbeat_epoch_utc"], "| clock:", chk["clock_read"])
