"""r997 bm-a final: pit-machine direct-write entry (r666/r943 precedent, main
CODELY.md over cap 31063B>30720B) + round report addendum line (collision
disclosure). Append-only writes, no state touch (parallel instance in flight)."""
import io, datetime

NOW = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

# ---- 1) pit-machine.md direct-write entry ----
entry = (
    "- [2026-10-14 20:1x r997 bm-a] **S0 并行执行体检测缺口（同树双 r997 实录·防撞铁律 S0 侧盲区）**："
    "fetch 后 behind=0/ahead=0 ≠ 独占执行——本机 schtasks 循环实例（Bigmoney-IterationLoop）与另一 CLI 实例共享同一工作树时，"
    "他实例的提交已进本机 HEAD（无 behind 信号）+ 轮首脏面被误读为「后台任务运行态」（实为并行实例链产物），"
    "双实例同跑 r997 至收尾相撞（origin 侧 19:11/19:31/19:33 三笔 r997 提交=并行实例；本实例 19:29 起跑漏检）。"
    "并行实例签名三面=①git log 存在晚于上轮收尾 ts 的新提交（对 r996 收尾 18:44 而言 19:11+ 即铁证）"
    "②state round_no/报告尾行轮号已被推进③satengine/daemon face 尾 tick 与本窗提交序错位。"
    "S0 补腿=fetch 后必跑 `git log --format='%ci %s' -5` 对照上轮收尾时刻——见新提交=并行实例在飞→本轮只读退避（防撞铁律）；"
    "已开工窗止损=①冲突解面按 r997 实录配方（当日再生运行态面 live-wins 取新侧/satengine jsonl 行级 dict-only union）"
    "②推送后停笔勿开新腿③state 写最小化防覆写他实例在飞字段（本窗 state 已被本实例写——若并行实例在飞，其收尾自愈覆盖）。"
    "How to apply：同机 schtasks 循环与交互窗共存时段（夜窗全面开工令后=常态），S0 锚定步必带近窗提交扫描；"
    "见 round_reports-bm-a.md 双 r997 行=双重执行证据。"
)
with io.open(r"research/pit-machine.md", "a", encoding="utf-8", newline="") as f:
    f.write("\r\n" + entry + "\r\n")

# ---- 2) round report addendum line ----
addendum = (
    "%s | r997 bm-a addendum (collision disclosure + closeout) | **同树双 r997 并行实例冲突实录+披露**："
    "本实例 19:29 起跑时未检出并行循环实例在飞（origin 侧已有 19:11 'S6 chain 33 legs'/19:31 'waits-upstream watch'/"
    "19:33 'sateng heal' 三笔 r997 提交=另一实例同树工作；S0 fetch behind=0 无信号+轮首脏面误读为后台任务面=检测缺口，"
    "入律 pit-machine.md r997 行）。收尾三推竞速：push 拒→dispatcher 面再拒→writer-pause 窗 rebase 撞 19UU（15 面当日再生运行态"
    "按 live-wins 取本侧新刻 19:43-19:46>19:24-19:28 + satengine 三面=base 侧外科 heal 版取新+history jsonl 行级 dict-only union "
    "120+120→122 双尾保全）→推成 e521f4536..bc257b91e behind=0 自证。**W241 finalize 已由 bm-c r1006 estate 落地（账本 954,535 "
    "EXACT·K 528,120）=W242 materialize 触发条件就位，让位并行实例 r998 消费**；本实例按防撞铁律就此停笔退避——"
    "state/心跳由在飞实例收尾自愈。| 本地未达 origin commit 数=0（bc257b91e 已达）"
) % NOW
with io.open(r"round_reports-bm-a.md", "a", encoding="utf-8") as f:
    f.write(addendum + "\n")

print("APPENDED: pit-machine entry + report addendum @", NOW)
