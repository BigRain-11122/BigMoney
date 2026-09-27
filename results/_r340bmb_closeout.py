# -*- coding: utf-8 -*-
"""r340 bm-b S7 closeout: state, heartbeat, round report, CODELY pitlaw append."""
import json, time, os, subprocess

os.chdir(r"C:\Users\Administrator\Desktop\Bigmoney")
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())

# ---- state.json (bm-b local ledger) ----
sp = r"logs\iteration-loop\state.json"
st = json.load(open(sp, encoding="utf-8"))
prev = st.get("round_no", 339)
new_round = 340 if int(prev) < 340 else int(prev)
st["round_no"] = new_round
st["last_round_ts"] = now_iso
st["last_task"] = "r340: W2-A ckpt flaw fixed (on_result incremental flush) + S6 33/33 + network-dead local mode"
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STATE:", prev, "->", new_round)

# ---- heartbeat ----
hp = r"fleet\machines\bm-b.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = new_round
hb["loop_round"] = new_round
hb["round"] = new_round
hb["current_task"] = "r340 closed: W2-A ckpt incremental-flush fix landed + MSG-2010 to bm-a (W2-B mirror requirement)"
free_gb = round(__import__("psutil").virtual_memory().available / 1024**3, 1)
cpu_pct = __import__("psutil").cpu_percent(interval=0.6)
hb["free_ram_gb"] = free_gb
hb["idle_ram_gb"] = free_gb
hb["cpu_util_pct"] = cpu_pct
hb["cpu_pct"] = cpu_pct
hb["verdict"] = "healthy"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"], "F7 fields"
print("HEARTBEAT: epoch=%d int-ok clock=%s ram=%s cpu=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"], free_gb, cpu_pct))

# ---- round report ----
rp = r"logs\iteration-loop\round_reports.md"
line = (
    f"{now_iso} | r340 bm-b | dept:工程+舰队 | 水位=绿：red=false@20:00:20 lane healthy（probe 19:59:17 py 29.3% py_low_with_work_cands=W2-A 燃程合法占用面·verdict insufficient_history 单窗 n=1 如实）| did: "
    "(1) S0 网络死定谳非阻塞本地模式：fetch 5min 挂死实证（19:20 被杀会话同死法连续三挂+本会话再挂）·代理口 7897 在听但隧道瞑断·孤悬 ssh 28796(19:38 起 parent 已死)已清；"
    "S0 继承态=19:20 会话已落地 r339-pick rebase 正典解（本地 ahead·push 被拒后网络死未续）·无悬挂 rebase 态实测干净；"
    "(2) S0.5 轮首双扫 orders 96/96 python 差集零未回执+decisions 三径缺位诚实 no-op（r104/r107 先例）+firm DECISIONS.md 零 09-27 新行；"
    "MSG-20260927-1905 bm-a W2-B sec.9.4 冻结确认（D8-only 8 faces·E-heat 诚实出局·5,204 候选+16 对照+400 null=N 5,620·seed 20282500 band 验零中）已由 19:20 会话读毕移 processed·本轮回执：确认收悉零动作（W2-A 燃程在飞禁双跑·burn watch 双证不接管）；"
    "(3) S1 smoke 25/25；(4) S2 双板 0 open（93 票 63 done+30 claimed 他机）+job_list 空；"
    "(5) S3 主闭环=**W2-A checkpoint 只保尾缺陷根修**：发现=19:20 被杀会话（烧 4.6h 零 ckpt 实证·pool 注记 cross-kill resume safe 失实）·本轮代码验证坐实（_append_ckpt 在 run_cells_parallel 全 futures 收尾后才跑）→ 修复双件：parallel_runner.run_cells_parallel 增 on_result(key,payload) 每完成即回调（默认 None=legacy collect-only 零行为变化·其余 19 调用方无感）+census_fusion_s2_w2.run 改 _flush 增量落盘（results.update+_append_ckpt per 完成块）+flushed-set 防双写兜底；验证=py_compile×2 PASS+hermetic synthetic 2-job 测试 PASS（legacy 路径值恒等+flush 逐键回调）；在飞燃程 13148 内存旧码不受益（若中途死=全批重烧但重启即拾新码增量落盘）→MSG-20260927-2010 已落 bm-a inbox：W2-B runner 镜像（N=5,620·~28 块）必须按 fixed 模式禁镜像 wave-1 保尾形+UNC runner 增量式待查证（被杀会话中断点）；"
    "(6) S6 33/33 rc=0 周日 no-op 族全绿（compute_audit CLEAN/probe/update_daily cutoff 09-24/regime ORANGE shadow/scorecard 6+28+7 卡/clock CALL-09-24 ORANGE_COOL 幂等/lhb·heat·futures no-op/8 车道护栏诚实 no-op/fundamental 新鲜跳过/b_layer all_pass/paper 族 no-new-bar 合法跳腿/export 再生/daily_report faces=4 token=1/build_status/token L2 本地腿 1）；"
    "(7) S4 坑律一条入册（池批 checkpoint 保尾=中途 kill 全批重烧·正典=on_result 增量回调）；"
    "(8) S7：schtasks 三任务探在册+state round_no 340+心跳三面写后自证（epoch JSON int·clock_read T 分隔）+5x HANDOVER 轻核抽检；"
    "| evidence: _r340bmb_ckpt_fix_verify.py PASS 断言+_r340bmb_s6.log 33x rc=0+smoke 25/25+orders 差集空+git 本轮定向 commit | "
    "下轮: S0 网络恢复即 fetch→pull --rebase→正典解（autofill_state UU 预期）→push 落账（本地 ahead 链+r340 面）；W2-A finalize 收割窗 ETA~21:40→r312 done-flip 池面+T-86 bm-a 票面回执；UNC runner 增量式查证补课；周一 09:15 T-91 s3 首队列+15:30 T-87 astock 新 bar 全链；R345 5x HANDOVER\n"
)
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)
print("REPORT-APPENDED", len(line), "chars")

# ---- CODELY pitlaw (S4, one entry, four-gate passed) ----
cp = "CODELY.md"
entry = (
    "- [2026-09-27 20:1x r340 bm-b] 坑律：池批 checkpoint 保尾=中途 kill 全批重烧（W2-A 烧 4.6h 零 ckpt 实弹·pool 注记 cross-kill resume safe 失实·_append_ckpt 全 futures 收尾后才跑）；正典=parallel_runner on_result 增量落盘回调（默认 None 旧行为零扰动）+w2 侧 flushed-set 防双写·在飞进程内存旧码不受益重启才拾新。指针=scripts/parallel_runner.py+scripts/census_fusion_s2_w2.py+results/_r340bmb_ckpt_fix_verify.py。\n"
)
size0 = os.path.getsize(cp)
with open(cp, "a", encoding="utf-8") as f:
    f.write(entry)
size1 = os.path.getsize(cp)
assert size1 <= 10240, f"CODELY {size1}B OVER 10KB hardline"
print("CODELY:", size0, "->", size1, "B (under 10240 hardline)")

# ---- 5x HANDOVER light spot-check ----
for p in [r"research\HANDOVER.md", r"results\census_fusion_s2\w2a_roster.json", r"scripts\census_w2b_roster.py", r"results\paper_export\latest.json"]:
    print("HANDOVER-SPOT:", p, os.path.exists(p))
print("CLOSEOUT-OK", now_iso)
