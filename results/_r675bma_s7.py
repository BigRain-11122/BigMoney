"""r675 bm-a S7 closeout: state bump + heartbeat + round report + CODELY append
(程序化写+写后自证 per r641/r645 laws)"""
import json, time

# 1) state-bm-a.json round_no 674 -> 675
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
st["round_no"] = 675
st["loop_round"] = int(st.get("loop_round") or 0) + 1
st["last_round"] = "r675"
st["last_round_at"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
st["last_round_ts"] = int(time.time())
st["current_task"] = "r675 closeout: theme_persist selftest red->green (stale guards) + THEME-METHODOLOGY-R1 S5 judge-verdict sentence"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
st2 = json.loads(open(sp, encoding="utf-8").read())
assert st2["round_no"] == 675, "state bump verify"

# 2) heartbeat fleet/machines/bm-a.json (epoch int + clock T-separator + verdict)
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["last_seen"] = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
hb["round_no"] = 675
hb["loop_round"] = st["loop_round"]
hb["current_task"] = "idle-post-r675 (theme line both faces closed; next: trial-labor standing supply scan)"
hb["verdict"] = "healthy"
hb["last_action"] = "r675: persist selftest red->green + R1 report S5"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
hb2 = json.loads(open(hp, encoding="utf-8").read())
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in hb2["clock_read"], "clock must be T-separated"

# 3) round report line (三行产品面 per 产品优先律 #5)
rr = "round_reports-bm-a.md"
ts = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
line = (f"{ts} | r675 (bm-a) | watermark=green (red=false; next_pick moneyflow-IC claimed, blocked on panel) | "
        "当前活: 题材线双面已闭环, 本机 idle, 常供线下批扫描 | "
        "最近实物: docs/theme_report/THEME-METHODOLOGY-R1-20261004.md 12:0x 重生(5句 missing=0, S5=T-167 judged_negative 族级关线全数字) + scripts/theme_persist_p1.py 修红(11/11 PASS) | "
        "下个里程碑: trio NULLS (bm-b 在飞 V/Q/D) 落地后 fund 三族判决收口, 窗≤48h | "
        "DONE-1 修红: theme_persist_p1 selftest 两处陈旧守卫假阳性(钝seed带距检查[r667 judge带注册后击穿]→extent-aware带隙法对齐 judge 正典; 整文件substring语法去重[自烧后自撞]→gen=行三元组扫描+own-burn守卫移run意图位, run 面防双烧闸实证拒) | "
        "DONE-2 产品: THEME-METHODOLOGY-R1 报告吸收 T-167 判负批 S5 句(TJ-SOLO-x1 sharpe 0.2735<技能线1.3172·四面全false·DSR 0·PBO 0.429·judged_negative) CEO 收口章完整 | "
        "S0: FF merge origin 9 commits + crash_fuse origin-base checkout+sync_face settle(墓碑恢复11:56:33 bm-a+残留sig压制) | S0.5: orders 153/153 acked x2扫 | D-19 MATCH (sparse clone fallback r631 配方) | "
        "S1 smoke 48/48 | S6 36/36 rc0 (CEO faces 刷新: daily_report REPORT-2026-10-04 + LIVE-2026-10-04 ORANGE cap50% + dashboard) | attrition CLEAN | S7 self-heal 4/4 | 本地未达 origin commit 数=0 (push 后自证)\n"
        )
with open(rr, "a", encoding="utf-8", newline="\n") as f:
    f.write(line)

# 4) CODELY.md one memory entry (入口四问门: 教训优先/一条一事/≤1.5KB)
cm = "CODELY.md"
entry = ("- [2026-10-04 12:1x r675 bm-a] 后冻结批 registry 增量击穿先冻结批钝守卫假阳性族（THEME_PERSIST_P1 复现性双红实弹·判负批审计面）：先冻结批（r657）runner 守卫按当窗 registry 写死钝判据（种子带钝基距≥10000/语法去重整文件 substring），后冻结批（r667 judge 带 20585000 入 registry+本批自烧录 ledger 行）使钝守卫在批后 selftest 永久红——破坏已闭批可复跑性（审计面）。正法=守卫一律建模增量面：①种子带 disjoint 检查=extent-aware 带隙法（本带 extent 从模块 substream map derive+他带保守 3000+带隙≥2000，judge 侧 _seed_band_check 同法正典）②语法去重=gen= 行三元组定向扫描（消费声明行=申报例外）+own-burn 防双烧守卫移 run 意图位（selftest 永绿·run 面实证拒）。How to apply：新预注册冻结窗的守卫禁用「对共享 registry 全量钝距离/整串 substring」类判据——一切跨批共享面（SEED_REGISTRY/TRIAL_GRAMMAR_LEDGER）守卫按「本批语义 extent+增量行定向」写；批闭后 selftest 必须可复跑（exploration 批审计律）。\n")
with open(cm, "a", encoding="utf-8", newline="\n") as f:
    f.write(entry)

print("STATE ok round_no=675; HEARTBEAT ok epoch=%d; REPORT line appended; CODELY entry appended" % hb2["heartbeat_epoch_utc"])
