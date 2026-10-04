add = """- [2026-10-04 14:3x r680 bm-a] EM lhb_detail 列位陷阱×GBK 隐名复合坑（LHB 普查 v1 实弹·当场自纠零污染）：EM 龙虎榜明细 schema 顺序=净买额在买入额/卖出额**之前**（pos7=净买额/8=买入额/9=卖出额），与直觉的「买/卖/净」序相反——v1 普查按位置映射把 pos9 卖出额当净买额=方向面全错号（错误结果静默产出无异常）；且 PS GBK console 把列名显示成 mojibake=按位猜列的诱惑面。正法=①pandas 列名先 dump 到 UTF-8 文件用 read_file 读真名（禁按 GBK console 显示猜）②一切 parquet/csv 列访问一律名字寻址禁位置寻址③普查 v1 产物发现后 v2 名字寻址重写+（code,day）去重（EM 每 code-day 每上榜原因一行=多行重复）。How to apply：新数据面普查探针先落 schema_check 件（列名+样本行 UTF-8 dump）再写统计腿；见结果对账表发现方向性异常时第一嫌疑=列位错配。
- [2026-10-04 14:4x r680 bm-a] 长链 runner 块缓冲 stdout×end-only 落盘=宿主静默斩首丢全窗坑（S6 链 r680 首跑实弹·harness 5min 零输出窗杀）：`python chain.py | Select-Object` 管道下 print 块缓冲=逐腿输出全滞缓冲区，宿主看「零输出」判死杀进程，而日志只在链尾写=进度全丢；r679 同款跑法侥幸（104s<5min 窗）未暴露。正法=①长链 runner 一律 `python -u` 起跑②每腿 print(..., flush=True)③日志改逐腿增量落盘（crash-safe）④每腿 subprocess 加 timeout 帽（240s）防单腿吊死全链。How to apply：一切 >2min 的驱动器/链 runner 四件套缺一不可；被宿主杀后先查「日志是否只在尾部写」再重跑，勿盲重发同命令。
"""
P = "CODELY.md"
d = open(P, encoding="utf-8").read()
assert "lhb_detail 列位陷阱" not in d
if not d.endswith("\n"):
    d += "\n"
open(P, "w", encoding="utf-8", newline="").write(d + add)
d2 = open(P, encoding="utf-8").read()
assert d2.count("r680 bm-a") >= 2 and len(d2) > len(d)
print("CODELY appended:", len(d), "->", len(d2))
