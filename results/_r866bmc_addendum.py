# -*- coding: utf-8 -*-
# r866 bm-c addendum: push-race rebase closeout record (r852 pre3 addendum precedent)
import json, time, io, datetime, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CANON = ROOT + r"\logs\iteration-loop\round_reports-bm-c.md"
GIT = r"C:\Program Files\Git\cmd\git.exe"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

addendum_line = ("2026-10-11T" + now_iso.split("T")[1] + " | r866 bm-c addendum | rebase-race closeout record（r852 pre3 先例法·收口后补账）: "
                 "r866 books 首推撞 pre-push 爪拦删集（origin 窗内前进=bm-b r873 四连 commit〔bd0313a3a/21ccb2735/bf44c8585/5932edbea·E14 census+S6 41 legs+31-UU rebase remedy addendum 同族实弹〕）→"
                 "fetch 后 rebase origin/main→31-UU 同窗 S6 再导出面族=_r866bmc_rebase_resolver.py（r856 血统 verbatim 升级：**stage 语义本窗 live 实证**〔rebase 反转：:2:=基座 bm-b 侧/:3:=我方重放 commit·daily_report prev_generated 探针钉侧 09:14:34 vs 09:53:45〕→"
                 "25 ts-audit json 全我方更新〔bm-b S6 10:07-10:09 vs 我方 10:08-10:11·每面 +50-90s〕+4 twin-follows〔3 md+dashboard_status.js 首例 js twin〕+compute_audit history ts-key UNION 201/201→201+x2_watch_log 三段 line-union 1787 行〕→"
                 "零 UU 仍拒（r863 家族·has_unstaged_changes 误导文案）→r811-bm-b/r868 三步法〔add -A 吸收+标记守卫 CLEAN+commit -F .git/rebase-merge/message 手工落 pick+continue〕一次过零 abort→"
                 "rebase 成功 main 重挂→push DELIVERED 5932edbea..71e6611da→fetch 自证 ahead=0/behind=0·零强推零 --no-verify（双爪零拦截） | "
                 "S7 收尾双扫: ORD ccf3ed9d/DEC 68d13893 双零增量（method pin 执法） | 查重锚=r734/r863/r811-bm-b 已有法零新律（stage 反转实证注记=防 r856 注释面再误标） | 本地未达 origin commit 数=0")

with io.open(CANON, "r", encoding="utf-8") as f:
    body = f.read()
lines = [l for l in body.splitlines() if l.strip()]
assert ("| r866 |" in lines[-1]), ("canonical tail not r866 main line", lines[-1][:80])
assert ("r866 bm-c addendum" not in body[-6000:]), "addendum already present"
with io.open(CANON, "a", encoding="utf-8", newline="") as f:
    f.write(addendum_line + "\n")

# state sync fields refresh (head_sha now = delivered commit; did/verify append race receipt)
p = ROOT + r"\state-bm-c.json"
with io.open(p, "r", encoding="utf-8") as f:
    d = json.load(f)
d["head_sha"] = "71e6611da"
d["sync"] = {"ahead_behind": "0/0 delivered", "origin_tip": "71e6611da", "ts": now_iso,
             "note": "r866 addendum: push-race rebase closeout (31-UU ts-newer-wins + r863-family manual pick commit); fetch self-proof 0/0"}
d["did"] = d.get("did", "") + (" ; ADDENDUM: push race -> pre-push claw block (stale base vs bm-b r873 quad) -> rebase "
                              "31-UU regen family resolved (_r866bmc_rebase_resolver.py: stage semantics live-verified "
                              "inverted [:2:=base bm-b, :3:=mine]; 25 ts-audit all mine-newer + 4 twins + compute_audit "
                              "union + x2 3-stage line-union 1787) -> zero-UU still-reject (r863 family) -> r811-bm-b "
                              "manual commit -F + continue -> DELIVERED 5932edbea..71e6611da, fetch self-proof 0/0")
d["verify"] = d.get("verify", "") + (" + addendum receipts: results/_r866bmc_rebase_resolver.py (31/31 resolved, "
                                     "marker-guard CLEAN) + push/fetch 0/0 self-proof (71e6611da on origin)")
for k in ["ts", "updated", "updated_at", "last_action_at"]:
    if k in d:
        d[k] = now_iso
d["last_action"] = "r866 S6 43/43 + QA r866 5/5 + push-race rebase closeout + books"
with io.open(p, "w", encoding="utf-8", newline="") as f:
    json.dump(d, f, ensure_ascii=False, indent=1)
    f.write("\n")

# heartbeat light touch (epoch + ts only, keep r866 books fields)
hp = ROOT + r"\fleet\machines\bm-c.json"
with io.open(hp, "r", encoding="utf-8") as f:
    h = json.load(f)
h["heartbeat_epoch_utc"] = epoch
for k in ["ts", "last_seen", "last_seen_at", "clock_read", "updated", "updated_at", "last_run_at"]:
    if k in h:
        h[k] = now_iso
h["head_sha"] = "71e6611da"
with io.open(hp, "w", encoding="utf-8", newline="") as f:
    json.dump(h, f, ensure_ascii=False, indent=1)
    f.write("\n")
raw = io.open(hp, "r", encoding="utf-8").read()
io.open(hp, "w", encoding="utf-8", newline="").write(raw.replace("\n", "\r\n"))

for path in [p, hp]:
    with io.open(path, "r", encoding="utf-8") as f:
        x = json.load(f)
    assert isinstance(x["heartbeat_epoch_utc"], int), path

print("ADDENDUM OK clock=%s" % now_iso)
