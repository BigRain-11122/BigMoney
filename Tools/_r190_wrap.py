"""r190 wrap: state-bm-a + heartbeat + round report line (S7)."""
import datetime
import json
import time
import platform
import psutil

NOW = datetime.datetime.now().astimezone()
NOW_ISO = NOW.isoformat(timespec="seconds")
EPOCH = int(time.time())

# --- state-bm-a.json -----------------------------------------------------------
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = st.get("round_no", 0) + 1
st["did"] = ("R190: T-65 s3 closeout = options exercise-price+expiry full-spectrum audit GATE PASS "
             "(results/option_s3_audit.json 6 green: strike coverage 50ETF/300ETF x 3 months x calls+puts zero-missing, "
             "triple-source crossverify 100%, expiry 6 cells, moneyness brackets, historical feasibility 202609+127-row full-life daily, "
             "cutoff 2026-09-24 zero-future; retention boundary disclosed: sina prunes deep expired months) "
             "+ T-65 DONE (4/4 slices) + T-67 claimed (gate verified same round, CEO immediate law) "
             "+ wave-3 T-68 opened (bonds capacity-gated + HK-connect re-probe-gated, O-1721 chain) "
             "+ bm-b r205 MSG receipt + push-race rebase resolved (autofill union r161/r185 recipe) + S6 16 legs green")
st["verdict"] = "green"
st["next"] = ("T-67 wave-2 options prereg draft (PREREG_TEMPLATE, covered call/protective put/cash-secured put, "
              "retention-window backfill decision frozen in prereg); T-68 open for any healthy machine; "
              "mf-rank + AH refresh spawned detached self-heal watch")
st["ts"] = NOW_ISO
st["last_round_ts"] = NOW_ISO
st["updated_at"] = NOW_ISO
st["current_task"] = "R190 done: T-65 closed 4/4; T-67 claimed (wave-2 options prereg = next main closure)"
st["last_run"] = NOW_ISO
st["last_round_at"] = "R190"
json.dump(st, open(sp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)

# --- heartbeat fleet/machines/bm-a.json ---------------------------------------
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
cpu = psutil.cpu_percent(interval=1)
vm = psutil.virtual_memory()
hb.update({
    "machine_id": "bm-a",
    "last_seen": NOW.strftime("%Y-%m-%d %H:%M:%S"),
    "current_task": "R190 done: T-65 closed 4/4 (s3 audit PASS); T-67 claimed wave-2 options; next = options prereg draft",
    "cpu_cores": psutil.cpu_count(logical=True),
    "cpu_pct": cpu,
    "free_ram_gb": round(vm.available / 1024**3, 1),
    "verdict": "healthy",
    "heartbeat_epoch_utc": EPOCH,
    "clock_read": NOW_ISO,
    "cores": psutil.cpu_count(logical=True),
    "idle_ram_gb": round(vm.available / 1024**3, 1),
    "task": "T-65 closed; T-67 wave-2 options claimed; T-68 wave-3 opened",
})
json.dump(hb, open(hp, "w", encoding="utf-8", newline="\n"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be JSON int (R170/R178 law)"
print("state round_no:", st["round_no"], "| hb epoch:", chk["heartbeat_epoch_utc"], type(chk["heartbeat_epoch_utc"]).__name__)

# --- round report line ---------------------------------------------------------
rp = "logs/iteration-loop/round_reports-bm-a.md"
line = (f"\nR190 | {NOW_ISO} | bm-a (dept:研究+数据+舰队) | 水位=绿（red=false lane healthy；probe 21:49 insufficient_history n=1 窗初合法；"
        f"audit CLEAN 旗空 load_state idle-starvation=池 0 ready 板 1 open(T-68 待 prereg 非可跑) 合法 idle；"
        f"WM red 21:20:02 tick red=false）| did: S0 pull→push 拒→rebase 重放 5eb8004f→737e217f（bm-b r205 同窗：CTA 冗余 runner 白烧停机收口+T-67 让位注记=零撞车）"
        f"+stash pop autofill 1-UU r161/r185 配方（块外公共尾+解析验证后才 add；launches 50+55→50 滚动帽；last_tick 21:40:02 取新；Tools/_r190_af_union.py 落件）；"
        f"S0.5 双扫 73/73 零未回执+P-32 decisions mtime 12:05 无新行零动作+身份四源互证=bm-a；S1 smoke 25/25；"
        f"S3 主闭环=T-65 s3 收尾（CEO 即时链 T-65→T-67→T-68）：**期权行权价+到期面全谱审计 GATE PASS**（results/option_s3_audit.json 六绿："
        f"G1 行权价全谱=50ETF/300ETF×3 挂牌月×认购认沽零缺（board 链级面 22-28 行/月）+G2 三源交叉验 100% 合（board/greeks/代码内嵌解析 2.750 三验）"
        f"+G3 到期 6 格+G4 moneyness 2.959∈[2.75,3.5]/4.515∈[4.1,5.25]+G5 历史=202609 枚举 14 合同+过期合同全生命周期日线 127 行+G6 128 观察日 cutoff 2026-09-24 零未来；"
        f"**保留窗数据债如实披露**=sina codes 面深过期月 202606/从未挂牌月 202608 双空载崩壳→期权链历史重建窗=保留窗，prereg 回测窗设计须绕；"
        f"探针 v1→v2 重spec 披露（历史月 202606→202609 空载发现后重spec+边界面移披露节 r186 对称律+G4 spot 键面修正 最近成交价））；"
        f"链式三动作：T-65 done（4/4 切片）+T-67 认领（21:47:25 CEO 即时律同轮认领即开动·门馈同轮验证）+T-68 开票（波-3 债券容量门+港股通复探门）；"
        f"近失自捕=T-65 done_at 手写估值 21:48:00→epoch 复核修正 21:47:18（r62 真钟律·R189 同款）；"
        f"bm-b MSG-2146 回执（pid10948 处置闭环确认+白烧停机判据互补入册+T-67 让位正确性确认）+答复 MSG-2200 已落 inbox；"
        f"S6 16 腿绿（update_daily 09-25 bar 上游仍未发布 0 新行 0 失败合法 no-op·regime ORANGE d2 shadow·lhb 节流·heat 已采·futures/ths/fundamental/b-layer 门过"
        f"·mf-rank spawn·AH refresh spawn conn-fuse 自愈·fp=bm-c 车道 no-op·无新 bar=live.paper 条件链合法跳过·scorecard 6 员·panel 刷新·token delta=72）；"
        f"S4 面律一条（期权枚举保留窗+三源行权价验 join 键律+门面集/边界披露面分离）；"
        f"S7 双扫 73/73 零未回执·schtasks 双任务在位·心跳 epoch int 自证 | 验证证据=results/option_s3_audit.json+commit 737e217f/5b43040e+push 干净 "
        f"| 下轮指针=T-67 wave-2 期权 prereg 起草（PREREG_TEMPLATE·保留窗回填决策冻结）+T-68 open 任一健康机+mf-rank/AH spawn 自愈观察\n")
with open(rp, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)
print("round report appended:", line[:80], "...")
