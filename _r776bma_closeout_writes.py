# -*- coding: utf-8 -*-
"""r776 bm-a closeout writes: CODELY pit entry + round report line + state
round_no + heartbeat (fresh read-modify-write per multi-writer law)."""
import datetime
import json
import time

# 1) CODELY.md pit entry (one entry, <1.5KB)
p = "CODELY.md"
src = open(p, encoding="utf-8").read()
assert "append_ledger 返回块丢弃坑" not in src
entry = (
    "\n- [2026-10-06 14:0x r776 bm-a] **append_ledger 返回块丢弃坑（THEME_DEEPEN_P1 首跑实弹·当场抓回零账本伤害）**："
    "`science_gates.append_ledger(batch, trials, file_name, evidence_cutoff)` 不写任何中央文件——它**返回** dict 块，"
    "由调用方**嵌入本批 results JSON 的 `trials_ledger` 键**；链头 `ledger_head()` 是数据驱动扫描（glob results/**/*.json 找各批件内的 trials_ledger 块取 max total）。"
    "runner 调用后丢弃返回值=批件零入账（本窗实弹：9,401 行首跑不可见，账本头纹丝不动 741,411 才暴露）。"
    "正法=①payload[`trials_ledger`]=sg.append_ledger(...) 在 write 之前嵌入②write 后断言 total==prev+trials③跑后核 ledger_head() 的 file 指向本批件。"
    "How to apply：一切新批 runner 的账本腿照此三步写死；探针后核链头 delta=入账自证面。\n"
)
open(p, "w", encoding="utf-8").write(src + entry)
print("CODELY pit appended, new size:", len((src + entry).encode("utf-8")))

# 2) round report line (bm-a own file)
now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
rr = (
    f"\n{now} | round 776 (bm-a, dept:研究·T-173 题材深化批冻结→建 runner→烧→报告首版全闭环) | "
    "[watermark verdict: 绿（red=false·lane healthy·probe py_low_board_clear 合法白名单=板全闭环+W16 已冻结在引擎队）] | "
    "当前活: T-173 题材深化批已烧完，48h 首版报告提前交付（due 10-08 午，今 10-06 已出） | "
    "最近实物: docs/theme_report/THEME-DEEPEN-R1-20261006.md（白话首版报告·14:0x 前落盘）+ "
    "results/theme_deepen_p1/ 六件（runner 21.4s·ledger 741,411→750,812 +9,401）+ "
    "research/THEME_DEEPEN_P1_PREREG.md（冻结 66d5ec5d4→§7/§8 同窗回填）+ "
    "scripts/theme_deepen_p1.py（selftest 14/14） | "
    "下个里程碑: ①CEO 消费题材报告（若点头 THEME_COOP_P1 配合面批开工·窗 ≤10-10）②T-174 核心仓验证收口批 prereg（唯一必烧项 ≤300 试·due 10-09）③T-175 外源目录 R1+T-176 排除书正典化（零烧）④W158 引擎烧录收尾（在飞）·窗 ≤48h | "
    "做了什么: S0 autostash rebase 吸收 bm-c r620（disjoint 面零冲突）+ orders 双扫零未回执 + D-19 dec hash 不变零动作（K: 缺席→本机集团树实径 fallback 走通 C:\\Users\\sjs20\\Desktop\\FluxGroup fetch+origin blob）+ "
    "T-173 主线：prereg 起草（8 扩容事件数据锚定枚举+24 行五类引入分类学+波位散户跟随规则+全起点分布 D-41 §1.3+逐波位独立判）→种子带 20600000 同窗注册（碰撞扫描零命中）→禁开方向闸首跑 BAN-04「常数网格」措辞假命中→M6 措辞归正复跑 ADMIT→冻结 commit+push 66d5ec5d4→"
    "runner scripts/theme_deepen_p1.py 同窗建成（面1 扩容管线+交叉表/面2 跟随路径+穷举分布+置换/符号检验/合成路径+D6）→selftest 14/14→"
    "首跑暴露两工程 bug（开放尾波 break_date=None 崩+append_ledger 返回块未嵌入=账本零入账）→修复→确定性重跑 verdicts 逐位恒等→"
    "读数：W1 唯一正面 +19.2%/73%（置换 p=0.0165 过线）·W2 −4.8%·W3+ −1.9% 判负照报·「涨20%才启动」单独未过硬门槛（p=0.082 方向倾向如实披露）·"
    "扩容 6/8 落选（5 员零点火触发=探针复核真严格性：银行全史零点火/创新药 max20td +17.2%<20%——慢热配置型引入不产生注意力点火签名=面1 真发现+TCM 窗前史落选预测命中）·"
    "交叉表：产业周期 6/6 long·海外映射 3/3·本土技术 3/3·政策 3/4·事件催化 1/2（小 n 禁方向性结论照报）·D6 max|corr| 0.164 零并族 | "
    "§7/§8 同窗回填（预测对账：a✓b✓半中c✓d△半对=点火规则对慢热型系统性漏检为本批最大教训 e✓f✓）→gate_attrition 追加一行（kind=measurement）+attrition scan CLEAN→"
    "E37 方法论卡（波位分层跟随测量法）+TREASURE_REGISTRY 出入记录行→CEO 报告白话首版落盘→"
    "S6 链 38 腿 rc0（dualrun streak 51 零漂移·compute_audit FLAG:gpu_unauthorized=池 worker 图形上下文假信号 util 0% 无 CUDA 计算不处置+supply_gap 池面 3/3 地板未破 W16 在队自愈·REPORT/LIVE-2026-10-06 再生·scorecard/build_status host=bm-a 执笔·token delta ~0） | "
    "verify: research/THEME_DEEPEN_P1_PREREG.md 冻结链+§7/§8 + results/theme_deepen_p1/ 六件 + smoke 48/48 (S1) + "
    "selftest 14/14 + ledger_head 750,812 file=theme_deepen_p1.json 自证 + attrition CLEAN + "
    "banned_direction_gate ADMIT 回执在件 + orders 双扫零未回执 | "
    "本地未达 origin commit 数=0（提交后 push+fetch 自证） | "
    "下轮指针: r777 = (a) T-174 P1 prereg 起草冻结（核心仓验证收口批·唯一必烧 ≤300 试）(b) T-175 外源想法目录 R1 零烧推进 (c) W158 引擎烧录 watch→finalize one-pass+§7/§8 回填+ledger 750,812+2,200 (d) 10-07 12:00 wrapper Step1 回看窗核收 (e) CEO 报告消费回执采集\n"
)
with open("round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(rr)
print("round report line appended")

# 3) state round_no 775 -> 776
sp = "state-bm-a.json"
st = json.load(open(sp, encoding="utf-8"))
prev = st.get("round_no")
st["round_no"] = 776
json.dump(st, open(sp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"state round_no {prev} -> 776")

# 4) heartbeat (bm-a own file)
hb = "fleet/machines/bm-a.json"
h = json.load(open(hb, encoding="utf-8"))
h["last_seen"] = now
h["current_task"] = "T-173 theme-deepen batch burned + first-version CEO report delivered; next T-174 prereg"
import os
h["cpu_cores"] = os.cpu_count()
h["verdict"] = "T-173 numbers out: W1-only positive (+19.2%/73%, p=0.0165); report delivered 2026-10-06 ahead of 10-08 deadline"
import psutil
vm = psutil.virtual_memory()
h["idle_ram_gb"] = round(vm.available / 1e9, 1)
epoch = int(time.time())
assert isinstance(epoch, int)
h["heartbeat_epoch_utc"] = epoch
h["clock_read"] = now
json.dump(h, open(hb, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
# self-verify epoch is JSON int
back = json.load(open(hb, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in back["clock_read"], "clock_read must be T-separated"
print("heartbeat written, epoch int:", back["heartbeat_epoch_utc"])
