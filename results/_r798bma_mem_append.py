# _r798bma_mem_append.py -- O-20261006-2110 §3 + O-20261006-2250 §3 memory writes
# Appends two feedback entries to user-scope CODELY.md (fresh-read-modify-write per
# r774 multi-writer law). One entry per law, compact, pointer-style.
import io, datetime

P = r"C:\Users\sjs20\.codely-cli\CODELY.md"
s = io.open(P, encoding="utf-8").read()
ts = "2026-10-06 23:1x"

e1 = ("- [{} r798 bm-a] **CEO 用机让路律触发词（机队最高机制·O-20261006-2110 bm-c 令·bm-a 已部署）**："
      "本机任何会话听到 CEO 原话「我要打游戏」/「我要工作」=立即进程内执行 "
      "`& \"C:\\Users\\sjs20\\Desktop\\FluxGroup\\.codely-cli\\machine-state.ps1\" -Mode pause`"
      "（停本机 Ollama/llama-server+GPU 生产任务 BigCompute 族与 MiniGameOllama 双任务+cron 班组备份停摆；"
      "EngineTick/值守簿记保留）勿再问；「我要工作」歧义判据=CEO 亲自用机才 pause、派活语义不触发；"
      "「全面开工」=`-Mode resume`+写 fleet O 令 §全员 resume 广播（resume 后他机 ≤10min 各自 resume）。"
      "pause 期间他机照常全力运转。本机部署回执=O-20261006-2110 回执节。\n").format(ts)

e2 = ("- [{} r798 bm-a] **机队静默工作律·零窗律（O-20261006-2250 bm-c 令·bm-a 已执法）**："
      "一切会话内工具执行=进程内 `&` 禁 spawn 控制台子进程（U060·闪黑窗=违例）；"
      "一切自建计划任务=wscript //B //nologo InvisibleRunner 隐藏链"
      "（本机 13 任务已转换：CarGZH×8/QuantOversightDigest/GimmeAll/MoneyAutoGuardian/FluxBoardAuto/ResidentQA；"
      "双路通知闸 NOC_GLOBAL_SETTING_TOASTS_ENABLED=0/0 已设值读回）。10-13 治理窗回访判据。\n").format(ts)

def insert_feedback(text, entry):
    anchor = "### Feedback"
    i = text.find(anchor)
    assert i >= 0, "Feedback section missing"
    # insert after last line of the Feedback block = before '### Project' following it
    j = text.find("### Project", i)
    assert j >= 0, "Project anchor missing"
    # find start of the line containing '### Project'
    lj = text.rfind("\n", i, j) + 1
    return text[:lj] + entry + text[lj:]

if e1.strip() not in s:
    s = insert_feedback(s, e1)
if e2.strip() not in s:
    s = insert_feedback(s, e2)
io.open(P, "w", encoding="utf-8", newline="").write(s)
# verify
s2 = io.open(P, encoding="utf-8").read()
print("e1 in:", e1.strip()[:40] in s2, "| e2 in:", e2.strip()[:40] in s2, "| bytes:", len(s2.encode("utf-8")))
