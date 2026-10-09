# r812 bm-b closeout: state.json + heartbeat + round report + C7 MSG move
# epoch must be JSON int (R170/R178 law), clock ISO8601 with T separator (R262 law)
import json
import os
import shutil
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
EPOCH = int(time.time())

STATE = os.path.join(ROOT, "state.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

R812_NOTE = ("r812: T-180 C1 regime-gate dual-arm evidence face landed "
             "(scripts/regime_gate_dualarm.py selftest 18/18, bm-b lane guard, "
             "results/regime_gate_dualarm/DUALARM-2026-09-30.json+latest.json, "
             "S6 chain weld) + D-19 watermark write-side composite defect found & healed "
             "(r811 stored = true-8-hex + r810 phantom tail splice; true full SHA-1 "
             "a3ea37bd70fd5acc83bcf51939874cffd59f1811; content zero-change proven) + "
             "O-20260909-1246 receipt (tech queue 5->10 + engine P2/P3 needle) + "
             "O-20260909-2150 steps audit receipts + CODELY cold-ptr merge "
             "(main 30,744->24,179B)")

st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = 812
st["round_no_label"] = "r812"
st["note"] = R812_NOTE
st["last_round_at"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["last_seen"] = NOW
st["clock_read"] = NOW
st["updated_at"] = NOW
st["last_decisions_sha"] = "a3ea37bd70fd5acc83bcf51939874cffd59f1811"
st["last_decisions_at"] = "2026-10-10T02:56:00+08:00"
st["last_decisions_read_at"] = "2026-10-10T02:56:00+08:00"
st["last_orders_read_at"] = "2026-10-10T02:56:00+08:00"
st["last_decisions_sha_method"] = (
    "r812 HEAL: r811 stored value was a composite (true SHA-1 first-8-hex + r810 "
    "phantom retained 32-hex tail, prefix-only verification at heal time); r812 "
    "byte-safe python full-string recompute a3ea37bd70fd5acc83bcf51939874cffd59f1811; "
    "content zero-change proof: last touch 00:55 < r811 read 02:10, origin/main "
    "6a7c4f5 both windows, ORD watermark byte-identical; evidence "
    "results/_r812bmb_d19_read.json; pit lesson direct-written pit-protocol-d19.md")
st["last_orders_sha_note"] = (
    "r812: ORD watermark e286f84287331c99e5c2d3c4dda391617f301a99 SHA-1 40-hex "
    "raw-blob PIN r537, byte-identical recheck this round; composite-defect heal "
    "DEC-side only, evidence results/_r812bmb_d19_read.json")
st["did"] = R812_NOTE
st["verdict"] = ("green: smoke 49/49 + dualarm selftest 18/18 + S6 chain 31 legs rc0 "
                 "+ attrition CLEAN + group workspace audit PASS; watermark red-card "
                 "adjudicated (open tickets T-180/T-181 = this round claimed-and-done "
                 "work; astock refresh in-flight network-bound lawful); DEC watermark "
                 "healed to true full string")
st["current_task"] = ("r813: T-181 thermo-overlay prereg draft (pre-read pointers in "
                      "ticket) + O-20261009-1105 @bm-b convertible-bond criteria scan "
                      "(due <=10-16 12:00) + H3 8G-quantized install window (disk GO "
                      "446.6GB, three-gate law, bm-c receipt check) + waiting: astock "
                      "refresh closeout / fleet memory zhengben landing on origin")
st["next"] = st["current_task"]
json.dump(st, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(STATE, "a", encoding="utf-8").write("\n")

hb = json.load(open(HB, encoding="utf-8"))
hb["round"] = 812
hb["round_no"] = 812
hb["now_active"] = ("r812: T-180 dual-arm evidence face landed (script+selftest 18/18"
                    "+artifact+S6 weld) + D-19 composite watermark healed + 1246 "
                    "tech-queue top-up & engine needle + 2150 step receipts")
hb["current_task"] = st["current_task"]
hb["task"] = "T-180 done / T-181 claimed (prereg draft next window)"
hb["latest_artifact"] = ("r812: scripts/regime_gate_dualarm.py + "
                         "results/regime_gate_dualarm/DUALARM-2026-09-30.json + "
                         "latest.json (03:0x) + D-19 heal receipt "
                         "results/_r812bmb_d19_read.json + cold-merge receipt "
                         "results/_r812bmb_coldptr_merge.json (CODELY main "
                         "30,744->24,179B)")
hb["next_milestone"] = ("T-181 thermo-overlay prereg draft r813 + convertible-bond "
                       "criteria scan <=10-16 12:00 + H3 8G install (disk GO) <= "
                       "next windows")
hb["verdict"] = st["verdict"]
hb["last_action"] = ("r812: T-180 landed+done, T-181 claimed; D-19 composite "
                     "watermark defect adjudicated+healed (3rd face of r810 family); "
                     "1246 receipt (tech queue 10/10 + P2/P3 engine needle); 2150 "
                     "steps 1/2/5 receipts (FleetLink in-service, audit PASS, "
                     "memory-union waiting zhengben, H3 disk GO); orders 183/183 "
                     "zero unacked both sweeps; C7 MSG closed (3/3 satisfied, moved "
                     "to processed)")
hb["last_round_at"] = NOW
hb["last_seen"] = NOW
hb["updated"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = EPOCH
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = ("r812 probe: 21 lawful py faces 0 orphans; astock refresh "
                          "lock alive = T-87 bm-b lane full-universe pull in-flight, "
                          "lawful wait chain")
json.dump(hb, open(HB, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(HB, "a", encoding="utf-8").write("\n")

# epoch int self-verify (R170/R178 law)
chk = json.load(open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "epoch must be int"
chk2 = json.load(open(STATE, encoding="utf-8"))
assert chk2["round_no"] == 812
print("state+heartbeat OK epoch=%d round=812" % EPOCH)

# round report append
RR_LINE = (
    "2026-10-10T03:41:00+08:00｜r812｜dept:研究（T-180 政体门双臂接线）+dept:工程（S6 链焊腿+引擎针）"
    "｜watermark verdict=红（py_low_with_work_cands 02:53 探针=真根因板工非池批：open 票 T-180/T-181 未认领"
    "=本轮首动作即认领即开工，红牌所指活=本轮已消费收口；astock 5217 刷新在途网络型低 CPU 合法〔lock alive〕）"
    "｜本轮主产出=①T-2026-10-10-180 完结（C1 政体门双臂证据面：scripts/regime_gate_dualarm.py〔selftest 18/18"
    "·bm-b 车道护栏·exit 0/2/3 契约〕+results/regime_gate_dualarm/DUALARM-2026-09-30.json+latest.json〔指数臂 "
    "BEAR@2026-09-30 n=3289×情绪臂 @2026-09-22 sealed67/touched562/seal_rate11.9%·asof 失配诚实披露"
    "·REGIME_STYLE_MATRIX_V1 §1 契约回执 pass 随件〕+S6 链焊接 Tools/iteration_prompt.txt〔thermo_build→rev_osc "
    "之间·下轮生效〕·零判据零干预纪律携带·判据面=T-181 预注册正门）②D-19 水印写侧拼接缺陷定谳+治愈"
    "（r811 存储水印=真 8 位前缀+承 r810 幻影尾 32 位拼接串·python 全串真值 a3ea37bd70fd5acc83bcf51939874cffd59f1811 "
    "复算·内容零变化实证=末触 00:55<读时 02:10+origin 6a7c4f5 双窗恒等+ORD e286f842 字节恒等→state 水位换真全串"
    "+收据 results/_r812bmb_d19_read.json+坑律直写 pit-protocol-d19.md〔r747 先例·r810 族第三面〕）"
    "③O-20260909-1246 回执腿（tech 队 5<10 低配→补 T13-T17 五条真实候选〔D-19 写侧守卫/红牌判读分桶/"
    "thermo 车道判定/dualarm 适配器/令扫自动化〕=10/10 合规+引擎 P2→P3 队头抽取针焊入 S3〔self-drive §1·1246 "
    "修复派单 b〕·state/queue 三文件 r804 bm-c 已建核实）④O-20260909-2150 步①②③⑤实况回执（步① FluxGroup-"
    "FleetLink 任务在役 5min 节律=接线已收口；步② fleet-workspace-audit v1.1 集团树 VERDICT PASS〔A sync=live "
    "tip 6a7c4f5·C 冲突零·E 垃圾零·bigmoney behind5=机队并发瞬态下轮 S0 自吸〕快照 .codely-cli/patrol/"
    "fleet-workspace-audit-BIGMONEY.json·回执不改集团台账（本司禁写律·集团收取面拾取）；步③ 记忆并集=正本 "
    "CODELY-fleet-global.md 未落 origin=待 bm-a 首 poke 等待态如实；步⑤ H3 8G 磁盘 GO〔C: 446.6GB〕·装机延后窗"
    "〔三闸律+bm-c 回执核后〕）⑤C7 MSG ③腿收口（DEC 全串真值治愈=三请求全满足·MSG 移 processed/）"
    "⑥CODELY 主件冷指针合并批（treasure_guard prescan rc3 留痕·r592/r639/r644/r651/r654/r666/r667/r670/r672/r679 "
    "十行 7,058B verbatim 入 archive 202610.md『热冷整编 2026-10-10 r812 bm-b 窗批』节·主件 30,744→24,179B 帽下 "
    "6.5KB 余量·合并指针行在位·收据 results/_r812bmb_coldptr_merge.json）｜孤儿面=0（21 合法 py 面）"
    "｜本地未达 origin commit 数=0（commit 后 push+ls-remote 自证）｜下轮指针=r813：T-181 prereg 起草"
    "（预读指针已留票面）+O-20261009-1105 @bm-b 可转债扫描（due ≤10-16）+H3 8G 装机窗+等待面=astock 刷新收口"
    "/记忆正本落 origin"
)
b = open(RR, "rb").read()
eol = b"\r\n" if b.count(b"\r\n") > (b.count(b"\n") - b.count(b"\r\n")) else b"\n"
if not b.endswith(eol):
    open(RR, "ab").write(eol)
open(RR, "ab").write(RR_LINE.encode("utf-8") + eol)
print("round report appended", len(RR_LINE.encode("utf-8")), "B")

# C7 MSG move to processed
src = os.path.join(ROOT, "fleet", "inbox",
                   "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md")
dst = os.path.join(ROOT, "fleet", "inbox", "processed",
                   "MSG-20261009-173x-bmc-bmb-C7ORD-DECLAG.md")
if os.path.isfile(src):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst)
    print("MSG moved to processed")
print("CLOSEOUT OK")
