# r237 (bm-a): append S9 R237 addendum to MF_COLLECTOR.md (CRLF, UTF-8, no PS relay)
import io

addendum = [
    "",
    "## §9 R237 复拉修正案（2026-09-26 R237 addendum·R236 修正案族移植·T-63 车道加固·零判据面）",
    "",
    "- **缺陷家族同构确认（E1 设计期自捕·炸点在 ~2026-10-27+）**：本采集器与 sina 双子（T-72）共享同一构造缺陷——",
    "  ①`done` 集=首拉语义永不重置：stale>20td 触发的 refresh 走 not-done todo 面=结构性空集（首拉完成后恒空）＝复拉面死码；",
    "  ②零符号轮终态把 mirror `panel.cutoff` 写 None 覆盖活面板真值→gate stale_gate(None) 恒触发→30min spawn 永动零拉取。",
    "  触发时序=首次全宇宙拉取完成后 +20 交易日（rank 道只更新 rank 节不更新 panel.cutoff，panel.cutoff 仅由",
    "  refresh 终态写——即使 rank 道健康日日更新，daykline 面的 20td 门仍将准时触发死码面）。当前实况=首拉 53/5222",
    "  源阻断在飞（§7 live-fire），缺陷尚未武装；修正案在武装前落地＝时间引信拆除。",
    "- **修正案四件（scripts/update_moneyflow.py，R236 同构配方 1:1 移植）**：`_is_repull`（mirror complete+真实 cutoff",
    "  →复拉面判定）/`_todo_for`（repull=True 重置 done 全宇宙复拉；attempts 累计保留=隔离律不随复拉放宽）/",
    "  `_panel_cutoff_from_bytes`（512B 尾读逐文件 derive 真实 cutoff；坏尾/纯表头/schema-foreign 邻件诚实跳过）/",
    "  `_terminal_cutoff`（零符号轮禁 None 覆写活面板）。gate spawn 面=spawn_mode 字段披露+`refresh-repull` 子命令分流；",
    "  main 派发加 `refresh-repull`；selftest 20/20→**21/21**（S21 死码夹具：done 覆盖宇宙→首拉 todo 空→repull 重置→",
    "  全 todo 减隔离；_is_repull 三面；零符号轮字节 derive 夹具=r157 夹具镜像生产形态律）。",
    "- **零行为变化面（现役车道）**：首拉/续拉/隔离/quarantine/conn-fuse/rank 道/窗卫全部语义不变；",
    "  `spawn_detached_refresh` 包装件随调用点直化退役。诚实披露：本修正案在首拉完成前落地，repull 真弹首触发",
    "  将在 ~2026-10-27 窗（与 sina 月度复拉同窗）——届时 spawn_mode=re-pull (done-reset) 实况入轮报告。",
]
with io.open("research/shortline/MF_COLLECTOR.md", "a", encoding="utf-8", newline="") as f:
    f.write("\r\n".join(addendum) + "\r\n")
raw = open("research/shortline/MF_COLLECTOR.md", "rb").read()
print("after append: crlf=%d lf=%d" % (raw.count(b"\r\n"), raw.count(b"\n")))
