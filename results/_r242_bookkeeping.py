"""r242 bm-b round bookkeeping: state.json round_no++, round report append,
heartbeat refresh (epoch int + clock_read). Text-level state edit per
R230 law; heartbeat single-writer file; orders_ack unchanged (78/78)."""
import datetime as dt
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "logs", "iteration-loop", "state.json")
REPORT = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
HEART = os.path.join(ROOT, "fleet", "machines", "bm-b.json")

now = dt.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M:%S")
epoch = int(now.timestamp())
clock_read = now.isoformat(timespec="seconds")

# -- system metrics --------------------------------------------------
import psutil
vm = psutil.virtual_memory()
free_gb = round(vm.available / 1024 ** 3, 1)
cpu_pct = round(psutil.cpu_percent(interval=1), 1)
gpu_free_mb = 2252
try:
    import subprocess
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=10)
    gpu_free_mb = int(out.stdout.strip().splitlines()[0])
except Exception:
    pass

# -- state.json: text-level field update -----------------------------
with io.open(STATE, "r", encoding="utf-8-sig", newline="") as fh:
    raw = fh.read()
crlf = "\r\n" in raw
st = json.loads(raw)
old_round = st["round_no"]
assert old_round == 241, f"unexpected round_no {old_round}"
st2 = dict(st)
st2["round_no"] = 242
st2["did"] = ("r242: T-78 s4 winner wiring -- 3 members registered with "
              "maximal WIN cells (C01 tp_ladder / C02+ENGULF ov_full), "
              "dd_control kwarg plumbed paper 4 sites + AGGR sleeve worker, "
              "anchor+x2+x2_watch expectations re-derived same round, "
              "batch parity 0.0000 x3, sleeve inheritance PASS; "
              "commit f95adf89")
st2["verdict"] = "GREEN"
st2["next"] = ("T-78 CN-GRID-SLEEVE prereg (9, unlock-4); 09-28 Monday "
               "new-bar full chain (paper first run on wired configs, "
               "anchor expectations ready); 10-01 month-first three-pack "
               "+ REGIME_GUARD v3 date gate")
nl = "\r\n" if crlf else "\n"
body = json.dumps(st2, ensure_ascii=False, indent=1)
with io.open(STATE, "w", encoding="utf-8", newline="") as fh:
    fh.write(body + nl)
with io.open(STATE, "r", encoding="utf-8-sig") as fh:
    back = json.load(fh)
assert back["round_no"] == 242 and isinstance(back["round_no"], int)
print(f"state.json: round {old_round} -> 242 (crlf={crlf})")

# -- round report append --------------------------------------------
verdict_line = (ts + " | r242 watermark verdict: GREEN py_low_board_clear "
                "(board bm-b lane 0 open + bandit 0 + pool 0 ready = "
                "legitimate idle; probe 10:58:39 py series tail 0.4/0.2/0; "
                "no zombie, GPU 1%)")
main_line = (ts + " | r242 | T-78 s4 winner wiring delivered (dept:策略+"
             "组合与资金+工程联合): S0 stash-pull-pop 1-UU autofill_state "
             "(skill 正典 mixed-dict+ledger: last_tick ts-取新整dict "
             "10:50:01 / launches union cap50 / CRLF 镜像, "
             "results/_r242_resolve.py); S0.5 双扫 78/78 全对账零未回执+"
             "decisions.md 缺位零动作; S1 smoke 25/25; **s4 落地**=独立 "
             "commit f95adf89 per prereg 10: C01<-ov_tp_ladder (levels "
             "5/8%+fractions .5/.5), C02+ENGULF<-ov_full (tp_ladder+trail "
             "3%/5%+dd_control -10%/50%/-5%), 接线分辨率规则=maximal "
             "winning cell (嵌套族, 每一 wired 配置=过冻结双面门的冻结 "
             "cell); code face=dd_control kwarg 4 调用点 (anchor/prospect/"
             "paper-window/cost_x2) + t28 _sleeve_worker (AGGR 宿主); "
             "registration face=anchor+x2+x2_watch 种子同轮 re-derive @09-22 "
             "(old-config CostPatch(2) 奇偶校验 x3, max |d|=0.0003): C01 "
             "IS 0.4514->0.4696 OOS 1.6085->1.7479 x2 margin 0.1238 ok / "
             "C02 IS 0.4585->0.5346 OOS 1.4853->1.6392 x2 margin "
             "0.0307->0.0491 probation(改善仍薄) / ENGULF IS 0.6239->0.6121 "
             "(合成面 IS 段微降) OOS 0.2944->0.3835 x2 margin 0.0016->0.0143 "
             "probation(改善); 三态=立法 commit f95adf89 / 生效 anchor "
             "PASS x3 + batch-caliber parity 0.0000 x3 (wired==judged) + "
             "AGGR sleeve 继承 PASS (dd_control keys + eq tail 字节等价 "
             "1457319.1) / 验收=post_review 待; REJECT 18 面不接线 (教训 "
             "prereg 8); S6 21 腿全绿 (周末 no-op 族: daily 0 新行 cutoff "
             "09-24 / regime ORANGE d2 shadow / clock ORANGE_COOL / lhb "
             "节流 / heat 周末 / futures+fundamental(13.8h fresh)+b_layer "
             "5222 码全门过 / options+mf+sina_mf+ths+ah=bm-a 车道+fp=bm-c "
             "车道诚实 no-op / 无新 bar->paper 链合法跳 / aggr+alloc 幂等 "
             "no-op / scorecard 6 员 / daily_report 幂等再生 / "
             "build_status 10 因子 / token delta=0, L2 legs=1) | evidence: "
             "commit f95adf89 + results/_r242_wire.py SELFCHK x3 + "
             "results/_r242_inherit_check.py PASS + smoke 25/25 + "
             "fleet/tasks/T-2026-09-26-78-P1.json progress_r242 + S6 全 "
             "exit 0 | next: 1) T-78 CN-GRID-SLEEVE prereg (9) 2) 09-28 "
             "周一新 bar 全链 (paper 首跑 wired 配置, anchor 已就绪) 3) "
             "10-01 月首轮三件套+REGIME_GUARD v3 日期门")

with io.open(REPORT, "ab") as fh:
    pass  # probe EOL via text read below
with io.open(REPORT, "r", encoding="utf-8", errors="replace", newline="") as fh:
    rraw = fh.read()
r_crlf = "\r\n" in rraw
sep = "\r\n" if r_crlf else "\n"
with io.open(REPORT, "a", encoding="utf-8", newline="") as fh:
    if not rraw.endswith(sep):
        fh.write(sep)
    fh.write(verdict_line + sep)
    fh.write(main_line + sep)
print(f"round_reports.md: r242 2 lines appended (crlf={r_crlf})")

# -- heartbeat (single-writer bm-b file) ------------------------------
with io.open(HEART, "r", encoding="utf-8-sig", newline="") as fh:
    hraw = fh.read()
h_crlf = "\r\n" in hraw
hb = json.loads(hraw)
hb["last_seen"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock_read
hb["current_task"] = ("T-78 s4 winner wiring delivered (r242, commit "
                      "f95adf89); CN-GRID-SLEEVE prereg next")
hb["cpu_cores"] = 16
hb["free_ram_gb"] = free_gb
hb["gpu_free_vram_gb"] = round(gpu_free_mb / 1024, 1)
hb["total_ram_gb"] = round(vm.total / 1024 ** 3, 1)
hb["cpu_util_pct"] = cpu_pct
hb["round_no"] = 242
hb["verdict"] = "GREEN"
hb["cores"] = 16
hb["idle_ram_gb"] = free_gb
hb["gpu_free_vram_mb"] = gpu_free_mb
hb["idle_ram_mb"] = int(free_gb * 1024)
hb["gpu_idle_vram_mb"] = gpu_free_mb
hbody = json.dumps(hb, ensure_ascii=False, indent=1)
with io.open(HEART, "w", encoding="utf-8", newline="") as fh:
    fh.write(hbody + ("\r\n" if h_crlf else "\n"))
with io.open(HEART, "r", encoding="utf-8-sig") as fh:
    back = json.load(fh)
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert back["round_no"] == 242
print(f"heartbeat: epoch={epoch} (int OK) clock={clock_read} "
      f"free_ram={free_gb}GB gpu_free={gpu_free_mb}MB cpu={cpu_pct}% "
      f"(crlf={h_crlf})")
