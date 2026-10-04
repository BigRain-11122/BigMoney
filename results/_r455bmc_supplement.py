# -*- coding: utf-8 -*-
"""r455 bm-c S7-supplement round-report line: closeout push-race + claw-block
resolution record (r453/r454 lineage form). Bytes append with EOL detect."""
import datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CLOCK = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

LINE = (
    CLOCK + "｜r455 bm-c S7-supplement｜closeout 双段收口（r648/r437 净路实录）："
    "round commit 53efd6846（45 件=本轮产出+lane daemon 面）首推被 pre-push 爪正确拦截"
    "（删除集=本地 behind 型幻影：origin 新 wave 的 _r657bmb_race_closeout.py+"
    "_r665bma_* 族系他机新件未合并=r519 族正例·零强推零绕爪）→fetch 实核 behind=4"
    "（bm-b r658+bm-a r665 双 wave）→merge origin/main 撞 14 UU（同日幂等再生态双机 "
    "S6 竞写族·r450/r452 同型）→survey receipt results/_r455bmc_uu_survey.py+结构 peek "
    "_r455bmc_uu_peek.py 逐面定侧：12 再生面 take-ours（ts 诚实比较 ours 08:39-08:41>"
    "theirs 08:35-08:37·REPORT/LIVE/attrition/b_layer/futures/regime[tie 确定性取 ours "
    "r452 判例]/token_usage[键集同 ours 值新=per-m union 等价面]/update_status）+"
    "lhb_update_status take-THEIRS（08:36:02>ours 08:20:09 诚实取新）+compute_audit 跨机 "
    "union（hist 201+201→212 ts-identity 去重零丢失·双侧 containment 断言过·latest 取新 "
    "08:39:02·theirs 超集顶键 machines/ts 保全）→行首 marker 扫+JSON reparse 14/14 PASS→"
    "merge 2a12c8fad→push rc0→fetch+ahead==0 送达自证 DELIVERED（零 fatal 词·r436 律）·"
    "本地未达 origin commit 数=0")

rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, "rb") as f:
    raw = f.read()
eol = b"\r\n" if b"\r\n" in raw[-400:] else b"\n"
addition = LINE.encode("utf-8") + eol
if not raw.endswith(b"\n"):
    addition = eol + addition
with open(rp, "ab") as f:
    f.write(addition)
with open(rp, "rb") as f:
    back = f.read()
assert LINE.encode("utf-8") in back, "supplement line not found after append"
print("SUPPLEMENT_OK bytes=" + str(len(addition)) + " clock=" + CLOCK)
