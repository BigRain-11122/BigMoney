"""r243 fix: correct round report line + state timestamps (pre-commit,
same-round correction of a wrong clock assumption: autofill task healthy,
no tick stall; actual time ~11:36 not 12:0x)."""
import io
import json

P = r"logs\iteration-loop\round_reports-bm-a.md"
txt = io.open(P, encoding="utf-8").read()
bad = "发现=11:30 后 autofill tick 停摆（11:40/11:50 缺）→S7 schtasks 核查中"
good = ("S7 schtasks 实勘（R49 律）四任务全健康（IterationLoop Running/"
        "Watchdog Ready 11:50/Autofill Last 11:30:01 Result 0 Next 11:40/"
        "IntradayMarks 09-28 9:25）——早前钟面误判「tick 停摆」撤回，无异常")
assert bad in txt
assert good not in txt
txt = txt.replace(bad, good).replace(
    "2026-09-26 12:0x | R243 |", "2026-09-26 11:3x | R243 |")
txt = txt.replace("2026-09-26 12:0x | R243 | [wm:", "2026-09-26 11:3x | R243 | [wm:")
# normalize any leftover 12:0x stamp in the R243 line
if "12:0x | R243" in txt:
    txt = txt.replace("12:0x | R243", "11:3x | R243")
io.open(P, "w", encoding="utf-8", newline="").write(txt)
assert "12:0x" not in txt

SP = "state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
st["ts"] = "2026-09-26 11:3x"
st["updated_at"] = "2026-09-26 11:3x"
st["next"] = (
    "harvest proof.json + flip pool done (r224 window law); 09-28 Mon new-bar "
    "chain; 10-01 month trio + REGIME_GUARD v3 date gate; 10-09 T-70 midterm "
    "verdict window")
io.open(SP, "w", encoding="utf-8", newline="").write(
    json.dumps(st, ensure_ascii=False, indent=1))
back = json.load(io.open(SP, encoding="utf-8"))
assert back["round_no"] == 243 and "12:0x" not in back["next"]
print("report+state corrected; no 12:0x stamps left")
