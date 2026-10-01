# r524 bm-a: Tools/iteration_prompt.txt per-machine registry self-annotation
# (MSG-161x bm-b request: bm-a annotates its actual engine command on first read).
# Surgical raw-text replace, anchor count==1 asserted, format preserved verbatim.
path = "Tools/iteration_prompt.txt"
raw = open(path, encoding="utf-8", newline="").read()
needle = "bm-a＝本机自建实例命令（r522 落地·首轮过此项时自注实际路径）"
repl = ("bm-a＝python scripts\\saturation_engine.py status"
        "（r524 bm-a 自注：本机跑共享仓单源脚本=与 bm-b 同相对路径；"
        "注册任务名 Bigmoney-SatEngine-bm-b（fleet 共享本地名）·"
        "注册脚本 Tools\\register_satengine_task.ps1·"
        "tick=python scripts\\saturation_engine.py tick）")
assert raw.count(needle) == 1, f"anchor count {raw.count(needle)} != 1"
out = raw.replace(needle, repl)
open(path, "w", encoding="utf-8", newline="").write(out)
print("self-annotation landed; bytes", len(raw), "->", len(out))
