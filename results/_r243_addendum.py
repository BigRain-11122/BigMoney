# r243 addendum: freeze-hash re-anchor (r242 drift law) + resolver archive
# + round-report addendum line + heartbeat refresh
import io
import json
import shutil
import time

# 1) ticket progress_r243: db8ac757 -> bd42a609 (text-level, LF, indent intact)
tp = r"fleet\tasks\T-2026-09-26-78-P1.json"
t = io.open(tp, encoding="utf-8", newline="").read()
assert "commit db8ac757" in t
io.open(tp, "w", encoding="utf-8", newline="").write(
    t.replace("commit db8ac757", "commit bd42a609"))
json.load(io.open(tp, encoding="utf-8-sig"))
print("ticket re-anchored")

# 2) round report r243 line: hash re-anchor both refs
rr = r"logs\iteration-loop\round_reports.md"
t = io.open(rr, encoding="utf-8", newline="").read()
assert "commit db8ac757" in t and "7c6bd66d" in t
t = t.replace("commit db8ac757", "commit bd42a609")
t = t.replace("独立 commit 7c6bd66d", "独立 commit 99a3043c")
addendum = ("2026-09-26 11:29 | r243 addendum (bm-b): S7 push rejected "
            "(bm-a landed 3ddd741f+89740a29 mid-round = T-70 两轴收口+其 r242 "
            "撞车 addendum) -> stash-pull-rebase 3-commit 重放：step1 "
            "autofill_state UU（mixed-dict+ledger：last_tick 11:10:01、"
            "launches union cap50、CRLF 翻译写回=r234 修正版解器 vs r242 LF-flip）"
            "；step2 冻结件应用零冲突；step3 12-UU 批按分类器正典（CODELY "
            "line-union 62+62->63 双机教训行全保 / compute_audit history "
            "union 203+201->204 零丢失 indent=2 / regime history union / "
            "dashboard 对 stage3 按 meta.generated_at 11:18:24>11:09:22 整字节"
            "包装保真 / daily-report 对 stage3 按 generated_at 11:18:22>11:09:21"
            "（分类器 UNKNOWN->r242 手工先例）/ 6 snapshot 件 ts 字段实探全取 "
            "stage3 新面）；毒化扫描 22 件零行首标记+14 JSON parse 净；"
            "stash-pop tick UU 再解（last_tick 11:20:01 union cap50 CRLF）；"
            "冻结 hash 漂移 re-anchor db8ac757->bd42a609（r242 漂移律）；"
            "解器存档 results/_r243bmb_replay_resolver.py（外置 TEMP 跑后回填，"
            "r231 律） | evidence: commits 99a3043c/bd42a609/75ca9a7f+本 addendum "
            "| next: T-78 s5b runner+SEED_REGISTRY+池注册+跑数判决\n")
with io.open(rr, "a", encoding="utf-8", newline="") as f:
    f.write(addendum)
print("round report re-anchored + addendum appended")

# 3) state.json did re-anchor
sp = r"logs\iteration-loop\state.json"
s = json.load(io.open(sp, encoding="utf-8"))
s["did"] = s["did"].replace("db8ac757", "bd42a609")
s["did"] += "; S7 push-collision replay-resolved (12-UU per skill canon, zero-loss)"
s["updated_at"] = "2026-09-26 11:29"
io.open(sp, "w", encoding="utf-8", newline="").write(
    json.dumps(s, ensure_ascii=False, indent=1) + "\n")
print("state re-anchored")

# 4) heartbeat: current_task re-anchor + last_seen refresh (epoch int law)
hp = r"fleet\machines\bm-b.json"
h = json.load(io.open(hp, encoding="utf-8"))
h["current_task"] = h["current_task"].replace("db8ac757", "bd42a609")
h["last_seen"] = "2026-09-26 11:29:30"
h["heartbeat_epoch_utc"] = int(time.time())
h["clock_read"] = time.strftime("%Y-%m-%dT%H:%M:%S")
io.open(hp, "w", encoding="utf-8", newline="").write(
    json.dumps(h, ensure_ascii=False, indent=1) + "\n")
d = json.load(io.open(hp, encoding="utf-8"))
assert isinstance(d["heartbeat_epoch_utc"], int)
print("heartbeat re-anchored epoch-int:", d["heartbeat_epoch_utc"])

# 5) archive replay resolver with provenance header
header = '''"""r243 addendum: S7 push-replay resolver provenance (bm-b).

Origin: %TEMP% r243_replay_resolver.py (+ r243_stash_resolver.py for
the post-rebase stash-pop tick) ran EXTERNAL per r231 law during the
S7 push-rejection rebase replay vs bm-a 3ddd741f+89740a29. Replay:
step1 99a3043c autofill UU mixed-dict+ledger (CRLF translation write =
r234 fix; r242 archived resolver had append-only-final-EOL bug leaving
LF body = the flip my S0 commit converged); step2 bd42a609 freeze
applied clean; step3 75ca9a7f 12-UU batch: CODELY line-union 62+62->63,
compute_audit history union 203+201->204 zero-loss (indent=2), regime
history union, dashboard pair stage3 by meta.generated_at 11:18:24>
11:09:22 raw bytes (r226 twin law), daily-report pair stage3 by
generated_at 11:18:22>11:09:21 (classifier UNKNOWN -> r242 manual
precedent), 6 snapshots field-probed take-side (updated/ts/generated
real keys per r242 lesson). Poison scan 22 files zero line-start
markers, 14 JSON parse-clean. Freeze hash drift db8ac757->bd42a609
re-anchored same round (r242 drift law).

--- resolver body as-run (step-3 batch) ---
'''
src = io.open(r"C:\Users\Administrator\AppData\Local\Temp\r243_replay_resolver.py",
              encoding="utf-8").read()
tail = '''

--- stash-pop resolver body as-run ---
'''
src2 = io.open(r"C:\Users\Administrator\AppData\Local\Temp\r243_stash_resolver.py",
               encoding="utf-8").read()
io.open(r"results\_r243bmb_replay_resolver.py", "w", encoding="utf-8",
        newline="\n").write(header + src + tail + src2)
print("resolver archived")
