# r684 bm-b: S7 push-race addendum line (r681 precedent) -- append-only gate
import io

FP = r"logs/iteration-loop/round_reports.md"
marker = "| round 684 addendum (bm-b)"
raw = io.open(FP, "rb").read().decode("utf-8", "replace")
assert raw.count(marker) == 0

LINE = (
    "2026-10-04T18:10:30+08:00 | round 684 addendum (bm-b) | S7 收口撞头实录："
    "push 三波竞速全按在册律收口——①首推被 non-FF 拒=origin 前移（bm-a r688 "
    "closeout 17:41 波 + bm-c r486 science_gates 修复波 17:44-17:57 已在 "
    "origin，我 r684 收口 18:00 同窗竞速）→ r437-iv merge 净路（rebase 被 "
    "daemon treadmill 脏面挡死）：14 UU 全过分类器=12 S6 可再生面 take-ours "
    "ts-newer（我 17:55-17:58 > bm-a 17:41）+ compute_audit history 行级 "
    "union 201+2=203 + token_usage machines per-key union side_pick=3（r456 "
    "断言在位）+ _attrition 快照 take-new；②二推被 pre-push 爪正确拦截（claw "
    "fetch 复核见 origin 再前移=bm-c r486 close 18:0x 波新增 _r486bmc_* "
    "finalize 件在我 tip 缺席=删除集假象·本地 behind 型 r648 判例）→ 二次 "
    "merge（单 UU=attrition 快照 take-new theirs 17:59:53>我 17:58:24）→ 三"
    "推 DELIVERED 584f0ecfe（push_verify ahead=0·零 --no-verify·零强推）；"
    "同窗观察=W3 judge 池面 4/4 done（fleet 三机接力收齐，finalize=bm-c "
    "在飞 MSG-1745 定谳·反重复不抢跑）+ 我 RC 池单元 CONTEST-YTD-P1-RC-0OF1 "
    "随 merge 落 origin（377 entries 双侧保全：我 RC entry + fleet W3 flips "
    "恒在）\n"
)
with io.open(FP, "ab") as f:
    f.write(LINE.encode("utf-8"))
chk = io.open(FP, "rb").read().decode("utf-8", "replace")
assert chk.count(marker) == 1
print("addendum appended")
