# -*- coding: utf-8 -*-
"""r775 bm-c pre-push claw escape-hatch disclosure row (protocol contract:
唯一逃生口 git push --no-verify 须轮报告留痕). The claw blocked the
corrective commit c4d92395f's 68-file deletion set as "no owner evidence"
(r519 phantom-deletion conservative gate: the files lived for exactly ONE
commit = no cross-machine ownership history to attribute). Escape grounds:
all 68 files were created by THIS machine's own commit aecdc94a4 in the same
round and are being untracked (files stay on disk); git log --all over the
path shows only the two same-round commits (create + delete)."""
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ROW = ("2026-10-08T20:3x+08:00 | r775-tail | 爪逃生口留痕行：pre-push 爪拦矫正提交 c4d92395f 删除集"
       "（68 件 mv_work untrack·爪判 'no owner evidence'=文件单 commit 生命周期无跨机属主史·按 r519 "
       "幻影删除族保守拦截=正确执法面）→ 使用 git push --no-verify 逃生口，理由留痕：删除集全部 68 件由本机 "
       "aecdc94a4（[via bm-c r775]·本同轮前序提交）单一 commit 创建并同轮矫正 untrack（git log --all "
       "results/mv_work/ 全史仅两 commit=aecdc94a4 建+c4d92395f 删·零他机触碰）·盘上文件全保留零真删除"
       "·mp3/产线资产 untrack 恢复 r770-r774 frozen-lane 先例 | 证据: git log --all --oneline -- "
       "results/mv_work/ 两行铁证+矫正提交 c4d92395f+心跳 ADDENDUM r775-tail | [via bm-c r775]")


def main():
    path = os.path.join(REPO, "round_reports-bm-c.md")
    with open(path, "rb") as fh:
        data = fh.read()
    bom = data.startswith(b"\xef\xbb\xbf")
    if bom:
        data = data[3:]
    text = data.decode("utf-8")
    tail = text[-400:]
    crlf = tail.count("\r\n")
    eol = "\r\n" if crlf >= (tail.count("\n") - crlf) else "\n"
    if text and not text.endswith("\n"):
        text += eol
    text += ROW + eol
    payload = text.encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with open(path, "wb") as fh:
        fh.write(payload)
    print("CLAW_ESCAPE row appended")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
