"""r671 CODELY.md memory append: gate coverage format-mismatch pit (one line, LF)."""
import io
P = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\CODELY.md"
entry = (
    "- [2026-10-04 10:5x r671 bm-a] 覆盖门存储形×枚举形错配坑（update_fund_statements 实弹·r458 水位键口径族姊妹面）：gate 从面板字节 derive 覆盖时，"
    "装配面存的 EM 原生 dashed period_end（'2005-03-31'·F6 断言固化了此形）而 expected 枚举集=紧凑 'YYYYMMDD'——集合交恒空→完备面板被读成 258/258 全缺→"
    "每轮 gate 幽灵 spawn 全量重拉子进程（子进程 checkpoint 基判完备自愈→status face 完备/残缺反复翻面·verdict=spawn 与 complete=true 同帧并立=指征）。"
    "同文件 panel_cutoff 早有 .replace('-','') 而 coverage 交比对漏归一=同族半修陷阱。修=单点 panel_coverage 内 dash 归一+selftest F7 回归腿"
    "（断言改紧凑形+交非空腿）。How to apply：一切「从存储字节 derive 覆盖/水位」的门，写前先钉死存储形==枚举形（或单点归一）；selftest 断言禁抄实现现值"
    "（dashed 断言=盲点本体）——断言要对着「与 expected 可交」写勿对着「与实现一致」写；status face 同帧 verdict=spawn+complete=true=覆盖门错配第一指征。\n"
)
raw = open(P, "rb").read()
assert b"r671" not in raw or raw.count(b"r671 bm-a") == 0, "dedup: entry may already exist"
with io.open(P, "ab") as f:
    f.write(entry.encode("utf-8"))
back = open(P, "rb").read()
assert b"\xe8\xa6\x86\xe7\x9b\x96\xe9\x97\xa8\xe5\xad\x98\xe5\x82\xa8\xe5\xbd\xa2" in back  # title anchor present
import json
print("CODELY appended bytes:", len(back) - len(raw))
