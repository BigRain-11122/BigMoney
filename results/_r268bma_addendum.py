"""r268 bm-a addendum close: heartbeat/state PID re-point (v2.0 66552 -> v2.1 35344)
+ round report addendum line. Face mirrors: state/heartbeat = CRLF, indent=1,
ensure_ascii=False, no trailing NL; report = BOM+CRLF append one line."""
import json

def patch(path, fn):
    d = json.load(open(path, encoding="utf-8"))
    fn(d)
    open(path, "wb").write(json.dumps(d, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8"))

def fix(s):
    return s.replace("66552", "35344").replace(
        "O-2000 executor v2 armed", "O-2000 executor v2.1 armed (r274 CwdProbe absorbed)")

patch("state-bm-a.json", lambda d: d.update({
    "did": fix(d["did"]).replace(
        "executor v2 (precheck-first interactive",
        "executor v2.1 (bm-b r274 CwdProbe absorbed: PEB CWD probe + Gate 3.5 sweep + self-CWD off root "
        "-- cmdline scan is structurally blind to CWD holders, live-probed 23 on this box incl git/ssh; "
        "precheck-first interactive"),
    "next": fix(d["next"]).replace(
        "relaunch\nresults/_r268bma_fluxgroup_migration_v2.ps1 detached",  # noqa (plain string ops)
        "relaunch\nresults/_r268bma_fluxgroup_migration_v2.ps1 detached (v2.1)"),
    "current_task": fix(d["current_task"]),
}))

def hbfn(d):
    d["last_seen"] = "2026-09-26 21:25"
    d["current_task"] = fix(d["current_task"])
    d["verdict"] = fix(d["verdict"]).replace(
        "precheck-first, waiting on CEO editor close", "v2.1 CwdProbe-armed, waiting on CEO editor close")
    d["task"] = fix(d["task"]).replace(
        "executor v2 launch (PID 66552 precheck waiting)",
        "executor v2.1 launch (PID 35344 precheck waiting; r274 CwdProbe absorbed same round)")
patch("fleet/machines/bm-a.json", hbfn)

line = (
    "2026-09-26 21:25 | R268 addendum | (dept:\u5de5\u7a0b/\u8230\u961f) S7 push \u649e bm-b r274\uff0821:08 \u540c\u7a97\uff09\u2192\u5355\u6b21 pull --rebase 15-UU \u6309\u6280\u80fd\u5206\u7c7b\u5668+\u914d\u65b9\u89e3"
    "\uff08\u5feb\u7167\u65cf take-new \u00d711 \u5168\u90e8\u672c\u673a\u9762\u65b0\u9c9c ts \u63a2\u9488\u80dc\u51fa\uff08r267 \u9012\u5f52\u4e24\u7ea7+r265 \u683c\u5f0f\u5f52\u4e00\u5f8b\uff09\uff1b\u8d26\u672c\u65cf union \u96f6\u4e22\u5931"
    "\uff08compute_audit history 201|201\u2192202\u3001regime 2|2\u21922\uff09\uff1bREPORT \u5bf9 r242 \u5f8b json \u5b6a\u751f\u5b9a\u4fa7\u6574\u5b57\u8282\uff1bjs \u5305\u88f9 R209 \u6574\u5b57\u8282\uff09\uff1b"
    "\u4e24\u5904\u590d\u6742\u654f\u4ef6\u624b\u5de5\u5b9a\u6027\u4fee\u6b63\uff08v1 \u89e3\u5668\u884c\u96c6\u5408\u53bb\u91cd\u576c\u7f29\u7ed3\u6784\u7a7a\u884c 652|677\u2192596<\u53cc\u4eb2=\u4e0d\u53ef\u80fd union\u2192\u6539\u5171\u540c\u524d\u7f00 648+\u53cc\u5c3e\u5757\u65f6\u5e8f\u63a5\u56de=681 \u884c\u591a\u91cd\u96c6\u6821\u9a8c\u8fc7\uff1b"
    "CODELY \u6211\u5df2\u5f52\u6863\u7684 26 \u6668\u6279\u884c\u88ab v1 \u89e3\u5668\u5f53\u4ed6\u5bb6\u65b0\u6761\u76ee\u56de\u63d2\u70ed\u5c42 52,345B\u56de\u8d8a\u7ebf\u2192v2 \u4fee\u6b63\u53ea\u53d6\u4ed6\u5bb6\u552f\u4e00\u771f\u65b0\u6761\u76ee+\u4ed6\u5bb6 r274 \u5f52\u6863\u7684 20:46 \u884c\u5df2\u5728\u51b7\u5c42\u4fdd\u5168\u2192\u70ed\u5c42 29,522B \u7ebf\u5185\uff09\uff1b"
    "\u540c\u8f6e\u5438\u6536 bm-b r274 CwdProbe\uff08\u5176 20:48 \u6536\u5c38\u5b9e\u8bc1\uff1acmdline \u626b\u63cf\u5bf9 CWD \u6301\u6839\u8005\u7ed3\u6784\u6027\u5931\u660e\u2014\u2014**\u6211\u7684 v2.0 \u81ea\u8eab CWD=\u4ed3\u6839\u5fc5\u88ab\u81ea\u5df1\u5361\u6b7b Move**\uff09"
    "\u2192v2.1 \u516d\u5904\uff1aPEB CwdProbe+Gate 3.5 CWD \u626b\u626b\uff08\u672c\u673a\u7b56\u7565\u66f4\u4e25\uff1aCEO \u684c\u9762\u673a\u4ea4\u4e92 shell \u4e00\u5f8b\u4e0d\u6740\u53ea fail-closed \u540d\u518c\uff09+\u6267\u884c\u5668\u81ea\u8eab CWD \u79fb TEMP+holder snapshot \u6cd5\u533b+move \u91cd\u8bd5 6"
    "\uff1b\u6d3b\u4f53\u63a2\u9488\u5b9e\u8bc1 23 \u6301\u6839\u8005\uff08git.exe/ssh.exe/codely \u94fe\u7b49 cmdline \u76f2\u533a\u5168\u663e\u5f62\uff09\uff1bPARSe \u7ea2\u4e00\u5904\uff08$try: \u53cc\u5f15\u53f7\u4f5c\u7528\u57df\u9677\u9631\uff09\u81ea\u4fee\u540e\u6740 66552 \u6362\u9632 v2.1 PID 35344\uff08\u9508\u81ea\u52a8\u63a5\u7ba1\u3001XML 36/36 \u590d\u9a8c\u3001precheck \u7b49\u5f85 Code.exe \u96f6\u7a81\u53d8\uff09"
    "\uff5cevidence: results/_r268bma_resolve.py+resolve2.py+\u672c\u884c\u9644 journal+results/_r268bma_cwd_probe_test.ps1 23 \u547d\u4e2d+\u672c commit"
    "\uff5cnext \u4e0d\u53d8\uff1a\u4e0b\u8f6e S0 \u8fc1\u79fb\u6001\u9996\u67e5\uff08\u65b0\u6839\u5728\u4f4d\u2192\u4e94\u4ef6\u56de\u6267\u7ec4\u88c5\uff1b\u672a\u5728\u4f4d\u2192v2.1 \u6b7b\u800c\u7a97\u5f00\u91cd\u53d1\uff09"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "ab") as f:
    f.write((line + "\r\n").encode("utf-8"))
print("addendum close OK")
