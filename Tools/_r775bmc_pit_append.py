# -*- coding: utf-8 -*-
"""r775 bm-c S4 pit codify: check-ignore -v empty-pattern misread x add -A
staged-count red flag composite pit -> research/pit-git-parse.md direct-write
(r666 direct-write precedent; main CODELY 30,581B only 139B headroom = no
room for the ~0.7KB entry). One matter = the mv_work accidental-sweep
incident with its two sub-causes. EOL-preserving append + count assert."""
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
ENTRY = (
    "- [2026-10-08 20:3x r775 bm-c] **check-ignore -v 空 pattern 列误读×add -A staged 数红旗未盘问复合坑"
    "（frozen-lane 目录 68 件 41.4MB 误入 git·mp3 9.4MB 版权敏感）**："
    "①`git check-ignore -v <path>` 输出 `<src>:<line>:<pattern><TAB><path>`——pattern 列为空"
    "（.gitignore L163=空行·无 mv_work 模式）时 rc=0 被误读为「已忽略」（实际未忽略·add -A 照收）；"
    "正法=判忽略必核 pattern 列非空或改用 `git check-ignore -q -- <path>`（真忽略才 exit 0·零 -v 歧义）"
    "+目录级 untracked 预期在 add -A 后 `git status --porcelain` 复核零膨胀。"
    "②add -A 后 staged 数（124）远超预期产品集（~40）未当场盘问即 commit→随 aecdc94a4 入 origin；"
    "正法=commit 前 staged 清单必对照本轮预期产出集，超集即停查"
    "（本例矫正当窗=git rm -r --cached+补真 .gitignore 模式·r731 新提交快进·已推史 r307 保全·"
    "pre-push 爪对单 commit 生命周期删除集判 no-owner 须 --no-verify 逃生口+轮报告留痕）。"
    "How to apply：一切「这个目录该被 ignore」的判定走 check-ignore -q 或 pattern 列非空核验；"
    "closeout add -A 后 staged 数=硬门必盘问。"
)


def main():
    path = os.path.join(REPO, "research", "pit-git-parse.md")
    with open(path, "rb") as fh:
        data = fh.read()
    bom = data.startswith(b"\xef\xbb\xbf")
    if bom:
        data = data[3:]
    text = data.decode("utf-8")
    assert "r775 bm-c] **check-ignore" not in text, "entry already present"
    tail = text[-400:]
    crlf = tail.count("\r\n")
    eol = "\r\n" if crlf >= (tail.count("\n") - crlf) else "\n"
    if text and not text.endswith("\n"):
        text += eol
    text += eol + ENTRY + eol
    payload = text.encode("utf-8")
    if bom:
        payload = b"\xef\xbb\xbf" + payload
    with open(path, "wb") as fh:
        fh.write(payload)
    sz = os.path.getsize(path)
    assert sz <= 30720, "pit-git-parse over D-06 line: %d" % sz
    print("PIT_APPEND ok pit-git-parse=%dB (<=30720) eol=%r" % (sz, eol))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
