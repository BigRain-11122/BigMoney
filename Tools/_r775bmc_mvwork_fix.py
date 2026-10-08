# -*- coding: utf-8 -*-
"""r775 bm-c closeout-tail corrective: mv_work accidental sweep (68 files,
41.4MB incl. mv001_source_320k.mp3 9.4MB copyright-sensitive) tracked via
add -A in commit aecdc94a4 and delivered to origin. Root causes (both mine):
(a) .gitignore has NO results/mv_work/ pattern (L163 is an EMPTY line) so the
r770-r774 frozen-lane-untracked precedent was enforced only by TARGETED adds,
which r751 add-A law silently broke; (b) my `git check-ignore -v` read was a
false positive -- the -v output was `<src>:163:<TAB>path` = EMPTY pattern
column (no real match) and I misread rc=0 as ignored. Empirical truth: add -A
tracked it (staged=124 red flag missed pre-commit).
Fix (r731 law family: pushed commit never amended, no force -- NEW fast-forward commit):
 1. append a REAL ignore pattern 'results/mv_work/' to .gitignore;
 2. untrack via `git rm -r --cached results/mv_work` (PS batch, files stay on
    disk = production lane intact);
 3. honest addendum appended to state+heartbeat did/verify fields.
History keeps the 41.4MB (r307 preservation, no rewrite); disclosed."""
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ADDENDUM = (
    " | ADDENDUM r775-tail（收口事故+矫正如实披露）: mv_work 误收编——"
    "add -A 把 frozen-lane 目录 68 件 41.4MB（含 mv001_source_320k.mp3 9.4MB 版权敏感）"
    "随 aecdc94a4 推入 origin（<95MB 红线未破·单批 <200MB 合规·但违 r770-r774 untracked 先例）；"
    "双根因=.gitignore 无 mv_work 模式（L163=空行）+check-ignore -v 空 pattern 列误读（rc=0 假象）+"
    "staged=124 红旗未当场盘问（应约 40）；矫正=新提交快进 untrack（git rm -r --cached·盘上产线零触碰）+"
    "补正 .gitignore 真模式+frozen-lane 先例恢复；已入史 41.4MB 按 r307 保全不重写，如实披露"
)


def main():
    # 1. gitignore: append real pattern (idempotent)
    gi = os.path.join(REPO, ".gitignore")
    with open(gi, "rb") as fh:
        data = fh.read()
    text = data.decode("utf-8")
    assert "results/mv_work/" not in text, "pattern already present?!"
    if text and not text.endswith("\n"):
        text += "\n"
    text += "# mv frozen-lane scratch: keep untracked per r770-r774 precedent (r775-tail fix)\nresults/mv_work/\n"
    with open(gi, "wb") as fh:
        fh.write(text.encode("utf-8"))
    print("GITIGNORE pattern appended")

    # 2. heartbeat + state honest addendum (did/verify append, epoch untouched)
    for path in (os.path.join(REPO, "state-bm-c.json"),
                 os.path.join(REPO, "fleet", "machines", "bm-c.json")):
        with open(path, encoding="utf-8") as fh:
            j = json.load(fh)
        for k in ("did", "verdict", "note", "last_action", "last_round_summary"):
            if k in j and isinstance(j[k], str) and "ADDENDUM r775-tail" not in j[k]:
                j[k] = j[k] + ADDENDUM
        if isinstance(j.get("verify"), str) and "ADDENDUM r775-tail" not in j["verify"]:
            j["verify"] = j["verify"] + ADDENDUM
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(j, fh, indent=1, ensure_ascii=False)
        back = json.loads(open(path, encoding="utf-8").read())
        assert isinstance(back["heartbeat_epoch_utc"], int)
        assert "ADDENDUM r775-tail" in back["verify"]
    print("HEARTBEAT addendum ok (did/verdict/note/verify x2 files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
