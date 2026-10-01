"""r511 bm-b: per-machine round-zero engine registry edit in the shared
loop prompt (MSG-20261001-154x option (a), bm-c proposal, bm-b concurs as
the native platform of the previously-hardcoded path). Surgical UTF-8
replace, single anchor, no BOM, no reflow."""
import io

PATH = "Tools/iteration_prompt.txt"
raw = open(PATH, "rb").read()
t = raw.decode("utf-8")

old = ("项）**：python scripts\\saturation_engine.py status——exit 0=活·照常下序；"
       "exit 1=引擎死=当轮 P0 同轮修复（powershell -NoProfile -ExecutionPolicy "
       "Bypass -File Tools\\register_satengine_task.ps1 重注册+python scripts\\"
       "saturation_engine.py tick 实弹验证点火后收轮，轮报告注明修复实况；"
       "本机引擎面=本地队列 N1 引擎波烧录·不入池·禁手工代烧池面批）")
new = ("项）**（per-machine 注册表·MSG-20261001-154x 提案(a) 三机生效）："
       "bm-b＝python scripts\\saturation_engine.py status；"
       "bm-c＝python Tools\\saturation_engine.py status；"
       "bm-a＝本机自建实例命令（r522 落地·首轮过此项时自注实际路径）"
       "——exit 0=活·照常下序；exit 1=引擎死=当轮 P0 同轮修复"
       "（修复链同走各机实例面：bm-b＝powershell -NoProfile -ExecutionPolicy "
       "Bypass -File Tools\\register_satengine_task.ps1 重注册+python scripts\\"
       "saturation_engine.py tick；bm-a/bm-c＝各自实例注册脚本+tick）"
       "实弹验证点火后收轮，轮报告注明修复实况；"
       "本机引擎面=本地队列 N1 引擎波烧录·不入池·禁手工代烧池面批）")

assert t.count(old) == 1, "anchor not unique: %d" % t.count(old)
t2 = t.replace(old, new)
with io.open(PATH, "wb") as f:
    f.write(t2.encode("utf-8"))
print("replaced OK, delta bytes:", len(t2.encode("utf-8")) - len(raw))
