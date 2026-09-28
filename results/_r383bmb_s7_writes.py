# -*- coding: utf-8 -*-
# r383 bm-b S7: state.json round bump + heartbeat refresh + round report line (byte-style preserving)
import json, time, datetime, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# --- state.json (CRLF, no trailing newline) ---
b = open("state.json", "rb").read()
assert b.count(b"\r\n") > 0 and not b.endswith(b"\n")
st = json.loads(b.decode("utf-8"))
assert st["round_no"] == 382, st["round_no"]
st["round_no"] = 383
st["note"] = ("r383: town.html O-2250 alignment closure (fac KPI row + fac/hall STRATEGY_LIBRARY pointers, "
              "node --check head/cur 0/0) + CODELY batch-49 water-line archival (r161 verbatim -> archive, "
              "+r383 kengru) + W4-SCREEN RAM probe [5.23,2.38,0.48]GB gate closed (census W2B slow-tail) + "
              "W5 stays parked (funnel headroom unchanged) + S6 legs rc=0 + daily_scorecard stale-takeover derive "
              "(bm-a stale 174min, O-2100 s2.4 law)")
out = json.dumps(st, ensure_ascii=False, indent=1)
out = out.replace("\n", "\r\n")
open("state.json", "wb").write(out.encode("utf-8"))
chk = json.loads(open("state.json", "rb").read().decode("utf-8"))
assert chk["round_no"] == 383
print("state.json -> round_no 383 OK (CRLF preserved)")

# --- heartbeat fleet/machines/bm-b.json ---
now = datetime.datetime.now().astimezone()
clock = now.isoformat(timespec="seconds")
epoch = int(time.time())
assert isinstance(epoch, int)
assert clock.endswith("+08:00"), clock
import psutil
vm = psutil.virtual_memory()
hb_path = "fleet/machines/bm-b.json"
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = clock
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = clock
hb["current_task"] = ("r383 done: town.html O-2250 alignment closure (策略厂 KPI row + fac §一/hall §二 STRATEGY_LIBRARY "
                      "pointers + footer token; node --check HEAD=0/cur=0 after one extra-brace catch) + CODELY batch-49 "
                      "archival; next: W4-SCREEN flip (any machine RAM>=4GB 3-sample; census ETA ~15:00) -> screen-finalize "
                      "-> W4-JUDGE entry; judge family W1/W2/W3 + V2-P1 relaunch post-census RAM window")
hb["cpu_cores"] = psutil.cpu_count(logical=True)
hb["free_ram_gb"] = round(vm.available / 1e9, 2)
hb["cpu_util_pct"] = psutil.cpu_percent(interval=1)
hb["round_no"] = 383
hb["round"] = 383
hb["loop_round"] = 383
hb["verdict"] = ("healthy: smoke 25/25, orders 99/99 dual-scan clean, S6 all legs rc=0 (scorecard meta-only drift 2 lines "
                 "L1-idempotent disclosed; daily_scorecard stale-takeover derive lawful bm-a stale 174min); W4-SCREEN open "
                 "waiting RAM flip (3-sample [5.23,2.38,0.48]GB closed; census W2B 4200+/5620 slow-tail burning no-kill ETA "
                 "~15:00); W5 prereg stays parked (r162 freeze-trigger: judge funnel headroom unchanged); board 0 open; "
                 "watermark py_low_with_work_cands lawful structural occupancy")
hb["n_orders_ack"] = len(hb["orders_ack"])
with open(hb_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
v = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(v["heartbeat_epoch_utc"], int) and v["heartbeat_epoch_utc"] == epoch
assert "T" in v["clock_read"] and v["clock_read"].endswith("+08:00")
print("heartbeat ->", hb_path, "epoch int OK clock OK round 383")

# --- round report line (bm-b file: logs/iteration-loop/round_reports.md) ---
line = ("2026-09-28T" + now.strftime("%H:%M:%S") + "+08:00 | round 383 bm-b | dept:工程 (J12 城镇面对齐小闭环+水位整编) | "
        "WM-VERDICT: 绿 (red=false; probe 12:50 py_low_with_work_cands=合法: census W2B 4-worker 慢尾在烧 [4200+/5620·pid 28820·ETA ~15:00] "
        "+ 池候选全 RAM 门 r354 [W4-SCREEN 3-sample 12:47 实探 [5.23,2.38,0.48]GB 闩关·W1/W2/W3 judge+V2-P1 序门待窗] + 板 0 open + bandit 0 open) | "
        "did: S0-1 锚定 bm-b→S0 up-to-date (HEAD==origin 0e607ea1)→S0.5 双扫 99/99 零未回执 (decisions.md 本机不存在=委员会队列零可读面如实披露·C-20260927-01 意见窗至 09-29 已出件)→"
        "S1 smoke 25/25→S2 板 0 open→S3 常设线: W5 维持挂起 (r162 冻结触发器=判官漏斗 headroom 未变: W4 停在 screen RAM 门+W1/W2/W3 judge 全 waiting) 零开波动作; "
        "J12 邻面小闭环=town.html O-2250 对齐 (策略厂 KPI dim row 补齐=唯一缺 KPI 面楼+fac mandate §一/hall mandate §二 STRATEGY_LIBRARY 指针+footer r383 token; "
        "实弹坑=expression-bodied info 尾从邻楼复制 } }, 模板多一 } 秒红→git show HEAD: 提 script 双跑 node --check 定责→修后 HEAD=0/cur=0)→"
        "S4 坑律 r383 入册+CODELY 10,066B 超线→四十九批当窗整编 (r161 strftime verbatim→archive 202609.md·行级零丢失校验·指针行+r383 条落位)→"
        "S6 全链 rc=0 (update_daily 0 新行 cutoff 09-24·regime shadow 触发面 hs300<MA200+breadth 0.77·market clock ORANGE_COOL sleeves4·lhb/futures/repo/options/mf/sina_mf/ths/ah/fund_premium 车道守卫诚实 no-op·astock 面板新鲜 no-op·rev_osc 幂等 no-op·t35 export 09-24 6 员 18 持仓·t24a 22/22 drift0·t24b eligible 0/22·aggr/alloc/grid 幂等 no-op·sysv1 车道守卫 no-op·scorecard meta-only 2 行漂移 L1 幂等披露·daily_scorecard=bm-b stale-takeover derive (bm-a 心跳 174min 陈旧·O-2100 s2.4 法)·daily_report REPORT-20260928 再生·build_status 刷新·token delta=0)→"
        "S7: 两计划任务在位 (:02/:10 针位)·pre-commit 钳一致·state 383 | next: W4-SCREEN flip 窗 (本机 post-census 或他机 RAM 开窗)→screen-finalize→W4-JUDGE entry; V2-P1 relaunch 待 RAM 窗 (bm-c MSG-1205 零新修维持)\n")
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report line appended")
