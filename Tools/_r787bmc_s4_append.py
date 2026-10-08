# -*- coding: utf-8 -*-
"""r787 bm-c S4 solidification appends (three anchored, count-asserted,
EOL-adaptive; anchors verified unique before insertion):
1. pit-engine-freeze-editor.md  -- W192 freeze compound-pit entry
2. knowledge/METHODOLOGY_ASSETS.md -- E48 preflight dry-run card + capture line
3. knowledge/TREASURE_REGISTRY.md  -- E48 treasure-registry row"""
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

PIT_ADD = (
    "- [2026-10-09 04:1x r787 bm-c] **死会话收养冻结编辑器首活四坑复合+preflight "
    "干跑律（W192 五面冻结窗实弹·E48·方法论卡已入 knowledge/METHODOLOGY_ASSETS.md）**："
    "①G2 机读计数断言须分桶——owners 字典 sum(values) 含 None 桶（无主 8 行）≠owned 181，"
    "期望数按回执 leg0 语义排除 None 桶；②替换表计数=子串出现次数非行数"
    "（n3r1_used190 一行两现共 3 处·Select-String 行计数 2 的假象）；③G4/G8 边界三件——"
    "chunk 起点标记须含 4 空格缩进（缺=滚面注释头落 0 列）、滚块插入须补尾 \"\\n\""
    "（缺=与下一节头粘行成代码尾注释）、插入后标记计数须从靶文件实 derive"
    "（\"    # --- T-141\" 4 空格形全文件仅 1 处·0 列形不匹配不计数）；"
    "④G11 subprocess JSON round-trip 断言须 list 归一（tuple 经 json 反序列化成 list"
    "·值对型不等=写后假红）。根治面=preflight 干跑（Tools/_r787bmc_w192_countcheck.py"
    "=全 G 链零写入仿真·表从源码切片 exec 取局部量·一次抓全部计数失配防逐断言慢迭代）；"
    "写后假红=幂等件楔死态（G0 已应用门拒重跑）正法=收口件重验+补收据"
    "（_r787bmc_w192_receipt_complete.py 法）非回滚非手改靶件。How to apply："
    "一切门控一次性手术件（冻结/池登记/外科重放）首活前先写 preflight 干跑件；"
    "表计数用 str.count 非行扫；断言面过 JSON 一律 list 归一；期望计数按回执语义分桶。")

MA_ADD = (
    "\n- **E48 门控一次性手术件 preflight 干跑法（gated one-shot instrument "
    "preflight dry-run）**（proven·工程面）：任何带 G 门链+后置写步（write 后仍有断言步）"
    "的一次性手术件（冻结编辑器/池登记/外科重放）首活前，先做零写入全链仿真件——"
    "同源 chunk 抽取+表滚面+插入+全部计数断言+AST 门逐门复刻（表可从源码切片 exec 取 "
    "main 内局部量），一次抓全部计数失配（防逐断言慢迭代）并在真活前暴露边界缺陷"
    "（缩进/粘行/标记计数/类型面）；写后断言假红=幂等件楔死态（已应用门拒重跑）——"
    "正法=收口件（receipt-completer）重验+补写收据，非回滚非手改靶件。类型面律："
    "subprocess JSON round-trip 断言一律 list 归一（tuple→list 值对型不等假红）；"
    "计数面律：str.count 子串计数非行计数（一行可多现）；语义面律：机读计数期望数按回执"
    "语义分桶（owned 排 None 桶）。证据=Tools/_r787bmc_w192_countcheck.py（preflight "
    "一次过 155 项表核·唯一失配 mat-39 当场归正）+Tools/_r787bmc_w192_receipt_complete.py"
    "（G11 假红楔死态收口）+W192 五面冻结 f8703842c 上 origin（A=437_204..439_203 "
    "B=439_204..439_403·引擎自燃 12/12）。\n"
    "- 2026-10-09 04:1x（bm-c r787·W192 五面冻结收口步）：捕获律 append E48 门控一次性"
    "手术件 preflight 干跑法（工程净路收口步·O-20261002-2100 捕获律 live 实证）。")

TR_ADD = (
    "- 2026-10-09 04:1x bm-c r787 W192 五面冻结收口捕获（方法论卡 append 类）："
    "E48 门控一次性手术件 preflight 干跑法入库（METHODOLOGY_ASSETS.md 工程面）——"
    "死会话冻结编辑器收养首活四坑复合（owner 分桶/子串计数/边界三件/JSON list 归一）"
    "+preflight 零写入仿真根治+receipt-completer 楔死态收口正法；W192=第 182 引擎波 "
    "bm-c 第 35 枚自有波 A=437_204..439_203 B=439_204..439_403 阶梯第 52 例·五面 "
    "f8703842c 上 origin·引擎 mtime-watch 自燃 12/12；O-20261002-2100 捕获律 live 实证。")

JOBS = [
    (ROOT + r"\research\pit-engine-freeze-editor.md",
     "且 count(W182 名单形)==0 且残渣零。", PIT_ADD),
    (ROOT + r"\knowledge\METHODOLOGY_ASSETS.md",
     "·append E47 REGIME 路由验证方法族（live 实证：results/regime5_validation/"
     "REGIME5-VALIDATION-2026-09-30.json）", MA_ADD),
    (ROOT + r"\knowledge\TREASURE_REGISTRY.md",
     "（CHOP/GRIND 结构性信号在案·修订窗=另批预注册·O-2215 回访 10-21）", TR_ADD),
]


def main():
    for path, anchor, add in JOBS:
        with open(path, encoding="utf-8", errors="replace", newline="") as fh:
            txt = fh.read()
        n = txt.count(anchor)
        assert n == 1, "anchor count %d in %s" % (n, path)
        crlf = txt.count("\r\n") > txt.count("\n") / 2
        nl = "\r\n" if crlf else "\n"
        i = txt.find(anchor)
        j = i + len(anchor)
        rest = txt[j:]
        assert rest.strip() == "", "anchor not at file tail in %s" % path
        addition = add.replace("\n", nl)
        out = txt[:j] + nl + addition
        out += rest if rest else nl
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(out)
        print("APPENDED %s (+%dB)" % (path.split("\\")[-1], len(addition)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
