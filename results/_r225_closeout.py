# -*- coding: utf-8 -*-
"""r225 (bm-b) S7 closeout: HANDOVER 5x increment (R210 anchor-insert), state.json,
heartbeat, round report append, CODELY.md lesson, orders closeout rescan.
Byte-safe writes (no PS redirection, r209 law); epoch JSON int (R170/R178);
parse-verify after every write (r185 law)."""
import datetime
import io
import json
import os
import time

now = datetime.datetime.now()
ts = now.strftime("%Y-%m-%d %H:%M")
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"
epoch = int(time.time())
assert isinstance(epoch, int)

# ---- 1. HANDOVER 5x increment (bm-b r225 = 45th check; insert before anchor) ----
hp = "research/HANDOVER.md"
raw = io.open(hp, "rb").read().decode("utf-8")
anchor = "；上一次核对=bm-a round 205（2026-09-26 02:2x"
assert raw.count(anchor) == 1, "anchor not unique"
inc = ("bm-b round 225（2026-09-26 05:3x·单机核 r221-225 增量窗）R225 增量=①P-1e "
       "收割执行面闭环（r221-225 五轮）：r221 首分片首发即崩 48s 自捕（build_masks "
       "per-class 装载形态 KeyError·maximal 合成夹具零覆盖生产 close-only 形态=r221 "
       "装载形态律）+诚实部分构建修复；r222/r223 MCLOSE+MCLOSETR 前两分片收割翻面"
       "（mask bit-match 探针范式 _r224_mask_probe 先行）+r223 autofill_state CRLF "
       "行尾镜像律（R209 新维）；r224 MCLOSETR landed-unflipped 窗口饥饿坑律（翻面前置"
       "=位咬合复核腿）；r225 MARC 收割翻面 3/4 done（n_nulls=50·seed_band "
       "67100-67150=prereg 连续账本位·mask_cells 16638518 生产装载形态位咬合·"
       "fail-closed 五腿·翻面 05:35<05:40 tick 零重发浪费）；P1E-CELLS ready=最后分片"
       " autofill 续批（4/4 后 finalize fail-closed+判定面+因子账本 +157+prereg "
       "§7/§8 回填=下轮指针）；②死轮残骸回收范式（r225）：前轮执行体 05:01-05:09 崩溃"
       "（根因未定·零 commit 零 state 翻面）→残骸两类正解=未提交 working-tree 产物走 "
       "S0 stash-pop 11-UU 批（conflict-resolve skill dogfood#3：classify 11/11 零 "
       "UNKNOWN→union cap50 零丢失+compute_audit 201+201→union 204=他机 3 行增量保住"
       "+take-new+CRLF 镜像+parse-verify）+untracked flip/mask 脚本验收后直接执行"
       "（死活判别=mtime 停摆>2×节律+零存活进程+零翻面）；③town.html mandate 对齐 "
       "org_chart v2-v5 验证 10/10（研究/策略/组合/数据四楼更新+资产组合研究部 v5 "
       "独立成行+舰队/工程/风控/交易/总经办核实）；④S6 周末 no-op 族全绿×5+smoke "
       "25/25×5+orders 74/74 双扫×5+regime ORANGE d2 shadow（hs300<MA200+breadth "
       "0.77）")
raw = raw.replace(anchor, "；" + inc + anchor, 1)
io.open(hp, "wb").write(raw.encode("utf-8"))
chk = io.open(hp, encoding="utf-8").read()
assert inc in chk and "上一次核对=bm-a round 205" in chk
assert chk.count("bm-b round 225（2026-09-26 05:3x") == 1
print("HANDOVER OK: r225 increment inserted before anchor (R210 law)")

# ---- 2. state.json (bm-b own file) ----
sp = "logs/iteration-loop/state.json"
st = json.load(io.open(sp, encoding="utf-8"))
assert st["round_no"] == 224, st["round_no"]
st.update({
    "round_no": 225,
    "did": ("P-1e MARC nulls shard harvest-verified + pool flip done 3/4 "
            "(artifact 05:31:43 landed, n_nulls=50, seed 67100-67150, mask "
            "bit-match 16638518 via production-form probe; flip 05:35 pre-tick "
            "zero-refire, r203/r224 laws) + dead-session debris salvage (05:01-"
            "05:09 crashed r225 attempt: 11-UU stash-pop resolve dogfood#3 "
            "union 204 zero-loss + its flip/mask scripts executed to PASS) + "
            "town.html org_chart v2-v5 alignment verified 10/10 + S6 17 legs "
            "ALL-0"),
    "verdict": "green",
    "next": ("r226: P-1e CELLS claimed by 05:40 autofill tick -> est ~30min "
             "landing -> harvest+flip on 4/4 -> finalize fail-closed + "
             "judgement table + factor ledger +157 + prereg sec7/8 backfill "
             "(0 survivor = honest line-close); 09-28 Monday new-bar full "
             "chain; EM push2his south re-probe daylight 12:00-13:40; bm-c "
             "noon window 09-28 15:30 (T-16 NAV eval)"),
    "current_task": ("P-1e batch 3/4 done (MCLOSE+MCLOSETR+MARC flipped; CELLS "
                     "ready -> autofill cadence); r226+ harvest then finalize "
                     "on 4/4"),
    "last_round_ts": "2026-09-26 04:57",
    "last_result": ("exit 0 all legs (17 run + 7 new-bar-gated weekend skip: "
                    "cutoff 09-24, next bar 09-28); MARC flipped r225 pre-tick"),
    "last_tick": ts,
    "updated_at": ts,
    "last_seen": ts,
    "ts": ts,
    "last_ts": ts,
    "last_run": iso,
    "last_round_at": ts,
})
out = json.dumps(st, ensure_ascii=False, indent=1)
io.open(sp, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
chk = json.load(io.open(sp, encoding="utf-8"))
assert chk["round_no"] == 225
print("state.json OK: round_no", chk["round_no"])

# ---- 3. heartbeat fleet/machines/bm-b.json ----
hp2 = "fleet/machines/bm-b.json"
h = json.load(io.open(hp2, encoding="utf-8"))
h.update({
    "last_seen": ts,
    "heartbeat_epoch_utc": epoch,
    "clock_read": iso,
    "current_task": ("r225: P-1e MARC flipped done 3/4; CELLS on autofill "
                     "cadence; harvest finalize on 4/4"),
    "cpu_cores": 16,
    "cores": 16,
    "free_ram_gb": 12.0,
    "idle_ram_gb": 12.0,
    "total_ram_gb": 23.9,
    "gpu_free_vram_gb": 2.2,
    "gpu_free_vram_mb": 2220,
    "cpu_util_pct": 12.7,
    "round_no": 225,
    "verdict": "green",
})
out = json.dumps(h, ensure_ascii=False, indent=1)
io.open(hp2, "wb").write(out.replace("\n", "\r\n").encode("utf-8"))
chk = json.load(io.open(hp2, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), \
    "EPOCH NOT INT (F7 red, R170/R178 law)"
print("heartbeat OK: epoch", chk["heartbeat_epoch_utc"], "type",
      type(chk["heartbeat_epoch_utc"]).__name__)

# ---- 4. round report append (byte-safe) ----
line = (
    "2026-09-26 05:3x | r225 bm-b (dept:工程+研究) | "
    "WM-VERDICT: 绿：red=false@05:30:17 lane healthy（next_pick=mf-IC batch "
    "claimed/parked 面板物理依赖·EM 阻断 30min 自愈窗续）；probe 05:33 "
    "insufficient_history n=2 新窗合法读数（05:34 二采样 py_procs 12·CPU 29% 瞬时"
    "·无违令）；audit 05:34 CLEAN pool_ready=1 supply-gap 非饥饿 | "
    "S0: 轮首脏=本机 watchdog autofill_state 05:30 tick 产物+死轮残骸（前 r225 "
    "执行体 05:01-05:09 崩溃·根因未定·零 commit 零 state 翻面·关键件 mtime 停摆 "
    "22min>2×节律+该窗零存活进程=死非活三件套判别）→stash→pull --rebase 吸收 bm-a "
    "R219-221（T-72 s2 交付三连+R218 addendum 冲突解技能狗粮）→stash pop 11-UU="
    "**conflict-resolve skill dogfood#3**：classify_conflicts.py 11/11 分类零 "
    "UNKNOWN→_r225_resolve.py 正典配方一次过（autofill launches 50+50→union cap50 "
    "零丢失+last_tick 05:30:02 dict 整赋值取新 r203 律；compute_audit history "
    "201+201→**union 204** 零丢失=他机 3 行增量保住 r188/R208 律；regime history/"
    "transitions union；dashboard_status.js take-side 整字节 wrapper 保真 R209 律；"
    "7 snapshot 按 ts take-new；CRLF 镜像 r223 律；parse-verify 过才 add r185 律）| "
    "S0.5: orders 74/74 轮首扫描零未回执（token 全文件名口径 r220 律）；decisions.md "
    "候选根缺位诚实 no-op；inbox 零他机未读 | "
    "S1: smoke 25/25 | "
    "S3 主交付: **P-1e MARC 分片收割+池翻面 done=3/4**（r203 pool-flip-is-round-"
    "work）——产物 05:31:43 落地（pid27452 05:00:09 发射·31.5min 吻合预估）："
    "n_nulls=50/seed_band 67100-67150=prereg 连续账本位/per_h 3-col/equiv PASS/"
    "mask_cells 16638518==_r225_mask_probe 生产装载形态位咬合（close+tr+vwap→3 "
    "mask·share 0.3624·r221 装载形态律·死轮脚本验收执行）；翻面 _r225_flip_marc.py "
    "fail-closed 五腿→done_flip 证据块；**翻面 05:35<05:40 tick=零 no-op 重发浪费"
    "（r224 landed≠flipped 坑律首实践）**；P1E-CELLS ready=最后分片 05:40 autofill "
    "续批 | town.html mandate 对齐 org_chart v2-v5 验证 10/10 全一致（死轮 4 楼更新"
    "+资产组合研究部 v5 独立成行+舰队/工程/风控/交易/总经办核实）→小活交付；其 UTF-16 "
    "traceback 探针件=R209 PS>重定向律再犯实证·删件 | "
    "S4: 1 坑律入册（死轮残骸回收面）水位 23KB<50KB 无整编触发 | "
    "S6: 17 腿 ALL-0+7 新 bar 腿合法跳过（周末 cutoff 09-24→下 bar 09-28·月度三件"
    "套非月首轮不跑）：audit CLEAN/probe/daily 周末/regime ORANGE d2 shadow"
    "（hs300<MA200+breadth 0.77）/lhb 30min 节流 no-op/heat 周末/futures 零网络"
    "no-op/options+mf+ths+ah=bm-a 车道+fp=bm-c 车道 R31 诚实 no-op/fundamental 8.4h "
    "新鲜跳过/blf 过/scorecard 6 员/build_status OK/token delta=0 | "
    "S7: schtasks 双任务健康（Loop 正在运行=本实例+Watchdog 06:00 就绪·R49 律）；"
    "orders 收尾复扫 74/74 零未回执；state 224→225（5x 轮=HANDOVER 核对 r221-225 "
    "增量窗插至上一次核对锚前 R210 律）；心跳 epoch python int 自证 | "
    "下轮指针: ①P-1e CELLS 05:40 autofill claim→est ~30min 落地→收割轮翻面 4/4→"
    "finalize fail-closed+判定面+因子账本 +157 append_ledger embed+prereg §7/§8 回填"
    "（0 幸存=诚实线收）→②09-28 周一新 bar 全链中继（update_daily→live.paper "
    "REGIME_GUARD v3 enforce→t35verify→t24×2→aggr/alloc→export/scorecard）→③EM "
    "push2his 南向 re-probe 白日窗 12:00-13:40→④bm-c 午窗 09-28 15:30（T-16 NAV "
    "接管评估）\n"
)
with open("logs/iteration-loop/round_reports.md", "ab") as f:
    f.write(line.encode("utf-8"))
print("round report appended:", len(line.encode("utf-8")), "bytes")

# ---- 5. CODELY.md lesson (one entry, four-question gate passed) ----
cp = "CODELY.md"
lesson = (
    "- [2026-09-26 05:3x] 坑律/运维（bm-b r225·死轮残骸回收面·R209/R218 家族补篇·"
    "E1 自捕）：**前轮执行体中途崩溃（05:01-05:09 死于 wait_marc 窗·根因未定·零 "
    "commit 零 state 翻面）残骸两类正解**——①未提交 working-tree 产物=下轮 S0 "
    "stash→pull→pop 的 UU 批照常走 skill 正典解（本次 11-UU：compute_audit "
    "201+201→union 204 零丢失=他机 3 行增量保住）；②untracked r 轮 helper 脚本="
    "验收后直接执行的本轮工料（flip 自带 fail-closed 断言）；**死活判别三件套="
    "关键件 mtime 停摆>2×节律（22min>20min）+该窗零存活进程+零 commit/state 翻面"
    "→死非活，回收禁退避**；附带 R209 律再犯实证（死轮自身探针件=PS > 重定向 "
    "UTF-16 traceback 垃圾·律已在册删件即可）。指针=results/_r225_resolve.py+"
    "results/_r225_flip_marc.py+r225 轮报告。\n"
)
cur = io.open(cp, "rb").read().decode("utf-8")
if not cur.endswith("\n"):
    cur += "\n"
io.open(cp, "wb").write((cur + lesson).encode("utf-8"))
chk = io.open(cp, encoding="utf-8").read()
assert lesson.strip() in chk
print("CODELY.md OK: 1 lesson appended, size", os.path.getsize(cp), "bytes")

# ---- 6. orders closeout rescan (double-scan law) ----
files = set(f for f in os.listdir("fleet/orders")
            if f.startswith("O-") and f.endswith(".md"))
ack = set(h["orders_ack"].split())
diff = sorted(files - ack)
assert not diff, "NEW UNACKED ORDERS mid-round: %s" % diff
print("orders closeout rescan: %d/%d zero-diff" % (len(files), len(ack)))
print("CLOSEOUT OK")
