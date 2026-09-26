# r237 (bm-a): CODELY.md memory append (four-question gate passed; CRLF, no BOM)
import io

entry = (
    "- [2026-09-26 09:5x] 坑律/家族面（bm-a R237·T-39 moneyflow 修正案族移植·R235/R236 家族第三例）："
    "**checkpoint 采集器 done 集重置语义=R235 缺陷家族的免疫判据——pass-scoped"
    "（update_options load_cells 按 pass_target 过滤=每新 bar 日天然重置）结构性免疫；"
    "first-pull-scoped（sina/moneyflow done 永续集）必有复拉死码+零符号轮 None 覆写双病**；"
    "修复=R236 四件配方移植（_is_repull/_todo_for/_panel_cutoff_from_bytes/_terminal_cutoff"
    "+refresh-repull 分流+spawn_mode 披露），但**移植前必实读目标采集器 done 集构造**"
    "（本轮假说「options+moneyflow 同病」实查=options 免疫——禁按同构外观盲拷）。"
    "moneyflow 特有触发链=rank 道只写 st.rank 节不写 panel.cutoff，rank 道健康也救不了"
    " daykline 20td 门准时触发死码面（炸点 ~10-27 与 sina 复拉同窗；修正案在首拉完成前"
    "落地=引信拆除）。指针=scripts/update_moneyflow.py S21+MF_COLLECTOR.md §9+results/_r237a-d"
)
assert len(entry.encode("utf-8")) <= 1600, "entry over 1.5KB-ish budget"

with io.open("CODELY.md", "a", encoding="utf-8", newline="") as f:
    f.write("\r\n\r\n" + entry + "\r\n")

raw = open("CODELY.md", "rb").read()
assert raw.count(b"\r\n") == raw.count(b"\n"), "CRLF purity broken"
import os
print("append OK: size=%d bytes (<50KB: %s) crlf=%d" % (
    os.path.getsize("CODELY.md"), os.path.getsize("CODELY.md") < 51200,
    raw.count(b"\r\n")))
