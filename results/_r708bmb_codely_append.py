# -*- coding: utf-8 -*-
"""r708 bm-b: append pit-law entry to CODELY.md (UTF-8 append, twin-face law)."""
entry = (
    "- [2026-10-05 03:5x r708 bm-b] merge resolver 孪生面同侧律（r708 实弹·当场治愈零 origin 伤害）："
    "take-new 类 merge resolver 对孪生序列化面（dashboard_status.js/json、REPORT/LIVE md/json）必须绑定同侧决策——"
    "js 探针腿兜底取 theirs 而 json 决策腿取 ours 时=同轮落盘的 js/json 内容不一致"
    "（js=origin 03:33 旧面·json=bm-b 03:41 新面）；实弹当场 HEAD blob 恢复同侧治愈（git show HEAD:<path>，stage 已清后 ours 侧正取路）。"
    "How to apply：resolver 决策表先做孪生配对（.js/.md 跟随同名 .json 决策），探针腿失败兜底前先查孪生主面决策，禁独立兜底。"
    "| dept:工程 | r708 收口窗（18 UU take-new 全 ours 新面·treadmill 三轮竞态窗零 --no-verify 全正解 merge 路径）\n"
)
with open("CODELY.md", "ab") as f:
    f.write(entry.encode("utf-8"))
print("CODELY entry appended (utf-8)")
