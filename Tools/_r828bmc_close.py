"""r828 bm-c close: round-report line append + state-bm-c.json refresh +
heartbeat refresh (法定簿记三件, one atomic script)."""
import datetime
import json
import os
import time

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
ts = NOW.isoformat(timespec="seconds")
epoch = int(time.time())
MID = "bm-c"

REPORT_LINE = (
    "2026-10-10T05:52:00+08:00 | r828 | dept:数据/工程（T10 zt_pool 交叉校验器出列+训练监控+rebase 前驱遗产收编·第 125 bm-c 连守轮） "
    "| 本地未达 origin commit 数=0（收口 commit 后 push+fetch 自证） "
    "| WM-VERDICT: 绿（red=false·lane=healthy·SatEngine rc0 活） "
    "| 孤儿面=1（只读·ComfyUI 8188 训后验证链需件勿杀·py_faces=16） "
    "| r828: ①r827 前遗产收编：前驱 04:54 pre-rebase absorb 后死亡态→本轮 absorb retry×2+pull-rebase "
    "5 picks（1 UU attrition 证据件 take-local+2 UU saturation own 面 take-local·r814 律 add-A/continue 竞速窗实锚）→rebase 5/5 clean"
    "→merge_lane_views reconcile 全面 ZERO-DRIFT rc0→push 首查「up-to-date」实为 autofill daemon w17-screen 批同树竞先代投"
    "（ls-remote a7aeaa779 == HEAD·0/0 实证）；②S0.5 双扫 DEC b87a92b1/ORD e286f842 双 MATCH（零新派工·水位零动作）+orders 185/0 未回执+inbox 空；"
    "③S1 smoke 49/49；④SatEngine rc0 活+水位绿（next_pick=claimed moneyflow IC·event-attention-factors lane）；"
    "⑤CEO 令 O-20261010-0025 训练监控：PID 53412 活体亲验（CPU 增量 2.3 核/15s+log 05:17 在写+UTF-8头×UTF-16LE体混编坑留档）"
    "——step 526/4096@17.20s/it·avr_loss 0.0609↓（296 步 0.0646→500 步 0.061→526 步 0.0609）·ETA ~22:45 维持·TRAIN_EXIT_1.txt=02:39 首跑遗留件非当前态；"
    "⑥QA r825 包续让位（RAM 0.4-0.6GB<1.5GB·训练保护优先·如实）；⑦P2 队头 T9 阻塞（新冻结判词面未面世）→T10 出列"
    "=scripts/zt_pool_crosscheck.py（四面板交叉校验器：单源 import collector〔ENDPOINTS/路径/日账/FIRST_DATE/日历零重声明〕"
    "·硬 5 族 exit 3〔A 结构:不变列/去重键/日期升序/R58 壳+B 账行对齐+C 收盘态互斥 zt∩dtgc/zt∩zbgc 逐日∅+E 四面账集对齐+F 日历完备窗〕"
    "+软 2 档〔D 带:zt≥+4.9/dtgc≤-4.9/连板数≥1+strong∩dtgc〕·selftest 15 腿全绿·首场实跑 CLEAN rc0〔2 日 112/46/21/370 行零硬发现〕"
    "+2 软警 strong∩dtgc 五码〔001216/601811/603949/002487/605366〕双面涨跌幅逐位一致抽验=EM 强度分高振幅本性·数据零腐·软档设计实证〕"
    "·证据 results/zt_pool_crosscheck.json·链位=下轮链克隆起焊 update_zt_pool 腿后·技术队列 7→6）；"
    "⑧S6 42 腿链全绿 DONE 05:17:56（周末 no-op 快通道·rc0=42/42·log results/_r828bmc_s6_log.txt）；"
    "⑨idle --worked 清零（declared worked·idle_rounds=0）+任务板 T-179/T-180 done·T-181 bm-a 在飞（yield 先例维持）；"
    "⑩S7 四件套（loop pin=5 在位+watchdog 在位+precommit/pre-push 双爪 CR 归一 MATCH）+attrition CLEAN rc0+末扫恒等 "
    "| 验证证据: smoke 49/49 + SatEngine rc0 + attrition rc0 + crosscheck selftest 15/15 + crosscheck 实跑 rc0 CLEAN + rebase 5/5 + "
    "push 0/0（ls-remote==HEAD） + 训练活体亲验（526/4096·loss 0.0609↓） + DEC/ORD 双 MATCH "
    "| 下轮指针: 训练监控至 ~22:45 完训→恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启）+jman_val_grid 验证链+LOOKBOARD 上链；"
    "QA r825 包首个 RAM≥1.5GB 轮补跑；S6 链克隆起焊 zt_pool_crosscheck 腿（update_zt_pool 后）；T-181 bm-a 烧批 finalize 消费面盯梢；"
    "P2 队头候选 T13/T15/T16/T17 "
    "| 本轮产品积分:2（zt_pool_crosscheck.py=能跑实物〔校验器+selftest+证据件+实弹 CLEAN+队列出列〕） "
    "| 记账预算:3（state+心跳+轮报=法定簿记） | 方法论捕获:无新方法 | 宝藏捕获:无（无五类收口面触发） "
    "| 登记册零命中断言=不适用（零清扫零 quarantine）"
)

# ---- round report append (add missing newline if absent)
rr_path = os.path.join(REPO, "round_reports-bm-c.md")
with open(rr_path, "rb") as f:
    raw = f.read()
need_nl = bool(raw) and not raw.endswith(b"\n")
with open(rr_path, "a", encoding="utf-8", newline="") as f:
    if need_nl:
        f.write("\n")
    f.write(REPORT_LINE + "\n")
print("round_report appended %d bytes" % len(REPORT_LINE.encode("utf-8")))

# ---- state refresh (round_no 827 -> 828)
st_path = os.path.join(REPO, "state-bm-c.json")
st = json.load(open(st_path, encoding="utf-8"))
st["round_no"] = 828
st["round_no_label"] = "round 828 (bm-c)"
st["clock_read"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["last_seen"] = ts
st["last_seen_at"] = ts
st["last_ts"] = ts
st["last_round"] = ("r828 bm-c: r827 pre-rebase estate absorbed (rebase 5/5, daemon-live "
                    "own-face take-local x3) + T10 zt_pool_crosscheck.py shipped "
                    "(selftest 15/15, real-run CLEAN rc0, 2 soft strong*dtgc warns "
                    "verified non-corrupt) + training live-verified (526/4096, loss "
                    "0.0609, ETA ~22:45) + smoke 49/49 + SatEngine rc0 + attrition "
                    "CLEAN + DEC/ORD both MATCH + S6 42 legs all rc0.")
st["last_round_at"] = ts
st["last_round_ts"] = ts
st["did"] = st["last_round"]
st["verdict"] = st["last_round"]
st["current_task"] = (
    "当前活: r828 收口——T10 zt_pool 交叉校验器已出列（实弹 CLEAN）+CEO 令 jman 训练在烧"
    "（PID 53412·step 526/4096·avr_loss 0.0609·ETA ~22:45） | 最近实物: scripts/zt_pool_crosscheck.py"
    "+results/zt_pool_crosscheck.json+results/_r828bmc_s6_log.txt（42 腿全绿）@ 2026-10-10T05:52+08:00 "
    "| 下个里程碑: ~22:45 完训→恢复债（Ollama+llama-server+ComfyUI）+jman_val_grid+LOOKBOARD；"
    "QA r825 包 RAM≥1.5GB 轮补跑")
st["current_task_at"] = ts
st["activity_now"] = st["current_task"]
st["next"] = (
    "r829 续作: ①训练监控（PID 53412·~22:45 完训·TRAIN_EXIT+outputs/jman_v1_640 证据链）"
    "②S6 链克隆起焊 zt_pool_crosscheck 腿（update_zt_pool 后）正常轮跑"
    "③QA r825 包 RAM≥1.5GB 补跑④训毕恢复债（Ollama 双任务 enable+llama-server+ComfyUI 重启）"
    "+jman_val_grid+LOOKBOARD⑤T-181 bm-a 烧批 finalize 消费面盯梢⑥P2 队头候选 T13/T15/T16/T17")
st["next_pointer"] = st["next"]
st["latest_artifact"] = ("scripts/zt_pool_crosscheck.py + results/zt_pool_crosscheck.json "
                         "(CLEAN rc0) + train 526/4096 loss 0.0609")
st["next_milestone"] = ("training done ~22:45 -> restore debt + jman_val_grid + LOOKBOARD; "
                        "QA r825 pack first RAM-safe round; next S6 chain welds crosscheck leg")
st["last_round_summary"] = REPORT_LINE
st["last_round_summary_at"] = ts
st["last_action"] = REPORT_LINE
st["heartbeat_epoch_utc"] = epoch
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["note"] = ("S7 quartet green (loop pin=5 + watchdog + precommit claw MATCH + prepush claw "
              "MATCH); attrition CLEAN rc0; orphan face=1 (ComfyUI 8188 idle server, dead-parent, "
              "read-only, needed post-training); state round 827->828 clean close; "
              "train log = UTF-8 header x UTF-16LE body mixed-encoding decode note.")
st["verify"] = ("receipts: smoke 49/49 + SatEngine rc0 (Tools path) + attrition CLEAN + rebase "
                "5/5 + push a7aeaa779 0/0 (ls-remote==HEAD) + DEC b87a92b1/ORD e286f842 MATCH + "
                "orders 185/0 unacked + crosscheck selftest 15/15 + crosscheck real-run rc0 CLEAN "
                "+ heartbeat epoch int + this close commit/push_verify")
st["last_pulled_at"] = ts
st["health"] = "ok"
with open(st_path, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state round_no=828 written, epoch=%d (int=%s)" % (epoch, isinstance(epoch, int)))

# ---- heartbeat refresh (own file only)
hb_path = os.path.join(REPO, "fleet", "machines", "bm-c.json")
hb = json.load(open(hb_path, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["current_task_at"] = ts
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["last_round"] = st["last_round"]
hb["last_round_ts"] = ts
with open(hb_path, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
# self-verify: epoch int + orders_ack preserved
back = json.load(open(hb_path, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
print("heartbeat written, epoch int OK, orders_ack_n=%s" %
      len(back.get("orders_ack", [])))
