# -*- coding: utf-8 -*-
"""R272 bm-a: state/heartbeat/report write-backs (five-face law: no-BOM, CRLF, indent=1,
no trailing newline, ensure_ascii=False; single now() instance per R271 timestamp law)."""
import datetime
import json
import os
import psutil

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
epoch = int(now.timestamp())
clock = now.astimezone().isoformat()


def dump_preserve(path, obj):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    with open(path, "wb") as f:
        f.write(txt.replace("\n", "\r\n").encode("utf-8"))  # CRLF, no trailing newline


# ---- state-bm-a.json ----
st = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
st["round_no"] = 272
st["last_round"] = 272
st["did"] = ("R272 unattended maintenance+supervision round: orders both scans empty 84/84; "
             "decisions tail D-20260926-09/10/11 = HQ faces zero BigMoney execution cases; "
             "smoke 25/25; board 29 tickets all-claimed zero open, job_list 0; "
             "S6 25 legs rc=0 (weekend no-op family; moneyflow rank-spawn throttle 23min<30min; "
             "AH spawn throttled panel incomplete EM block; alloc/grid lanes honest owner no-ops; "
             "token delta=0, L2 retro 1 leg local); migration v2.1 supervised alive "
             "(PID 35344 journal 22:20 advancing, sole holder = CEO Code.exe/28276 fail-closed); "
             "GPU-FACTOR-LANE-PROOF verified done+harvested (r244 gate), pool 49/49 done")
st["verdict"] = ("R272: watermark GREEN (red=false py_low_board_clear, next_pick=claimed MF_IC_P1 "
                 "on panel source recovery = legal-idle whitelist), smoke 25/25, S6 25x rc=0, "
                 "post_review recent 0 NO, pool_starvation 199min = weekend legal-idle "
                 "(open 0/bandit 0/ready 0/09-28 next-bar carriers), orders 84/84 both scans")
st["next"] = ("(1) 09-28 Mon new-bar chain (cutoff 09-24; daily->live.paper REGIME_GUARD v3 enforce->"
              "t35v->t24x2->aggr/grid marks->export->scorecard->daily_report); (2) O-2000 migration "
              "receipt on v2.1 fire + first push from new root; (3) MF_IC_P1 on moneyflow panel "
              "recovery (EM block since 09-25 00:32, 30-min gate retry); (4) 10-01 monthly trio + "
              "REGIME_GUARD v3 date gate + T-73 10-01 monthly verdict-bench wiring")
for k in ("ts", "last_round_ts", "updated_at", "last_run", "last_round_at", "updated"):
    st[k] = ts
st["current_task"] = ("R272 closed (maintenance+supervision round; migration v2.1 armed waiting CEO "
                      "editor; MF_IC_P1 on panel source recovery)")
dump_preserve("state-bm-a.json", st)

# ---- heartbeat fleet/machines/bm-a.json ----
hb = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
hb["machine_id"] = "bm-a"
hb["last_seen"] = ts
hb["current_task"] = st["current_task"]
hb["cpu_cores"] = os.cpu_count()
hb["cpu_pct"] = cpu
hb["free_ram_gb"] = round(vm.available / (1024 ** 3), 1)
gpu_free = None
try:
    import subprocess
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True, timeout=10).stdout.strip().splitlines()
    gpu_free = round(float(out[0]) / 1024, 1)
except Exception:
    pass
if gpu_free is not None:
    hb["gpu_free_vram_gb"] = gpu_free
hb["verdict"] = ("R272 maintenance+supervision: watermark GREEN py_low_board_clear legal-idle "
                 "(weekend), smoke 25/25, S6 25 legs rc0, orders 84/84, migration v2.1 armed "
                 "waiting CEO editor, pool 49/49 done 0 ready")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["round_no"] = 272
dump_preserve("fleet/machines/bm-a.json", hb)

# ---- round report append ----
rep_path = "logs/iteration-loop/round_reports-bm-a.md"
raw = open(rep_path, "rb").read()
eol = "\r\n" if b"\r\n" in raw else "\n"
line = ("2026-09-26 %s | R272 | 维护监督轮（水位绿 py_low_board_clear）| did: S0 pull up-to-date；"
        "S0.5 令双扫 84/84 零差集+decisions 尾行 D-09/10/11=HQ 收口面零本仓执行例；S1 smoke 25/25；"
        "S2 板 29 票全 claimed 零 open、job_list 0；S3 水位 next_pick=claimed（MF_IC_P1 源阻塞=合法 "
        "idle 白名单延续 R269-271 同面）+post_review 近行 0 NO+GPU 巷道 done/收割复核+T-73 剩腿=CEO "
        "简报（GM 会话面）+10-01 接线（日期门控）＝零可开新批；S6 25 腿全 rc=0（周末 no-op 族；"
        "moneyflow 节流 23min/30min 自愈环活；AH 同门；token delta=0）；S7 迁移哨兵 PID 35344 活"
        "（journal 22:20 推进·唯一占柄=CEO Code.exe/28276 fail-closed 等待）| 验证: smoke 25/25+"
        "S6 25x rc0+双扫零差集+schtasks 两任务在位 | 下轮: 09-28 周一新 bar 链+迁移点火回执+10-01 "
        "月度三件套 [via bm-a]" % ts[-5:])
with open(rep_path, "ab") as f:
    f.write((eol + line).encode("utf-8"))

# ---- self-verify: epoch int + clock T-sep + five-face ----
hb2 = json.load(open("fleet/machines/bm-a.json", encoding="utf-8-sig"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch not int"
assert "T" in hb2["clock_read"], "clock_read missing T separator"
for p in ("state-bm-a.json", "fleet/machines/bm-a.json"):
    r = open(p, "rb").read()
    assert r[:3] != b"\xef\xbb\xbf" and b"\r\n" in r and not r.endswith(b"\n"), p
st2 = json.load(open("state-bm-a.json", encoding="utf-8-sig"))
assert st2["round_no"] == 272
print("write-backs OK: round 272, epoch=%d int, clock=%s, cpu=%.1f%% ram_free=%.1fGB" %
      (epoch, clock, cpu, hb["free_ram_gb"]))
